import asyncio
from curl_cffi import requests

def test_cf():
    url = "https://intercity-buses.com/en/routes/limassol-paphos-paphos-limassol/"
    print("Testing curl_cffi...")
    try:
        r = requests.get(url, impersonate="chrome110")
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            print(f"Success! Content length: {len(r.text)}")
            return True
        else:
            print("Failed to bypass CF.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_cf()
