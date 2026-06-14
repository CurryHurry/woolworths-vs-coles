# Known Issues

Running record of issues hit during development. Resolved issues are removed.

---

## Active Issues

None.

---

## Resolved Issues (recent)

---

### Prices not comparable 1-for-1 (e.g. WW $22 chicken vs Coles $4 chicken)
- Vague search terms like `"chicken breast per kg"` returned per-kg butcher prices from WW and a small pre-pack from Coles — completely different products.
- **Fix:** Tightened all search terms in `items.py` to specify pack sizes (e.g. `"chicken breast 500g"`). Also renamed item display names to include the size (e.g. "Chicken Breast 500g") so the selected item clearly states what pack is expected. Added matched product name + unit display under each price in the results table so mismatches are immediately visible without expanding the collapsible section.

---

## Resolved Issues (older)

### `pip` not recognised
- `pip` command not found in terminal
- **Fix:** Python was not installed. Install from python.org with "Add Python to PATH" ticked.

### `streamlit` not recognised after install
- `streamlit` command not found even after `pip install`
- **Fix:** Python Scripts folder not in PATH. Use `python -m streamlit run app.py` instead of `streamlit run app.py` — works every time regardless of PATH.

### Store locator APIs returning 404
- Both Woolworths and Coles store locator endpoints (`/apis/ui/StoreLocator/pickup` and `/api/2.0/storelocator/search`) returned 404
- **Fix:** Removed dynamic store selection entirely. For packaged goods, prices are the same nationwide. App now compares standard national prices.

### `get_prices()` missing `woolworths_store_id` and `coles_store_id` after code update
- Streamlit had the old `scraper.py` cached in memory after the file was updated
- **Fix:** Close the terminal running Streamlit and reopen a new one, then run `python -m streamlit run app.py` again.

### Coles mobile API returning N/A
- The Coles iOS Shopmate app API credentials (`X-Coles-API-Key` / `X-Coles-API-Secret`) were from 2018 and are expired
- **Fix:** Switched to the Coles website's Next.js data API (`/_next/data/{buildId}/en/search/products.json`) which needs no credentials.

### Coles homepage blocked by Incapsula / Akamai bot detection
- `requests` returned a bot-challenge page instead of real HTML. `curl_cffi` with Chrome TLS impersonation bypasses Incapsula, but Coles also runs Akamai which requires JavaScript execution — something `curl_cffi` alone cannot fake.
- **Fix:** Use `browser_cookie3` to load session cookies from the user's Chrome browser. Chrome already solved Akamai's JS challenge when the user last visited coles.com.au, so those cookies are trusted. Added `browser_cookie3>=0.19.1` to `requirements.txt`.
- **Ongoing behaviour:** If Coles prices stop working, visit `https://www.coles.com.au` in Chrome for a few seconds to refresh the cookies, then re-run the app. Cookies typically last days to weeks.

### Coles `_next/data` API returning redirect with no results
- `/en/search.json` returned a `__N_REDIRECT` to `/search/products` with empty results
- **Fix:** Corrected URL path to `/en/search/products.json`.
