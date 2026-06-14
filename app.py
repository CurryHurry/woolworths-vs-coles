import html as _html
from datetime import datetime
import streamlit as st
from items import ITEMS, get_search_term, is_per_kg
from scraper import get_prices, format_price, clear_cache

CATEGORY_ICONS = {
    "Proteins":  "🥩",
    "Dairy":     "🥛",
    "Bread":     "🍞",
    "Pantry":    "🥫",
    "Produce":   "🥦",
    "Frozen":    "❄️",
    "Drinks":    "🥤",
    "Household": "🧴",
}

st.set_page_config(
    page_title="Supermarket Price Checker",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Page background ---- */
.stApp { background-color: #f9fafb; }

/* ---- Top toolbar (the "Deploy" bar) ---- */
[data-testid="stHeader"] {
    background-color: #0f172a !important;
    border-bottom: none !important;
}
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"]::before {
    content: "Supermarket Price Checker";
    font-size: 1.0rem;
    font-weight: 700;
    color: #ffffff;
    position: absolute;
    left: 4rem;
    top: 10px;
}
[data-testid="stHeader"]::after {
    content: "Woolworths vs Coles  ·  Standard shelf prices. Meats & produce compared per kg.";
    font-size: 0.75rem;
    font-weight: 400;
    color: rgba(255,255,255,0.60);
    position: absolute;
    left: 4rem;
    bottom: 10px;
}

/* Make all header toolbar icons/buttons white on dark bg */
[data-testid="stToolbar"] button { color: rgba(255,255,255,0.85) !important; }
[data-testid="stToolbar"] button svg { fill: rgba(255,255,255,0.85) !important; stroke: rgba(255,255,255,0.85) !important; }
[data-testid="stToolbar"] span, [data-testid="stToolbar"] p { color: rgba(255,255,255,0.85) !important; }
[data-testid="stStatusWidget"] { color: rgba(255,255,255,0.85) !important; }
[data-testid="stStatusWidget"] svg { fill: rgba(255,255,255,0.85) !important; }
/* Sidebar collapse/expand toggle button */
[data-testid="stSidebarCollapsedControl"] { background: #1e293b !important; border-right: 1px solid #334155 !important; }
[data-testid="stSidebarCollapsedControl"] button { color: #ffffff !important; }
[data-testid="stSidebarCollapsedControl"] button svg { fill: #ffffff !important; stroke: #ffffff !important; }
[data-testid="collapsedControl"] svg { fill: #ffffff !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }

/* ---- Expanders: main content (category sections) ---- */
[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    box-shadow: none !important;
    margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.90rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    background: #f8fafc !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    border: none !important;
}
[data-testid="stExpander"] summary:hover { background: #f1f5f9 !important; }
[data-testid="stExpander"] summary p { font-size: 0.90rem !important; color: #0f172a !important; font-weight: 700 !important; }

/* ---- Expanders: sidebar override (item selection) ---- */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: none !important;
    border-radius: 8px !important;
    background: transparent !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    background: #f3f4f6 !important;
    border-radius: 8px !important;
    padding: 7px 10px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover { background: #e5e7eb !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p { font-size: 0.85rem !important; color: #374151 !important; font-weight: 600 !important; }

/* ---- Custom 4-metric row ---- */
.metrics-row {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px; margin: 12px 0 16px;
}

/* ---- Price freshness line ---- */
.freshness {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.80rem; color: #64748b; margin: 0 0 14px 2px;
}
.freshness .dot { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; display: inline-block; }
.metric-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 14px 16px;
}
.metric-card.metric-ww  { background: #f0fdf4; border-color: #bbf7d0; }
.metric-card.metric-col { background: #fff1f2; border-color: #fecdd3; }
.metric-label {
    font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.5px;
    color: #64748b; margin-bottom: 6px; font-weight: 600;
}
.metric-value { font-size: 1.3rem; font-weight: 700; color: #0f172a; }
.metric-card.metric-ww  .metric-value { color: #166534; }
.metric-card.metric-col .metric-value { color: #991b1b; }

/* ---- Buttons ---- */
.stButton > button[kind="primary"] {
    background-color: #166534; border: none; font-weight: 700;
    font-size: 0.9rem; border-radius: 9px; padding: 10px 0; color: #fff;
}
.stButton > button[kind="primary"]:hover { background-color: #14532d; }
/* Scope to main content + sidebar only — prevents styling header toolbar buttons */
.main .stButton > button:not([kind="primary"]),
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    border: 1.5px solid #166534 !important; color: #166534 !important; font-size: 0.82rem;
    border-radius: 7px; background: #ffffff !important; font-weight: 600;
}
.main .stButton > button:not([kind="primary"]):hover,
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
    background: #f0fdf4 !important; border-color: #14532d !important;
}

/* ---- Pills ---- */
.pill-ww    { display:inline-block; background:#dcfce7; color:#166534; border-radius:20px; padding:3px 12px; font-size:0.80rem; font-weight:700; }
.pill-coles { display:inline-block; background:#fee2e2; color:#991b1b; border-radius:20px; padding:3px 12px; font-size:0.80rem; font-weight:700; }

/* ---- Winner banner ---- */
.winner-banner { border-radius: 12px; padding: 20px 24px; margin-bottom: 4px; }
.winner-banner.ww  { background: #166534; }
.winner-banner.col { background: #991b1b; }
.winner-banner.tie { background: #374151; }
.wbanner-title  { font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.wbanner-saving { font-size: 2.0rem; font-weight: 800; color: #ffffff; line-height: 1.1; margin-bottom: 6px; }
.wbanner-detail { font-size: 0.82rem; color: rgba(255,255,255,0.80); }

/* ---- Item cards ---- */
.item-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 8px; margin-bottom: 6px; overflow: hidden;
}
.card-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 14px; border-bottom: 1px solid #e2e8f0; background: #f1f5f9;
}
.card-title {
    font-size: 0.88rem; font-weight: 600; color: #374151;
    display: flex; align-items: center; gap: 7px;
}
.per-kg-chip {
    font-size: 0.68rem; font-weight: 600; color: #64748b;
    border: 1px solid #cbd5e1; border-radius: 10px; padding: 1px 6px; letter-spacing: 0.2px;
}

/* ---- Save badge ---- */
.save-badge {
    font-size: 0.80rem; font-weight: 700;
    padding: 3px 11px; border-radius: 20px; white-space: nowrap;
}
.badge-ww   { background: #dcfce7; color: #166534; }
.badge-col  { background: #fee2e2; color: #991b1b; }
.badge-tie  { background: #f1f5f9; color: #475569; }
.badge-na   { background: #f1f5f9; color: #64748b; }

/* ---- Store panels ---- */
.stores-row { display: flex; }
.store-panel { flex: 1; padding: 14px 16px; border-right: 2px solid #e2e8f0; }
.store-panel:last-child { border-right: none; }
.store-panel.win-ww    { background: #f0fdf4; border-top: 3px solid #166534; }
.store-panel.win-col   { background: #fff1f2; border-top: 3px solid #991b1b; }
.store-panel.lose      { background: #ffffff; border-top: 3px solid transparent; }
.store-panel.no-price  { background: #ffffff; border-top: 3px solid transparent; opacity: 0.5; }

/* ---- Store label ---- */
.store-label {
    font-size: 0.85rem; font-weight: 700;
    letter-spacing: 0.1px; margin-bottom: 10px;
    display: flex; align-items: center; gap: 5px;
}
.lbl-ww   { color: #166534; }
.lbl-col  { color: #991b1b; }
.lbl-muted{ color: #6b7280; }

/* ---- On-sale pill ---- */
.sale-pill {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    background: #fef9c3; color: #854d0e;
    padding: 1px 5px; border-radius: 3px; letter-spacing: 0.2px;
}

/* ---- Prices ---- */
.price-row { display: flex; align-items: baseline; gap: 5px; margin-bottom: 3px; }
.price-big { font-size: 1.45rem; font-weight: 800; color: #0f172a; line-height: 1; }
.price-big.p-ww    { color: #166534; }
.price-big.p-col   { color: #991b1b; }
.price-big.p-muted { color: #9ca3af; font-size: 1.2rem; font-weight: 400; }
.price-unit { font-size: 0.85rem; color: #475569; align-self: flex-end; padding-bottom: 2px; }
.price-was  { font-size: 0.80rem; color: #6b7280; text-decoration: line-through; align-self: flex-end; padding-bottom: 2px; }
.pack-info  { font-size: 0.76rem; color: #475569; font-style: italic; margin-bottom: 6px; }

/* ---- Matched product name ---- */
.matched-name {
    font-size: 0.76rem; color: #475569; font-style: italic;
    margin-bottom: 9px; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}

/* ---- View product link ---- */
.view-link {
    font-size: 0.80rem; font-weight: 600; text-decoration: none;
    display: inline-flex; align-items: center; gap: 3px;
}
.link-ww    { color: #166534; }
.link-col   { color: #991b1b; }
.link-muted { color: #9ca3af; pointer-events: none; }
.view-link:hover { text-decoration: underline; }

/* ---- Page header ---- */
.page-header {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 18px 22px; margin-bottom: 20px;
}
.page-title  { font-size: 1.6rem; font-weight: 800; color: #0f172a; margin: 0 0 8px; line-height: 1.2; }
.page-subheader { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 0.88rem; color: #475569; }
.header-vs  { color: #6b7280; }
.header-sep { color: #cbd5e1; margin: 0 2px; }

/* ---- Category sections (details/summary collapsible) ---- */
details.cat-section {
    border: 1px solid #e2e8f0; border-radius: 10px;
    background: #ffffff; margin-bottom: 10px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
details.cat-section > summary {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; background: #ffffff;
    cursor: pointer; list-style: none;
    font-size: 1.05rem; font-weight: 800; color: #0f172a;
    user-select: none; letter-spacing: -0.2px;
}
details.cat-section > summary::-webkit-details-marker { display: none; }
details.cat-section > summary::marker { display: none; }
details.cat-section > summary:hover { background: #f8fafc; }
.cat-chevron { margin-left: auto; color: #94a3b8; font-size: 0.80rem; display: inline-block; transition: transform 0.2s; }
details.cat-section[open] .cat-chevron { transform: rotate(180deg); }
.cat-body { padding: 10px 0 6px; }

/* ---- Category winner pills (in section header) ---- */
.cat-winner-ww  { background:#dcfce7; color:#166534; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-winner-col { background:#fee2e2; color:#991b1b; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-winner-tie { background:#f1f5f9; color:#475569; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-winner-na  { background:#f1f5f9; color:#64748b; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-item-count { font-size:0.78rem; font-weight:400; color:#64748b; }
.row-error { font-size:0.76rem; color:#b45309; margin:0 0 8px 4px; }

/* ---- Hero (empty state) ---- */
.hero { text-align: center; padding: 64px 24px; }
.hero-emoji { font-size: 2.8rem; margin-bottom: 14px; }
.hero h3 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.hero p  { font-size: 0.9rem; color: #374151; max-width: 380px; margin: 0 auto 6px; }
.hero-hint { font-size: 0.80rem; color: #6b7280; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
all_item_names = [item["name"] for items in ITEMS.values() for item in items]

with st.sidebar:
    # Authoritative selection store. Survives search-filtering, which would
    # otherwise drop widget state for any checkbox not rendered this run.
    if "selected" not in st.session_state:
        st.session_state.selected = set()

    # Apply any pending bulk action BEFORE checkboxes are instantiated
    if st.session_state.get("_select_all"):
        st.session_state.selected = set(all_item_names)
        st.session_state["_select_all"] = False
    if st.session_state.get("_clear_all"):
        st.session_state.selected = set()
        st.session_state["_clear_all"] = False

    def _sync_item(name):
        if st.session_state[f"item_{name}"]:
            st.session_state.selected.add(name)
        else:
            st.session_state.selected.discard(name)

    query = st.text_input(
        "Search items",
        placeholder="🔍  Search items…",
        label_visibility="collapsed",
        key="item_search",
    ).strip().lower()

    with st.container(height=430, border=False):
        any_match = False
        for category, items in ITEMS.items():
            matching = [it for it in items if not query or query in it["name"].lower()]
            if not matching:
                continue
            any_match = True
            icon = CATEGORY_ICONS.get(category, "")
            with st.expander(f"{icon}  {category}", expanded=bool(query)):
                for item in matching:
                    name = item["name"]
                    # Seed widget from the authoritative store BEFORE instantiating
                    st.session_state[f"item_{name}"] = name in st.session_state.selected
                    st.checkbox(name, key=f"item_{name}", on_change=_sync_item, args=(name,))
        if not any_match:
            st.caption("No items match your search.")

    st.divider()

    c1, c2 = st.columns(2)
    if c1.button("Select All", use_container_width=True):
        st.session_state["_select_all"] = True
        st.rerun()
    if c2.button("Clear All", use_container_width=True):
        st.session_state["_clear_all"] = True
        st.rerun()

    selected_items = [n for n in all_item_names if n in st.session_state.selected]
    st.markdown(f"**{len(selected_items)}** of {len(all_item_names)} items selected")
    compare_clicked = st.button(
        "⚖️  Compare Prices",
        use_container_width=True,
        type="primary",
        disabled=not selected_items,
    )

    st.divider()
    col_r, col_f = st.columns([1, 1])
    with col_r:
        if st.button("🗑️ Clear cache", use_container_width=True):
            clear_cache()
            st.session_state.results = None
            st.success("Cleared.")
    with col_f:
        force_refresh = st.checkbox("Force refresh", value=False)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
if "results" not in st.session_state:
    st.session_state.results = None
if "cats_open" not in st.session_state:
    st.session_state.cats_open = True

# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------
if compare_clicked:
    search_terms = {name: get_search_term(name) for name in selected_items}
    with st.spinner(f"Fetching prices for {len(selected_items)} items…"):
        st.session_state.results = get_prices(
            item_names=selected_items,
            search_terms=search_terms,
            force_refresh=force_refresh,
        )
        st.session_state.fetched_at = datetime.now()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if not st.session_state.results:
    st.markdown("""
<div class="hero">
  <div class="hero-emoji">🛒</div>
  <h3>Compare prices, shop smarter</h3>
  <p>Select the groceries you buy regularly from the sidebar, then hit <strong>Compare Prices</strong>.</p>
</div>
""", unsafe_allow_html=True)

else:
    results = st.session_state.results

    # ---- Price freshness line ----------------------------------------------
    fetched_at = st.session_state.get("fetched_at")
    if fetched_at:
        # %I is zero-padded on Windows (e.g. "03"); rebuild with a bare hour.
        hour = fetched_at.strftime("%I").lstrip("0") or "12"
        when = fetched_at.strftime("%a %d %b · ") + hour + fetched_at.strftime(":%M %p")
        n = len(results)
        st.markdown(
            f'<div class="freshness"><span class="dot"></span>'
            f'Prices as of {when} · {n} item{"s" if n != 1 else ""}</div>',
            unsafe_allow_html=True,
        )

    # Coles cookie error banner
    if any("buildId" in (r.get("error") or "") for r in results.values()):
        st.error(
            "**Coles prices couldn't load** — your browser session cookies have expired.\n\n"
            "Open **Google Chrome**, visit [coles.com.au](https://www.coles.com.au) for a few seconds, "
            "then click **Clear cache** and compare again."
        )

    # ---- Build rows --------------------------------------------------------

    def _display_name(entry):
        if not entry:
            return "Not found"
        name = entry.get("display_name", "")
        unit = entry.get("unit", "")
        if unit and unit.lower() not in name.lower():
            name = f"{name} ({unit})"
        return name

    rows = []
    ww_total = coles_total = 0.0
    ww_count = coles_count = 0
    wins_ww = wins_col = tied = 0
    has_per_kg = False

    for item_name, data in results.items():
        ww  = data.get("woolworths")
        col = data.get("coles")
        per_kg = is_per_kg(item_name)

        if per_kg:
            ww_cmp  = (ww.get("unit_price")  if ww  else None) or (ww["price"]  if ww  else None)
            col_cmp = (col.get("unit_price") if col else None) or (col["price"] if col else None)
            per_kg_active = per_kg and (
                (ww  is not None and ww.get("unit_price")  is not None) or
                (col is not None and col.get("unit_price") is not None)
            )
        else:
            ww_cmp = ww["price"]  if ww  else None
            col_cmp= col["price"] if col else None
            per_kg_active = False

        if per_kg_active:
            has_per_kg = True

        if ww_cmp is not None and col_cmp is not None:
            if   ww_cmp < col_cmp:  cheaper, saving = "Woolworths", col_cmp - ww_cmp;  wins_ww  += 1
            elif col_cmp < ww_cmp:  cheaper, saving = "Coles",       ww_cmp - col_cmp; wins_col += 1
            else:                    cheaper, saving = "Same",         0.0;              tied     += 1
        else:
            cheaper, saving = "—", None

        if ww_cmp  is not None: ww_total    += ww_cmp;  ww_count    += 1
        if col_cmp is not None: coles_total += col_cmp; coles_count += 1

        rows.append({
            "item":           item_name,
            "per_kg":         per_kg_active,
            "ww_cmp":         ww_cmp,
            "col_cmp":        col_cmp,
            "ww_pack":        ww["price"]           if ww  else None,
            "col_pack":       col["price"]           if col else None,
            "ww_unit":        ww.get("unit", "")    if ww  else "",
            "col_unit":       col.get("unit", "")   if col else "",
            "ww_was":         ww.get("was_price")   if ww  else None,
            "col_was":        col.get("was_price")  if col else None,
            "ww_name":        _display_name(ww),
            "col_name":       _display_name(col),
            "ww_url":         ww.get("url", "")     if ww  else "",
            "col_url":        col.get("url", "")    if col else "",
            "cheaper":        cheaper,
            "saving":         saving,
            "error":          data.get("error"),
        })

    # ---- Group by category, sort within each group -------------------------

    item_to_cat = {
        item["name"]: cat
        for cat, items in ITEMS.items()
        for item in items
    }

    cat_rows: dict[str, list] = {cat: [] for cat in ITEMS}
    for row in rows:
        cat = item_to_cat.get(row["item"], "Other")
        cat_rows.setdefault(cat, []).append(row)

    def _sort_key(r):
        if r["saving"] is None: return (1, 0)
        return (0, -(r["saving"]))

    for cat in cat_rows:
        cat_rows[cat].sort(key=_sort_key)

    # ---- Winner banner -------------------------------------------------------
    compared = min(ww_count, coles_count)
    if ww_total and coles_total:
        diff = abs(ww_total - coles_total)
        tied_str = f" · {tied} tied" if tied else ""
        if ww_total < coles_total:
            banner_html = (
                f'<div class="winner-banner ww">'
                f'<div class="wbanner-title">🏆 Woolworths cheaper this week</div>'
                f'<div class="wbanner-saving">${diff:.2f} saved vs Coles basket</div>'
                f'<div class="wbanner-detail">Cheaper on {wins_ww} of {compared} items · {wins_col} at Coles{tied_str}</div>'
                f'</div>'
            )
        elif coles_total < ww_total:
            banner_html = (
                f'<div class="winner-banner col">'
                f'<div class="wbanner-title">🏆 Coles cheaper this week</div>'
                f'<div class="wbanner-saving">${diff:.2f} saved vs Woolworths basket</div>'
                f'<div class="wbanner-detail">Cheaper on {wins_col} of {compared} items · {wins_ww} at Woolworths{tied_str}</div>'
                f'</div>'
            )
        else:
            banner_html = (
                f'<div class="winner-banner tie">'
                f'<div class="wbanner-title">🤝 It\'s a tie this week</div>'
                f'<div class="wbanner-saving">$0.00 difference</div>'
                f'<div class="wbanner-detail">Both supermarkets equal across {compared} items</div>'
                f'</div>'
            )
        st.markdown(banner_html, unsafe_allow_html=True)

    # ---- 4 metrics ----------------------------------------------------------
    ww_total_str    = f"${ww_total:.2f}"    if ww_count    else "N/A"
    coles_total_str = f"${coles_total:.2f}" if coles_count else "N/A"
    wins_ww_str     = f"{wins_ww} item{'s' if wins_ww != 1 else ''}"
    wins_col_str    = f"{wins_col} item{'s' if wins_col != 1 else ''}"
    st.markdown(f"""
<div class="metrics-row">
  <div class="metric-card metric-ww">
    <div class="metric-label">Woolworths total</div>
    <div class="metric-value">{ww_total_str}</div>
  </div>
  <div class="metric-card metric-col">
    <div class="metric-label">Coles total</div>
    <div class="metric-value">{coles_total_str}</div>
  </div>
  <div class="metric-card metric-ww">
    <div class="metric-label">Cheaper at Woolworths</div>
    <div class="metric-value">{wins_ww_str}</div>
  </div>
  <div class="metric-card metric-col">
    <div class="metric-label">Cheaper at Coles</div>
    <div class="metric-value">{wins_col_str}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if has_per_kg:
        st.caption("⚖ Meats and produce shown at $/kg · totals assume 1 kg for those items.")

    # ---- Expand / collapse all toggle --------------------------------------
    tog1, tog2, _ = st.columns([1, 1, 6])
    if tog1.button("⊕ Expand all", use_container_width=True):
        st.session_state.cats_open = True
    if tog2.button("⊖ Collapse all", use_container_width=True):
        st.session_state.cats_open = False

    # ---- Card rendering helpers --------------------------------------------

    def _price_block(cmp, pack, unit, was, css_cls, per_kg_active):
        if cmp is None:
            return '<div class="price-row"><span class="price-big p-muted">N/A</span></div>'
        if per_kg_active:
            pack_str = ""
            if pack is not None:
                size_part = f" ({unit})" if unit else ""
                was_str   = f" · was ${was:.2f}" if was else ""
                pack_str  = f'<div class="pack-info">Pack: ${pack:.2f}{size_part}{was_str}</div>'
            return (
                f'<div class="price-row">'
                f'<span class="price-big {css_cls}">${cmp:.2f}</span>'
                f'<span class="price-unit">/kg</span>'
                f'</div>{pack_str}'
            )
        else:
            was_part = f'<span class="price-was">${was:.2f}</span>' if was else ""
            return (
                f'<div class="price-row">'
                f'<span class="price-big {css_cls}">${cmp:.2f}</span>'
                f'{was_part}'
                f'</div>'
            )

    def _link(url, link_cls):
        if not url:
            return '<span class="view-link link-muted">View product ↗</span>'
        safe = _html.escape(url)
        return f'<a href="{safe}" target="_blank" rel="noopener" class="view-link {link_cls}">View product ↗</a>'

    # ---- Render cards by category (details/summary for collapsible headers)-
    open_attr = "open" if st.session_state.cats_open else ""

    for cat, c_rows in cat_rows.items():
        if not c_rows:
            continue

        icon = CATEGORY_ICONS.get(cat, "")

        cat_ww_wins  = sum(1 for r in c_rows if r["cheaper"] == "Woolworths")
        cat_col_wins = sum(1 for r in c_rows if r["cheaper"] == "Coles")
        cat_na       = sum(1 for r in c_rows if r["cheaper"] == "—")
        cat_compared = len(c_rows) - cat_na

        if cat_compared == 0:
            winner_pill = '<span class="cat-winner-na">No data</span>'
        elif cat_ww_wins > cat_col_wins:
            winner_pill = '<span class="cat-winner-ww">Woolworths</span>'
        elif cat_col_wins > cat_ww_wins:
            winner_pill = '<span class="cat-winner-col">Coles</span>'
        else:
            winner_pill = '<span class="cat-winner-tie">Tied</span>'

        count_str = f'<span class="cat-item-count">{cat_compared} of {len(c_rows)} compared</span>' \
                    if cat_na else \
                    f'<span class="cat-item-count">{len(c_rows)} items</span>'

        # Build all card HTML for this category in one block
        cards_html = ""
        for row in c_rows:
            unit_sfx = "/kg" if row["per_kg"] else ""

            if row["saving"] is None:
                badge_cls, badge_txt = "badge-na", "—"
            elif row["cheaper"] == "Same":
                badge_cls, badge_txt = "badge-tie", "Same price"
            elif row["cheaper"] == "Woolworths":
                badge_cls, badge_txt = "badge-ww", f"WW saves ${row['saving']:.2f}{unit_sfx}"
            else:
                badge_cls, badge_txt = "badge-col", f"Coles saves ${row['saving']:.2f}{unit_sfx}"

            if row["cheaper"] == "Woolworths":
                ww_panel, col_panel = "win-ww", "lose"
                ww_pcls, col_pcls  = "p-ww", "p-muted"
                ww_lcls, col_lcls  = "lbl-ww", "lbl-muted"
                ww_check, col_check = "✓ ", ""
                ww_lnk, col_lnk   = "link-ww", "link-col"
            elif row["cheaper"] == "Coles":
                ww_panel, col_panel = "lose", "win-col"
                ww_pcls, col_pcls  = "p-muted", "p-col"
                ww_lcls, col_lcls  = "lbl-muted", "lbl-col"
                ww_check, col_check = "", "✓ "
                ww_lnk, col_lnk   = "link-ww", "link-col"
            else:
                ww_panel  = "" if row["ww_cmp"]  is not None else "no-price"
                col_panel = "" if row["col_cmp"] is not None else "no-price"
                ww_pcls = col_pcls = ""
                ww_lcls = "lbl-ww" if row["ww_cmp"] is not None else "lbl-muted"
                col_lcls = "lbl-col" if row["col_cmp"] is not None else "lbl-muted"
                ww_check = col_check = ""
                ww_lnk, col_lnk = "link-ww", "link-col"

            chip = '<span class="per-kg-chip">per kg</span>' if row["per_kg"] else ""
            ww_sale  = '<span class="sale-pill">On sale</span>' if row["ww_was"]  else ""
            col_sale = '<span class="sale-pill">On sale</span>' if row["col_was"] else ""

            item_s    = _html.escape(row["item"])
            ww_name_s = _html.escape(row["ww_name"])
            col_name_s= _html.escape(row["col_name"])

            cards_html += f"""
<div class="item-card">
  <div class="card-header">
    <span class="card-title">{item_s}{chip}</span>
    <span class="save-badge {badge_cls}">{badge_txt}</span>
  </div>
  <div class="stores-row">
    <div class="store-panel {ww_panel}">
      <div class="store-label {ww_lcls}">{ww_check}Woolworths {ww_sale}</div>
      {_price_block(row['ww_cmp'], row['ww_pack'], row['ww_unit'], row['ww_was'], ww_pcls, row['per_kg'])}
      <div class="matched-name">{ww_name_s}</div>
      {_link(row['ww_url'], ww_lnk)}
    </div>
    <div class="store-panel {col_panel}">
      <div class="store-label {col_lcls}">{col_check}Coles {col_sale}</div>
      {_price_block(row['col_cmp'], row['col_pack'], row['col_unit'], row['col_was'], col_pcls, row['per_kg'])}
      <div class="matched-name">{col_name_s}</div>
      {_link(row['col_url'], col_lnk)}
    </div>
  </div>
</div>"""
            if row["error"] and "buildId" not in row["error"]:
                err_s = _html.escape(row["error"])
                cards_html += f'<p class="row-error">⚠️ {item_s}: {err_s}</p>'

        cat_s = _html.escape(cat)
        st.markdown(f"""
<details class="cat-section" {open_attr}>
  <summary>
    {icon}&nbsp;<strong>{cat_s}</strong>
    {winner_pill}
    {count_str}
    <span class="cat-chevron">▼</span>
  </summary>
  <div class="cat-body">{cards_html}</div>
</details>
""", unsafe_allow_html=True)

    st.markdown("")
    st.caption(
        "Prices are standard shelf prices only — Everyday Rewards / Flybuys member pricing excluded. "
        "Matching uses each store's top search result. Click 'View product' to verify."
    )
