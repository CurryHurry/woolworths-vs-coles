import json
import os
import re as _re
from datetime import date
from urllib.parse import quote as _urlquote

import requests

CACHE_FILE = "cache.json"
TODAY = str(date.today())

# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"woolworths": {}, "coles": {}}


def _save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def _is_fresh(entry: dict) -> bool:
    return entry.get("fetched_at") == TODAY


def clear_cache() -> None:
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)


# ---------------------------------------------------------------------------
# Per-kg price helpers
# ---------------------------------------------------------------------------

def _grams_from_size(size: str) -> float | None:
    """Parse '500g', '1kg', '1.5kg' → grams. Returns None if unparseable."""
    if not size:
        return None
    s = size.lower().strip()
    if m := _re.search(r"([\d.]+)\s*kg", s):
        return float(m.group(1)) * 1000
    if m := _re.search(r"([\d.]+)\s*g\b", s):
        return float(m.group(1))
    return None


def _per_kg(price: float, size: str) -> float | None:
    """Calculate $/kg from a pack price and size string. Returns None if size unknown."""
    grams = _grams_from_size(size)
    if grams and grams > 0:
        return round(price / (grams / 1000), 2)
    return None


# ---------------------------------------------------------------------------
# Woolworths
# Confirmed working endpoint — no API key required.
# ---------------------------------------------------------------------------

