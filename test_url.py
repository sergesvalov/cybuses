import urllib.request
req = urllib.request.Request('https://intercity-buses.com/en/routes/nicosia-limassol-limassol-nicosia/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    print(urllib.request.urlopen(req).getcode())
except Exception as e:
    print(e)
