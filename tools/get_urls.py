from curl_cffi import requests
import re

def main():
    print("Fetching Intercity Routes...")
    r = requests.get('https://intercity-buses.com/en/routes/', impersonate='chrome120')
    links = set(re.findall(r'href="(https://intercity-buses\.com/en/routes/[^"]+)"', r.text))
    for link in sorted(links):
        print(link)
        
    print("\nFetching PafosBuses Routes...")
    r = requests.get('https://www.pafosbuses.com/busroutes', impersonate='chrome120')
    links = set(re.findall(r'href="(https://www\.pafosbuses\.com/[^"]+612[^"]*)"', r.text))
    for link in sorted(links):
        print(link)

if __name__ == "__main__":
    main()
