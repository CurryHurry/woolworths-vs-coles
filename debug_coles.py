"""Run this once to inspect the raw Coles API response structure."""
import re
import json
from curl_cffi import requests as curl_requests

session = curl_requests.Session(impersonate="chrome")

print("Fetching Coles homepage to get buildId (using Chrome TLS fingerprint)...")
resp = session.get("https://www.coles.com.au/", timeout=20)
print(f"Status code: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('Content-Type', 'unknown')}")
print(f"\nFirst 500 chars of response:\n{resp.text[:500]}")

match = re.search(r'"buildId"\s*:\s*"([^"]+)"', resp.text)
if not match:
    print("\nERROR: buildId not found in page")
    exit(1)

build_id = match.group(1)
print(f"buildId: {build_id}")

url = f"https://www.coles.com.au/_next/data/{build_id}/en/search/products.json"
print(f"\nFetching: {url}?q=milk&page=1")
resp2 = session.get(url, params={"q": "milk", "page": 1}, headers={"Accept": "application/json"}, timeout=15)
print(f"Status: {resp2.status_code}")

data = resp2.json()

# Print the top-level keys
print(f"\nTop-level keys: {list(data.keys())}")

# Try to navigate to results
page_props = data.get("pageProps", {})
print(f"pageProps keys: {list(page_props.keys())}")

search = page_props.get("searchResults") or page_props.get("search") or {}
print(f"searchResults/search keys: {list(search.keys()) if isinstance(search, dict) else type(search)}")

results = search.get("results", []) if isinstance(search, dict) else []
print(f"\nNumber of results: {len(results)}")
if results:
    print(f"\nFirst result keys: {list(results[0].keys())}")
    print(f"\nFirst result (pretty):")
    print(json.dumps(results[0], indent=2, default=str)[:1500])
else:
    # Dump pageProps to help diagnose
    print("\nNo results found. Dumping pageProps structure (first 2000 chars):")
    print(json.dumps(page_props, indent=2, default=str)[:2000])
