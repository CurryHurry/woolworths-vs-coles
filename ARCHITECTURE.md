# Supermarket Checker — Architecture & Progress

Personal app to compare Woolworths vs Coles grocery prices at specific Melbourne stores.
Built with Python + Streamlit. Local-first; can be deployed to Streamlit Cloud later.

---

## Stack
- **Python 3.10+** + **Streamlit** — UI and app logic, one command to run
- **requests** — HTTP calls to supermarket APIs
- **No database** — prices cached in `cache.json` (gitignored)

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501

## Deploy Later (free)
Push to GitHub → connect to https://streamlit.io/cloud → one-click deploy.

---

## File Map

| File | Purpose | Status |
|---|---|---|
| `ARCHITECTURE.md` | This file — living doc | ✅ done |
| `requirements.txt` | Python dependencies | ✅ done |
| `.gitignore` | Excludes cache, pycache | ✅ done |
| `items.py` | ~30 predefined grocery items by category | ✅ done |
| `stores.py` | Dynamic Melbourne store search by suburb | ✅ done |
| `scraper.py` | API clients for Woolworths + Coles + cache layer | ✅ done |
| `app.py` | Streamlit UI — store pickers, checklist, results | ✅ done |
| `cache.json` | Auto-generated at runtime, gitignored | auto |
| `stores_cache.json` | Auto-generated at runtime, gitignored | auto |

## ALL PARTS COMPLETE — Built 2026-06-13

---

## Data Flow

```
User selects stores + items → clicks Compare
  └─ scraper.py checks cache.json (valid if fetched today)
       ├─ cache hit  → return cached prices immediately
       └─ cache miss → call Woolworths API + Coles API
                         └─ save to cache.json
app.py renders results table + winner
```

---

## API Notes

Both supermarkets use **unofficial APIs** (reverse-engineered from their websites).
No API key needed. Widely used by Australian developers for personal projects.
Risk: could break if either supermarket redesigns their site.

### Woolworths
- Search: `https://www.woolworths.com.au/apis/ui/Search/products`
- Params: `searchTerm`, `pageSize`, `pageNumber`, `sortType=TraderRelevance`, `storeId`
- Store finder: `https://www.woolworths.com.au/apis/ui/StoreLocator/pickup`
- Returns JSON; top result price used

### Coles
- Search: `https://www.coles.com.au/api/2.0/catalog/products`
- Params: `q` (search term), `storeId`, `pageSize`, `page`
- Returns JSON; top result price used
- Note: Coles API requires `ocp-apim-subscription-key` header — value scraped from their page or using known working key

---

## Cache Format (cache.json)

```json
{
  "woolworths": {
    "STORE_ID": {
      "chicken breast": {
        "price": 12.00,
        "unit": "kg",
        "display_name": "Woolworths RSPCA Approved Chicken Breast",
        "fetched_at": "2026-06-13"
      }
    }
  },
  "coles": { ... }
}
```

Cache is considered fresh if `fetched_at` matches today's date.
Force Refresh button bypasses the cache.

---

## Predefined Items (items.py)

~30 common grocery items grouped into categories. These map to search terms
sent to each supermarket's API. The top matching result is used.

Categories: Proteins, Dairy, Bread, Pantry, Produce, Frozen, Drinks, Household

---

## Known Limitations

1. Product matching is search-based (top result). Not guaranteed to be the exact
   product you'd physically buy in-store.
2. Prices are standard shelf price — not Everyday Rewards / Flybuys member pricing.
3. Unofficial APIs may break without notice if supermarkets update their websites.
4. Store IDs in stores.py were verified as of mid-2026; may need updating if stores open/close.

---

## Session Resume Notes

If picking up from a new Claude session:
- Read this file first for full context
- Check the File Map table above for what's done vs pending
- The plan file is at: C:\Users\ashle\.claude\plans\transient-drifting-metcalfe.md
