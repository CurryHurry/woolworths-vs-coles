import json
import os
import requests

STORES_CACHE_FILE = "stores_cache.json"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def fetch_woolworths_stores(suburb: str) -> list[dict]:
    url = "https://www.woolworths.com.au/apis/ui/StoreLocator/pickup"
    params = {
        "suburb": suburb,
        "sortType": "Distance",
        "pageSize": 20,
        "pageNumber": 1,
    }
    headers = {**_HEADERS, "Referer": "https://www.woolworths.com.au/"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    stores = []
    for s in data.get("Stores", []):
        stores.append({
            "id": str(s["StoreId"]),
            "name": s["Name"],
            "suburb": s["Suburb"],
            "display": f"{s['Name']} ({s['Suburb']})",
        })
    return stores


def fetch_coles_stores(suburb: str) -> list[dict]:
    # Coles store locator — endpoint may need updating if Coles redesigns their site
    url = "https://www.coles.com.au/api/2.0/storelocator/search"
    params = {"q": suburb, "pageSize": 20}
    headers = {**_HEADERS, "Referer": "https://www.coles.com.au/"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    stores = []
    # Coles returns stores under different keys depending on API version — try both
    raw = data.get("stores") or data.get("outlets") or data.get("results") or []
    for s in raw:
        store_id = str(s.get("id") or s.get("storeId") or s.get("store_id", ""))
        name = s.get("name") or s.get("storeName", "Unknown")
        suburb_val = s.get("suburb") or s.get("locality", "")
        stores.append({
            "id": store_id,
            "name": name,
            "suburb": suburb_val,
            "display": f"{name} ({suburb_val})",
        })
    return stores


def load_stores_cache() -> dict:
    if os.path.exists(STORES_CACHE_FILE):
        with open(STORES_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_stores_cache(cache: dict) -> None:
    with open(STORES_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_stores(suburb: str) -> tuple[list[dict], list[dict], list[str]]:
    """
    Returns (woolworths_stores, coles_stores, errors).
    Results are cached per suburb so repeat searches don't hit the network.
    """
    cache = load_stores_cache()
    key = suburb.strip().lower()
    errors = []

    woolworths_stores = cache.get("woolworths", {}).get(key)
    if not woolworths_stores:
        try:
            woolworths_stores = fetch_woolworths_stores(suburb)
            cache.setdefault("woolworths", {})[key] = woolworths_stores
            save_stores_cache(cache)
        except Exception as e:
            errors.append(f"Woolworths store search failed: {e}")
            woolworths_stores = []

    coles_stores = cache.get("coles", {}).get(key)
    if not coles_stores:
        try:
            coles_stores = fetch_coles_stores(suburb)
            cache.setdefault("coles", {})[key] = coles_stores
            save_stores_cache(cache)
        except Exception as e:
            errors.append(f"Coles store search failed: {e}")
            coles_stores = []

    return woolworths_stores, coles_stores, errors


def clear_stores_cache() -> None:
    if os.path.exists(STORES_CACHE_FILE):
        os.remove(STORES_CACHE_FILE)
