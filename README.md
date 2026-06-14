# Woolworths vs Coles Price Comparison

A Streamlit web app to compare grocery prices between **Woolworths** and **Coles** in Melbourne. Tests the hypothesis that only one supermarket goes on sale each week.

## Features

- **Side-by-side price comparison** — See which supermarket is cheaper for your regular groceries
- **Weekly savings calculation** — Know exactly how much you'd save by shopping at the cheaper store
- **Per-kg normalization** — Meats and produce are compared fairly on a $/kg basis, regardless of pack size
- **Daily price caching** — Prices are cached locally and refresh daily; no repeated API calls
- **Expandable category sections** — Collapse/expand by category (Proteins, Dairy, Produce, etc.) with visual winner indicators
- **Smart search** — Find items quickly with the sidebar search box; categories auto-expand as you type
- **Visual hierarchy** — Clear distinction between category headers, item names, and store prices
- **Price freshness indicator** — See exactly when prices were last fetched
- **Responsive design** — Metrics grid adapts to narrow screens

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

### 3. Use it
- Select your regular grocery items from the sidebar (use the search box to find them quickly)
- Click **Compare Prices**
- See the results: which supermarket is cheaper this week, and by how much

## How It Works

The app fetches live prices from both supermarkets using their unofficial APIs:

- **Woolworths** — Public search API (no authentication required)
- **Coles** — Next.js data API with bot-detection bypass using Chrome browser cookies

Prices are cached daily by item name in `cache.json`. The first comparison of the day fetches fresh prices; subsequent comparisons reuse the cache. Use **Force refresh** to bypass the cache and re-fetch immediately.

### Per-kg Normalization

Items marked `per_kg: True` in `items.py` (meats, produce) are compared on a **$/kg basis** rather than pack price, so a 500g chicken breast and a 1kg chicken breast are fairly compared. Totals assume 1 kg for these items.

## Caveats

- **Prices are standard shelf prices only** — Does not include Everyday Rewards member pricing (Woolworths) or Flybuys pricing (Coles)
- **Product matching is search-based** — The app uses each store's top search result; it may not be the exact product you'd buy. Click "View product" in the results to verify
- **Unofficial APIs** — Both Woolworths and Coles APIs are reverse-engineered from their websites. The app may break if either store redesigns their site
- **Coles cookies** — The app uses browser cookies from Chrome to bypass Coles' bot detection. If Coles prices stop loading, visit https://www.coles.com.au in Chrome for a few seconds, then clear the cache and try again

## File Structure

```
.
├── app.py              # Streamlit UI (sidebar, results, metrics, styling)
├── scraper.py          # Woolworths + Coles API clients, price fetching
├── items.py            # Predefined grocery list (~33 items, 8 categories)
├── stores.py           # Store IDs (for future multi-store support)
├── cache.json          # Auto-generated; daily price cache (gitignored)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Stack

- **Streamlit** — Single-command web app framework (Python only, no JavaScript needed)
- **requests** + **curl_cffi** — HTTP clients for supermarket APIs
- **browser_cookie3** — Load Chrome cookies to bypass Coles bot detection

## Future Ideas

- Support for other Australian cities (Sydney, Brisbane, etc.)
- Multi-store selection within Melbourne (compare specific suburbs)
- Historical price trends (has chicken breast been on sale every week?)
- Email alerts when a store goes on sale
- Streamlit Cloud deployment

## License

MIT — See LICENSE file for details.

---

Built to test the hypothesis: *Does only one supermarket go on sale each week?*
