import os
from pathlib import Path
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from difflib import SequenceMatcher

# ==========================================================
# HOTEL REVENUE INTELLIGENCE — Dynamic Column Mapping Edition
# Supports any uploaded file with any column names.
# Users map their columns to the expected schema once,
# and the dashboard adapts accordingly.
# ==========================================================

st.set_page_config(
    page_title="Hotel Revenue Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #060B18; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #0A1020 !important; border-right: 1px solid #1A2540; }
section[data-testid="stSidebar"] * { color: #8899BB !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #E0E6F0 !important; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0D1628 0%, #152240 100%);
    border: 1px solid #2A3F6A; border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
}
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] [data-testid="stMetricLabel"],
div[data-testid="metric-container"] [data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
    color: #FFFFFF !important; font-size: 11px !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.10em;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"],
div[data-testid="metric-container"] div[data-testid="stMetricValue"] > div,
div[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"] {
    color: #FFFFFF !important; font-size: 32px !important;
    font-weight: 800 !important; letter-spacing: -0.5px;
    text-shadow: 0 0 20px rgba(74,158,255,0.3); line-height: 1.15 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] { font-size: 12px !important; font-weight: 500 !important; }
.section-header {
    font-size: 16px; font-weight: 600; color: #C8D8F0;
    margin: 1.5rem 0 1rem 0; letter-spacing: 0.02em;
    display: flex; align-items: center; gap: 8px;
}
.section-header::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, #1A2A45 0%, transparent 100%);
}
.file-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0F1E38; border: 1px solid #2A4070;
    border-radius: 8px; padding: 4px 10px;
    font-size: 12px; color: #7ABAFF; margin: 3px;
}
.insight-card {
    background: linear-gradient(135deg, #0D1628, #0F1A2E);
    border: 1px solid #1A2A45; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.insight-title { font-size: 12px; color: #5577AA; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.insight-value { font-size: 22px; font-weight: 700; margin-bottom: 2px; }
.insight-desc { font-size: 12px; color: #5577AA; line-height: 1.5; }
.mapping-card {
    background: linear-gradient(135deg, #0A1428, #0D1A30);
    border: 1px solid #1E3050; border-radius: 14px;
    padding: 1.25rem 1.5rem; margin-bottom: 1rem;
}
.mapping-header { color: #E0E6F0; font-size: 15px; font-weight: 700; margin-bottom: 4px; }
.mapping-desc { color: #5577AA; font-size: 12px; margin-bottom: 12px; line-height: 1.5; }
.auto-badge {
    display: inline-flex; align-items: center; gap: 4px;
    background: #0A2510; border: 1px solid #1A5020;
    border-radius: 6px; padding: 2px 8px;
    font-size: 11px; color: #22D47B;
}
.manual-badge {
    display: inline-flex; align-items: center; gap: 4px;
    background: #251A0A; border: 1px solid #50380A;
    border-radius: 6px; padding: 2px 8px;
    font-size: 11px; color: #FFB830;
}
.skip-badge {
    display: inline-flex; align-items: center; gap: 4px;
    background: #1A1A2A; border: 1px solid #3A3A5A;
    border-radius: 6px; padding: 2px 8px;
    font-size: 11px; color: #667799;
}
div[data-testid="stTabs"] button { color: #6688AA !important; font-size: 13px !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #4A9EFF !important; }
hr { border-color: #1A2A45 !important; }
span[data-baseweb="tag"] { background-color: #1A3A6A !important; border: 1px solid #2A5099 !important; }
span[data-baseweb="tag"] span { color: #7ABAFF !important; }
span[data-baseweb="tag"] button svg { fill: #7ABAFF !important; }
.stSelectbox > div > div { background: #0D1628 !important; border-color: #1A2A45 !important; }
</style>
""", unsafe_allow_html=True)

BLUE   = "#4A9EFF"
GREEN  = "#22D47B"
RED    = "#FF5A5A"
AMBER  = "#FFB830"
PURPLE = "#A855F7"
CYAN   = "#06B6D4"
PINK   = "#EC4899"
COLORS = [BLUE, GREEN, AMBER, RED, PURPLE, CYAN, PINK, "#F97316"]

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

def merged_layout(height, **overrides):
    layout = dict(**CHART_LAYOUT)
    layout.update(overrides)
    layout['height'] = height
    return layout

def chart(fig, height=340):
    fig.update_layout(**merged_layout(height))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def get_season(m):
    if pd.isna(m): return "Unknown"
    m = str(m).strip()
    if m in ['June','July','August']: return '☀️ Summer'
    elif m in ['March','April','May']: return '🌸 Spring'
    elif m in ['September','October','November']: return '🍂 Autumn'
    elif m in ['December','January','February']: return '❄️ Winter'
    return "Unknown"


def month_to_number(value):
    """Convert month names/abbreviations/numbers to month number 1-12."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        month_num = int(value) if 1 <= int(value) <= 12 else np.nan
        return month_num
    text = str(value).strip()
    if text.isdigit():
        month_num = int(text)
        return month_num if 1 <= month_num <= 12 else np.nan
    lookup = {m.lower(): i for i, m in enumerate(MONTH_ORDER, start=1)}
    lookup.update({m[:3].lower(): i for i, m in enumerate(MONTH_ORDER, start=1)})
    return lookup.get(text.lower()[:3], lookup.get(text.lower(), np.nan))


def month_number_to_name(value):
    try:
        value = int(value)
        if 1 <= value <= 12:
            return MONTH_ORDER[value - 1]
    except Exception:
        pass
    return np.nan


def normalize_cancel_flag(series):
    """Normalise cancellation/status columns into 1 = cancelled, 0 = not cancelled."""
    numeric = pd.to_numeric(series, errors='coerce')
    if numeric.notna().mean() >= 0.70:
        return (numeric.fillna(0) > 0).astype(int)

    text = series.astype(str).str.strip().str.lower()
    positive_not_cancelled = text.str.contains(
        r'not cancelled|not canceled|not cancel|no cancellation|confirmed|active|booked|checked.?in|stayed',
        regex=True, na=False
    )
    cancelled = text.str.contains(
        r'cancelled|canceled|cancel|no.?show|noshow',
        regex=True, na=False
    ) & ~positive_not_cancelled
    return cancelled.astype(int)


def normalize_bool_flag(series):
    """Normalise yes/no, true/false, 1/0 fields into boolean."""
    numeric = pd.to_numeric(series, errors='coerce')
    if numeric.notna().mean() >= 0.70:
        return numeric.fillna(0).astype(float).gt(0)
    text = series.astype(str).str.strip().str.lower()
    return text.isin(['1', 'yes', 'y', 'true', 't', 'long weekend', 'regional'])

def money_m(x):
    if pd.isna(x): return "$0.00M"
    return f"${x/1_000_000:,.2f}M"

def pct(x):
    if pd.isna(x): return "0.0%"
    return f"{x:,.1f}%"

@st.cache_data(show_spinner=False)
def read_any_file(file_bytes, file_name):
    if file_name.lower().endswith('.csv'):
        return pd.read_csv(io.BytesIO(file_bytes))
    return pd.read_excel(io.BytesIO(file_bytes))

@st.cache_data(show_spinner=False)
def read_default_excel(path):
    if Path(path).exists():
        return pd.read_excel(path)
    return None

def load_dataset(uploaded_file, default_path=None):
    """
    Load a dataset from the uploader.
    File names are NOT fixed; users upload files by data type.
    default_path is optional and only used if you want to support local demo files.
    """
    if uploaded_file is not None:
        return read_any_file(uploaded_file.getvalue(), uploaded_file.name), uploaded_file.name

    if default_path:
        default_df = read_default_excel(default_path)
        if default_df is not None:
            return default_df, default_path

    return None, None

# ==========================================================
# COLUMN MAPPING SYSTEM
# ==========================================================

# Schema: field_key -> (label, description, required, aliases)
HOTEL_SCHEMA = {
    "arrival_date":              ("Arrival Date",             "Date the guest arrives",                               False, ["arrival_date","check_in","checkin","check_in_date","arrival","date_of_arrival","checkin_date"]),
    "arrival_year":              ("Arrival Year",             "Year of arrival (integer)",                            False, ["arrival_year","year","check_in_year","checkin_year"]),
    "arrival_month":             ("Arrival Month (number)",   "Month number 1–12",                                    False, ["arrival_month","month","arrival_month_num","month_num"]),
    "arrival_month_name":        ("Arrival Month (name)",     "Month name e.g. January",                              False, ["arrival_month_name","month_name","arrival_month_label"]),
    "is_canceled":               ("Is Canceled",              "1 = cancelled, 0 = not cancelled",                     True,  ["is_canceled","is_cancelled","cancelled","canceled","cancellation","booking_status"]),
    "adr":                       ("Average Daily Rate",       "Room rate per night (numeric)",                        True,  ["adr","avg_daily_rate","average_daily_rate","rate","room_rate","daily_rate","price_per_night"]),
    "lead_time":                 ("Lead Time",                "Days between booking and arrival",                     False, ["lead_time","leadtime","days_in_advance","booking_lead_time","days_before_arrival"]),
    "stays_in_weekend_nights":   ("Weekend Nights",           "Weekend nights stayed",                                False, ["stays_in_weekend_nights","weekend_nights","weekend_stay","nights_weekend"]),
    "stays_in_week_nights":      ("Week Nights",              "Weekday nights stayed",                                False, ["stays_in_week_nights","week_nights","weekday_nights","nights_week","weeknight"]),
    "total_stay_nights":         ("Total Stay Nights",        "Total nights (if pre-calculated)",                     False, ["total_stay_nights","total_nights","nights_stayed","length_of_stay","los","nights"]),
    "hotel":                     ("Hotel Type / Name",        "Hotel type or property name",                          False, ["hotel","hotel_type","property","hotel_name","property_name","accommodation_type"]),
    "country":                   ("Country",                  "Guest origin country code or name",                    False, ["country","country_of_origin","nationality","guest_country","origin_country","market"]),
    "market_segment":            ("Market Segment",           "Booking segment e.g. Online, Corporate",               False, ["market_segment","segment","booking_segment","channel_segment","customer_segment"]),
    "distribution_channel":      ("Distribution Channel",     "How the booking was made",                             False, ["distribution_channel","channel","booking_channel","sales_channel","dist_channel"]),
    "deposit_type":              ("Deposit Type",             "e.g. No Deposit, Non Refund",                          False, ["deposit_type","deposit","payment_type","payment_method","refund_policy"]),
    "customer_type":             ("Customer Type",            "e.g. Transient, Group, Contract",                      False, ["customer_type","guest_type","booker_type","traveller_type","traveler_type"]),
    "agent":                     ("Agent ID",                 "Travel agent ID (0 or blank = direct)",                False, ["agent","agent_id","travel_agent","agent_code","ota_id"]),
    "estimated_revenue":         ("Estimated Revenue",        "Pre-calculated revenue column (optional)",             False, ["estimated_revenue","revenue","total_revenue","booking_revenue","gross_revenue"]),
    "is_repeated_guest":         ("Repeated Guest",           "1 = returning guest, 0 = new",                         False, ["is_repeated_guest","repeat_guest","returning_guest","loyal_guest","guest_repeat"]),
    "total_of_special_requests": ("Special Requests",         "Number of special requests",                           False, ["total_of_special_requests","special_requests","requests","num_requests"]),
    "previous_cancellations":    ("Previous Cancellations",   "Number of previous cancellations by this guest",       False, ["previous_cancellations","prior_cancellations","past_cancellations","hist_cancellations"]),
}

ARRIVALS_SCHEMA = {
    "year":                   ("Year",                   "Year (integer)",                               True,  ["year","yr","arrival_year","period_year"]),
    "month":                  ("Month",                  "Month number 1–12",                            True,  ["month","mo","period_month","arrival_month","month_num"]),
    "international_arrivals": ("International Arrivals", "Number of international tourist arrivals",     True,  ["international_arrivals","arrivals","tourist_arrivals","intl_arrivals","visitors","total_arrivals","tourists"]),
}

HOLIDAYS_SCHEMA = {
    "holiday_date":       ("Holiday Date",      "Date of the public holiday",       True,  ["holiday_date","date","public_holiday","holiday","event_date","festivity_date"]),
    "holiday_name":       ("Holiday Name",      "Name of the holiday",              False, ["holiday_name","name","holiday_label","event_name","festivity","occasion"]),
    "is_long_weekend":    ("Is Long Weekend",   "1 if it creates a long weekend",   False, ["is_long_weekend","long_weekend","extended_weekend","bridge_day"]),
    "is_regional_holiday":("Is Regional",       "1 if regional/local only",         False, ["is_regional_holiday","regional","local_holiday","regional_only"]),
}


def similarity(a, b):
    return SequenceMatcher(None, a.lower().replace(" ","_"), b.lower().replace(" ","_")).ratio()


def auto_guess_mapping(df_columns, schema):
    """
    For each schema field, find the best matching df column using:
    1. Exact alias match (highest confidence)
    2. Fuzzy similarity score
    Returns dict: field_key -> (best_col or None, confidence: 'auto'|'fuzzy'|'none')
    """
    cols_lower = {c.lower().replace(" ", "_"): c for c in df_columns}
    guesses = {}

    for field_key, (label, desc, required, aliases) in schema.items():
        best_col = None
        confidence = 'none'

        # 1. Exact alias match
        for alias in aliases:
            if alias in cols_lower:
                best_col = cols_lower[alias]
                confidence = 'auto'
                break

        # 2. Fuzzy match on original column names
        if best_col is None:
            best_score = 0.0
            for alias in aliases:
                for col_norm, col_orig in cols_lower.items():
                    score = similarity(alias, col_norm)
                    if score > best_score:
                        best_score = score
                        if score >= 0.75:
                            best_col = col_orig
                            confidence = 'fuzzy'

        guesses[field_key] = (best_col, confidence)

    return guesses


def render_mapping_ui(df, schema, session_key, title, description):
    """
    Renders the column mapping interface.
    Returns dict: field_key -> column_name_in_df (or None if skipped)
    Persists selections in st.session_state[session_key].
    """
    df_cols = list(df.columns)
    options_with_skip = ["— skip this field —"] + df_cols

    guesses = auto_guess_mapping(df_cols, schema)

    if session_key not in st.session_state:
        st.session_state[session_key] = {
            fk: guess for fk, (guess, _) in guesses.items()
        }

    st.markdown(f"""
    <div class='mapping-card'>
        <div class='mapping-header'>🗂️ {title}</div>
        <div class='mapping-desc'>{description}</div>
    </div>
    """, unsafe_allow_html=True)

    auto_count = sum(1 for fk, (g, c) in guesses.items() if g and c == 'auto')
    fuzzy_count = sum(1 for fk, (g, c) in guesses.items() if g and c == 'fuzzy')
    skipped_count = sum(1 for fk, (g, c) in guesses.items() if not g)

    badge_row = (
        f"<span class='auto-badge'>✅ {auto_count} auto-matched</span>&nbsp;"
        f"<span class='manual-badge'>⚠️ {fuzzy_count} fuzzy-matched — please verify</span>&nbsp;"
        f"<span class='skip-badge'>⏭ {skipped_count} not found</span>"
    )
    st.markdown(badge_row, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    updated = {}
    required_fields = [fk for fk, (_, _, req, _) in schema.items() if req]

    for field_key, (label, desc, required, aliases) in schema.items():
        guessed_col, confidence = guesses[field_key]
        current = st.session_state[session_key].get(field_key, guessed_col)

        if current and current in df_cols:
            default_idx = options_with_skip.index(current)
        else:
            default_idx = 0

        col_a, col_b = st.columns([1, 2])
        with col_a:
            badge = ""
            if confidence == 'auto' and guessed_col:
                badge = "<span class='auto-badge'>✅ auto</span>"
            elif confidence == 'fuzzy' and guessed_col:
                badge = "<span class='manual-badge'>⚠️ verify</span>"
            else:
                badge = "<span class='skip-badge'>⏭ not found</span>"
            req_star = " <span style='color:#FF5A5A;'>*</span>" if required else ""
            st.markdown(
                f"<div style='padding-top:28px;'>"
                f"<span style='color:#C8D8F0;font-size:13px;font-weight:600;'>{label}{req_star}</span><br>"
                f"<span style='color:#5577AA;font-size:11px;'>{desc}</span><br><br>"
                f"{badge}</div>",
                unsafe_allow_html=True
            )

        with col_b:
            chosen = st.selectbox(
                f"",
                options=options_with_skip,
                index=default_idx,
                key=f"map_{session_key}_{field_key}",
                label_visibility="collapsed"
            )
            if chosen and chosen != "— skip this field —":
                updated[field_key] = chosen
                st.session_state[session_key][field_key] = chosen
            else:
                updated[field_key] = None
                st.session_state[session_key][field_key] = None

        if guessed_col and df is not None:
            col_to_preview = updated.get(field_key) or guessed_col
            if col_to_preview in df.columns:
                sample_vals = df[col_to_preview].dropna().head(3).tolist()
                sample_str = " · ".join(str(v) for v in sample_vals)
                st.markdown(
                    f"<div style='margin:-8px 0 10px 0;padding-left:4px;'>"
                    f"<span style='color:#334466;font-size:11px;'>📋 Sample: {sample_str}</span></div>",
                    unsafe_allow_html=True
                )

    # Validate required fields
    missing_required = [
        schema[fk][0] for fk in required_fields if not updated.get(fk)
    ]
    if missing_required:
        st.error(f"⚠️ Required fields not mapped: **{', '.join(missing_required)}**. Please assign a column for each.")
        return None

    return updated


def apply_hotel_mapping(df_raw, mapping):
    """
    Apply column mapping to raw hotel df, creating standardised column names.
    Only the mapped fields are renamed; unmapped fields are dropped from analysis.
    """
    df = df_raw.copy()
    rename_map = {}
    for field_key, col_in_df in mapping.items():
        if col_in_df and col_in_df in df.columns and col_in_df != field_key:
            rename_map[col_in_df] = field_key

    # Handle conflicts: if target name already exists as a source we'd overwrite
    # by doing a two-pass approach
    safe_rename = {}
    for old, new in rename_map.items():
        if new in df.columns and new != old:
            df[f"__orig_{new}"] = df[new]
        safe_rename[old] = new

    df = df.rename(columns=safe_rename)
    return df


def apply_arrivals_mapping(df_raw, mapping):
    if df_raw is None or not mapping: return None
    df = df_raw.copy()
    rename_map = {col: fk for fk, col in mapping.items() if col and col in df.columns and col != fk}
    return df.rename(columns=rename_map)


def apply_holidays_mapping(df_raw, mapping):
    if df_raw is None or not mapping: return None
    df = df_raw.copy()
    rename_map = {col: fk for fk, col in mapping.items() if col and col in df.columns and col != fk}
    return df.rename(columns=rename_map)


# ==========================================================
# DATA PREPARATION — same logic, now operates on normalised columns
# ==========================================================

def prepare_hotel_data(df):
    df = df.copy()

    # Arrival date / month / year
    if 'arrival_date' in df.columns:
        df['arrival_date'] = pd.to_datetime(df['arrival_date'], errors='coerce')
    else:
        df['arrival_date'] = pd.NaT

    if 'arrival_year' in df.columns:
        df['arrival_year'] = pd.to_numeric(df['arrival_year'], errors='coerce')
    else:
        df['arrival_year'] = df['arrival_date'].dt.year

    if 'arrival_month' in df.columns:
        df['arrival_month'] = df['arrival_month'].apply(month_to_number)
    else:
        df['arrival_month'] = df['arrival_date'].dt.month

    if 'arrival_month_name' in df.columns:
        existing_month_name = df['arrival_month_name']
        df['arrival_month_name'] = existing_month_name.where(existing_month_name.notna(), df['arrival_month'].apply(month_number_to_name))
    else:
        df['arrival_month_name'] = df['arrival_month'].apply(month_number_to_name)

    # If arrival_date exists, use it to fill missing year/month/name
    if 'arrival_date' in df.columns:
        df['arrival_year'] = df['arrival_year'].where(df['arrival_year'].notna(), df['arrival_date'].dt.year)
        df['arrival_month'] = df['arrival_month'].where(df['arrival_month'].notna(), df['arrival_date'].dt.month)
        df['arrival_month_name'] = df['arrival_month_name'].where(df['arrival_month_name'].notna(), df['arrival_date'].dt.strftime('%B'))

    # Cancellation flag can be 0/1 or text statuses such as Cancelled / Confirmed
    if 'is_canceled' in df.columns:
        df['is_canceled'] = normalize_cancel_flag(df['is_canceled'])

    # Numeric fields
    for col in ['adr','lead_time','total_stay_nights',
                'stays_in_weekend_nights','stays_in_week_nights',
                'previous_cancellations','is_repeated_guest','total_of_special_requests']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'total_stay_nights' not in df.columns:
        weekend = df['stays_in_weekend_nights'] if 'stays_in_weekend_nights' in df.columns else 0
        week = df['stays_in_week_nights'] if 'stays_in_week_nights' in df.columns else 0
        df['total_stay_nights'] = weekend + week

    df['total_stay_nights'] = pd.to_numeric(df['total_stay_nights'], errors='coerce').fillna(0)
    df['stay_nights_for_revenue'] = df['total_stay_nights'].clip(lower=1)

    if 'estimated_revenue' not in df.columns:
        df['estimated_revenue'] = df.get('adr', pd.Series(0, index=df.index)) * df['stay_nights_for_revenue']
    else:
        df['estimated_revenue'] = pd.to_numeric(df['estimated_revenue'], errors='coerce').fillna(0)

    df['season'] = df['arrival_month_name'].apply(get_season)

    if 'booking_source' not in df.columns:
        if 'agent' in df.columns:
            df['booking_source'] = np.where(
                pd.to_numeric(df['agent'], errors='coerce').fillna(0) > 0,
                'Agent / Third Party', 'Direct Booking'
            )
        else:
            df['booking_source'] = 'Unknown'

    df['confirmed_booking'] = (df['is_canceled'] == 0).astype(int)
    df['cancelled_booking'] = (df['is_canceled'] == 1).astype(int)
    df['confirmed_revenue'] = np.where(df['is_canceled'] == 0, df['estimated_revenue'], 0)
    df['lost_revenue'] = np.where(df['is_canceled'] == 1, df['estimated_revenue'], 0)
    return df

def prepare_arrivals_data(arrivals_df):
    if arrivals_df is None:
        return None
    a = arrivals_df.copy()
    if 'year' in a.columns:
        a['year'] = pd.to_numeric(a['year'], errors='coerce')
    if 'month' in a.columns:
        a['month'] = a['month'].apply(month_to_number)
    if 'international_arrivals' in a.columns:
        a['international_arrivals'] = pd.to_numeric(a['international_arrivals'], errors='coerce')
    return a

def add_holiday_window(hotel_df, holidays_df, days=7):
    df = hotel_df.copy()
    df['_order'] = np.arange(len(df))
    df['holiday_window'] = False
    df['long_weekend_window'] = False
    df['regional_holiday_window'] = False
    df['nearest_holiday'] = 'None'

    if holidays_df is None or holidays_df.empty or 'holiday_date' not in holidays_df.columns:
        return df.drop(columns=['_order'])

    holidays = holidays_df.copy()
    holidays['holiday_date'] = pd.to_datetime(holidays['holiday_date'], errors='coerce')
    holidays = holidays.dropna(subset=['holiday_date']).sort_values('holiday_date')
    if holidays.empty:
        return df.drop(columns=['_order'])

    valid = df[df['arrival_date'].notna()].sort_values('arrival_date').copy()
    invalid = df[df['arrival_date'].isna()].copy()

    if not valid.empty:
        cols = ['holiday_date'] + [c for c in ['holiday_name','is_long_weekend','is_regional_holiday'] if c in holidays.columns]
        merged = pd.merge_asof(valid, holidays[cols],
            left_on='arrival_date', right_on='holiday_date',
            direction='nearest', tolerance=pd.Timedelta(days=days))
        merged['holiday_window'] = merged['holiday_date'].notna()
        merged['nearest_holiday'] = merged.get('holiday_name', pd.Series(index=merged.index, dtype='object')).fillna('None')
        if 'is_long_weekend' in merged.columns:
            long_weekend_flag = normalize_bool_flag(merged['is_long_weekend'])
        else:
            long_weekend_flag = pd.Series(False, index=merged.index)

        if 'is_regional_holiday' in merged.columns:
            regional_flag = normalize_bool_flag(merged['is_regional_holiday'])
        else:
            regional_flag = pd.Series(False, index=merged.index)

        merged['long_weekend_window'] = merged['holiday_window'] & long_weekend_flag
        merged['regional_holiday_window'] = merged['holiday_window'] & regional_flag
        df = pd.concat([merged, invalid], ignore_index=True)

    return df.sort_values('_order').drop(columns=['_order'])


def monthly_summary(df, arrivals_df=None):
    if df.empty: return pd.DataFrame()

    agg_dict = dict(
        bookings=('is_canceled','count'),
        confirmed=('confirmed_booking','sum'),
        cancelled=('cancelled_booking','sum'),
        confirmed_revenue=('confirmed_revenue','sum'),
        lost_revenue=('lost_revenue','sum'),
    )
    if 'adr' in df.columns:
        agg_dict['avg_adr'] = ('adr', lambda s: s[df.loc[s.index,'is_canceled']==0].mean())
    if 'lead_time' in df.columns:
        agg_dict['avg_lead_time'] = ('lead_time','mean')

    m = df.groupby(['arrival_year','arrival_month','arrival_month_name'], dropna=False).agg(**agg_dict).reset_index()
    m['cancel_rate'] = np.where(m['bookings']>0, m['cancelled']/m['bookings']*100, 0)
    m['total_revenue_risk'] = m['confirmed_revenue'] + m['lost_revenue']
    m['month_sort'] = pd.to_numeric(m['arrival_year'],errors='coerce').fillna(0)*100 + pd.to_numeric(m['arrival_month'],errors='coerce').fillna(0)

    arrivals = prepare_arrivals_data(arrivals_df)
    if arrivals is not None and {'year','month','international_arrivals'}.issubset(arrivals.columns):
        m = m.merge(arrivals, left_on=['arrival_year','arrival_month'], right_on=['year','month'], how='left')
        m['capture_index'] = np.where(m['international_arrivals']>0, m['confirmed']/m['international_arrivals']*100, np.nan)
        m['arrival_demand_rank'] = m['international_arrivals'].rank(pct=True)*100
        if 'avg_adr' in m.columns:
            m['adr_rank'] = m['avg_adr'].rank(pct=True)*100
            m['pricing_gap'] = m['arrival_demand_rank'] - m['adr_rank']

    return m.sort_values('month_sort')


def quality_table(df, group_col, min_bookings=50):
    if df.empty or group_col not in df.columns: return pd.DataFrame()

    agg_dict = dict(
        bookings=('is_canceled','count'),
        confirmed=('confirmed_booking','sum'),
        cancelled=('cancelled_booking','sum'),
        confirmed_revenue=('confirmed_revenue','sum'),
        lost_revenue=('lost_revenue','sum'),
    )
    if 'adr' in df.columns:
        agg_dict['avg_adr'] = ('adr', lambda s: s[df.loc[s.index,'is_canceled']==0].mean())
    if 'lead_time' in df.columns:
        agg_dict['avg_lead_time'] = ('lead_time','mean')

    q = df.groupby(group_col, dropna=False).agg(**agg_dict).reset_index()
    q['cancel_rate'] = np.where(q['bookings']>0, q['cancelled']/q['bookings']*100, 0)
    q['revenue_m'] = q['confirmed_revenue']/1_000_000
    q['lost_revenue_m'] = q['lost_revenue']/1_000_000
    q['net_revenue_quality'] = q['confirmed_revenue'] - q['lost_revenue']
    return q[q['bookings']>=min_bookings].sort_values('confirmed_revenue', ascending=False)


def safe_idxmax_label(df, value_col, label_col, default='N/A'):
    if df is None or df.empty or value_col not in df.columns or label_col not in df.columns: return default
    try: return df.loc[df[value_col].idxmax(), label_col]
    except: return default


# ==========================================================
# SIDEBAR — file upload
# ==========================================================
with st.sidebar:
    st.markdown("## 🏨 Hotel Revenue\nIntelligence")
    st.markdown("---")
    st.markdown("### 📂 Upload Your Data")
    st.caption("Upload any files — you'll map your columns to the required fields on the next screen.")

    hotel_upload = st.file_uploader("1️⃣ Hotel booking data", type=["xlsx","xls","csv"], help="Main bookings dataset")
    arrivals_upload = st.file_uploader("2️⃣ Arrivals / demand data", type=["xlsx","xls","csv"], help="e.g. Portugal international arrivals")
    holidays_upload = st.file_uploader("3️⃣ Public holidays data", type=["xlsx","xls","csv"], help="e.g. public holidays calendar")

    st.caption("Files auto-load if saved next to this app as: cleaned_hotel_data.xlsx, cleaned_portugal_arrivals.xlsx, cleaned_Portugal_Public_Holidays_2015_2017.xlsx")

hotel_raw, hotel_name   = load_dataset(hotel_upload,    "cleaned_hotel_data.xlsx")
arrivals_raw, arr_name  = load_dataset(arrivals_upload, "cleaned_portugal_arrivals.xlsx")
holidays_raw, hol_name  = load_dataset(holidays_upload, "cleaned_Portugal_Public_Holidays_2015_2017.xlsx")


def landing_page():
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem;'>
        <div style='font-size:64px;margin-bottom:1rem;'>🏨</div>
        <h1 style='color:#E0E6F0;font-size:36px;font-weight:700;margin-bottom:0.5rem;'>
            Hotel Revenue Intelligence
        </h1>
        <p style='color:#5577AA;font-size:18px;margin-bottom:2rem;'>
            Upload any hotel dataset — the dashboard adapts to your column names automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col, icon, label in zip([c1,c2,c3,c4],
        ["🗂️","📊","💰","🎯"],
        ["Any Column Names","Revenue Analysis","Cancellation Insights","Smart Recommendations"]):
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#111E35);border:1px solid #1A2A45;
            border-radius:16px;padding:1.5rem;text-align:center;'>
                <div style='font-size:32px;margin-bottom:8px;'>{icon}</div>
                <div style='font-size:13px;color:#8899BB;font-weight:500;'>{label}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Upload all 3 files on the left to start: hotel booking data, arrivals/demand data, and public holidays data.")


if hotel_raw is None:
    landing_page()
    st.stop()


# ==========================================================
# COLUMN MAPPING SCREENS — shown once per uploaded file
# ==========================================================

# Determine if mapping step should be shown
def needs_mapping(session_key, df, schema):
    """Show mapping UI if user has never confirmed mapping for this file, or file changed."""
    return session_key not in st.session_state.get('confirmed_mappings', set())

show_mapping = (
    needs_mapping('hotel_mapping', hotel_raw, HOTEL_SCHEMA) or
    (arrivals_raw is not None and needs_mapping('arrivals_mapping', arrivals_raw, ARRIVALS_SCHEMA)) or
    (holidays_raw is not None and needs_mapping('holidays_mapping', holidays_raw, HOLIDAYS_SCHEMA))
)

if 'confirmed_mappings' not in st.session_state:
    st.session_state['confirmed_mappings'] = set()

# Add remapping button to sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🗂️ Re-map Columns", use_container_width=True):
        st.session_state['confirmed_mappings'] = set()
        for key in ['hotel_mapping','arrivals_mapping','holidays_mapping']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if show_mapping:
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>
            🗂️ Map Your Data Columns
        </h1>
        <p style='color:#5577AA;font-size:14px;'>
            Your file has been loaded. Tell the dashboard which of your columns maps to each field.
            Auto-matched columns are pre-filled — review fuzzy matches and correct anything that looks wrong.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("column_mapping_form"):
        # Hotel mapping
        st.markdown("## 1️⃣ Hotel Booking Data")
        st.markdown(f"<p style='color:#5577AA;font-size:12px;'>File: <strong>{hotel_name}</strong> · {len(hotel_raw):,} rows · {len(hotel_raw.columns)} columns</p>", unsafe_allow_html=True)

        col_preview, _ = st.columns([3,1])
        with col_preview:
            with st.expander("👀 Preview raw columns in your file", expanded=False):
                st.dataframe(hotel_raw.head(5), use_container_width=True)

        hotel_mapping = render_mapping_ui(
            hotel_raw, HOTEL_SCHEMA, 'hotel_mapping',
            "Hotel Booking Columns",
            "Match your file's column names to the expected fields. Fields marked * are required."
        )

        if arrivals_raw is not None:
            st.markdown("---")
            st.markdown("## 2️⃣ Arrivals / Demand Data")
            st.markdown(f"<p style='color:#5577AA;font-size:12px;'>File: <strong>{arr_name}</strong> · {len(arrivals_raw):,} rows · {len(arrivals_raw.columns)} columns</p>", unsafe_allow_html=True)
            with st.expander("👀 Preview raw columns in your file", expanded=False):
                st.dataframe(arrivals_raw.head(5), use_container_width=True)

            arrivals_mapping = render_mapping_ui(
                arrivals_raw, ARRIVALS_SCHEMA, 'arrivals_mapping',
                "Arrivals Data Columns",
                "Match your arrivals file columns to the expected fields."
            )
        else:
            arrivals_mapping = None

        if holidays_raw is not None:
            st.markdown("---")
            st.markdown("## 3️⃣ Public Holidays Data")
            st.markdown(f"<p style='color:#5577AA;font-size:12px;'>File: <strong>{hol_name}</strong> · {len(holidays_raw):,} rows · {len(holidays_raw.columns)} columns</p>", unsafe_allow_html=True)
            with st.expander("👀 Preview raw columns in your file", expanded=False):
                st.dataframe(holidays_raw.head(5), use_container_width=True)

            holidays_mapping = render_mapping_ui(
                holidays_raw, HOLIDAYS_SCHEMA, 'holidays_mapping',
                "Holidays Data Columns",
                "Match your holidays file columns to the expected fields."
            )
        else:
            holidays_mapping = None

        st.markdown("---")
        submitted = st.form_submit_button(
            "✅ Confirm Mapping & Load Dashboard",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if hotel_mapping is None:
                st.error("Please fix required hotel column mappings before continuing.")
            else:
                st.session_state['final_hotel_mapping']    = hotel_mapping
                st.session_state['final_arrivals_mapping'] = arrivals_mapping
                st.session_state['final_holidays_mapping'] = holidays_mapping
                st.session_state['confirmed_mappings'].add('hotel_mapping')
                if arrivals_raw is not None:
                    st.session_state['confirmed_mappings'].add('arrivals_mapping')
                if holidays_raw is not None:
                    st.session_state['confirmed_mappings'].add('holidays_mapping')
                st.rerun()

    st.stop()


# ==========================================================
# APPLY MAPPINGS — normalise column names before analysis
# ==========================================================

hotel_mapped    = apply_hotel_mapping(hotel_raw,    st.session_state.get('final_hotel_mapping', {}))
arrivals_mapped = apply_arrivals_mapping(arrivals_raw, st.session_state.get('final_arrivals_mapping'))
holidays_mapped = apply_holidays_mapping(holidays_raw, st.session_state.get('final_holidays_mapping'))

hotel_df = prepare_hotel_data(hotel_mapped)

# The dashboard needs month/year for demand analysis and arrival_date for holiday-window analysis.
if hotel_df['arrival_year'].isna().all() or hotel_df['arrival_month'].isna().all():
    st.error("Please re-map your hotel booking file. The dashboard needs either an Arrival Date column, or both Arrival Year and Arrival Month columns.")
    st.stop()

if hotel_df['arrival_date'].isna().all():
    st.warning("No valid Arrival Date was mapped, so holiday-window analysis may be limited. For full holiday impact analysis, map a check-in / arrival date column.")

hotel_df = add_holiday_window(hotel_df, holidays_mapped, days=7)


# ==========================================================
# SIDEBAR FILTERS
# ==========================================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### ✅ Loaded Files")
    badges = [f"<span class='file-badge'>🏨 {hotel_name}</span>"]
    if arr_name:  badges.append(f"<span class='file-badge'>📈 {arr_name}</span>")
    if hol_name:  badges.append(f"<span class='file-badge'>📅 {hol_name}</span>")
    st.markdown("".join(badges), unsafe_allow_html=True)
    st.success(f"✅ **{len(hotel_df):,}** booking rows loaded")

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

    holiday_filter = st.selectbox("📅 Holiday Window",
        ["All dates","Holiday ±7 days only","Normal dates only","Long-weekend window only"])

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
if holiday_filter == "Holiday ±7 days only":  mask &= hotel_df['holiday_window'] == True
elif holiday_filter == "Normal dates only":   mask &= hotel_df['holiday_window'] == False
elif holiday_filter == "Long-weekend window only": mask &= hotel_df['long_weekend_window'] == True

df = hotel_df[mask].copy()

if df.empty:
    st.warning("No data available after applying the selected filters.")
    st.stop()

monthly_df = monthly_summary(df, arrivals_mapped)

confirmed   = df['confirmed_revenue'].sum()
lost        = df['lost_revenue'].sum()
total       = len(df)
cancelled   = int(df['cancelled_booking'].sum())
confirmed_bookings = int(df['confirmed_booking'].sum())
cancel_rate = cancelled / total * 100 if total > 0 else 0
avg_adr     = df[df['is_canceled']==0]['adr'].mean() if 'adr' in df.columns else 0
loss_ratio  = lost / confirmed if confirmed > 0 else 0
holiday_rows = int(df['holiday_window'].sum()) if 'holiday_window' in df.columns else 0

source_count = 1 + (1 if arrivals_mapped is not None else 0) + (1 if holidays_mapped is not None else 0)
source_tag = f" · <strong style='color:#22D47B'>{source_count} data source{'s' if source_count > 1 else ''} connected</strong>"

st.markdown(
    f"<div style='margin-bottom:1.5rem;'>"
    f"<h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>🏨 Hotel Revenue Intelligence</h1>"
    f"<p style='color:#5577AA;font-size:14px;'>Hospitality Analysis · <strong style='color:#7ABAFF'>{total:,}</strong> bookings{source_tag} · Auto-generated insights</p>"
    f"</div>",
    unsafe_allow_html=True
)

k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("✅ Confirmed Revenue", money_m(confirmed), f"{confirmed_bookings:,} stayed")
with k2: st.metric("❌ Revenue Lost", money_m(lost), f"-{loss_ratio:.0%} loss ratio" if confirmed>0 else "N/A", delta_color="inverse")
with k3: st.metric("📉 Cancel Rate", pct(cancel_rate), f"{cancelled:,} bookings", delta_color="inverse")
with k4: st.metric("💳 Avg Daily Rate", f"${avg_adr:.0f}" if not pd.isna(avg_adr) else "N/A", "confirmed bookings")
with k5: st.metric("📋 Total Bookings", f"{total:,}", f"{holiday_rows:,} near holidays")

st.markdown("---")

tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "📈 Revenue Overview","❌ Cancellation Analysis","🌍 Market Intelligence",
    "📅 Seasonality","📊 Demand & Pricing","🎉 Holiday Impact","🎯 Recommendations"
])

# ── TAB 1 ──────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">📊 Monthly Revenue Performance</div>', unsafe_allow_html=True)
    monthly_plot = monthly_df.copy()
    monthly_plot['month_label'] = monthly_plot['arrival_month_name'].str[:3] + " " + monthly_plot['arrival_year'].astype(int).astype(str)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='✅ Confirmed', x=monthly_plot['month_label'], y=monthly_plot['confirmed_revenue']/1e6,
        marker=dict(color=BLUE,opacity=0.9),
        text=(monthly_plot['confirmed_revenue']/1e6).apply(lambda x: f'${x:.2f}M'),
        textposition='outside', textfont=dict(size=10,color='#8899BB')))
    fig.add_trace(go.Bar(name='❌ Lost', x=monthly_plot['month_label'], y=monthly_plot['lost_revenue']/1e6,
        marker=dict(color=RED,opacity=0.8),
        text=(monthly_plot['lost_revenue']/1e6).apply(lambda x: f'${x:.2f}M'),
        textposition='outside', textfont=dict(size=10,color='#8899BB')))
    fig.update_layout(**merged_layout(380, barmode='group',
        yaxis=dict(tickprefix='$',ticksuffix='M',gridcolor='#1A2A45',showline=False,zeroline=False),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,bgcolor='rgba(0,0,0,0)',bordercolor='#1A2A45',font=dict(color='#8899BB'))))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🏨 Revenue by Hotel Type</div>', unsafe_allow_html=True)
        if 'hotel' in df.columns:
            hotel_type_df = df.groupby('hotel')['confirmed_revenue'].sum().reset_index()
            fig2 = px.pie(hotel_type_df, values='confirmed_revenue', names='hotel',
                color_discrete_sequence=[BLUE,PURPLE], hole=0.55)
            fig2.update_traces(textinfo='percent+label', textfont_color='white',
                marker=dict(line=dict(color='#060B18',width=3)))
            chart(fig2, 310)
        else:
            st.info("No 'hotel type' column mapped.")

    with col2:
        st.markdown('<div class="section-header">📦 Revenue by Market Segment</div>', unsafe_allow_html=True)
        if 'market_segment' in df.columns:
            seg_df = quality_table(df,'market_segment',min_bookings=20).sort_values('confirmed_revenue')
            fig3 = px.bar(seg_df, x='confirmed_revenue', y='market_segment', orientation='h',
                color='confirmed_revenue', color_continuous_scale=[[0,'#0D1628'],[1,BLUE]])
            fig3.update_traces(texttemplate='$%{x:.2s}', textposition='outside',
                textfont=dict(color='#8899BB',size=11))
            fig3.update_layout(**merged_layout(310,
                xaxis=dict(tickprefix='$',gridcolor='#1A2A45',showline=False,zeroline=False),
                coloraxis_showscale=False))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No 'market segment' column mapped.")

# ── TAB 2 ──────────────────────────────────────────────────
with tab2:
    c1,c2,c3 = st.columns(3)
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
            <div class='insight-desc'>Bookings cancelled as % of total bookings</div>
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

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">💳 Cancellation Rate by Deposit Type</div>', unsafe_allow_html=True)
        if 'deposit_type' in df.columns:
            dep_df = quality_table(df,'deposit_type',min_bookings=1).sort_values('cancel_rate',ascending=True)
            colors_dep = [RED if x>50 else AMBER if x>25 else GREEN for x in dep_df['cancel_rate']]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dep_df['cancel_rate'], y=dep_df['deposit_type'], orientation='h',
                marker=dict(color=colors_dep,opacity=0.85),
                text=dep_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside', textfont=dict(color='#E0E6F0',size=12)))
            fig.update_layout(**merged_layout(300,
                xaxis=dict(ticksuffix='%',range=[0,max(100,dep_df['cancel_rate'].max()*1.2)],gridcolor='#1A2A45')))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No 'deposit type' column mapped.")

    with col2:
        st.markdown('<div class="section-header">👥 Cancellation by Customer Type</div>', unsafe_allow_html=True)
        if 'customer_type' in df.columns:
            cust_df = quality_table(df,'customer_type',min_bookings=1)
            fig = px.bar(cust_df, x='customer_type', y='cancel_rate',
                color='cancel_rate', color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,RED]],
                text=cust_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'))
            fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0',size=12))
            fig.update_layout(**merged_layout(300,
                yaxis=dict(ticksuffix='%',gridcolor='#1A2A45'),coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No 'customer type' column mapped.")

    st.markdown('<div class="section-header">📊 Revenue Lost vs Confirmed — Monthly Trend</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_plot['month_label'], y=monthly_plot['confirmed_revenue']/1e6,
        name='✅ Confirmed', fill='tozeroy', fillcolor='rgba(74,158,255,0.15)',
        line=dict(color=BLUE,width=3)))
    fig.add_trace(go.Scatter(x=monthly_plot['month_label'], y=monthly_plot['lost_revenue']/1e6,
        name='❌ Lost', fill='tozeroy', fillcolor='rgba(255,90,90,0.15)',
        line=dict(color=RED,width=3,dash='dot')))
    fig.update_layout(**merged_layout(300,
        yaxis=dict(tickprefix='$',ticksuffix='M',gridcolor='#1A2A45',showline=False,zeroline=False)))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── TAB 3 ──────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">🌍 Top Source Markets — Revenue vs Cancellation Rate</div>', unsafe_allow_html=True)
    if 'country' in df.columns:
        country_df = quality_table(df,'country',min_bookings=100).nlargest(10,'confirmed_revenue')
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(name='Revenue ($M)', x=country_df['country'], y=country_df['revenue_m'],
            marker=dict(color=BLUE,opacity=0.85),
            text=country_df['revenue_m'].apply(lambda x: f'${x:.2f}M'),
            textposition='outside', textfont=dict(color='#8899BB',size=11)), secondary_y=False)
        fig.add_trace(go.Scatter(name='Cancel Rate', x=country_df['country'], y=country_df['cancel_rate'],
            mode='lines+markers+text', line=dict(color=RED,width=3),
            marker=dict(size=10,color=RED,line=dict(color='white',width=2)),
            text=country_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'),
            textposition='top center', textfont=dict(color=RED,size=11)), secondary_y=True)
        fig.update_layout(**merged_layout(380,
            yaxis=dict(tickprefix='$',ticksuffix='M',gridcolor='#1A2A45'),
            yaxis2=dict(ticksuffix='%',gridcolor='rgba(0,0,0,0)')))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No 'country' column mapped.")

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">📡 Distribution Channel</div>', unsafe_allow_html=True)
        if 'distribution_channel' in df.columns:
            dist_df = df.groupby('distribution_channel')['confirmed_revenue'].sum().reset_index()
            fig = px.pie(dist_df, values='confirmed_revenue', names='distribution_channel',
                color_discrete_sequence=COLORS, hole=0.5)
            fig.update_traces(textinfo='percent+label', textfont_color='white',
                marker=dict(line=dict(color='#060B18',width=3)))
            chart(fig, 310)
        else:
            st.info("No 'distribution channel' column mapped.")
    with col2:
        st.markdown('<div class="section-header">🧳 Booking Source Breakdown</div>', unsafe_allow_html=True)
        if 'booking_source' in df.columns:
            src_df = quality_table(df,'booking_source',min_bookings=20).sort_values('confirmed_revenue',ascending=True).tail(6)
            fig = px.bar(src_df, x='confirmed_revenue', y='booking_source', orientation='h',
                color='cancel_rate', color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,RED]])
            fig.update_layout(**merged_layout(310,
                xaxis=dict(tickprefix='$',gridcolor='#1A2A45'),
                coloraxis_colorbar=dict(title='Cancel %')))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header">🧭 Market Quality Matrix</div>', unsafe_allow_html=True)
    if 'country' in df.columns:
        market_quality = quality_table(df,'country',min_bookings=300)
        if not market_quality.empty and 'avg_adr' in market_quality.columns:
            fig = px.scatter(market_quality, x='cancel_rate', y='revenue_m',
                size='bookings', color='avg_adr', hover_name='country',
                color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,PURPLE]],
                labels={'cancel_rate':'Cancellation Rate (%)','revenue_m':'Confirmed Revenue ($M)','avg_adr':'ADR'})
            fig.add_vline(x=market_quality['cancel_rate'].median(), line_dash='dash', line_color='#5577AA')
            fig.add_hline(y=market_quality['revenue_m'].median(), line_dash='dash', line_color='#5577AA')
            chart(fig, 420)
            st.caption("Top-left = high revenue, low risk → best targets for retention campaigns.")

# ── TAB 4 ──────────────────────────────────────────────────
with tab4:
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🌞 Revenue by Season</div>', unsafe_allow_html=True)
        season_df = df.groupby('season').agg(
            revenue=('confirmed_revenue','sum'),
            bookings=('is_canceled','count'),
            cancelled=('cancelled_booking','sum')
        ).reset_index()
        season_df['revenue_m'] = season_df['revenue']/1e6
        season_df['cancel_rate'] = np.where(season_df['bookings']>0, season_df['cancelled']/season_df['bookings']*100, 0)
        season_colors = {'☀️ Summer':AMBER,'🌸 Spring':GREEN,'🍂 Autumn':CYAN,'❄️ Winter':BLUE}
        fig = px.pie(season_df, values='revenue_m', names='season',
            color='season', color_discrete_map=season_colors, hole=0.55)
        fig.update_traces(textinfo='percent+label', textfont_color='white',
            marker=dict(line=dict(color='#060B18',width=3)))
        chart(fig, 330)

    with col2:
        st.markdown('<div class="section-header">📊 Season Performance Summary</div>', unsafe_allow_html=True)
        total_season_rev = season_df['revenue_m'].sum()
        for _, row in season_df.sort_values('revenue_m',ascending=False).iterrows():
            s = row['season']
            c = season_colors.get(s, BLUE)
            pct_r = row['revenue_m']/total_season_rev*100 if total_season_rev>0 else 0
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
                    <div style='font-size:12px;color:#5577AA;'>{pct_r:.1f}% of revenue</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📅 ADR vs Arrival Volume by Month</div>', unsafe_allow_html=True)
    if 'adr' in df.columns and 'avg_adr' in monthly_df.columns:
        adr_df = monthly_df.copy()
        adr_df['month_label'] = adr_df['arrival_month_name'].str[:3]+' '+adr_df['arrival_year'].astype(int).astype(str)
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(name='Bookings Volume', x=adr_df['month_label'], y=adr_df['bookings'],
            marker=dict(color=BLUE,opacity=0.5)), secondary_y=False)
        fig.add_trace(go.Scatter(name='Avg Daily Rate', x=adr_df['month_label'], y=adr_df['avg_adr'],
            mode='lines+markers', line=dict(color=AMBER,width=3),
            marker=dict(size=8,color=AMBER,line=dict(color='white',width=2))), secondary_y=True)
        fig.update_layout(**merged_layout(330,
            yaxis=dict(title='Bookings',gridcolor='#1A2A45'),
            yaxis2=dict(title='Avg ADR ($)',tickprefix='$',gridcolor='rgba(0,0,0,0)')))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── TAB 5 ──────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">📊 Arrivals Demand vs Hotel Revenue</div>', unsafe_allow_html=True)
    has_arrivals = arrivals_mapped is not None and 'international_arrivals' in monthly_df.columns
    if not has_arrivals:
        st.info("Upload an arrivals / demand file and map its columns to enable this analysis.")
    else:
        demand_df = monthly_df.dropna(subset=['international_arrivals']).copy()
        if demand_df.empty:
            st.warning("The arrivals file was uploaded, but its year/month values do not overlap with the hotel booking data after filters.")
        else:
            demand_df['month_label'] = demand_df['arrival_month_name'].str[:3]+' '+demand_df['arrival_year'].astype(int).astype(str)
            fig = make_subplots(specs=[[{'secondary_y':True}]])
            fig.add_trace(go.Bar(name='International Arrivals', x=demand_df['month_label'],
                y=demand_df['international_arrivals']/1e6, marker=dict(color=CYAN,opacity=0.45)), secondary_y=False)
            fig.add_trace(go.Scatter(name='Hotel Confirmed Revenue', x=demand_df['month_label'],
                y=demand_df['confirmed_revenue']/1e6, mode='lines+markers',
                line=dict(color=BLUE,width=3), marker=dict(size=8)), secondary_y=True)
            fig.update_yaxes(title_text='Arrivals (M)', secondary_y=False)
            fig.update_yaxes(title_text='Hotel Revenue ($M)', tickprefix='$', ticksuffix='M', secondary_y=True)
            fig.update_layout(**merged_layout(400))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            best_rev = demand_df.sort_values('confirmed_revenue',ascending=False).iloc[0]
            highest_cancel = demand_df.sort_values('cancel_rate',ascending=False).iloc[0]
            pricing_opp = demand_df.dropna(subset=['pricing_gap']).sort_values('pricing_gap',ascending=False).head(5) if 'pricing_gap' in demand_df.columns else pd.DataFrame()

            a,b,c = st.columns(3)
            a.markdown(f"""<div class='insight-card'>
                <div class='insight-title'>Best Revenue Month</div>
                <div class='insight-value' style='color:{BLUE};'>{best_rev['arrival_month_name']} {int(best_rev['arrival_year'])}</div>
                <div class='insight-desc'>{money_m(best_rev['confirmed_revenue'])} confirmed with {pct(best_rev['cancel_rate'])} cancellation.</div>
            </div>""", unsafe_allow_html=True)
            b.markdown(f"""<div class='insight-card'>
                <div class='insight-title'>Highest Cancellation Month</div>
                <div class='insight-value' style='color:{RED};'>{highest_cancel['arrival_month_name']} {int(highest_cancel['arrival_year'])}</div>
                <div class='insight-desc'>This month needs stronger deposit and reconfirmation controls.</div>
            </div>""", unsafe_allow_html=True)
            if not pricing_opp.empty:
                opp = pricing_opp.iloc[0]
                c.markdown(f"""<div class='insight-card'>
                    <div class='insight-title'>Pricing Opportunity</div>
                    <div class='insight-value' style='color:{AMBER};'>{opp['arrival_month_name']} {int(opp['arrival_year'])}</div>
                    <div class='insight-desc'>Demand rank exceeds ADR rank — room to review rates or packages.</div>
                </div>""", unsafe_allow_html=True)

                st.markdown('<div class="section-header">💰 Underpriced Demand Windows</div>', unsafe_allow_html=True)
                show_cols = [c for c in ['arrival_year','arrival_month_name','international_arrivals','avg_adr','cancel_rate','confirmed_revenue','pricing_gap'] if c in pricing_opp.columns]
                display_opp = pricing_opp[show_cols].copy()
                if 'confirmed_revenue' in display_opp: display_opp['confirmed_revenue'] = display_opp['confirmed_revenue'].map(lambda x: f"${x:,.0f}")
                if 'avg_adr' in display_opp: display_opp['avg_adr'] = display_opp['avg_adr'].map(lambda x: f"${x:,.0f}")
                if 'cancel_rate' in display_opp: display_opp['cancel_rate'] = display_opp['cancel_rate'].map(lambda x: f"{x:.1f}%")
                if 'pricing_gap' in display_opp: display_opp['pricing_gap'] = display_opp['pricing_gap'].map(lambda x: f"{x:.1f}")
                st.dataframe(display_opp, use_container_width=True, hide_index=True)
# ── TAB 6 ──────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-header">🎉 Public Holiday Booking Behaviour</div>', unsafe_allow_html=True)
    if holidays_mapped is None:
        st.info("Upload a public holidays file and map its columns to enable this analysis.")
    else:
        temp = df.copy()
        temp['date_type'] = np.where(temp['holiday_window'],'Holiday ±7 days','Normal dates')
        holiday_compare = temp.groupby('date_type').agg(
            bookings=('is_canceled','count'), confirmed=('confirmed_booking','sum'),
            cancelled=('cancelled_booking','sum'), confirmed_revenue=('confirmed_revenue','sum'),
            lost_revenue=('lost_revenue','sum'),
            avg_adr=('adr', lambda s: s[temp.loc[s.index,'is_canceled']==0].mean()) if 'adr' in temp.columns else ('confirmed_revenue','sum')
        ).reset_index()
        holiday_compare['cancel_rate'] = np.where(holiday_compare['bookings']>0, holiday_compare['cancelled']/holiday_compare['bookings']*100, 0)
        holiday_compare['revenue_m'] = holiday_compare['confirmed_revenue']/1e6

        col1,col2 = st.columns(2)
        with col1:
            fig = px.bar(holiday_compare, x='date_type', y='revenue_m', color='cancel_rate',
                color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,RED]],
                text=holiday_compare['revenue_m'].map(lambda v: f'${v:.2f}M'))
            fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0'))
            fig.update_layout(**merged_layout(330,
                yaxis=dict(tickprefix='$',ticksuffix='M',gridcolor='#1A2A45'),
                coloraxis_colorbar=dict(title='Cancel %')))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with col2:
            if 'avg_adr' in holiday_compare.columns:
                fig = px.bar(holiday_compare, x='date_type', y='avg_adr', color='date_type',
                    color_discrete_sequence=[BLUE,AMBER],
                    text=holiday_compare['avg_adr'].map(lambda v: f'${v:.0f}'))
                fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0'))
                fig.update_layout(**merged_layout(330,
                    yaxis=dict(tickprefix='$',gridcolor='#1A2A45'), showlegend=False))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-header">🏖️ Top Holiday Windows by Booking Volume</div>', unsafe_allow_html=True)
        holiday_only = df[df['holiday_window']].copy()
        if holiday_only.empty:
            st.warning("No bookings within ±7 days of a public holiday in the current filter.")
        else:
            agg_dict = dict(bookings=('is_canceled','count'), confirmed=('confirmed_booking','sum'),
                cancelled=('cancelled_booking','sum'), confirmed_revenue=('confirmed_revenue','sum'),
                lost_revenue=('lost_revenue','sum'), long_weekend=('long_weekend_window','max'))
            if 'adr' in holiday_only.columns:
                agg_dict['avg_adr'] = ('adr', lambda s: s[holiday_only.loc[s.index,'is_canceled']==0].mean())
            holiday_rank = holiday_only.groupby('nearest_holiday').agg(**agg_dict).reset_index()
            holiday_rank['cancel_rate'] = np.where(holiday_rank['bookings']>0, holiday_rank['cancelled']/holiday_rank['bookings']*100, 0)
            holiday_rank = holiday_rank.sort_values('bookings',ascending=False).head(10)
            display_h = holiday_rank.copy()
            display_h['confirmed_revenue'] = display_h['confirmed_revenue'].map(lambda x: f"${x:,.0f}")
            display_h['lost_revenue'] = display_h['lost_revenue'].map(lambda x: f"${x:,.0f}")
            if 'avg_adr' in display_h: display_h['avg_adr'] = display_h['avg_adr'].map(lambda x: f"${x:,.0f}")
            display_h['cancel_rate'] = display_h['cancel_rate'].map(lambda x: f"{x:.1f}%")
            display_h['long_weekend'] = display_h['long_weekend'].map(lambda x: 'Yes' if x else 'No')
            st.dataframe(display_h, use_container_width=True, hide_index=True)
            st.caption("High-volume holidays: use minimum-stay rules, early prepayment, and bundled packages.")

# ── TAB 7 ──────────────────────────────────────────────────
with tab7:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D1628,#0A1A35);border:1px solid #1A2A45;
    border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;text-align:center;'>
        <p style='font-size:20px;font-weight:600;color:#4A9EFF;font-style:italic;margin-bottom:8px;'>
            "A confirmed booking is not confirmed revenue until the guest actually stays."
        </p>
        <p style='font-size:13px;color:#5577AA;'>Connecting booking behaviour · demand signals · holiday pressure · cancellation risk</p>
    </div>
    """, unsafe_allow_html=True)

    country_quality = quality_table(df,'country',min_bookings=300) if 'country' in df.columns else pd.DataFrame()
    segment_quality = quality_table(df,'market_segment',min_bookings=20) if 'market_segment' in df.columns else pd.DataFrame()
    channel_quality = quality_table(df,'distribution_channel',min_bookings=20) if 'distribution_channel' in df.columns else pd.DataFrame()

    top_country = safe_idxmax_label(country_quality,'confirmed_revenue','country')
    reliable_country = 'N/A'
    risky_country    = 'N/A'
    if not country_quality.empty:
        reliable_country = country_quality.sort_values(['cancel_rate','confirmed_revenue'],ascending=[True,False]).iloc[0]['country']
        risky_country    = country_quality.sort_values(['cancel_rate','lost_revenue'],ascending=[False,False]).iloc[0]['country']

    risky_segment = 'N/A'
    if not segment_quality.empty:
        risky_segment = segment_quality.sort_values(['cancel_rate','lost_revenue'],ascending=[False,False]).iloc[0]['market_segment']

    risky_channel = 'N/A'
    if not channel_quality.empty:
        risky_channel = channel_quality.sort_values(['cancel_rate','lost_revenue'],ascending=[False,False]).iloc[0]['distribution_channel']

    best_season = safe_idxmax_label(season_df,'revenue','season') if 'season_df' in locals() else 'N/A'
    worst_deposit = 'N/A'
    if 'deposit_type' in df.columns:
        dep_quality = quality_table(df,'deposit_type',min_bookings=1)
        if not dep_quality.empty:
            worst_deposit = dep_quality.sort_values('cancel_rate',ascending=False).iloc[0]['deposit_type']

    recovery_target = lost * 0.30

    recs = [
        (RED,"01","🚨 Reduce Cancellation Revenue Loss","Flag high-risk bookings before they block inventory.",[
            f"Revenue lost from cancellations: **{money_m(lost)}**.",
            f"Set a 30% reduction target to recover around **{money_m(recovery_target)}**.",
            f"High-risk segment to review: **{risky_segment}**.",
            f"Highest-risk deposit type: **{worst_deposit}**."
        ]),
        (AMBER,"02","💰 Price for Real Demand, Not Only Season","Use demand data as a pricing signal.",[
            "Compare ADR rank with arrivals demand rank each month.",
            "If arrivals are high but ADR is low, review rate fences and minimum-stay rules.",
            f"Best revenue season: **{best_season}**."
        ]),
        (GREEN,"03","🎯 Shift Acquisition Toward Reliable Markets","Separate market size from market quality.",[
            f"Top revenue market: **{top_country}**.",
            f"Most reliable market: **{reliable_country}**.",
            f"Risk-control market to monitor: **{risky_country}**."
        ]),
        (CYAN,"04","🏨 Improve Operational Planning Around Holidays","Use public holidays as revenue events.",[
            f"Bookings near holiday windows: **{holiday_rows:,}**.",
            "For high-volume holiday windows, prepare staffing and capacity earlier.",
            f"Risky channel to monitor: **{risky_channel}**."
        ])
    ]

    for color,num,title,subtitle,points in recs:
        with st.expander(f"**{num} — {title}**", expanded=True):
            st.markdown(f"<p style='color:#8899BB;font-size:13px;font-style:italic;margin-bottom:1rem;'>💡 {subtitle}</p>", unsafe_allow_html=True)
            for p in points:
                st.markdown(f"<p style='color:#C8D8F0;font-size:13px;margin-bottom:6px;'>→ {p}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📊 Auto-Generated Key Insights</div>', unsafe_allow_html=True)
    i1,i2,i3,i4 = st.columns(4)
    for col,icon,label,val,desc in zip([i1,i2,i3,i4],
        ["🏆","✅","🌞","⚠️"],
        ["Top Revenue Market","Most Reliable Market","Best Season","Highest Risk Deposit"],
        [top_country,reliable_country,best_season,worst_deposit],
        ["by confirmed revenue","lowest cancel rate","by revenue contribution","highest cancel rate"]):
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#0F1A2E);border:1px solid #1A2A45;
            border-radius:14px;padding:1.1rem;text-align:center;'>
                <div style='font-size:28px;margin-bottom:6px;'>{icon}</div>
                <div style='font-size:11px;color:#5577AA;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>{label}</div>
                <div style='font-size:16px;font-weight:700;color:#E0E6F0;margin-bottom:4px;'>{val}</div>
                <div style='font-size:11px;color:#5577AA;'>{desc}</div>
            </div>""", unsafe_allow_html=True)
