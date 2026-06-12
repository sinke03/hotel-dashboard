import os
from pathlib import Path
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================================
# HOTEL REVENUE INTELLIGENCE
# Original dashboard style + updated multi-source analysis
# Files supported:
# 1. cleaned_hotel_data.xlsx
# 2. cleaned_portugal_arrivals.xlsx
# 3. cleaned_Portugal_Public_Holidays_2015_2017.xlsx
# ==========================================================

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Hotel Revenue Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme CSS — kept from your original code ──────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #060B18; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0A1020 !important; border-right: 1px solid #1A2540; }
section[data-testid="stSidebar"] * { color: #8899BB !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #E0E6F0 !important; }

/* KPI Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0D1628 0%, #152240 100%);
    border: 1px solid #2A3F6A;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
}
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] [data-testid="stMetricLabel"],
div[data-testid="metric-container"] [data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.10em;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"],
div[data-testid="metric-container"] div[data-testid="stMetricValue"] > div,
div[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    text-shadow: 0 0 20px rgba(74,158,255,0.3);
    line-height: 1.15 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] {
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* Section headers */
.section-header {
    font-size: 16px; font-weight: 600; color: #C8D8F0;
    margin: 1.5rem 0 1rem 0; letter-spacing: 0.02em;
    display: flex; align-items: center; gap: 8px;
}
.section-header::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, #1A2A45 0%, transparent 100%);
}

/* File badge row */
.file-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0F1E38; border: 1px solid #2A4070;
    border-radius: 8px; padding: 4px 10px;
    font-size: 12px; color: #7ABAFF; margin: 3px;
}