def _fetch_woolworths_price(search_term: str) -> dict | None:
    url = "https://www.woolworths.com.au/apis/ui/Search/products"
    params = {
        "searchTerm": search_term,
        "pageNumber": 1,
        "pageSize": 5,
        "sortType": "TraderRelevance",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.woolworths.com.au/",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    bundles = data.get("Products") or []
    for bundle in bundles:
        for p in (bundle.get("Products") or []):
            price = p.get("Price")
            if price is None:
                continue

            price = float(price)
            size  = p.get("PackageSize", "")

            # Woolworths provides CupPrice / CupMeasure (e.g. $1.80 per 100g).
            # Normalise to $/kg so we can compare fairly across different pack sizes.
            unit_price: float | None = None
            cup_price   = p.get("CupPrice")
            cup_measure = (p.get("CupMeasure") or "").lower()
            if cup_price is not None:
                if "100g" in cup_measure:
                    unit_price = round(float(cup_price) * 10, 2)
                elif "kg" in cup_measure:
                    unit_price = round(float(cup_price), 2)
            # Fallback: calculate from pack size if API didn't give a cup price
            if unit_price is None:
                unit_price = _per_kg(price, size)

            stockcode = p.get("Stockcode", "")
            url_name  = p.get("UrlFriendlyName", "")
            if stockcode and url_name:
                product_url = f"https://www.woolworths.com.au/shop/productdetails/{stockcode}/{url_name}"
            else:
                product_url = f"https://www.woolworths.com.au/shop/search/products?searchTerm={_urlquote(search_term)}"

            return {
                "price":      price,
                "was_price":  float(p["WasPrice"]) if p.get("WasPrice") else None,
                "unit":       size,
                "unit_price": unit_price,   # $/kg, or None if weight unknown
                "display_name": p.get("Name", search_term),
                "url":        product_url,
                "fetched_at": TODAY,
            }
    return None


# ---------------------------------------------------------------------------
# Coles
# Coles runs on Next.js and is protected by Incapsula bot detection, which
# checks the TLS fingerprint of the client. Regular `requests` is blocked.
# curl_cffi impersonates Chrome's TLS fingerprint and passes the check.
#
# Flow:
#   1. Open a persistent curl_cffi session (carries Incapsula cookies)
#   2. GET coles.com.au/ → extract buildId from __NEXT_DATA__ JSON in HTML
#   3. GET /_next/data/{buildId}/en/search/products.json?q={term}
# ---------------------------------------------------------------------------

from curl_cffi import requests as _curl

_coles_session: "_curl.Session | None" = None
_coles_build_id: "str | None" = None


def _get_coles_session() -> "_curl.Session":
    global _coles_session
    if _coles_session is not None:
        return _coles_session

    session = _curl.Session(impersonate="chrome120")

    # Load cookies from the user's Chrome browser — these have already passed
    # Akamai's JS challenge so the site treats our requests as a real browser.
    # Requires visiting coles.com.au in Chrome at least once before running.
    try:
        import browser_cookie3
        cj = list(browser_cookie3.chrome(domain_name=".coles.com.au"))
        for c in cj:
            session.cookies.set(c.name, c.value, domain=c.domain, path=c.path)
        print(f"[coles] loaded {len(cj)} Chrome cookies")
    except Exception as e:
        print(f"[coles] Chrome cookie load failed — visit coles.com.au in Chrome first: {e}")

    _coles_session = session
    return _coles_session


def _get_coles_build_id() -> str:
    global _coles_build_id
    if _coles_build_id:
        return _coles_build_id
    session = _get_coles_session()
    resp = session.get("https://www.coles.com.au/", timeout=20)
    resp.raise_for_status()
    match = _re.search(r'"buildId"\s*:\s*"([^"]+)"', resp.text)
    if not match:
        raise ValueError(
            "Could not find Coles buildId — Coles may have changed their site structure"
        )
    _coles_build_id = match.group(1)
    return _coles_build_id


def _fetch_coles_price(search_term: str) -> dict | None:
    build_id = _get_coles_build_id()
    session  = _get_coles_session()
    url = f"https://www.coles.com.au/_next/data/{build_id}/en/search/products.json"
    resp = session.get(
        url,
        params={"q": search_term, "page": 1},
        headers={"Accept": "application/json"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    results = (
        data.get("pageProps", {})
            .get("searchResults", {})
            .get("results", [])
    )
    for item in results:
        # Skip non-purchasable tiles (ads, banners). Any item with a name and
        # a price is a real product regardless of what _type Coles assigns it.
        if not item.get("name"):
            continue
        pricing = item.get("pricing") or {}
        price = pricing.get("now") or pricing.get("price")
        if price is None:
            continue

        price = float(price)
        was   = pricing.get("was")
        size  = item.get("size") or ""
        name  = item.get("name", search_term)

        # Coles stores a per-unit price in pricing.unit.
        # ofMeasureUnits is a unit-label STRING (e.g. "kg"), not a quantity.
        unit_price: float | None = None
        unit_obj  = pricing.get("unit") or {}
        raw_up    = unit_obj.get("price")
        up_unit   = (unit_obj.get("ofMeasureUnits") or "").lower().strip()
        if raw_up is not None:
            if up_unit in ("kg", "g"):
                # Coles normalises unit.price to $/kg for all weight-based products.
                # "g" means the product is measured in grams, NOT that the price is per gram.
                unit_price = round(float(raw_up), 2)
            # ea / l / ml → don't normalise to $/kg
        # Fallback: calculate from size string or label
        if unit_price is None:
            unit_price = _per_kg(price, size or unit_obj.get("label", ""))

        # Construct product URL
        coles_id = item.get("id", "")
        if coles_id:
            slug = _re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            product_url = f"https://www.coles.com.au/product/{slug}-{coles_id}"
        else:
            product_url = f"https://www.coles.com.au/search?q={_urlquote(search_term)}"

        return {
            "price":      price,
            "was_price":  float(was) if was else None,
            "unit":       size,
            "unit_price": unit_price,   # $/kg, or None if weight unknown
            "display_name": name,
            "url":        product_url,
            "fetched_at": TODAY,
        }
    return None


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_prices(
    item_names: list[str],
    search_terms: dict[str, str],
    force_refresh: bool = False,
) -> dict[str, dict]:
    cache = _load_cache()
    cache.setdefault("woolworths", {})
    cache.setdefault("coles", {})

    results = {}

    for item_name in item_names:
        search = search_terms.get(item_name, item_name)
        entry  = {"woolworths": None, "coles": None, "error": None}
        errors = []

        # Woolworths
        cached_ww = cache["woolworths"].get(item_name)
        if not force_refresh and cached_ww and _is_fresh(cached_ww):
            entry["woolworths"] = cached_ww
        else:
            try:
                result = _fetch_woolworths_price(search)
                if result:
                    cache["woolworths"][item_name] = result
                    entry["woolworths"] = result
                else:
                    errors.append("Woolworths: no match found")
            except Exception as e:
                errors.append(f"Woolworths error: {e}")

        # Coles
        cached_c = cache["coles"].get(item_name)
        if not force_refresh and cached_c and _is_fresh(cached_c):
            entry["coles"] = cached_c
        else:
            try:
                result = _fetch_coles_price(search)
                if result:
                    cache["coles"][item_name] = result
                    entry["coles"] = result
                else:
                    errors.append("Coles: no match found")
            except Exception as e:
                errors.append(f"Coles error: {e}")

        if errors:
            entry["error"] = "; ".join(errors)
        results[item_name] = entry

    _save_cache(cache)
    return results


def format_price(price: float | None) -> str:
    if price is None:
        return "N/A"
    return f"${price:.2f}"
