# ytvd.py

Script to download YouTube Video Data with an API key. Pretty much a pafy clone but without the youtube-dl bindings making it much faster. Useful to quickly check video data without a browser visit.

First you need to get (some) API keys at https://console.developers.google.com/ . If you have multiple google account you can get multiple of these api keys. 

Once you got these keys, manually put them in the "API_KEY_LST = []" in the ytvd.py file. Having multiple of these keys allows you to bypass the daily quota limit Google imposes on you if you do big YouTube data analysis. Once one api key has it's quota limit exceeded, it will toggle to the next one.  

Then, get the data on your python console with:

```
import ytvd

vd = ytvd.ytvd( URL OR ID )

#snippet. Snippet only? ytvd.ytvd( URL OR ID, fetch_stats=False, fetch_cd=False)
vd.published
vd.userid
vd.title
vd.description
vd.tags

#statistics. Statstistics only? ytvd.ytvd( URL OR ID, fetch_snips=False, fetch_cd=False)
vd.views
vd.likes
vd.dislikes
vd.comments

#contentDetails. Just this? ytvd.ytvd( URL OR ID, fetch_snips=False, fetch_stats=False)
vd.duration
```

Use the fetch_snips, fetch_stats, fetch_cd = True/False options in appropriate situations to minimise quota usage.

Want to log things over time? Use this general format:

```
#... in (main) Thread

while True:
  
  vd = ytvd.ytvd( URL OR ID )
  
  DO STUFF ON VD
  
  time.sleep(60)
```

Want to quickly check which API keys that are stored in the API_KEYS_LST work and which don't?

```
import ytvd

ytvd.test_api_keys()
```

