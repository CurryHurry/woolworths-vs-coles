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
/* ---- Page background: soft, blurred mesh backdrop ---- */
.stApp { background: #eef2f7; }
/* Blurred atmospheric layer (reads like an out-of-focus photo). Self-contained
   mesh of soft colour blobs — swap the radial-gradients for url('...') to use a
   real photo. */
.stApp::before {
    content: "";
    position: fixed; inset: -60px; z-index: -2;
    background:
        radial-gradient(42% 46% at 12% 16%, rgba(134, 239, 172, 0.55) 0%, rgba(134,239,172,0) 60%),
        radial-gradient(38% 42% at 86% 12%, rgba(253, 186, 186, 0.50) 0%, rgba(253,186,186,0) 62%),
        radial-gradient(46% 52% at 80% 84%, rgba(165, 213, 255, 0.45) 0%, rgba(165,213,255,0) 60%),
        radial-gradient(42% 46% at 16% 90%, rgba(253, 230, 138, 0.42) 0%, rgba(253,230,138,0) 62%),
        linear-gradient(135deg, #f7fafc 0%, #eef3f8 100%);
    filter: blur(64px) saturate(1.15);
    transform: scale(1.06);
}
/* Light frosted veil so glass surfaces and text stay crisp */
.stApp::after {
    content: "";
    position: fixed; inset: 0; z-index: -1;
    background: rgba(248, 250, 252, 0.28);
}
/* Let content sit over the backdrop */
[data-testid="stAppViewContainer"],
.main .block-container { background: transparent !important; }

/* ---- Top toolbar (the "Deploy" bar) ---- */
[data-testid="stHeader"] {
    background-color: #0f172a !important;
    border-bottom: none !important;
    box-shadow: 0 4px 18px rgba(15,23,42,0.18);
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

/* ---- Sidebar (frosted glass) ---- */
[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.70) !important;
    backdrop-filter: blur(18px) saturate(1.4);
    -webkit-backdrop-filter: blur(18px) saturate(1.4);
    border-right: 1px solid rgba(255, 255, 255, 0.55);
    box-shadow: 1px 0 0 rgba(255,255,255,0.4), 6px 0 24px rgba(15,23,42,0.06);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }

/* Sidebar header — fills the top-left space and labels the panel's purpose */
.sb-head {
    display: flex; align-items: center; gap: 11px;
    padding: 0 2px 14px; margin-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
}
.sb-head-icon {
    width: 38px; height: 38px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(155deg, #1c8043 0%, #166534 100%);
    box-shadow: 0 4px 12px rgba(22,101,52,0.40), inset 0 1px 0 rgba(255,255,255,0.30);
}
.sb-head-icon svg { width: 20px; height: 20px; }
.sb-head-title { font-size: 0.98rem; font-weight: 800; color: #f1f5f9; line-height: 1.15; }
.sb-head-sub   { font-size: 0.76rem; color: #94a3b8; margin-top: 1px; }

/* Flat category group label (replaces cluttered expanders) */
.sb-cat {
    font-size: 0.70rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.7px; color: #94a3b8;
    margin: 15px 0 5px; padding-bottom: 5px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

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
    background: rgba(255, 255, 255, 0.62);
    backdrop-filter: blur(14px) saturate(1.4);
    -webkit-backdrop-filter: blur(14px) saturate(1.4);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 12px; padding: 14px 16px;
    box-shadow: 0 8px 22px rgba(15,23,42,0.08), inset 0 1px 0 rgba(255,255,255,0.85);
}
.metric-card.metric-ww  {
    background: linear-gradient(155deg, rgba(220,252,231,0.88) 0%, rgba(240,253,244,0.55) 100%);
    border-color: rgba(187,247,208,0.85);
}
.metric-card.metric-col {
    background: linear-gradient(155deg, rgba(254,226,226,0.88) 0%, rgba(255,241,242,0.55) 100%);
    border-color: rgba(254,205,211,0.85);
}
.metric-label {
    font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.5px;
    color: #64748b; margin-bottom: 6px; font-weight: 600;
}
.metric-value { font-size: 1.3rem; font-weight: 700; color: #0f172a; }
.metric-card.metric-ww  .metric-value { color: #166534; }
.metric-card.metric-col .metric-value { color: #991b1b; }

/* ---- Buttons ---- */
.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #1c8043 0%, #166534 100%);
    border: none; font-weight: 700;
    font-size: 0.9rem; border-radius: 10px; padding: 10px 0; color: #fff;
    box-shadow: 0 4px 14px rgba(22,101,52,0.30), inset 0 1px 0 rgba(255,255,255,0.28);
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #22994f 0%, #15803d 100%);
    box-shadow: 0 6px 18px rgba(22,101,52,0.38), inset 0 1px 0 rgba(255,255,255,0.30);
}
/* Scope to main content + sidebar only — prevents styling header toolbar buttons */
.main .stButton > button:not([kind="primary"]),
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    border: 1.5px solid rgba(22,101,52,0.55) !important; color: #166534 !important; font-size: 0.82rem;
    border-radius: 9px;
    background: rgba(255,255,255,0.55) !important;
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    font-weight: 600;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}
.main .stButton > button:not([kind="primary"]):hover,
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
    background: rgba(240,253,244,0.85) !important; border-color: #166534 !important;
}

/* ---- Pills ---- */
.pill-ww    { display:inline-block; background:#dcfce7; color:#166534; border-radius:20px; padding:3px 12px; font-size:0.80rem; font-weight:700; }
.pill-coles { display:inline-block; background:#fee2e2; color:#991b1b; border-radius:20px; padding:3px 12px; font-size:0.80rem; font-weight:700; }

/* ---- Winner banner (glossy) ---- */
.winner-banner {
    border-radius: 14px; padding: 22px 26px; margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 12px 30px rgba(15,23,42,0.22), inset 0 1px 0 rgba(255,255,255,0.28);
}
.winner-banner.ww  {
    background:
        linear-gradient(160deg, rgba(255,255,255,0.24) 0%, rgba(255,255,255,0.05) 34%, rgba(255,255,255,0) 60%),
        linear-gradient(135deg, #18a249 0%, #166534 55%, #14532d 100%);
}
.winner-banner.col {
    background:
        linear-gradient(160deg, rgba(255,255,255,0.24) 0%, rgba(255,255,255,0.05) 34%, rgba(255,255,255,0) 60%),
        linear-gradient(135deg, #d62828 0%, #991b1b 55%, #7f1d1d 100%);
}
.winner-banner.tie {
    background:
        linear-gradient(160deg, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0.04) 34%, rgba(255,255,255,0) 60%),
        linear-gradient(135deg, #4b5563 0%, #374151 55%, #1f2937 100%);
}
.wbanner-title  { font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 4px; text-shadow: 0 1px 2px rgba(0,0,0,0.18); }
.wbanner-detail { font-size: 0.82rem; color: rgba(255,255,255,0.85); }

/* ---- Item cards ---- */
.item-card {
    background: rgba(255, 255, 255, 0.78); border: 1px solid rgba(226,232,240,0.9);
    border-radius: 10px; margin-bottom: 7px; overflow: hidden;
    box-shadow: 0 2px 8px rgba(15,23,42,0.05), inset 0 1px 0 rgba(255,255,255,0.9);
}
.card-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 14px; border-bottom: 1px solid rgba(226,232,240,0.8);
    background: linear-gradient(180deg, rgba(248,250,252,0.95) 0%, rgba(241,245,249,0.85) 100%);
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
.store-panel.win-ww    { background: linear-gradient(160deg, rgba(220,252,231,0.75), rgba(240,253,244,0.35)); border-top: 3px solid #166534; }
.store-panel.win-col   { background: linear-gradient(160deg, rgba(254,226,226,0.75), rgba(255,241,242,0.35)); border-top: 3px solid #991b1b; }
.store-panel.lose      { background: transparent; border-top: 3px solid transparent; }
.store-panel.no-price  { background: transparent; border-top: 3px solid transparent; opacity: 0.5; }

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

/* ---- Category sections (details/summary collapsible, frosted glass) ---- */
details.cat-section {
    border: 1px solid rgba(255,255,255,0.6); border-radius: 14px;
    background: rgba(255, 255, 255, 0.58);
    backdrop-filter: blur(16px) saturate(1.4);
    -webkit-backdrop-filter: blur(16px) saturate(1.4);
    margin-bottom: 12px; overflow: hidden;
    box-shadow: 0 8px 24px rgba(15,23,42,0.09), inset 0 1px 0 rgba(255,255,255,0.85);
}
details.cat-section > summary {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; background: rgba(255,255,255,0.28);
    cursor: pointer; list-style: none;
    font-size: 1.05rem; font-weight: 800; color: #0f172a;
    user-select: none; letter-spacing: -0.2px;
}
details.cat-section > summary::-webkit-details-marker { display: none; }
details.cat-section > summary::marker { display: none; }
details.cat-section > summary:hover { background: rgba(255,255,255,0.5); }
.cat-chevron { margin-left: auto; color: #94a3b8; font-size: 0.80rem; display: inline-block; transition: transform 0.2s; }
details.cat-section[open] .cat-chevron { transform: rotate(180deg); }
.cat-body { padding: 10px 14px 8px; }

/* ---- Category winner pills (in section header) ---- */
.cat-winner-ww  { background:#dcfce7; color:#166534; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-winner-col { background:#fee2e2; color:#991b1b; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-winner-tie { background:#f1f5f9; color:#475569; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-winner-na  { background:#f1f5f9; color:#64748b; border-radius:20px; padding:2px 10px; font-size:0.76rem; font-weight:700; white-space:nowrap; }
.cat-item-count { font-size:0.78rem; font-weight:400; color:#64748b; }
.row-error { font-size:0.76rem; color:#b45309; margin:0 0 8px 4px; }

/* ---- Hero (empty state, frosted glass) ---- */
.hero {
    text-align: center; padding: 56px 24px; margin-top: 8px;
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(16px) saturate(1.4);
    -webkit-backdrop-filter: blur(16px) saturate(1.4);
    border: 1px solid rgba(255,255,255,0.6); border-radius: 18px;
    box-shadow: 0 12px 36px rgba(15,23,42,0.10), inset 0 1px 0 rgba(255,255,255,0.85);
}
.hero-emoji { font-size: 2.8rem; margin-bottom: 14px; }
.hero h3 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.hero p  { font-size: 0.9rem; color: #374151; max-width: 380px; margin: 0 auto 6px; }
.hero-hint { font-size: 0.80rem; color: #6b7280; margin-top: 12px; }

/* ======================================================================
   Dark sidebar (left panel) — clean menu, high contrast vs light content
   ====================================================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    box-shadow: 6px 0 24px rgba(15,23,42,0.18) !important;
}
/* Checkbox item rows */
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label span,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label { color: #e2e8f0 !important; font-size: 0.86rem; }
/* Selected-count + helper text */
[data-testid="stSidebar"] .stMarkdown p { color: #cbd5e1; }
[data-testid="stSidebar"] .sb-head-title { color: #f1f5f9; }
/* Search field */
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.07) !important; color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: #94a3b8 !important; }
/* Ghost secondary buttons (Select all / Clear all / Clear cache) */
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #e2e8f0 !important;
    backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
    background: rgba(255,255,255,0.12) !important; border-color: rgba(255,255,255,0.30) !important;
}
/* Dividers */
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.10) !important; }
/* Force-refresh checkbox label */
[data-testid="stSidebar"] [data-testid="stCheckbox"] { color: #cbd5e1; }

/* ---- Winner banner: emphasised dollar amount ---- */
.wbanner-amt {
    font-size: 2.9rem; font-weight: 800; color: #ffffff; line-height: 1.0;
    letter-spacing: -1.2px; margin: 2px 0 2px;
    text-shadow: 0 2px 6px rgba(0,0,0,0.28);
}
.wbanner-sub { font-size: 0.86rem; font-weight: 600; color: rgba(255,255,255,0.88); margin-bottom: 8px; }

/* ======================================================================
   Uniform SHARP corners across the whole app
   ====================================================================== */
[data-testid="stHeader"],
.stButton > button, .stTextInput input, .stTextInput > div,
[data-testid="stExpander"], [data-testid="stExpander"] summary,
.metric-card, .item-card, .card-header,
details.cat-section, details.cat-section > summary,
.store-panel, .winner-banner, .hero, .sb-head-icon,
.save-badge, .per-kg-chip, .sale-pill,
.cat-winner-ww, .cat-winner-col, .cat-winner-tie, .cat-winner-na,
.pill-ww, .pill-coles, .freshness .dot {
    border-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
all_item_names = [item["name"] for items in ITEMS.values() for item in items]

with st.sidebar:
    st.markdown(
        '<div class="sb-head">'
        '<div class="sb-head-icon">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle>'
        '<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>'
        '</svg>'
        '</div>'
        '<div><div class="sb-head-title">Your shopping list</div>'
        '<div class="sb-head-sub">Tick items, then compare</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

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
            st.markdown(f'<div class="sb-cat">{icon} {category}</div>', unsafe_allow_html=True)
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
                f'<div class="wbanner-amt">${diff:.2f}</div>'
                f'<div class="wbanner-sub">saved on your basket vs Coles</div>'
                f'<div class="wbanner-detail">Cheaper on {wins_ww} of {compared} items · {wins_col} at Coles{tied_str}</div>'
                f'</div>'
            )
        elif coles_total < ww_total:
            banner_html = (
                f'<div class="winner-banner col">'
                f'<div class="wbanner-title">🏆 Coles cheaper this week</div>'
                f'<div class="wbanner-amt">${diff:.2f}</div>'
                f'<div class="wbanner-sub">saved on your basket vs Woolworths</div>'
                f'<div class="wbanner-detail">Cheaper on {wins_col} of {compared} items · {wins_ww} at Woolworths{tied_str}</div>'
                f'</div>'
            )
        else:
            banner_html = (
                f'<div class="winner-banner tie">'
                f'<div class="wbanner-title">🤝 It\'s a tie this week</div>'
                f'<div class="wbanner-amt">$0.00</div>'
                f'<div class="wbanner-sub">no difference across {compared} items</div>'
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
