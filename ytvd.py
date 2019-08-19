import datetime
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import build_opener

API_KEY_LST = []

i = 0
API_KEY = API_KEY_LST[0]

class GdataError(Exception):
    """Gdata query failed."""
    pass


opener = build_opener() #so it's not built everytime a video is to be fetched

def fetch_video_gdata(video_id, fetch_snips=True, fetch_stats=True, fetch_cd=True, api_key=API_KEY):

	"""
		Fetch Gdata on a video
	"""
	
	#"part" string for the query. will save some quota.
	part_str = 'id'
	if fetch_snips:
		part_str += ",snippet"
	if fetch_stats:
		part_str += ",statistics"
	if fetch_cd:
		part_str += ",contentDetails"
	
	#query to get right data from googleapi
	query = {'part': part_str,
		'maxResults': 1,
		'id': video_id}

	#make a request URL to fetch the youtube gdata api
	query['key'] = api_key
	gdata_url = "https://www.googleapis.com/youtube/v3/videos?" + urlencode(query)

	#read url, raises error if failed to fetch data
	try:
		gdata = json.loads(opener.open(gdata_url).read().decode('utf-8'))
	except HTTPError as e:
		errdata = e.file.read().decode()
		error = json.loads(errdata)['error']['message']
		errmsg = 'Youtube Error %d: %s' % (e.getcode(), error)
		raise GdataError(errmsg)
	
	#return data as dict and gdata url
	return gdata, gdata_url


def test_api_keys():
	
	"""
		Test if the API keys are valid to fetch data
	"""
	
	for api_key in API_KEY_LST:
		try:
			_ = fetch_video_gdata("lYHA_7vxrgc", False, False, False, api_key=api_key)
			print(api_key)
		except GdataError as e:
			print("\n!!! API key: %s has FAILED to fetch data !!!\n%s\n"%(api_key,e))


def make_gdata_request(func, *args, api_key=None):

	"""
		Try making a request via the function "func". If
		a request has failed, this could either main no
		connection has been made or the API key has exceeded
		maximum quota. 
	"""

	global i, API_KEY
	
	#I though api_key = API_KEY as the keyword variable would work because that's
	#then called again when API_KEY is updated. But it seems that it would just 
	#be assigned to the first value of API_KEY.
	if api_key is None:
		api_key = API_KEY

	while True:
		try:
			return func(*args, api_key=api_key)
		except URLError as e:
			raise URLError("No connection made.")
		except GdataError as e:
			i += 1
			try: 
				api_key = API_KEY_LST[i]
				API_KEY = api_key
			except IndexError:
				raise GdataError("No api keys left.")


def url_to_id(id_or_url):
	
	"""
		Get ID of YouTube video from URL or pass the input
		if it's 11 characters long, which is the length of a
		YouTube ID. 
	"""
	
	if len(id_or_url) == 11:
		vid_id = id_or_url
	else:
		try:
			vid_id = re.findall(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',id_or_url)[0]
		except IndexError:
			raise IndexError("Insert valid URL or ID string.")
	return vid_id


class ytvd():
	
	"""
		Main class of the python program.
		
		fetch_snips: boolean to greenlight the download of data belonging to
			snippet item in the dictionary, which are "published, userid, title, 
			description, username and tags."
		fetch_stats: boolean to download statistics. Includes: "views, likes, dislikes
			and (mount of) comments".
		fetch_cd: boolean to download content details, of which the ONLY useful item is
			the "duration" of the video. 
	"""
	
	def __init__(self, id_or_url=None, gdata_dict=None, api_key=None, fetch_snips=True, fetch_stats=True, fetch_cd=True):
		
		#
		if not id_or_url and not gdata_dict:
			raise ValueError("Insert either video id/url or gdata dictionary.")
		elif id_or_url and gdata_dict:
			raise ValueError("Can't add both video id AND comment id!")
		
		#download gdata for the video, get gdata_dict
		self.connection_made = True
		self.no_api_keys = False
		
		if id_or_url is not None:
		
			video_id = url_to_id(id_or_url)

			try:
				gdata_dict, gdata_url = make_gdata_request(fetch_video_gdata, video_id, fetch_snips, fetch_stats, fetch_cd, api_key=api_key)
			except URLError:
				self.connection_made = False
			except GdataError:
				self.no_api_keys = True
		
		#
		if self.connection_made or (not self.no_api_keys):
		
			self.gdata_dict = gdata_dict
			
			items = gdata_dict['items'][0]
			
			self.video_id = items['id']
			self.video_url = "https://www.youtube.com/watch?v=%s"%self.video_id
			
			#make some variables to make parsing the dict easier
			#then store variables into class variables
			if 'snippet' in items:
				snippet = items['snippet']
				self.published = datetime.datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ") #UTC
				self.userid = snippet['channelId']
				self.title = snippet['title']
				self.description = snippet['description']
				self.username = snippet['channelTitle']
				if 'tags' in snippet:
					self.tags = snippet['tags']
				else:
					self.tags = None
			if 'statistics' in items:
				statistics = items['statistics']
				self.views = int(statistics['viewCount'])
				if 'likeCount' in statistics:
					self.likes = int(statistics['likeCount'])
				else:
					self.likes = None
				if 'dislikeCount' in statistics:
					self.dislikes = int(statistics['dislikeCount'])
				else:
					self.dislikes = None
				if 'commentCount' in statistics:
					self.comments = int(statistics['commentCount'])
				else:
					self.comments = None
			if 'contentDetails' in items:
				contentdetails = items['contentDetails']
				#duration gives a little bit of problems due to weird formatting :'D
				#converts PT3M27S to 00:03:27
				gdur = contentdetails['duration']
				gdur_split = re.findall(r"(\d+)", gdur)[::-1]
				dur = ['00' for _ in range(3)]
				for j in range(len(gdur_split)): 
					dur[j] = gdur_split[j]
				self.duration = "".join(["%02d:"%int(t) for t in dur[::-1]])[:-1]