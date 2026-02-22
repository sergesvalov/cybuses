import urllib.request, re
from bs4 import BeautifulSoup

url = 'https://intercity-buses.com/en/routes/paphos-ayia-napa-paralimni-paphos/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')

    print('--- RAW ASTERISKS TEXT IN HTML ---')
    for tag in soup.find_all(['p', 'div', 'span', 'li', 'td', 'strong', 'em', 'b', 'i']):
        txt = tag.get_text(' ', strip=True)
        if txt.startswith('*'):
            print(repr(txt))
            match = re.match(r'^(\*+)\s*(.+)', txt)
            if match:
                print(f"MATCH: key={match.group(1)} val={match.group(2)}")
            else:
                print("NO MATCH")
except Exception as e:
    print(f"Error: {e}")
