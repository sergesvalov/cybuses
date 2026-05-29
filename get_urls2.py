import requests
import re

def main():
    print("INTERCITY:")
    r = requests.get('https://intercity-buses.com/en/routes/', headers={'User-Agent': 'Mozilla/5.0'})
    links = set(re.findall(r'href="(https://intercity-buses\.com/en/routes/[^"]+)"', r.text))
    for link in sorted(links):
        print(link)
        
    print("\nPAFOS:")
    r = requests.get('https://www.pafosbuses.com/busroutes', headers={'User-Agent': 'Mozilla/5.0'})
    links = set(re.findall(r'href="(https://www\.pafosbuses\.com/[^"]+612[^"]*)"', r.text))
    for link in sorted(links):
        print(link)

if __name__ == "__main__":
    main()
