import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import re

st.set_page_config(
    page_title="ShyAway - Target User Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (only styles custom HTML — theme handled by config.toml) ──────
st.markdown("""
<style>
/* metric cards */
.metric-card {
    border-radius: 16px;
    padding: 1.15rem 1rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 8px 20px rgba(0,0,0,0.07);
    transition: transform 0.18s, box-shadow 0.18s;
    margin-bottom: 0.4rem;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: -16px; right: -16px;
    width: 68px; height: 68px;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.12), 0 18px 36px rgba(0,0,0,0.09);
}
.metric-card h3 {
    font-size: 2rem; font-weight: 700; margin: 0 0 0.2rem;
    color: #fff; letter-spacing: -0.5px; line-height: 1;
}
.metric-card p {
    font-size: 0.67rem; font-weight: 600; margin: 0;
    color: rgba(255,255,255,0.82);
    text-transform: uppercase; letter-spacing: 0.9px;
}
.card-pink   { background: linear-gradient(145deg,#b5114a,#e8457a); }
.card-purple { background: linear-gradient(145deg,#5e0f8b,#9c40cc); }
.card-teal   { background: linear-gradient(145deg,#005f57,#1fada0); }
.card-amber  { background: linear-gradient(145deg,#b03a00,#f0892a); }
.card-blue   { background: linear-gradient(145deg,#0b3fa1,#3d86e0); }
.card-rose   { background: linear-gradient(145deg,#7a0944,#d81b7a); }
.card-green  { background: linear-gradient(145deg,#175218,#4caf50); }
.card-indigo { background: linear-gradient(145deg,#162078,#5c6bc0); }
.card-coral  { background: linear-gradient(145deg,#9a1010,#e05555); }
.card-cyan   { background: linear-gradient(145deg,#005159,#22b5c8); }
.card-gold   { background: linear-gradient(145deg,#c45000,#f5c842); }
.card-gold h3, .card-gold p { color: #2a1200; }
.card-lime   { background: linear-gradient(145deg,#2e5e14,#8bc34a); }
.card-lime h3, .card-lime p { color: #162800; }

/* section title */
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #7a0944;
    padding: 0.4rem 0.85rem; margin: 0.9rem 0 0.55rem;
    border-left: 3px solid #d81b7a;
    background: linear-gradient(90deg,rgba(216,27,122,0.07),transparent);
    border-radius: 0 8px 8px 0;
}

/* insight box */
.insight-box {
    background: linear-gradient(135deg,#fff8f2,#fdf0f7);
    border-left: 3px solid #d81b7a;
    border-radius: 0 12px 12px 0;
    padding: 0.85rem 1.1rem;
    margin: 0.4rem 0 0.9rem;
    font-size: 0.87rem; line-height: 1.65; color: #3a1030;
    box-shadow: 0 2px 8px rgba(216,27,122,0.07);
}

/* dash title block */
.dash-title {
    font-size: 2rem; font-weight: 800; color: #1a0030;
    letter-spacing: -0.3px; line-height: 1.2; margin-bottom: 0.1rem;
}
.dash-subtitle {
    font-size: 0.83rem; color: #9a889e; font-weight: 400; letter-spacing: 0.2px;
}

/* badges */
.target-badge {
    display: inline-block; padding: 0.18rem 0.65rem;
    border-radius: 20px; font-size: 0.73rem; font-weight: 600;
    letter-spacing: 0.3px; margin: 2px;
}
.badge-high   { background:#fce4ec; color:#880e4f; border:1px solid #f48fb1; }
.badge-medium { background:#ede7f6; color:#4a148c; border:1px solid #ce93d8; }
.badge-low    { background:#e3f2fd; color:#0d47a1; border:1px solid #90caf9; }

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: white;
    padding: 5px 6px; border-radius: 12px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.08),0 0 0 1px rgba(216,27,122,0.1);
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.79rem !important; font-weight: 600 !important;
    padding: 7px 14px !important; border-radius: 9px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#b5114a,#d81b7a) !important;
    color: white !important;
    box-shadow: 0 3px 10px rgba(216,27,122,0.28) !important;
}

/* download button */
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg,#7a0944,#d81b7a) !important;
    color: white !important; border: none !important;
    border-radius: 9px !important; font-weight: 600 !important;
    padding: 0.45rem 1.4rem !important;
    box-shadow: 0 3px 10px rgba(216,27,122,0.25) !important;
}
div[data-testid="stDownloadButton"] button:hover {
    box-shadow: 0 6px 18px rgba(216,27,122,0.38) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ─────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "input-data", "visitor04052025.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, low_memory=False, on_bad_lines="skip")
    df.columns = df.columns.str.strip()

    # Parse visit_time — handles both "YYYY-MM-DD HH:MM:SS" and "DD-MM-YYYY HH:MM"
    df["visit_time"] = pd.to_datetime(df["visit_time"], dayfirst=True, errors="coerce")
    df["visit_date"] = df["visit_time"].dt.date
    df["visit_hour"] = df["visit_time"].dt.hour
    df["visit_dow"]  = df["visit_time"].dt.day_name()
    df["visit_week"] = df["visit_time"].dt.isocalendar().week.astype(str)

    # User type
    df["user_type"] = df["customerId"].apply(
        lambda x: "Logged In" if pd.notna(x) and str(x).strip() not in ["0", ""] else "Guest"
    )

    # Platform normalise
    df["platform"] = df["stream"].str.strip().str.title().fillna("Unknown")

    # Network type
    df["networkType"] = df["networkType"].fillna("Unknown").str.upper()

    # Category / action
    df["category"] = df["category"].fillna("Unknown")
    df["action"]   = df["action"].fillna("Unknown")

    # Parse actionDetails JSON
    def safe_json(val):
        try:
            if pd.isna(val):
                return {}
            return json.loads(str(val))
        except Exception:
            return {}

    df["_ad"] = df["actionDetails"].apply(safe_json)
    df["mrp"]          = pd.to_numeric(df["_ad"].apply(lambda d: d.get("mrp", None)), errors="coerce")
    df["specialprice"] = pd.to_numeric(df["_ad"].apply(lambda d: d.get("specialprice", None)), errors="coerce")
    df["timeTracked"]  = df["_ad"].apply(lambda d: d.get("timeTracked", None))
    df["reviews"]      = pd.to_numeric(df["_ad"].apply(lambda d: d.get("reviews", None)), errors="coerce")

    # Discount %
    df["discount_pct"] = ((df["mrp"] - df["specialprice"]) / df["mrp"] * 100).round(1)
    df["discount_pct"] = df["discount_pct"].clip(lower=0)
    df["has_offer"] = df["_ad"].apply(
        lambda d: bool(d.get("offerDetails") and d["offerDetails"] != "" and d["offerDetails"] != [])
    )

    # Color extracted from SKU (e.g. "A2052-DarkPink" → "DarkPink")
    def extract_color(sku):
        if pd.isna(sku) or str(sku).strip() == "":
            return None
        parts = str(sku).split("-")
        return "-".join(parts[1:]) if len(parts) > 1 else None

    df["sku_color"] = df["sku"].apply(extract_color)

    # Time tracked → seconds
    def parse_time_sec(val):
        if not val:
            return None
        val = str(val)
        total = 0
        m = re.search(r"(\d+)\s*min", val)
        s = re.search(r"(\d+)\s*sec", val)
        if m:
            total += int(m.group(1)) * 60
        if s:
            total += int(s.group(1))
        return total if (m or s) else None

    df["time_tracked_sec"] = df["timeTracked"].apply(parse_time_sec)

    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.image("https://www.shyaway.com/media/logo/default/shyaway-logo.png", width=160)
st.sidebar.title("Dashboard Filters")

platform_opts = sorted(df["platform"].unique().tolist())
selected_platforms = st.sidebar.multiselect("Platform", platform_opts, default=platform_opts)

user_type_opts = df["user_type"].unique().tolist()
selected_user_types = st.sidebar.multiselect("User Type", user_type_opts, default=user_type_opts)

# ── 2-level category hierarchy ────────────────────────────────────────────
def _main_cat(cat):
    c = cat.lower()
    if 'bra' in c:                           return 'Bra'
    if 'panty' in c or 'pantie' in c:        return 'Panty'
    if 'nightwear' in c or 'sleepwear' in c: return 'Nightwear'
    if 'sport' in c:                         return 'Sportswear'
    if 'lingerie' in c:                      return 'Lingerie Set'
    if 'camisole' in c or 'slip' in c:       return 'Camisole & Slip'
    if 'shapewear' in c:                     return 'Shapewear'
    if 'swimwear' in c or 'bikini' in c:     return 'Swimwear'
    if 'accessories' in c:                   return 'Accessories'
    if 'clothing' in c:                      return 'Clothing'
    return 'Other'

all_cats = sorted([c for c in df["category"].unique() if c != "Unknown"])
main_to_subs = {}
for _cat in all_cats:
    _m = _main_cat(_cat)
    main_to_subs.setdefault(_m, []).append(_cat)
for _m in main_to_subs:
    main_to_subs[_m] = sorted(main_to_subs[_m])

PRIORITY_MAINS = ["Bra", "Panty", "Nightwear", "Sportswear", "Lingerie Set",
                  "Camisole & Slip", "Shapewear", "Swimwear", "Accessories", "Clothing"]
all_main_cats = sorted(main_to_subs.keys())
default_mains = [m for m in PRIORITY_MAINS if m in all_main_cats]

st.sidebar.markdown("**Product Category**")
selected_main_cats = st.sidebar.multiselect(
    "Main Category", all_main_cats, default=default_mains,
    key="main_cat_filter"
)

avail_subs = sorted(set(
    cat for m in selected_main_cats for cat in main_to_subs.get(m, [])
))
selected_categories = st.sidebar.multiselect(
    "Sub-Category", avail_subs, default=avail_subs,
    help="Drill down to specific sizes / types",
    key="sub_cat_filter"
)

network_opts = sorted(df["networkType"].unique().tolist())
selected_networks = st.sidebar.multiselect("Network Type", network_opts, default=network_opts)

if df["visit_time"].notna().any():
    min_date = df["visit_time"].min().date()
    max_date = df["visit_time"].max().date()
    date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
else:
    date_range = None

st.sidebar.divider()
with st.sidebar.expander("View Source Code", expanded=False):
    with open(__file__, "r", encoding="utf-8") as _f:
        _src = _f.read()
    st.code(_src, language="python", line_numbers=True)

# Apply filters
fdf = df[
    df["platform"].isin(selected_platforms) &
    df["user_type"].isin(selected_user_types) &
    df["networkType"].isin(selected_networks)
]
if selected_categories:
    fdf = fdf[fdf["category"].isin(selected_categories) | (fdf["category"] == "Unknown")]

if date_range and len(date_range) == 2:
    fdf = fdf[
        (fdf["visit_time"].dt.date >= date_range[0]) &
        (fdf["visit_time"].dt.date <= date_range[1])
    ]

# ── Scoring function (module-level so @st.cache_data can hash cleanly) ───────
@st.cache_data
def compute_scores(data):
    # Drop unhashable dict column if present
    data = data.drop(columns=["_ad"], errors="ignore")

    # ── Count-based scoring (captures degree of engagement, not just presence) ─
    # This dataset contains active buyers, so we use raw counts weighted by
    # action value, then assign tiers using percentile ranks so the distribution
    # is always meaningful regardless of the absolute score range.
    ac = data.groupby(["userId", "action"]).size().unstack(fill_value=0).reset_index()
    for col in ["add", "sizeUpdate", "qtyUpdate", "searchPage", "search",
                "notificationClick", "MORE ON THIS OFFER", "SIMILAR PRODUCTS",
                "remove", "listPage", "notificationDelivered", "prepaid", "cod",
                "writeReview", "tab", "login"]:
        if col not in ac.columns:
            ac[col] = 0

    # Weighted score — purchase/cart actions capped to avoid one power-user dominating
    import numpy as np
    ac["action_score"] = (
        np.minimum(ac["prepaid"] + ac["cod"], 10) * 30 +
        np.minimum(ac["add"],         20)          * 15 +
        np.minimum(ac["writeReview"],  5)          * 20 +
        np.minimum(ac["qtyUpdate"],   10)          * 10 +
        np.minimum(ac["sizeUpdate"],  10)          * 8  +
        np.minimum(ac["notificationClick"], 10)    * 6  +
        np.minimum(ac["searchPage"],  20)          * 5  +
        np.minimum(ac["search"],      20)          * 4  +
        ac["MORE ON THIS OFFER"]                   * 3  +
        ac["SIMILAR PRODUCTS"]                     * 3  +
        np.minimum(ac["remove"],      10)          * 3  +
        np.minimum(ac["listPage"],    50)          * 2  +
        ac["login"]                                * 2  +
        ac["notificationDelivered"]                * 1
    )

    # Category diversity bonus
    cat_div = (
        data[data["category"] != "Unknown"]
        .groupby("userId")["category"].nunique()
        .reset_index()
        .rename(columns={"category": "cat_count"})
    )
    cat_div["cat_score"] = cat_div["cat_count"].apply(
        lambda c: 5 if c > 2 else (2 if c > 1 else 0)
    )

    # Logged-in bonus
    login_bonus = data.groupby("userId")["user_type"].first().reset_index()
    login_bonus["login_score"] = login_bonus["user_type"].apply(
        lambda t: 3 if t == "Logged In" else 0
    )

    scores = ac[["userId", "action_score"]].copy()
    scores["scroll_score"]    = 0
    scores["dwell_score"]     = 0
    scores["total_dwell_sec"] = 0
    scores = scores.merge(cat_div[["userId", "cat_score", "cat_count"]], on="userId", how="left")
    scores = scores.merge(login_bonus[["userId", "login_score", "user_type"]], on="userId", how="left")
    for _c in ["cat_score", "cat_count", "login_score"]:
        if _c in scores.columns:
            scores[_c] = scores[_c].fillna(0)

    scores["total_score"] = (
        scores["action_score"] + scores["cat_score"] + scores["login_score"]
    ).astype(int)

    # ── Percentile-rank tiers — always gives a balanced distribution ──────────
    # Top 15%: Hot Target | Next 25%: Warm Target | Next 35%: Potential | Rest: Cold Lead
    pct = scores["total_score"].rank(pct=True)
    def _tier(p):
        if p >= 0.85:   return "Hot Target"
        elif p >= 0.60: return "Warm Target"
        elif p >= 0.25: return "Potential"
        else:           return "Cold Lead"
    scores["_pct"] = pct

    scores["tier"] = scores["_pct"].apply(_tier)
    scores = scores.drop(columns=["_pct"])
    scores["tier_order"] = scores["tier"].map(
        {"Hot Target": 0, "Warm Target": 1, "Potential": 2, "Cold Lead": 3}
    )

    meta = data.groupby("userId").agg(
        platform=("platform", "first"),
        last_seen=("visit_time", "max"),
        total_events=("action", "count"),
        top_category=("category", lambda x: x[x != "Unknown"].value_counts().idxmax()
                      if (x != "Unknown").any() else "N/A"),
        top_sku=("sku", lambda x: x.dropna().value_counts().idxmax()
                 if x.dropna().shape[0] > 0 else "N/A"),
        email=("email", lambda x: x.dropna().iloc[0] if x.dropna().shape[0] > 0 else ""),
        mobile=("mobile", lambda x: x.dropna().iloc[0] if x.dropna().shape[0] > 0 else ""),
    ).reset_index()

    scores = scores.merge(meta, on="userId", how="left")
    return scores.sort_values(["tier_order", "total_score"], ascending=[True, False])


# ── Title ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="dash-title">ShyAway &mdash; Target User Dashboard</div>'
    f'<div class="dash-subtitle">Showing {len(fdf):,} of {len(df):,} events &nbsp;|&nbsp; '
    f'{df["visit_time"].min().strftime("%d %b %Y")} &ndash; {df["visit_time"].max().strftime("%d %b %Y")}</div>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── KPI Row 1 ─────────────────────────────────────────────────────────────────
total_events  = len(fdf)
unique_users  = fdf["userId"].nunique()
logged_in     = fdf[fdf["user_type"] == "Logged In"]["userId"].nunique()
guest_users   = fdf[fdf["user_type"] == "Guest"]["userId"].nunique()
total_clicks  = fdf[fdf["action"] == "notificationClick"].shape[0]
total_visits  = fdf[fdf["action"] == "listPage"].shape[0]
unique_skus   = fdf["sku"].dropna().nunique()
top_category  = (
    fdf[fdf["category"] != "Unknown"]["category"].value_counts().idxmax()
    if (fdf["category"] != "Unknown").any() else "N/A"
)

st.markdown('<div class="section-title">Overview Metrics</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
kpis_row1 = [
    (c1, "Total Events",    f"{total_events:,}",  "card-pink"),
    (c2, "Unique Users",    f"{unique_users:,}",   "card-purple"),
    (c3, "Logged-In Users", f"{logged_in:,}",      "card-teal"),
    (c4, "Guest Users",     f"{guest_users:,}",    "card-amber"),
    (c5, "Product Views",   f"{total_visits:,}",   "card-blue"),
    (c6, "Click Events",    f"{total_clicks:,}",   "card-rose"),
    (c7, "Unique SKUs",     f"{unique_skus:,}",    "card-green"),
    (c8, "Top Category",    top_category,          "card-indigo"),
]
for col, label, val, css in kpis_row1:
    col.markdown(f"""
    <div class="metric-card {css}">
        <h3>{val}</h3><p>{label}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Row 2 — Sales Targeting Signals ──────────────────────────────────────
size_clicks      = fdf[fdf["action"] == "sizeUpdate"].shape[0]
push_delivered   = fdf[fdf["action"] == "notificationDelivered"].shape[0]
high_intent_users = fdf[fdf["action"] == "sizeUpdate"]["userId"].nunique()
avg_time_on_prod = fdf[fdf["time_tracked_sec"].notna()]["time_tracked_sec"].mean()
avg_time_str     = f"{int(avg_time_on_prod // 60)}m {int(avg_time_on_prod % 60)}s" if pd.notna(avg_time_on_prod) else "N/A"
offer_clicks     = fdf[(fdf["action"] == "notificationClick") & fdf["has_offer"]].shape[0]
offer_click_pct  = round(offer_clicks / total_clicks * 100, 1) if total_clicks > 0 else 0

st.markdown('<div class="section-title">Sales Targeting Signals</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
kpis_row2 = [
    (c1, "Size Clicks (High Intent)", f"{size_clicks:,}",         "card-coral"),
    (c2, "Push Notifications Sent",   f"{push_delivered:,}",      "card-cyan"),
    (c3, "Avg Product Dwell Time",    avg_time_str,               "card-gold"),
    (c4, "Offer-Driven Clicks",       f"{offer_click_pct}%",      "card-lime"),
]
for col, label, val, css in kpis_row2:
    col.markdown(f"""
    <div class="metric-card {css}">
        <h3>{val}</h3><p>{label}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Traffic & Platform",
    "User Behaviour",
    "Product Insights",
    "Marketing Attribution",
    "Device & Network",
    "Time Patterns",
    "Sales Targeting",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Traffic & Platform
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Traffic Overview by Platform</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        plat_cnt = fdf["platform"].value_counts().reset_index()
        plat_cnt.columns = ["Platform", "Events"]
        fig = px.pie(plat_cnt, names="Platform", values="Events",
                     title="Events by Platform",
                     color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B", "#E65100", "#1565C0"],
                     hole=0.4)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        user_type_cnt = fdf.groupby("user_type")["userId"].nunique().reset_index()
        user_type_cnt.columns = ["User Type", "Unique Users"]
        fig = px.bar(user_type_cnt, x="User Type", y="Unique Users",
                     title="Unique Users: Logged-In vs Guest",
                     color="User Type",
                     color_discrete_sequence=["#E91E8C", "#7B1FA2"],
                     text="Unique Users")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_title="Unique Users",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    pt = fdf.groupby(["platform", "user_type"])["userId"].nunique().reset_index()
    pt.columns = ["Platform", "User Type", "Unique Users"]
    fig = px.bar(pt, x="Platform", y="Unique Users", color="User Type",
                 barmode="group",
                 title="Unique Users by Platform & User Type",
                 color_discrete_sequence=["#E91E8C", "#7B1FA2"])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — User Behaviour
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">User Action Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        action_cnt = fdf["action"].value_counts().head(15).reset_index()
        action_cnt.columns = ["Action", "Count"]
        fig = px.bar(action_cnt, x="Count", y="Action", orientation="h",
                     title="Top 15 User Actions",
                     color="Count",
                     color_continuous_scale=[[0, "#F3E5F5"], [0.5, "#AB47BC"], [1, "#6A1B9A"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        screen_cnt = fdf["pageScreenName"].fillna("Unknown").value_counts().head(10).reset_index()
        screen_cnt.columns = ["Page / Screen", "Events"]
        fig = px.bar(screen_cnt, x="Events", y="Page / Screen", orientation="h",
                     title="Top 10 Pages / Screens",
                     color="Events",
                     color_continuous_scale=[[0, "#E3F2FD"], [0.5, "#42A5F5"], [1, "#0D47A1"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Engagement: avg time on product per screen (derived from consecutive event gaps)
    st.markdown('<div class="section-title">Product Dwell Time by Screen</div>', unsafe_allow_html=True)
    if fdf["visit_time"].notna().any():
        _dwell = (
            fdf[fdf["visit_time"].notna() & fdf["pageScreenName"].notna()]
            .sort_values(["userId", "visit_time"])
            .copy()
        )
        _dwell["_next_time"] = _dwell.groupby("userId")["visit_time"].shift(-1)
        _dwell["_gap_sec"] = (_dwell["_next_time"] - _dwell["visit_time"]).dt.total_seconds()
        # Cap at 10 minutes to exclude session breaks
        _dwell = _dwell[(_dwell["_gap_sec"] > 0) & (_dwell["_gap_sec"] <= 600)]
        if not _dwell.empty:
            dwell_by_screen = (
                _dwell.groupby("pageScreenName")["_gap_sec"]
                .mean().round(1).reset_index()
                .sort_values("_gap_sec", ascending=False).head(10)
            )
            dwell_by_screen.columns = ["Screen", "Avg Dwell (sec)"]
            fig = px.bar(dwell_by_screen, x="Avg Dwell (sec)", y="Screen", orientation="h",
                         title="Avg Dwell Time per Screen — estimated from event gaps",
                         color="Avg Dwell (sec)",
                         color_continuous_scale=[[0, "#E8F5E9"], [0.5, "#66BB6A"], [1, "#1B5E20"]])
            fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    # Activity stream breakdown
    st.markdown('<div class="section-title">Activity Stream Breakdown</div>', unsafe_allow_html=True)
    act_stream = fdf.groupby(["activity", "action"]).size().reset_index(name="Count")
    act_stream = act_stream.sort_values("Count", ascending=False).head(30)
    fig = px.treemap(act_stream, path=["activity", "action"], values="Count",
                     title="Activity -> Action Treemap",
                     color="Count",
                     color_continuous_scale=[[0, "#FCE4EC"], [0.5, "#E91E8C"], [1, "#880E4F"]])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    # Scroll depth
    scroll_df = fdf[fdf["action"] == "listPage"].copy()
    if not scroll_df.empty:
        def extract_page(val):
            try:
                d = json.loads(str(val))
                return int(d.get("currentPage", 0))
            except Exception:
                return None
        scroll_df = scroll_df.copy()
        scroll_df["currentPage"] = scroll_df["actionDetails"].apply(extract_page)
        scroll_dist = scroll_df["currentPage"].dropna().value_counts().sort_index().reset_index()
        scroll_dist.columns = ["Page Depth", "Count"]
        st.markdown('<div class="section-title">Scroll Depth Distribution</div>', unsafe_allow_html=True)
        fig = px.bar(scroll_dist, x="Page Depth", y="Count",
                     title="Scroll Page Depth — How Far Users Browse",
                     color="Count",
                     color_continuous_scale=[[0, "#E8F5E9"], [0.5, "#26A69A"], [1, "#00695C"]])
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Product Insights
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Product Category Performance</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        cat_df = fdf[fdf["category"] != "Unknown"]["category"].value_counts().reset_index()
        cat_df.columns = ["Category", "Events"]
        fig = px.pie(cat_df, names="Category", values="Events",
                     title="Events by Category",
                     color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B", "#E65100",
                                              "#1565C0", "#BF360C", "#006064", "#33691E"],
                     hole=0.35)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cat_action = fdf[fdf["category"] != "Unknown"].groupby(["category", "action"]).size().reset_index(name="Count")
        cat_action = cat_action[cat_action["action"].isin(["listPage", "searchPage", "add", "sizeUpdate", "notificationClick"])]
        fig = px.bar(cat_action, x="category", y="Count", color="action",
                     title="Category Actions (Visit / Click / SizeClick / AddToCart)",
                     barmode="group",
                     color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B", "#E65100", "#1565C0"])
        fig.update_layout(xaxis_title="Category", yaxis_title="Count", xaxis_tickangle=-30,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Top SKUs
    st.markdown('<div class="section-title">Top Viewed / Clicked SKUs</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        sku_views = (
            fdf[fdf["sku"].notna() & (fdf["sku"] != "")]
            ["sku"].value_counts().head(15).reset_index()
        )
        sku_views.columns = ["SKU", "Views"]
        fig = px.bar(sku_views, x="Views", y="SKU", orientation="h",
                     title="Top 15 SKUs by Events",
                     color="Views",
                     color_continuous_scale=[[0, "#F3E5F5"], [0.5, "#AB47BC"], [1, "#6A1B9A"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sku_clicks = (
            fdf[(fdf["action"] == "add") & fdf["sku"].notna() & (fdf["sku"] != "")]
            ["sku"].value_counts().head(15).reset_index()
        )
        sku_clicks.columns = ["SKU", "Add to Cart"]
        fig = px.bar(sku_clicks, x="Add to Cart", y="SKU", orientation="h",
                     title="Top 15 SKUs by Add-to-Cart",
                     color="Add to Cart",
                     color_continuous_scale=[[0, "#FFF3E0"], [0.5, "#FFA726"], [1, "#BF360C"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Price range distribution
    price_df = fdf[fdf["mrp"].notna() & (fdf["mrp"] > 0)].copy()
    if not price_df.empty:
        st.markdown('<div class="section-title">Price Distribution (MRP vs Special Price)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=price_df["mrp"], name="MRP", opacity=0.7,
                                   marker_color="#7B1FA2", nbinsx=40))
        fig.add_trace(go.Histogram(x=price_df["specialprice"].dropna(), name="Special Price",
                                   opacity=0.7, marker_color="#E91E8C", nbinsx=40))
        fig.update_layout(barmode="overlay", title="Price Distribution of Viewed Products",
                          xaxis_title="Price (INR)", yaxis_title="Count",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Offer analysis
    st.markdown('<div class="section-title">Offer / Discount Engagement</div>', unsafe_allow_html=True)
    def extract_offers(val):
        try:
            d = json.loads(str(val))
            offers = d.get("offerDetails", [])
            if isinstance(offers, list):
                return offers
        except Exception:
            pass
        return []

    all_offers = fdf["actionDetails"].dropna().apply(extract_offers).explode()
    all_offers = all_offers[all_offers.notna() & (all_offers != "")]
    offer_cnt = all_offers.value_counts().head(20).reset_index()
    offer_cnt.columns = ["Offer", "Count"]
    if not offer_cnt.empty:
        fig = px.bar(offer_cnt, x="Count", y="Offer", orientation="h",
                     title="Top Offers Driving User Clicks",
                     color="Count",
                     color_continuous_scale=[[0, "#E0F7FA"], [0.5, "#4DD0E1"], [1, "#006064"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Marketing Attribution
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Traffic Source Attribution</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        src_df = fdf["utmSource"].fillna("Organic / Direct").value_counts().head(15).reset_index()
        src_df.columns = ["UTM Source", "Events"]
        fig = px.bar(src_df, x="Events", y="UTM Source", orientation="h",
                     title="Top Traffic Sources (UTM Source)",
                     color="Events",
                     color_continuous_scale=[[0, "#E3F2FD"], [0.5, "#42A5F5"], [1, "#0D47A1"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        med_df = fdf["utmMedium"].fillna("None").value_counts().head(15).reset_index()
        med_df.columns = ["UTM Medium", "Events"]
        fig = px.bar(med_df, x="Events", y="UTM Medium", orientation="h",
                     title="Traffic Medium (UTM Medium)",
                     color="Events",
                     color_continuous_scale=[[0, "#E8F5E9"], [0.5, "#66BB6A"], [1, "#1B5E20"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    camp_df = fdf["utmCampaign"].fillna("None").value_counts().head(20).reset_index()
    camp_df.columns = ["Campaign", "Events"]
    camp_df = camp_df[camp_df["Campaign"] != "None"]
    if not camp_df.empty:
        fig = px.bar(camp_df, x="Events", y="Campaign", orientation="h",
                     title="Top UTM Campaigns",
                     color="Events",
                     color_continuous_scale=[[0, "#F3E5F5"], [0.5, "#AB47BC"], [1, "#6A1B9A"]])
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        ref_src = fdf["refererSource"].fillna("Direct").value_counts().head(10).reset_index()
        ref_src.columns = ["Referrer Source", "Events"]
        fig = px.pie(ref_src, names="Referrer Source", values="Events",
                     title="Referrer Source Distribution",
                     color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B", "#E65100",
                                              "#1565C0", "#BF360C", "#006064", "#33691E", "#880E4F", "#0D47A1"],
                     hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ref_med = fdf["refererMedium"].fillna("Direct").value_counts().head(10).reset_index()
        ref_med.columns = ["Referrer Medium", "Events"]
        fig = px.pie(ref_med, names="Referrer Medium", values="Events",
                     title="Referrer Medium Distribution",
                     color_discrete_sequence=["#AB47BC", "#42A5F5", "#FFA726", "#66BB6A",
                                              "#4DD0E1", "#EF9A9A", "#7986CB", "#C5E1A5", "#F06292", "#80DEEA"],
                     hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    track_df = fdf["trackSrc"].fillna("None").value_counts().head(10).reset_index()
    track_df.columns = ["Track Source", "Events"]
    track_df = track_df[track_df["Track Source"] != "None"]
    if not track_df.empty:
        st.markdown('<div class="section-title">In-App Navigation Source (trackSrc)</div>', unsafe_allow_html=True)
        fig = px.bar(track_df, x="Track Source", y="Events",
                     title="Top In-App Navigation Sources",
                     color="Events",
                     color_continuous_scale=[[0, "#FFF3E0"], [0.5, "#FFA726"], [1, "#BF360C"]])
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — Device & Network
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Device & OS Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        os_df = fdf["deviceOs"].fillna("Web/Unknown").value_counts().reset_index()
        os_df.columns = ["OS", "Events"]
        fig = px.pie(os_df, names="OS", values="Events",
                     title="Events by Device OS",
                     color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B", "#E65100", "#1565C0"],
                     hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        net_df = fdf["networkType"].value_counts().reset_index()
        net_df.columns = ["Network", "Events"]
        fig = px.pie(net_df, names="Network", values="Events",
                     title="Network Type Distribution",
                     color_discrete_sequence=["#AB47BC", "#42A5F5", "#FFA726", "#66BB6A", "#4DD0E1"],
                     hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    device_df = fdf["deviceModel"].fillna("Unknown").value_counts().head(20).reset_index()
    device_df.columns = ["Device Model", "Events"]
    fig = px.bar(device_df, x="Events", y="Device Model", orientation="h",
                 title="Top 20 Device Models",
                 color="Events",
                 color_continuous_scale=[[0, "#E0F7FA"], [0.5, "#4DD0E1"], [1, "#006064"]])
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    os_ver = fdf["osVersion"].fillna("Unknown").astype(str).value_counts().head(15).reset_index()
    os_ver.columns = ["OS Version", "Events"]
    fig = px.bar(os_ver, x="Events", y="OS Version", orientation="h",
                 title="Top OS Versions",
                 color="Events",
                 color_continuous_scale=[[0, "#FCE4EC"], [0.5, "#E91E8C"], [1, "#880E4F"]])
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — Time Patterns
# ════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">Visitor Time Patterns</div>', unsafe_allow_html=True)

    hourly = fdf.groupby("visit_hour").size().reset_index(name="Events")
    fig = px.bar(hourly, x="visit_hour", y="Events",
                 title="Events by Hour of Day",
                 labels={"visit_hour": "Hour (24h)", "Events": "Event Count"},
                 color="Events",
                 color_continuous_scale=[[0, "#F3E5F5"], [0.5, "#AB47BC"], [1, "#6A1B9A"]])
    fig.update_layout(coloraxis_showscale=False,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = fdf.groupby("visit_dow").size().reset_index(name="Events")
        dow["visit_dow"] = pd.Categorical(dow["visit_dow"], categories=dow_order, ordered=True)
        dow = dow.sort_values("visit_dow")
        fig = px.bar(dow, x="visit_dow", y="Events",
                     title="Events by Day of Week",
                     labels={"visit_dow": "Day"},
                     color="Events",
                     color_continuous_scale=[[0, "#E3F2FD"], [0.5, "#42A5F5"], [1, "#0D47A1"]])
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        heat = fdf.groupby(["visit_hour", "platform"]).size().reset_index(name="Events")
        heat_pivot = heat.pivot(index="platform", columns="visit_hour", values="Events").fillna(0)
        fig = px.imshow(heat_pivot,
                        title="Heatmap: Platform vs Hour of Day",
                        labels={"x": "Hour", "y": "Platform", "color": "Events"},
                        color_continuous_scale=[[0, "#FCE4EC"], [0.5, "#E91E8C"], [1, "#880E4F"]],
                        aspect="auto")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    daily = fdf.groupby("visit_date").size().reset_index(name="Events")
    daily["visit_date"] = pd.to_datetime(daily["visit_date"])
    fig = px.line(daily, x="visit_date", y="Events",
                  title="Daily Event Volume",
                  markers=True,
                  line_shape="spline",
                  color_discrete_sequence=["#E91E8C"])
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(xaxis_title="Date", yaxis_title="Events",
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 7 — Sales Targeting
# ════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-title">Conversion Funnel</div>', unsafe_allow_html=True)

    # ── Conversion funnel ───────────────────────────────────────────────────
    funnel_steps = {
        "Product Browse (listPage)":     fdf[fdf["action"] == "listPage"]["userId"].nunique(),
        "Search Intent (searchPage)":    fdf[fdf["action"] == "searchPage"]["userId"].nunique(),
        "Add to Cart (add)":             fdf[fdf["action"] == "add"]["userId"].nunique(),
        "Size Selected (sizeUpdate)":    fdf[fdf["action"] == "sizeUpdate"]["userId"].nunique(),
        "Order Placed (prepaid/cod)":    fdf[fdf["action"].isin(["prepaid", "cod"])]["userId"].nunique(),
    }
    funnel_df = pd.DataFrame(list(funnel_steps.items()), columns=["Stage", "Users"])
    funnel_df = funnel_df[funnel_df["Users"] > 0]

    fig = go.Figure(go.Funnel(
        y=funnel_df["Stage"],
        x=funnel_df["Users"],
        textinfo="value+percent initial",
        marker=dict(color=["#E91E8C", "#7B1FA2", "#00897B", "#E65100"]),
        connector=dict(line=dict(color="#888", dash="dot", width=2)),
    ))
    fig.update_layout(
        title="Purchase Conversion Funnel",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Conversion rate metrics
    if not funnel_df.empty and funnel_df["Users"].iloc[0] > 0:
        browse_users  = funnel_df["Users"].iloc[0]
        cart_row      = funnel_df[funnel_df["Stage"].str.contains("Cart", case=False)]["Users"]
        size_row      = funnel_df[funnel_df["Stage"].str.contains("Size", case=False)]["Users"]
        order_row     = funnel_df[funnel_df["Stage"].str.contains("Order", case=False)]["Users"]
        col1, col2, col3 = st.columns(3)
        browse_to_cart = round(cart_row.values[0] / browse_users * 100, 1) if len(cart_row) > 0 else 0
        col1.markdown(f"""<div class="metric-card card-pink"><h3>{browse_to_cart}%</h3><p>Browse-to-Cart Rate</p></div>""", unsafe_allow_html=True)
        if len(size_row) > 0:
            intent_rate = round(size_row.values[0] / browse_users * 100, 1)
            col2.markdown(f"""<div class="metric-card card-purple"><h3>{intent_rate}%</h3><p>Browse-to-Size Select Rate</p></div>""", unsafe_allow_html=True)
        if len(order_row) > 0:
            conversion_rate = round(order_row.values[0] / browse_users * 100, 1)
            col3.markdown(f"""<div class="metric-card card-teal"><h3>{conversion_rate}%</h3><p>Overall Conversion Rate</p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Customer Scoring ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Customer Behaviour Scoring</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
        <b>How the Score Works:</b> Each user earns points based on 8 behavioural signals —
        <b>Add to Cart (+20)</b>, <b>Size Click (+15)</b>, <b>Filter Used (+10)</b>,
        <b>Product Click (+5)</b>, <b>Deep Scroll (+5)</b>, <b>Product View (+2)</b>,
        <b>Dwell Time (+up to 10)</b>, <b>Logged-In (+5)</b>.
        Higher score = stronger purchase intent = higher targeting priority.
    </div>""", unsafe_allow_html=True)

    score_df = compute_scores(fdf.drop(columns=["_ad"], errors="ignore"))

    # Score summary KPIs
    tier_colors = {
        "Hot Target":  "card-rose",
        "Warm Target": "card-amber",
        "Potential":   "card-blue",
        "Cold Lead":   "card-indigo",
    }
    tier_counts = score_df["tier"].value_counts()
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, tier_name in zip([sc1, sc2, sc3, sc4],
                               ["Hot Target", "Warm Target", "Potential", "Cold Lead"]):
        cnt = int(tier_counts.get(tier_name, 0))
        css = tier_colors[tier_name]
        col.markdown(f"""
        <div class="metric-card {css}">
            <h3>{cnt:,}</h3><p>{tier_name} Users</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        tier_dist = score_df["tier"].value_counts().reset_index()
        tier_dist.columns = ["Tier", "Users"]
        tier_order = ["Hot Target", "Warm Target", "Potential", "Cold Lead"]
        tier_dist["Tier"] = pd.Categorical(tier_dist["Tier"], categories=tier_order, ordered=True)
        tier_dist = tier_dist.sort_values("Tier")
        fig = px.bar(
            tier_dist, x="Tier", y="Users",
            title="User Distribution by Target Tier",
            color="Tier",
            color_discrete_map={
                "Hot Target":  "#E91E8C",
                "Warm Target": "#E65100",
                "Potential":   "#1565C0",
                "Cold Lead":   "#1A237E",
            },
            text="Users",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            score_df, x="total_score", nbins=30,
            title="Score Distribution Across All Users",
            color_discrete_sequence=["#E91E8C"],
            labels={"total_score": "Behaviour Score"},
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Score breakdown: what drives it
    score_breakdown = score_df[["action_score", "scroll_score", "dwell_score",
                                 "cat_score", "login_score"]].mean().round(1).reset_index()
    score_breakdown.columns = ["Component", "Avg Points"]
    score_breakdown["Component"] = score_breakdown["Component"].map({
        "action_score":  "Action Score (Cart/Click/View)",
        "scroll_score":  "Deep Scroll Bonus",
        "dwell_score":   "Dwell Time Bonus",
        "cat_score":     "Category Diversity Bonus",
        "login_score":   "Logged-In Bonus",
    })
    fig = px.bar(
        score_breakdown, x="Avg Points", y="Component", orientation="h",
        title="Avg Score Contribution by Signal (What Drives Targeting)",
        color="Avg Points",
        color_continuous_scale=[[0, "#FCE4EC"], [0.5, "#E91E8C"], [1, "#880E4F"]],
        text="Avg Points",
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    # Tier by platform
    tier_plat = score_df.groupby(["platform", "tier"]).size().reset_index(name="Users")
    fig = px.bar(
        tier_plat, x="platform", y="Users", color="tier",
        title="Target Tiers by Platform",
        barmode="stack",
        color_discrete_map={
            "Hot Target":  "#E91E8C",
            "Warm Target": "#E65100",
            "Potential":   "#1565C0",
            "Cold Lead":   "#1A237E",
        },
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    # Scored user table
    st.markdown('<div class="section-title">Scored User List — Prioritised for Targeting</div>',
                unsafe_allow_html=True)
    tier_filter = st.selectbox(
        "Filter by Tier",
        options=["All", "Hot Target", "Warm Target", "Potential", "Cold Lead"],
        index=0,
    )
    display_scores = score_df if tier_filter == "All" else score_df[score_df["tier"] == tier_filter]
    display_table = display_scores[[
        "userId", "tier", "total_score", "email", "mobile",
        "platform", "user_type", "top_category", "top_sku",
        "total_events", "last_seen",
    ]].copy()
    display_table["last_seen"] = display_table["last_seen"].dt.strftime("%d %b %Y %H:%M")
    display_table["email"]  = display_table["email"].replace("", "—")
    display_table["mobile"] = display_table["mobile"].astype(str).replace("nan", "—").replace("", "—")
    display_table.columns = [
        "User ID", "Target Tier", "Score", "Email", "Mobile",
        "Platform", "User Type", "Top Category", "Top SKU",
        "Total Events", "Last Seen",
    ]
    st.dataframe(display_table.head(100), use_container_width=True, hide_index=True)
    csv_scores = display_table.to_csv(index=False)
    st.download_button(
        "Download Scored Users CSV",
        data=csv_scores,
        file_name="shyaway_scored_users.csv",
        mime="text/csv",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Target Contact List ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">Target Contact List — Email & Phone</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
        Only users with a known <b>email</b> or <b>mobile number</b> are shown here,
        sorted by targeting priority (Hot Target first). Use this list for direct outreach,
        push campaigns, SMS/WhatsApp, or CRM import.
    </div>""", unsafe_allow_html=True)

    # Build contact list from score_df — keep only rows with contact info
    contact_df = score_df.copy()
    contact_df["email"]  = contact_df["email"].astype(str).str.strip()
    contact_df["mobile"] = contact_df["mobile"].astype(str).str.strip()
    # Normalise empty / nan
    contact_df["email"]  = contact_df["email"].replace({"nan": "", "0": "", "0.0": ""})
    contact_df["mobile"] = contact_df["mobile"].replace({"nan": "", "0": "", "0.0": ""})
    contact_df["has_contact"] = (
        (contact_df["email"] != "") | (contact_df["mobile"] != "")
    )
    contact_list = contact_df[contact_df["has_contact"]].copy()

    # Summary counts
    total_contacts   = len(contact_list)
    hot_contacts     = (contact_list["tier"] == "Hot Target").sum()
    warm_contacts    = (contact_list["tier"] == "Warm Target").sum()
    with_email       = (contact_list["email"] != "").sum()
    with_mobile      = (contact_list["mobile"] != "").sum()
    with_both        = ((contact_list["email"] != "") & (contact_list["mobile"] != "")).sum()

    cc1, cc2, cc3, cc4, cc5, cc6 = st.columns(6)
    for col, label, val, css in [
        (cc1, "Total Contacts",    f"{total_contacts:,}",  "card-pink"),
        (cc2, "Hot Targets",       f"{hot_contacts:,}",    "card-rose"),
        (cc3, "Warm Targets",      f"{warm_contacts:,}",   "card-amber"),
        (cc4, "Have Email",        f"{with_email:,}",      "card-teal"),
        (cc5, "Have Mobile",       f"{with_mobile:,}",     "card-blue"),
        (cc6, "Email + Mobile",    f"{with_both:,}",       "card-purple"),
    ]:
        col.markdown(f"""
        <div class="metric-card {css}">
            <h3>{val}</h3><p>{label}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter controls
    cf1, cf2, cf3 = st.columns(3)
    with cf1:
        contact_tier = st.selectbox(
            "Filter by Tier",
            options=["All", "Hot Target", "Warm Target", "Potential", "Cold Lead"],
            key="contact_tier_filter",
        )
    with cf2:
        contact_channel = st.selectbox(
            "Has Contact",
            options=["All", "Email only", "Mobile only", "Both Email & Mobile"],
            key="contact_channel_filter",
        )
    with cf3:
        min_score = st.slider("Minimum Score", min_value=0,
                              max_value=int(contact_list["total_score"].max()) if not contact_list.empty else 100,
                              value=0, key="contact_min_score")

    # Apply filters
    cl = contact_list.copy()
    if contact_tier != "All":
        cl = cl[cl["tier"] == contact_tier]
    if contact_channel == "Email only":
        cl = cl[(cl["email"] != "") & (cl["mobile"] == "")]
    elif contact_channel == "Mobile only":
        cl = cl[(cl["mobile"] != "") & (cl["email"] == "")]
    elif contact_channel == "Both Email & Mobile":
        cl = cl[(cl["email"] != "") & (cl["mobile"] != "")]
    cl = cl[cl["total_score"] >= min_score]

    # Build display table
    cl_display = cl[[
        "tier", "total_score", "email", "mobile",
        "platform", "user_type", "top_category", "top_sku", "last_seen",
    ]].copy()
    cl_display["last_seen"] = cl_display["last_seen"].dt.strftime("%d %b %Y %H:%M")
    cl_display["email"]  = cl_display["email"].replace("", "—")
    cl_display["mobile"] = cl_display["mobile"].replace("", "—")
    cl_display.columns = [
        "Target Tier", "Score", "Email", "Mobile",
        "Platform", "User Type", "Top Category", "Top SKU", "Last Active",
    ]

    st.caption(f"Showing {len(cl_display):,} contactable users")
    st.dataframe(cl_display, use_container_width=True, hide_index=True)

    csv_contacts = cl_display.to_csv(index=False)
    st.download_button(
        "Download Contact List CSV",
        data=csv_contacts,
        file_name="shyaway_target_contacts.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── User Intent Segments ────────────────────────────────────────────────
    st.markdown('<div class="section-title">User Intent Segments</div>', unsafe_allow_html=True)

    user_actions = fdf.groupby("userId")["action"].apply(list).reset_index()
    user_actions.columns = ["userId", "actions"]

    def classify_intent(actions):
        action_set = set(actions)
        if "sizeUpdate" in action_set or "add" in action_set:
            return "High Intent"
        elif "notificationClick" in action_set or "searchPage" in action_set:
            return "Medium Intent"
        else:
            return "Low Intent"

    user_actions["intent"] = user_actions["actions"].apply(classify_intent)
    intent_counts = user_actions["intent"].value_counts().reset_index()
    intent_counts.columns = ["Intent Segment", "Users"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            intent_counts, names="Intent Segment", values="Users",
            title="User Intent Distribution",
            color="Intent Segment",
            color_discrete_map={
                "High Intent":   "#E91E8C",
                "Medium Intent": "#7B1FA2",
                "Low Intent":    "#1565C0",
            },
            hole=0.45,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            intent_counts, x="Intent Segment", y="Users",
            title="Users by Intent Segment",
            color="Intent Segment",
            color_discrete_map={
                "High Intent":   "#E91E8C",
                "Medium Intent": "#7B1FA2",
                "Low Intent":    "#1565C0",
            },
            text="Users",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Insight box
    hi_users = intent_counts[intent_counts["Intent Segment"] == "High Intent"]["Users"].values
    med_users = intent_counts[intent_counts["Intent Segment"] == "Medium Intent"]["Users"].values
    if len(hi_users) > 0 and len(med_users) > 0:
        st.markdown(f"""
        <div class="insight-box">
            <b>Targeting Tip:</b> {int(hi_users[0]):,} High-Intent users selected a size — these are your hottest leads.
            Target them with limited-time offers or cart-recovery push notifications.
            {int(med_users[0]):,} Medium-Intent users clicked but didn't select a size — retarget with product
            recommendations and discount nudges.
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Color Preference Analysis ───────────────────────────────────────────
    st.markdown('<div class="section-title">Color Preference from Clicked SKUs</div>', unsafe_allow_html=True)

    color_clicks = (
        fdf[fdf["sku_color"].notna()]
        ["sku_color"].value_counts().head(20).reset_index()
    )
    color_clicks.columns = ["Color", "Clicks"]

    if not color_clicks.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                color_clicks.head(15), x="Clicks", y="Color", orientation="h",
                title="Top 15 Colors by Click Count",
                color="Clicks",
                color_continuous_scale=[[0, "#FCE4EC"], [0.5, "#E91E8C"], [1, "#880E4F"]],
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                color_clicks.head(10), names="Color", values="Clicks",
                title="Top 10 Color Share of Clicks",
                color_discrete_sequence=[
                    "#E91E8C", "#7B1FA2", "#00897B", "#E65100", "#1565C0",
                    "#BF360C", "#006064", "#880E4F", "#AB47BC", "#42A5F5"
                ],
                hole=0.4,
            )
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        # Color preference by user intent segment
        color_intent = fdf[fdf["sku_color"].notna()].copy()
        color_intent = color_intent.merge(user_actions[["userId", "intent"]], on="userId", how="left")
        ci_grouped = color_intent.groupby(["sku_color", "intent"]).size().reset_index(name="Clicks")
        ci_top = ci_grouped.groupby("sku_color")["Clicks"].sum().nlargest(10).index
        ci_grouped = ci_grouped[ci_grouped["sku_color"].isin(ci_top)]
        fig = px.bar(
            ci_grouped, x="sku_color", y="Clicks", color="intent",
            title="Color Preference by User Intent Segment",
            barmode="group",
            color_discrete_map={
                "High Intent":   "#E91E8C",
                "Medium Intent": "#7B1FA2",
                "Low Intent":    "#1565C0",
            },
        )
        fig.update_layout(xaxis_title="Color", xaxis_tickangle=-30,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Discount / Price Sensitivity ────────────────────────────────────────
    st.markdown('<div class="section-title">Discount & Price Sensitivity</div>', unsafe_allow_html=True)

    click_df = fdf[(fdf["action"] == "add") & fdf["mrp"].notna() & (fdf["mrp"] > 0)].copy()
    if not click_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            offer_split = click_df["has_offer"].value_counts().reset_index()
            offer_split.columns = ["Has Offer", "Clicks"]
            offer_split["Has Offer"] = offer_split["Has Offer"].map({True: "With Offer", False: "No Offer"})
            fig = px.pie(
                offer_split, names="Has Offer", values="Clicks",
                title="Clicks: With Offer vs No Offer",
                color="Has Offer",
                color_discrete_map={"With Offer": "#E91E8C", "No Offer": "#7B1FA2"},
                hole=0.45,
            )
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            discount_bins = pd.cut(click_df["discount_pct"].dropna(),
                                   bins=[0, 10, 20, 30, 40, 50, 60, 100],
                                   labels=["0-10%", "11-20%", "21-30%", "31-40%", "41-50%", "51-60%", "60%+"])
            disc_dist = discount_bins.value_counts().sort_index().reset_index()
            disc_dist.columns = ["Discount Range", "Clicks"]
            fig = px.bar(
                disc_dist, x="Discount Range", y="Clicks",
                title="Clicks by Discount Range",
                color="Clicks",
                color_continuous_scale=[[0, "#FFF3E0"], [0.5, "#FFA726"], [1, "#BF360C"]],
                text="Clicks",
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(coloraxis_showscale=False,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        # Price range vs click count
        price_bins = pd.cut(click_df["mrp"], bins=[0, 299, 499, 699, 999, 1499, 99999],
                            labels=["<300", "300-499", "500-699", "700-999", "1000-1499", "1500+"])
        price_dist = price_bins.value_counts().sort_index().reset_index()
        price_dist.columns = ["Price Range (MRP)", "Clicks"]
        fig = px.bar(
            price_dist, x="Price Range (MRP)", y="Clicks",
            title="Clicks by Product Price Range (MRP) — Where Demand Sits",
            color="Clicks",
            color_continuous_scale=[[0, "#E8F5E9"], [0.5, "#66BB6A"], [1, "#1B5E20"]],
            text="Clicks",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Push Notification Performance ───────────────────────────────────────
    st.markdown('<div class="section-title">Push Notification Performance</div>', unsafe_allow_html=True)

    push_actions = fdf[fdf["event"] == "appPush"]["action"].value_counts().reset_index()
    push_actions.columns = ["Action", "Count"]

    if not push_actions.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                push_actions, x="Action", y="Count",
                title="Push Notification Actions",
                color="Action",
                color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B", "#E65100"],
                text="Count",
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Extract push notification titles from actionDetails
            def extract_push_title(val):
                try:
                    d = json.loads(str(val))
                    nd = d.get("notificationDetails", {})
                    return nd.get("title", None)
                except Exception:
                    return None

            push_df = fdf[(fdf["event"] == "appPush") & (fdf["action"] == "notificationDelivered")].copy()
            push_df["push_title"] = push_df["actionDetails"].apply(extract_push_title)
            title_cnt = push_df["push_title"].dropna().value_counts().head(10).reset_index()
            title_cnt.columns = ["Push Title", "Count"]
            if not title_cnt.empty:
                fig = px.bar(
                    title_cnt, x="Count", y="Push Title", orientation="h",
                    title="Top Push Notification Campaigns Delivered",
                    color="Count",
                    color_continuous_scale=[[0, "#E0F7FA"], [0.5, "#4DD0E1"], [1, "#006064"]],
                )
                fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                                  plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

    # Push activity over time
    push_time = fdf[fdf["event"] == "appPush"].copy()
    if not push_time.empty:
        push_daily = push_time.groupby(["visit_date", "action"]).size().reset_index(name="Count")
        push_daily["visit_date"] = pd.to_datetime(push_daily["visit_date"])
        fig = px.line(
            push_daily, x="visit_date", y="Count", color="action",
            title="Push Notification Events Over Time",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#E91E8C", "#7B1FA2", "#00897B"],
        )
        fig.update_layout(xaxis_title="Date", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── High-Intent User Table ───────────────────────────────────────────────
    st.markdown('<div class="section-title">High-Intent Users — Ready to Buy</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
        <b>Who are High-Intent Users?</b> Users who performed a <b>sizeUpdate</b> (selected a size on a product)
        are the strongest purchase-intent signal — they are one step away from buying.
        Target these users with cart-recovery messages, limited stock alerts, or exclusive coupon codes.
    </div>""", unsafe_allow_html=True)

    hi_intent_df = fdf[fdf["action"] == "sizeUpdate"].copy()
    if not hi_intent_df.empty:
        def extract_simple_sku(val):
            try:
                d = json.loads(str(val))
                return d.get("simpleSku", d.get("sku", None))
            except Exception:
                return None

        hi_intent_df["simpleSku"] = hi_intent_df["actionDetails"].apply(extract_simple_sku)
        hi_summary = (
            hi_intent_df.groupby("userId")
            .agg(
                size_clicks=("action", "count"),
                skus_interested=("sku", lambda x: ", ".join(x.dropna().unique()[:3])),
                platform=("platform", "first"),
                last_seen=("visit_time", "max"),
                avg_mrp=("mrp", "mean"),
            )
            .reset_index()
            .sort_values("size_clicks", ascending=False)
        )
        hi_summary["avg_mrp"] = hi_summary["avg_mrp"].round(0)
        hi_summary["last_seen"] = hi_summary["last_seen"].dt.strftime("%d %b %Y %H:%M")
        hi_summary.columns = ["User ID", "Size Clicks", "Top SKUs Viewed", "Platform", "Last Seen", "Avg MRP (INR)"]
        st.dataframe(hi_summary.head(50), use_container_width=True, hide_index=True)

        csv_hi = hi_summary.to_csv(index=False)
        st.download_button(
            "Download High-Intent Users CSV",
            data=csv_hi,
            file_name="shyaway_high_intent_users.csv",
            mime="text/csv",
        )
    else:
        st.info("No sizeUpdate events found in the current filter. Try broadening your filters.")


# ── Raw Data Explorer ────────────────────────────────────────────────────────
with st.expander("Raw Data Explorer", expanded=False):
    st.markdown("Showing first 500 filtered rows")
    cols_show = ["visit_time", "user_type", "platform", "action", "category", "sku",
                 "pageScreenName", "utmSource", "utmMedium", "utmCampaign",
                 "deviceModel", "networkType", "email", "mobile"]
    cols_show = [c for c in cols_show if c in fdf.columns]
    st.dataframe(fdf[cols_show].head(500), use_container_width=True)
    csv_data = fdf[cols_show].to_csv(index=False)
    st.download_button("Download Filtered Data as CSV", data=csv_data,
                       file_name="shyaway_filtered_visitors.csv", mime="text/csv")

st.divider()
st.caption("ShyAway Target User Dashboard | Built with Streamlit & Plotly")