/* Insight cards */
.insight-card {
    background: linear-gradient(135deg, #0D1628, #0F1A2E);
    border: 1px solid #1A2A45; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.insight-title { font-size: 12px; color: #5577AA; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.insight-value { font-size: 22px; font-weight: 700; margin-bottom: 2px; }
.insight-desc { font-size: 12px; color: #5577AA; line-height: 1.5; }

/* Updated recommendation / explanation cards */
.action-card {
    background: linear-gradient(135deg, #0D1628, #0F1A2E);
    border: 1px solid #1A2A45;
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.action-title { color: #E0E6F0; font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.action-desc { color: #8899BB; font-size: 13px; line-height: 1.55; }

/* Tabs */
div[data-testid="stTabs"] button { color: #6688AA !important; font-size: 13px !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #4A9EFF !important; }

/* Divider */
hr { border-color: #1A2A45 !important; }

/* Plotly charts bg */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

/* File uploader */
[data-testid="stFileUploader"] { background: transparent !important; }

/* Info/success boxes */
div[data-testid="stAlert"] { border-radius: 10px !important; }

/* Multiselect tag: blue instead of red */
span[data-baseweb="tag"] {
    background-color: #1A3A6A !important;
    border: 1px solid #2A5099 !important;
}
span[data-baseweb="tag"] span { color: #7ABAFF !important; }
span[data-baseweb="tag"] button svg { fill: #7ABAFF !important; }
</style>
""", unsafe_allow_html=True)

# ── Color Palette ─────────────────────────────────────────
BLUE    = "#4A9EFF"
GREEN   = "#22D47B"
RED     = "#FF5A5A"
AMBER   = "#FFB830"
PURPLE  = "#A855F7"
CYAN    = "#06B6D4"
PINK    = "#EC4899"
COLORS  = [BLUE, GREEN, AMBER, RED, PURPLE, CYAN, PINK, "#F97316"]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,22,40,0.6)",
    font=dict(family="Inter", color="#8899BB", size=12),
    margin=dict(t=30, b=10, l=10, r=10),
    xaxis=dict(gridcolor="#1A2A45", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#1A2A45", showline=False, zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1A2A45", font=dict(color="#8899BB")),
    hoverlabel=dict(bgcolor="#0D1628", bordercolor="#1A2A45", font=dict(color="#E0E6F0")),
)

MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTH_ORDER)}

# ── Helper functions ──────────────────────────────────────
def merged_layout(height, **overrides):
    layout = dict(**CHART_LAYOUT)
    layout.update(overrides)
    layout['height'] = height
    return layout


def chart(fig, height=340):
    fig.update_layout(**merged_layout(height))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def get_season(m):
    if pd.isna(m):
        return "Unknown"
    if m in ['June','July','August']:
        return '☀️ Summer'
    elif m in ['March','April','May']:
        return '🌸 Spring'
    elif m in ['September','October','November']:
        return '🍂 Autumn'
    else:
        return '❄️ Winter'


def money_m(x):
    if pd.isna(x):
        return "$0.00M"
    return f"${x/1_000_000:,.2f}M"


def pct(x):
    if pd.isna(x):
        return "0.0%"
    return f"{x:,.1f}%"


@st.cache_data(show_spinner=False)
def read_any_file(file_bytes, file_name):
    """Read CSV or Excel from uploaded bytes."""
    if file_name.lower().endswith('.csv'):
        return pd.read_csv(io.BytesIO(file_bytes))
    return pd.read_excel(io.BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def read_default_excel(path):
    """Auto-load local files when the script is in the same folder as the datasets."""
    if Path(path).exists():
        return pd.read_excel(path)
    return None


def load_dataset(uploaded_file, default_path):
    """Upload-first, then default-local-file fallback."""
    if uploaded_file is not None:
        return read_any_file(uploaded_file.getvalue(), uploaded_file.name), uploaded_file.name
    default_df = read_default_excel(default_path)
    if default_df is not None:
        return default_df, default_path
    return None, None


def prepare_hotel_data(df):
    """Clean hotel booking data and create revenue/cancellation fields used by the dashboard."""
    df = df.copy()

    # Date + month fields
    if 'arrival_date' in df.columns:
        df['arrival_date'] = pd.to_datetime(df['arrival_date'], errors='coerce')
    else:
        df['arrival_date'] = pd.NaT

    if 'arrival_year' not in df.columns:
        df['arrival_year'] = df['arrival_date'].dt.year
    if 'arrival_month' not in df.columns:
        df['arrival_month'] = df['arrival_date'].dt.month
    if 'arrival_month_name' not in df.columns:
        df['arrival_month_name'] = df['arrival_date'].dt.strftime('%B')

    # Numeric safety
    for col in ['is_canceled', 'adr', 'lead_time', 'total_stay_nights',
                'stays_in_weekend_nights', 'stays_in_week_nights',
                'previous_cancellations', 'is_repeated_guest',
                'total_of_special_requests']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Stay nights + revenue
    if 'total_stay_nights' not in df.columns:
        weekend = df['stays_in_weekend_nights'] if 'stays_in_weekend_nights' in df.columns else 0
        week = df['stays_in_week_nights'] if 'stays_in_week_nights' in df.columns else 0
        df['total_stay_nights'] = weekend + week

    df['total_stay_nights'] = pd.to_numeric(df['total_stay_nights'], errors='coerce').fillna(0)
    df['stay_nights_for_revenue'] = df['total_stay_nights'].clip(lower=1)

    if 'estimated_revenue' not in df.columns:
        df['estimated_revenue'] = df['adr'] * df['stay_nights_for_revenue']
    else:
        df['estimated_revenue'] = pd.to_numeric(df['estimated_revenue'], errors='coerce').fillna(0)

    # Business fields
    if 'season' not in df.columns:
        df['season'] = df['arrival_month_name'].apply(get_season)
    else:
        # Keep your original season if it exists, but standardize to emoji label for visuals
        df['season'] = df['arrival_month_name'].apply(get_season)

    if 'booking_source' not in df.columns:
        if 'agent' in df.columns:
            df['booking_source'] = np.where(pd.to_numeric(df['agent'], errors='coerce').fillna(0) > 0,
                                            'Agent / Third Party', 'Direct Booking')
        else:
            df['booking_source'] = 'Unknown'

    # Revenue risk fields
    df['confirmed_booking'] = (df['is_canceled'] == 0).astype(int)
    df['cancelled_booking'] = (df['is_canceled'] == 1).astype(int)
    df['confirmed_revenue'] = np.where(df['is_canceled'] == 0, df['estimated_revenue'], 0)
    df['lost_revenue'] = np.where(df['is_canceled'] == 1, df['estimated_revenue'], 0)

    return df


def prepare_arrivals_data(arrivals_df):
    """Prepare Portugal arrivals data for monthly joining."""
    if arrivals_df is None:
        return None
    a = arrivals_df.copy()
    if 'year' in a.columns:
        a['year'] = pd.to_numeric(a['year'], errors='coerce')
    if 'month' in a.columns:
        a['month'] = pd.to_numeric(a['month'], errors='coerce')
    if 'international_arrivals' in a.columns:
        a['international_arrivals'] = pd.to_numeric(a['international_arrivals'], errors='coerce')
    return a


def add_holiday_window(hotel_df, holidays_df, days=7):
    """Mark booking arrival dates that fall close to a Portugal public holiday."""
    df = hotel_df.copy()
    df['_original_order'] = np.arange(len(df))
    df['holiday_window'] = False
    df['long_weekend_window'] = False
    df['regional_holiday_window'] = False
    df['nearest_holiday'] = 'None'

    if holidays_df is None or holidays_df.empty or 'holiday_date' not in holidays_df.columns:
        return df.drop(columns=['_original_order'])

    holidays = holidays_df.copy()
    holidays['holiday_date'] = pd.to_datetime(holidays['holiday_date'], errors='coerce')
    holidays = holidays.dropna(subset=['holiday_date']).sort_values('holiday_date')

    if holidays.empty:
        return df.drop(columns=['_original_order'])

    valid = df[df['arrival_date'].notna()].sort_values('arrival_date').copy()
    invalid = df[df['arrival_date'].isna()].copy()

    if not valid.empty:
        cols = ['holiday_date']
        for c in ['holiday_name', 'is_long_weekend', 'is_regional_holiday']:
            if c in holidays.columns:
                cols.append(c)

        merged = pd.merge_asof(
            valid,
            holidays[cols],
            left_on='arrival_date',
            right_on='holiday_date',
            direction='nearest',
            tolerance=pd.Timedelta(days=days)
        )
        merged['holiday_window'] = merged['holiday_date'].notna()
        merged['nearest_holiday'] = merged.get('holiday_name', pd.Series(index=merged.index, dtype='object')).fillna('None')
        merged['long_weekend_window'] = (
            merged['holiday_window'] &
            pd.to_numeric(merged.get('is_long_weekend', 0), errors='coerce').fillna(0).astype(int).eq(1)
        )
        merged['regional_holiday_window'] = (
            merged['holiday_window'] &
            pd.to_numeric(merged.get('is_regional_holiday', 0), errors='coerce').fillna(0).astype(int).eq(1)
        )
        df = pd.concat([merged, invalid], ignore_index=True)

    df = df.sort_values('_original_order').drop(columns=['_original_order'])
    return df


def monthly_summary(df, arrivals_df=None):
    """Monthly hotel summary + optional Portugal arrivals joined by year/month."""
    if df.empty:
        return pd.DataFrame()

    m = df.groupby(['arrival_year', 'arrival_month', 'arrival_month_name'], dropna=False).agg(
        bookings=('is_canceled', 'count'),
        confirmed=('confirmed_booking', 'sum'),
        cancelled=('cancelled_booking', 'sum'),
        confirmed_revenue=('confirmed_revenue', 'sum'),
        lost_revenue=('lost_revenue', 'sum'),
        avg_adr=('adr', lambda s: s[df.loc[s.index, 'is_canceled'] == 0].mean()),
        avg_lead_time=('lead_time', 'mean') if 'lead_time' in df.columns else ('is_canceled', 'count')
    ).reset_index()

    m['cancel_rate'] = np.where(m['bookings'] > 0, m['cancelled'] / m['bookings'] * 100, 0)
    m['total_revenue_risk'] = m['confirmed_revenue'] + m['lost_revenue']
    m['month_sort'] = pd.to_numeric(m['arrival_year'], errors='coerce').fillna(0) * 100 + pd.to_numeric(m['arrival_month'], errors='coerce').fillna(0)

    arrivals = prepare_arrivals_data(arrivals_df)
    if arrivals is not None and {'year', 'month', 'international_arrivals'}.issubset(arrivals.columns):
        m = m.merge(
            arrivals,
            left_on=['arrival_year', 'arrival_month'],
            right_on=['year', 'month'],
            how='left'
        )
        m['capture_index'] = np.where(
            m['international_arrivals'] > 0,
            m['confirmed'] / m['international_arrivals'] * 100,
            np.nan
        )
        m['arrival_demand_rank'] = m['international_arrivals'].rank(pct=True) * 100
        m['adr_rank'] = m['avg_adr'].rank(pct=True) * 100
        m['pricing_gap'] = m['arrival_demand_rank'] - m['adr_rank']

    return m.sort_values('month_sort')


def quality_table(df, group_col, min_bookings=50):
    """Revenue + cancellation quality by country/segment/channel/hotel/etc."""
    if df.empty or group_col not in df.columns:
        return pd.DataFrame()

    q = df.groupby(group_col, dropna=False).agg(
        bookings=('is_canceled', 'count'),
        confirmed=('confirmed_booking', 'sum'),
        cancelled=('cancelled_booking', 'sum'),
        confirmed_revenue=('confirmed_revenue', 'sum'),
        lost_revenue=('lost_revenue', 'sum'),
        avg_adr=('adr', lambda s: s[df.loc[s.index, 'is_canceled'] == 0].mean()),
        avg_lead_time=('lead_time', 'mean') if 'lead_time' in df.columns else ('is_canceled', 'count')
    ).reset_index()

    q['cancel_rate'] = np.where(q['bookings'] > 0, q['cancelled'] / q['bookings'] * 100, 0)
    q['revenue_m'] = q['confirmed_revenue'] / 1_000_000
    q['lost_revenue_m'] = q['lost_revenue'] / 1_000_000
    q['net_revenue_quality'] = q['confirmed_revenue'] - q['lost_revenue']
    q = q[q['bookings'] >= min_bookings]
    return q.sort_values('confirmed_revenue', ascending=False)


def safe_idxmax_label(df, value_col, label_col, default='N/A'):
    if df is None or df.empty or value_col not in df.columns or label_col not in df.columns:
        return default
    try:
        return df.loc[df[value_col].idxmax(), label_col]
    except Exception:
        return default


def landing_page():
    st.markdown("""
    <div style='text-align:center; padding: 4rem 2rem;'>
        <div style='font-size:64px; margin-bottom:1rem;'>🏨</div>
        <h1 style='color:#E0E6F0; font-size:36px; font-weight:700; margin-bottom:0.5rem;'>
            Hotel Revenue Intelligence
        </h1>
        <p style='color:#5577AA; font-size:18px; margin-bottom:2rem;'>
            Upload hotel bookings, Portugal arrivals, and public holiday data for hospitality-focused insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, label in zip([c1, c2, c3, c4],
        ["📊", "💰", "🌍", "🎯"],
        ["Revenue Analysis", "Cancellation Insights", "Market Breakdown", "Smart Recommendations"]):
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#111E35);border:1px solid #1A2A45;
            border-radius:16px;padding:1.5rem;text-align:center;'>
                <div style='font-size:32px;margin-bottom:8px;'>{icon}</div>
                <div style='font-size:13px;color:#8899BB;font-weight:500;'>{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Upload at least the hotel booking file to start. The arrivals and holiday files are optional but recommended for the updated analysis.")

# ==========================================================
# Sidebar: updated multi-source upload
# Original code allowed multiple uploads and stacked them together.
# Updated code separates the 3 different datasets so each file is used correctly.
# ==========================================================
with st.sidebar:
    st.markdown("## 🏨 Hotel Revenue\nIntelligence")
    st.markdown("---")

    st.markdown("### 📂 Upload Your Data")
    st.caption("Upload files separately so hotel bookings, Portugal arrivals, and holidays can be analysed together correctly.")

    hotel_upload = st.file_uploader(
        "1️⃣ Hotel booking data",
        type=["xlsx", "xls", "csv"],
        help="Example: cleaned_hotel_data.xlsx"
    )

    arrivals_upload = st.file_uploader(
        "2️⃣ Portugal arrivals data",
        type=["xlsx", "xls", "csv"],
        help="Example: cleaned_portugal_arrivals.xlsx"
    )

    holidays_upload = st.file_uploader(
        "3️⃣ Portugal public holidays data",
        type=["xlsx", "xls", "csv"],
        help="Example: cleaned_Portugal_Public_Holidays_2015_2017.xlsx"
    )

    st.caption("If the files are saved in the same folder as this app, they will auto-load even without upload.")

hotel_raw, hotel_name = load_dataset(hotel_upload, "cleaned_hotel_data.xlsx")
arrivals_raw, arrivals_name = load_dataset(arrivals_upload, "cleaned_portugal_arrivals.xlsx")
holidays_raw, holidays_name = load_dataset(holidays_upload, "cleaned_Portugal_Public_Holidays_2015_2017.xlsx")

if hotel_raw is None:
    landing_page()
    st.stop()

# Prepare data
hotel_df = prepare_hotel_data(hotel_raw)
hotel_df = add_holiday_window(hotel_df, holidays_raw, days=7)

# Sidebar filters
with st.sidebar:
    st.markdown("---")
    st.markdown("### ✅ Loaded Files")
    badges = []
    badges.append(f"<span class='file-badge'>🏨 {hotel_name}</span>")
    if arrivals_name:
        badges.append(f"<span class='file-badge'>📈 {arrivals_name}</span>")
    if holidays_name:
        badges.append(f"<span class='file-badge'>📅 {holidays_name}</span>")
    st.markdown("".join(badges), unsafe_allow_html=True)
    st.success(f"✅ **{len(hotel_df):,}** hotel booking rows loaded")

    st.markdown("---")
    st.markdown("### 🎛 Filters")

    years = sorted(hotel_df['arrival_year'].dropna().astype(int).unique().tolist())
    sel_years = st.multiselect("📅 Year", years, default=years)

    hotels = sorted(hotel_df['hotel'].dropna().astype(str).unique().tolist()) if 'hotel' in hotel_df.columns else []
    sel_hotels = st.multiselect("🏨 Hotel Type", hotels, default=hotels)

    top_countries = []
    if 'country' in hotel_df.columns:
        top_countries = hotel_df.groupby('country')['confirmed_revenue'].sum().nlargest(12).index.astype(str).tolist()
    sel_countries = st.multiselect("🌍 Top Source Market", top_countries, default=top_countries)

    market_segments = sorted(hotel_df['market_segment'].dropna().astype(str).unique().tolist()) if 'market_segment' in hotel_df.columns else []
    sel_segments = st.multiselect("📦 Market Segment", market_segments, default=market_segments)

    holiday_filter = st.selectbox(
        "📅 Holiday Window",
        ["All dates", "Holiday ±7 days only", "Normal dates only", "Long-weekend window only"]
    )

    st.markdown("---")
    st.markdown("<p style='font-size:11px;color:#334466;text-align:center;'>© 2026 Strateq Group · BDA Dept</p>", unsafe_allow_html=True)

# Apply filters
mask = hotel_df['arrival_year'].isin(sel_years) if sel_years else pd.Series(True, index=hotel_df.index)

if sel_hotels and 'hotel' in hotel_df.columns:
    mask &= hotel_df['hotel'].astype(str).isin(sel_hotels)
if sel_countries and 'country' in hotel_df.columns:
    mask &= hotel_df['country'].astype(str).isin(sel_countries)
if sel_segments and 'market_segment' in hotel_df.columns:
    mask &= hotel_df['market_segment'].astype(str).isin(sel_segments)

if holiday_filter == "Holiday ±7 days only":
    mask &= hotel_df['holiday_window'] == True
elif holiday_filter == "Normal dates only":
    mask &= hotel_df['holiday_window'] == False
elif holiday_filter == "Long-weekend window only":
    mask &= hotel_df['long_weekend_window'] == True

df = hotel_df[mask].copy()

if df.empty:
    st.warning("No data available after applying the selected filters.")
    st.stop()

monthly_df = monthly_summary(df, arrivals_raw)

# ── KPI calculations — original + updated risk metrics ────
confirmed   = df['confirmed_revenue'].sum()
lost        = df['lost_revenue'].sum()
total       = len(df)
cancelled   = int(df['cancelled_booking'].sum())
confirmed_bookings = int(df['confirmed_booking'].sum())
cancel_rate = cancelled / total * 100 if total > 0 else 0
avg_adr     = df[df['is_canceled'] == 0]['adr'].mean() if 'adr' in df.columns else 0
loss_ratio  = lost / confirmed if confirmed > 0 else 0
holiday_rows = int(df['holiday_window'].sum()) if 'holiday_window' in df.columns else 0

source_tag = ""
if arrivals_name and holidays_name:
    source_tag = " · <strong style='color:#22D47B'>3 data sources connected</strong>"
elif arrivals_name or holidays_name:
    source_tag = " · <strong style='color:#22D47B'>2 data sources connected</strong>"

header_html = (
    "<div style='margin-bottom:1.5rem;'>"
    "<h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>"
    "🏨 Hotel Revenue Intelligence"
    "</h1>"
    "<p style='color:#5577AA;font-size:14px;'>"
    f"Portugal Hospitality Market · <strong style='color:#7ABAFF'>{total:,}</strong> bookings analysed"
    f"{source_tag}"
    " · Auto-generated hospitality insights"
    "</p>"
    "</div>"
)
st.markdown(header_html, unsafe_allow_html=True)

# ── KPI Row — kept from original + adjusted wording ───────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("✅ Confirmed Revenue",  money_m(confirmed), f"{confirmed_bookings:,} stayed")
with k2:
    st.metric("❌ Revenue Lost",       money_m(lost),      f"-{loss_ratio:.0%} loss ratio" if confirmed > 0 else "N/A",  delta_color="inverse")
with k3:
    st.metric("📉 Cancel Rate",        pct(cancel_rate),    f"{cancelled:,} bookings",        delta_color="inverse")
with k4:
    st.metric("💳 Avg Daily Rate",     f"${avg_adr:.0f}",        "confirmed bookings")
with k5:
    st.metric("📋 Total Bookings",     f"{total:,}",             f"{holiday_rows:,} near holidays")

st.markdown("---")

# ── Tabs: original tabs + updated data-source tabs ────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Revenue Overview",
    "❌ Cancellation Analysis",
    "🌍 Market Intelligence",
    "📅 Seasonality",
    "📊 Demand & Pricing",
    "🎉 Holiday Impact",
    "🎯 Recommendations"
])

# ════════════════════════════════════════════════════
# TAB 1 — Revenue Overview, your original analysis
# ════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📊 Monthly Revenue Performance</div>', unsafe_allow_html=True)

    monthly_plot = monthly_df.copy()
    monthly_plot['month_label'] = monthly_plot['arrival_month_name'].str[:3] + " " + monthly_plot['arrival_year'].astype(int).astype(str)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='✅ Confirmed', x=monthly_plot['month_label'], y=monthly_plot['confirmed_revenue'] / 1e6,
        marker=dict(color=BLUE, opacity=0.9),
        text=(monthly_plot['confirmed_revenue'] / 1e6).apply(lambda x: f'${x:.2f}M'),
        textposition='outside', textfont=dict(size=10, color='#8899BB')
    ))
    fig.add_trace(go.Bar(
        name='❌ Lost', x=monthly_plot['month_label'], y=monthly_plot['lost_revenue'] / 1e6,
        marker=dict(color=RED, opacity=0.8),
        text=(monthly_plot['lost_revenue'] / 1e6).apply(lambda x: f'${x:.2f}M'),
        textposition='outside', textfont=dict(size=10, color='#8899BB')
    ))
    fig.update_layout(**merged_layout(
        380,
        barmode='group',
        yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45', showline=False, zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    bgcolor='rgba(0,0,0,0)', bordercolor='#1A2A45', font=dict(color='#8899BB'))
    ))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🏨 Revenue by Hotel Type</div>', unsafe_allow_html=True)
        if 'hotel' in df.columns:
            hotel_type_df = df.groupby('hotel')['confirmed_revenue'].sum().reset_index()
            fig2 = px.pie(hotel_type_df, values='confirmed_revenue', names='hotel',
                          color_discrete_sequence=[BLUE, PURPLE], hole=0.55)
            fig2.update_traces(textinfo='percent+label', textfont_color='white',
                               marker=dict(line=dict(color='#060B18', width=3)))
            chart(fig2, 310)

    with col2:
        st.markdown('<div class="section-header">📦 Revenue by Market Segment</div>', unsafe_allow_html=True)
        if 'market_segment' in df.columns:
            seg_df = quality_table(df, 'market_segment', min_bookings=20).sort_values('confirmed_revenue')
            fig3 = px.bar(seg_df, x='confirmed_revenue', y='market_segment', orientation='h',
                          color='confirmed_revenue', color_continuous_scale=[[0, '#0D1628'], [1, BLUE]])
            fig3.update_traces(texttemplate='$%{x:.2s}', textposition='outside',
                               textfont=dict(color='#8899BB', size=11))
            fig3.update_layout(**merged_layout(
                310,
                xaxis=dict(tickprefix='$', gridcolor='#1A2A45', showline=False, zeroline=False),
                coloraxis_showscale=False
            ))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 2 — Cancellation Analysis, your original analysis + safer dynamic captions
# ════════════════════════════════════════════════════
with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>Total Revenue Lost</div>
            <div class='insight-value' style='color:{RED};'>{money_m(lost)}</div>
            <div class='insight-desc'>Potential room revenue affected by cancelled bookings</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>Cancellation Rate</div>
            <div class='insight-value' style='color:{AMBER};'>{pct(cancel_rate)}</div>
            <div class='insight-desc'>A key hospitality risk because bookings are not the same as actual revenue</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        peak_month = 'N/A'
        if not monthly_df.empty:
            peak = monthly_df.loc[monthly_df['lost_revenue'].idxmax()]
            peak_month = f"{str(peak['arrival_month_name'])[:3]} {int(peak['arrival_year'])}"
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>Peak Loss Month</div>
            <div class='insight-value' style='color:{PURPLE};'>{peak_month}</div>
            <div class='insight-desc'>Use pre-arrival confirmation and stricter payment rules before this period</div>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">💳 Cancellation Rate by Deposit Type</div>', unsafe_allow_html=True)
        if 'deposit_type' in df.columns:
            dep_df = quality_table(df, 'deposit_type', min_bookings=1).sort_values('cancel_rate', ascending=True)
            colors_dep = [RED if x > 50 else AMBER if x > 25 else GREEN for x in dep_df['cancel_rate']]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dep_df['cancel_rate'], y=dep_df['deposit_type'], orientation='h',
                marker=dict(color=colors_dep, opacity=0.85),
                text=dep_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside', textfont=dict(color='#E0E6F0', size=12, family='Inter')
            ))
            fig.update_layout(**merged_layout(
                300,
                xaxis=dict(ticksuffix='%', range=[0, max(100, dep_df['cancel_rate'].max() * 1.2)],
                           gridcolor='#1A2A45', showline=False, zeroline=False)
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("⚠️ Deposit type should be reviewed together with cancellation rate, not only booking volume.")

    with col2:
        st.markdown('<div class="section-header">👥 Cancellation by Customer Type</div>', unsafe_allow_html=True)
        if 'customer_type' in df.columns:
            cust_df = quality_table(df, 'customer_type', min_bookings=1)
            fig = px.bar(cust_df, x='customer_type', y='cancel_rate',
                         color='cancel_rate', color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]],
                         text=cust_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'))
            fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0', size=12))
            fig.update_layout(**merged_layout(
                300,
                yaxis=dict(ticksuffix='%', gridcolor='#1A2A45', showline=False, zeroline=False),
                coloraxis_showscale=False
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header">📊 Revenue Lost vs Confirmed — Monthly Trend</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_plot['month_label'], y=monthly_plot['confirmed_revenue'] / 1e6, name='✅ Confirmed',
        fill='tozeroy', fillcolor='rgba(74,158,255,0.15)',
        line=dict(color=BLUE, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=monthly_plot['month_label'], y=monthly_plot['lost_revenue'] / 1e6, name='❌ Lost',
        fill='tozeroy', fillcolor='rgba(255,90,90,0.15)',
        line=dict(color=RED, width=3, dash='dot')
    ))
    fig.update_layout(**merged_layout(
        300,
        yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45', showline=False, zeroline=False)
    ))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 3 — Market Intelligence, original + updated quality matrix
# ════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🌍 Top Source Markets — Revenue vs Cancellation Rate</div>', unsafe_allow_html=True)

    if 'country' in df.columns:
        country_df = quality_table(df, 'country', min_bookings=100).nlargest(10, 'confirmed_revenue')
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            name='Revenue ($M)', x=country_df['country'], y=country_df['revenue_m'],
            marker=dict(color=BLUE, opacity=0.85),
            text=country_df['revenue_m'].apply(lambda x: f'${x:.2f}M'),
            textposition='outside', textfont=dict(color='#8899BB', size=11)
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            name='Cancel Rate', x=country_df['country'], y=country_df['cancel_rate'],
            mode='lines+markers+text', line=dict(color=RED, width=3),
            marker=dict(size=10, color=RED, line=dict(color='white', width=2)),
            text=country_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'),
            textposition='top center', textfont=dict(color=RED, size=11)
        ), secondary_y=True)
        fig.update_layout(**merged_layout(
            380,
            yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45', showline=False, zeroline=False),
            yaxis2=dict(ticksuffix='%', gridcolor='rgba(0,0,0,0)', showline=False, zeroline=False)
        ))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📡 Distribution Channel</div>', unsafe_allow_html=True)
        if 'distribution_channel' in df.columns:
            dist_df = df.groupby('distribution_channel')['confirmed_revenue'].sum().reset_index()
            fig = px.pie(dist_df, values='confirmed_revenue', names='distribution_channel',
                         color_discrete_sequence=COLORS, hole=0.5)
            fig.update_traces(textinfo='percent+label', textfont_color='white',
                              marker=dict(line=dict(color='#060B18', width=3)))
            chart(fig, 310)

    with col2:
        st.markdown('<div class="section-header">🧳 Booking Source Breakdown</div>', unsafe_allow_html=True)
        if 'booking_source' in df.columns:
            src_df = quality_table(df, 'booking_source', min_bookings=20).sort_values('confirmed_revenue', ascending=True).tail(6)
            fig = px.bar(src_df, x='confirmed_revenue', y='booking_source', orientation='h',
                         color='cancel_rate', color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]])
            fig.update_layout(**merged_layout(
                310,
                xaxis=dict(tickprefix='$', gridcolor='#1A2A45', showline=False, zeroline=False),
                coloraxis_colorbar=dict(title='Cancel %')
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header">🧭 Market Quality Matrix</div>', unsafe_allow_html=True)
    if 'country' in df.columns:
        market_quality = quality_table(df, 'country', min_bookings=300)
        if not market_quality.empty:
            fig = px.scatter(
                market_quality,
                x='cancel_rate', y='revenue_m', size='bookings', color='avg_adr',
                hover_name='country',
                color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, PURPLE]],
                labels={'cancel_rate': 'Cancellation Rate (%)', 'revenue_m': 'Confirmed Revenue ($M)', 'avg_adr': 'ADR'}
            )
            fig.add_vline(x=market_quality['cancel_rate'].median(), line_dash='dash', line_color='#5577AA')
            fig.add_hline(y=market_quality['revenue_m'].median(), line_dash='dash', line_color='#5577AA')
            chart(fig, 420)
            st.caption("Top-right = high revenue but risky. Top-left = high revenue and reliable, which is better for campaign targeting.")

# ════════════════════════════════════════════════════
# TAB 4 — Seasonality, original + holiday-aware view
# ════════════════════════════════════════════════════
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🌞 Revenue by Season</div>', unsafe_allow_html=True)
        season_df = df.groupby('season').agg(
            revenue=('confirmed_revenue', 'sum'),
            bookings=('is_canceled', 'count'),
            cancelled=('cancelled_booking', 'sum')
        ).reset_index()
        season_df['revenue_m'] = season_df['revenue'] / 1e6
        season_df['cancel_rate'] = np.where(season_df['bookings'] > 0, season_df['cancelled'] / season_df['bookings'] * 100, 0)
        season_colors = {'☀️ Summer': AMBER, '🌸 Spring': GREEN, '🍂 Autumn': CYAN, '❄️ Winter': BLUE}
        fig = px.pie(season_df, values='revenue_m', names='season',
                     color='season', color_discrete_map=season_colors, hole=0.55)
        fig.update_traces(textinfo='percent+label', textfont_color='white',
                          marker=dict(line=dict(color='#060B18', width=3)))
        fig.update_layout(**merged_layout(330))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown('<div class="section-header">📊 Season Performance Summary</div>', unsafe_allow_html=True)
        total_season_revenue = season_df['revenue_m'].sum()
        for _, row in season_df.sort_values('revenue_m', ascending=False).iterrows():
            s = row['season']
            c = season_colors.get(s, BLUE)
            pct_revenue = row['revenue_m'] / total_season_revenue * 100 if total_season_revenue > 0 else 0
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#0F1A2E);border:1px solid #1A2A45;
            border-left:4px solid {c};border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;
            display:flex;justify-content:space-between;align-items:center;'>
                <div>
                    <div style='font-size:14px;color:#C8D8F0;font-weight:600;'>{s}</div>
                    <div style='font-size:12px;color:#5577AA;'>{int(row['bookings']):,} bookings · {pct(row['cancel_rate'])} cancelled</div>
                </div>
                <div style='text-align:right;'>
                    <div style='font-size:18px;font-weight:700;color:{c};'>{money_m(row['revenue'])}</div>
                    <div style='font-size:12px;color:#5577AA;'>{pct_revenue:.1f}% of revenue</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📅 ADR vs Arrival Volume by Month</div>', unsafe_allow_html=True)
    if 'adr' in df.columns:
        adr_df = monthly_df.copy()
        adr_df['month_label'] = adr_df['arrival_month_name'].str[:3] + ' ' + adr_df['arrival_year'].astype(int).astype(str)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            name='Bookings Volume', x=adr_df['month_label'], y=adr_df['bookings'],
            marker=dict(color=BLUE, opacity=0.5)
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            name='Avg Daily Rate', x=adr_df['month_label'], y=adr_df['avg_adr'],
            mode='lines+markers', line=dict(color=AMBER, width=3),
            marker=dict(size=8, color=AMBER, line=dict(color='white', width=2))
        ), secondary_y=True)
        fig.update_layout(**merged_layout(
            330,
            yaxis=dict(title='Bookings', gridcolor='#1A2A45', showline=False, zeroline=False),
            yaxis2=dict(title='Avg ADR ($)', tickprefix='$', gridcolor='rgba(0,0,0,0)', showline=False, zeroline=False)
        ))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 5 — Demand & Pricing, updated using Portugal arrivals file
# ════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📊 Portugal Arrivals vs Hotel Revenue</div>', unsafe_allow_html=True)

    has_arrivals = arrivals_raw is not None and 'international_arrivals' in monthly_df.columns
    if not has_arrivals:
        st.info("Upload `cleaned_portugal_arrivals.xlsx` to enable the demand and pricing analysis.")
    else:
        demand_df = monthly_df.dropna(subset=['international_arrivals']).copy()
        demand_df['month_label'] = demand_df['arrival_month_name'].str[:3] + ' ' + demand_df['arrival_year'].astype(int).astype(str)

        fig = make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_trace(go.Bar(
            name='Portugal International Arrivals',
            x=demand_df['month_label'],
            y=demand_df['international_arrivals'] / 1e6,
            marker=dict(color=CYAN, opacity=0.45)
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            name='Hotel Confirmed Revenue',
            x=demand_df['month_label'],
            y=demand_df['confirmed_revenue'] / 1e6,
            mode='lines+markers',
            line=dict(color=BLUE, width=3),
            marker=dict(size=8)
        ), secondary_y=True)
        fig.update_yaxes(title_text='Portugal Arrivals (M)', secondary_y=False)
        fig.update_yaxes(title_text='Hotel Revenue ($M)', tickprefix='$', ticksuffix='M', secondary_y=True)
        fig.update_layout(**merged_layout(400))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Opportunity cards
        best_rev = demand_df.sort_values('confirmed_revenue', ascending=False).iloc[0]
        highest_cancel = demand_df.sort_values('cancel_rate', ascending=False).iloc[0]
        pricing_opp = demand_df.dropna(subset=['pricing_gap']).sort_values('pricing_gap', ascending=False).head(5)

        a, b, c = st.columns(3)
        a.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Best Revenue Month</div>
            <div class='insight-value' style='color:{BLUE};'>{best_rev['arrival_month_name']} {int(best_rev['arrival_year'])}</div>
            <div class='insight-desc'>{money_m(best_rev['confirmed_revenue'])} confirmed revenue with {pct(best_rev['cancel_rate'])} cancellation.</div>
        </div>
        """, unsafe_allow_html=True)

        b.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Highest Cancellation Month</div>
            <div class='insight-value' style='color:{RED};'>{highest_cancel['arrival_month_name']} {int(highest_cancel['arrival_year'])}</div>
            <div class='insight-desc'>This month needs stronger deposit, reconfirmation, and release-period control.</div>
        </div>
        """, unsafe_allow_html=True)

        if not pricing_opp.empty:
            opp = pricing_opp.iloc[0]
            c.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>Pricing Opportunity</div>
                <div class='insight-value' style='color:{AMBER};'>{opp['arrival_month_name']} {int(opp['arrival_year'])}</div>
                <div class='insight-desc'>Demand rank is higher than ADR rank, suggesting room to review rates or packages.</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">💰 Underpriced Demand Windows</div>', unsafe_allow_html=True)
            show_cols = ['arrival_year', 'arrival_month_name', 'international_arrivals', 'avg_adr',
                         'cancel_rate', 'confirmed_revenue', 'pricing_gap']
            display_opp = pricing_opp[show_cols].copy()
            display_opp['confirmed_revenue'] = display_opp['confirmed_revenue'].map(lambda x: f"${x:,.0f}")
            display_opp['avg_adr'] = display_opp['avg_adr'].map(lambda x: f"${x:,.0f}")
            display_opp['cancel_rate'] = display_opp['cancel_rate'].map(lambda x: f"{x:.1f}%")
            display_opp['pricing_gap'] = display_opp['pricing_gap'].map(lambda x: f"{x:.1f}")
            st.dataframe(display_opp, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 6 — Holiday Impact, updated using Portugal public holiday file
# ════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">🎉 Public Holiday Booking Behaviour</div>', unsafe_allow_html=True)

    if holidays_raw is None:
        st.info("Upload `cleaned_Portugal_Public_Holidays_2015_2017.xlsx` to enable holiday impact analysis.")
    else:
        temp = df.copy()
        temp['date_type'] = np.where(temp['holiday_window'], 'Holiday ±7 days', 'Normal dates')
        holiday_compare = temp.groupby('date_type').agg(
            bookings=('is_canceled', 'count'),
            confirmed=('confirmed_booking', 'sum'),
            cancelled=('cancelled_booking', 'sum'),
            confirmed_revenue=('confirmed_revenue', 'sum'),
            lost_revenue=('lost_revenue', 'sum'),
            avg_adr=('adr', lambda s: s[temp.loc[s.index, 'is_canceled'] == 0].mean())
        ).reset_index()
        holiday_compare['cancel_rate'] = np.where(
            holiday_compare['bookings'] > 0,
            holiday_compare['cancelled'] / holiday_compare['bookings'] * 100,
            0
        )
        holiday_compare['revenue_m'] = holiday_compare['confirmed_revenue'] / 1e6

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                holiday_compare,
                x='date_type', y='revenue_m', color='cancel_rate',
                color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]],
                text=holiday_compare['revenue_m'].map(lambda v: f'${v:.2f}M')
            )
            fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0'))
            fig.update_layout(**merged_layout(
                330,
                yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45'),
                coloraxis_colorbar=dict(title='Cancel %')
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col2:
            fig = px.bar(
                holiday_compare,
                x='date_type', y='avg_adr', color='date_type',
                color_discrete_sequence=[BLUE, AMBER],
                text=holiday_compare['avg_adr'].map(lambda v: f'${v:.0f}')
            )
            fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0'))
            fig.update_layout(**merged_layout(
                330,
                yaxis=dict(tickprefix='$', gridcolor='#1A2A45'),
                showlegend=False
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-header">🏖️ Top Holiday Windows by Booking Volume</div>', unsafe_allow_html=True)
        holiday_only = df[df['holiday_window']].copy()
        if holiday_only.empty:
            st.warning("No bookings are within ±7 days of a public holiday after filters.")
        else:
            holiday_rank = holiday_only.groupby('nearest_holiday').agg(
                bookings=('is_canceled', 'count'),
                confirmed=('confirmed_booking', 'sum'),
                cancelled=('cancelled_booking', 'sum'),
                confirmed_revenue=('confirmed_revenue', 'sum'),
                lost_revenue=('lost_revenue', 'sum'),
                avg_adr=('adr', lambda s: s[holiday_only.loc[s.index, 'is_canceled'] == 0].mean()),
                long_weekend=('long_weekend_window', 'max')
            ).reset_index()
            holiday_rank['cancel_rate'] = np.where(
                holiday_rank['bookings'] > 0,
                holiday_rank['cancelled'] / holiday_rank['bookings'] * 100,
                0
            )
            holiday_rank = holiday_rank.sort_values('bookings', ascending=False).head(10)
            display_holiday = holiday_rank.copy()
            display_holiday['confirmed_revenue'] = display_holiday['confirmed_revenue'].map(lambda x: f"${x:,.0f}")
            display_holiday['lost_revenue'] = display_holiday['lost_revenue'].map(lambda x: f"${x:,.0f}")
            display_holiday['avg_adr'] = display_holiday['avg_adr'].map(lambda x: f"${x:,.0f}")
            display_holiday['cancel_rate'] = display_holiday['cancel_rate'].map(lambda x: f"{x:.1f}%")
            display_holiday['long_weekend'] = display_holiday['long_weekend'].map(lambda x: 'Yes' if x else 'No')
            st.dataframe(display_holiday, use_container_width=True, hide_index=True)

            st.caption("Hospitality action: for high-volume holidays, use minimum-stay rules, early prepayment, and value-added packages instead of simple discounts.")

# ════════════════════════════════════════════════════
# TAB 7 — Recommendations, original style + updated personalised logic
# ════════════════════════════════════════════════════
with tab7:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D1628,#0A1A35);border:1px solid #1A2A45;
    border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;text-align:center;'>
        <p style='font-size:20px;font-weight:600;color:#4A9EFF;font-style:italic;margin-bottom:8px;'>
            "A confirmed booking is not confirmed revenue until the guest actually stays."
        </p>
        <p style='font-size:13px;color:#5577AA;'>
            Connect booking behaviour · market demand · holiday pressure · cancellation risk
        </p>
    </div>
    """, unsafe_allow_html=True)

    country_quality = quality_table(df, 'country', min_bookings=300) if 'country' in df.columns else pd.DataFrame()
    segment_quality = quality_table(df, 'market_segment', min_bookings=20) if 'market_segment' in df.columns else pd.DataFrame()
    channel_quality = quality_table(df, 'distribution_channel', min_bookings=20) if 'distribution_channel' in df.columns else pd.DataFrame()

    top_country = safe_idxmax_label(country_quality, 'confirmed_revenue', 'country')
    reliable_country = 'N/A'
    risky_country = 'N/A'
    if not country_quality.empty:
        reliable_country = country_quality.sort_values(['cancel_rate', 'confirmed_revenue'], ascending=[True, False]).iloc[0]['country']
        risky_country = country_quality.sort_values(['cancel_rate', 'lost_revenue'], ascending=[False, False]).iloc[0]['country']

    risky_segment = 'N/A'
    if not segment_quality.empty:
        risky_segment = segment_quality.sort_values(['cancel_rate', 'lost_revenue'], ascending=[False, False]).iloc[0]['market_segment']

    risky_channel = 'N/A'
    if not channel_quality.empty:
        risky_channel = channel_quality.sort_values(['cancel_rate', 'lost_revenue'], ascending=[False, False]).iloc[0]['distribution_channel']

    best_season = safe_idxmax_label(season_df, 'revenue', 'season') if 'season_df' in locals() else 'N/A'
    worst_deposit = 'N/A'
    if 'deposit_type' in df.columns:
        dep_quality = quality_table(df, 'deposit_type', min_bookings=1)
        if not dep_quality.empty:
            worst_deposit = dep_quality.sort_values('cancel_rate', ascending=False).iloc[0]['deposit_type']

    recovery_target = lost * 0.30

    recs = [
        (RED, "01", "🚨 Reduce Cancellation Revenue Loss",
         "Flag high-risk bookings before they block inventory.",
         [
             f"Current revenue lost from cancellations: **{money_m(lost)}**.",
             f"Set a 30% reduction target to potentially recover around **{money_m(recovery_target)}**.",
             f"High-risk segment to review first: **{risky_segment}**.",
             f"Highest-risk deposit type: **{worst_deposit}**. Review whether the policy is really protecting revenue."
         ]),
        (AMBER, "02", "💰 Price for Real Demand, Not Only Season",
         "Use Portugal arrival demand as a pricing signal.",
         [
             "Compare ADR rank with Portugal international arrival rank each month.",
             "If arrivals are high but ADR is low, review rate fences, packages, and minimum-stay rules.",
             "During peak or holiday windows, prioritise value-added bundles instead of simple discounts.",
             f"Best revenue season from current filter: **{best_season}**."
         ]),
        (GREEN, "03", "🎯 Shift Acquisition Toward Reliable Markets",
         "Separate market size from market quality.",
         [
             f"Top revenue market: **{top_country}**.",
             f"Most reliable market from filtered data: **{reliable_country}**.",
             f"Risk-control market to monitor: **{risky_country}**.",
             "Marketing should not only chase booking volume; it should chase guests who actually stay."
         ]),
        (CYAN, "04", "🏨 Improve Operational Planning Around Holidays",
         "Use public holidays as revenue events, not just calendar dates.",
         [
             f"Bookings near holiday windows in current filter: **{holiday_rows:,}**.",
             "For high-volume holiday windows, prepare staffing, housekeeping, and F&B capacity earlier.",
             "Use minimum-stay, prepayment, late-checkout bundles, breakfast packages, and airport-transfer add-ons.",
             f"Risky channel to monitor: **{risky_channel}**."
         ])
    ]

    for color, num, title, subtitle, points in recs:
        with st.expander(f"**{num} — {title}**", expanded=True):
            st.markdown(f"<p style='color:#8899BB;font-size:13px;font-style:italic;margin-bottom:1rem;'>💡 {subtitle}</p>", unsafe_allow_html=True)
            for p in points:
                st.markdown(f"<p style='color:#C8D8F0;font-size:13px;margin-bottom:6px;'>→ {p}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📊 Auto-Generated Key Insights</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    insight_values = [top_country, reliable_country, best_season, worst_deposit]
    for col, icon, label, val, desc in zip(
        [i1, i2, i3, i4],
        ["🏆", "✅", "🌞", "⚠️"],
        ["Top Revenue Market", "Most Reliable Market", "Best Season", "Highest Risk Deposit"],
        insight_values,
        ["by confirmed revenue", "lowest cancel rate", "by revenue contribution", "highest cancel rate"]
    ):
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#0F1A2E);border:1px solid #1A2A45;
            border-radius:14px;padding:1.1rem;text-align:center;'>
                <div style='font-size:28px;margin-bottom:6px;'>{icon}</div>
                <div style='font-size:11px;color:#5577AA;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>{label}</div>
                <div style='font-size:16px;font-weight:700;color:#E0E6F0;margin-bottom:4px;'>{val}</div>
                <div style='font-size:11px;color:#5577AA;'>{desc}</div>
            </div>""", unsafe_allow_html=True)
