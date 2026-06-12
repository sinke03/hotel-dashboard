import io
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==========================================================
# FULLY DYNAMIC HOSPITALITY INTELLIGENCE APP
# ----------------------------------------------------------
# What this version does:
# - No fixed file names
# - No fixed file count
# - No fixed file types such as "hotel / arrivals / holidays"
# - The first page is empty until the user uploads files
# - User uploads one or many hospitality-related CSV/Excel files
# - User confirms what each column means
# - The dashboard only generates analysis based on uploaded data
# ==========================================================

st.set_page_config(
    page_title="Hospitality Intelligence Studio",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# THEME
# ==========================================================
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
    color: #FFFFFF !important; font-size: 31px !important;
    font-weight: 800 !important; letter-spacing: -0.5px;
    text-shadow: 0 0 20px rgba(74,158,255,0.3); line-height: 1.15 !important;
}
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
.insight-card, .panel-card {
    background: linear-gradient(135deg, #0D1628, #0F1A2E);
    border: 1px solid #1A2A45; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.insight-title { font-size: 12px; color: #5577AA; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.insight-value { font-size: 22px; font-weight: 700; margin-bottom: 2px; color: #E0E6F0; }
.insight-desc { font-size: 12px; color: #5577AA; line-height: 1.5; }
.mapping-card {
    background: linear-gradient(135deg, #0A1428, #0D1A30);
    border: 1px solid #1E3050; border-radius: 14px;
    padding: 1.25rem 1.5rem; margin-bottom: 1rem;
}
.auto-badge, .manual-badge, .skip-badge {
    display: inline-flex; align-items: center; gap: 4px;
    border-radius: 6px; padding: 2px 8px; font-size: 11px;
}
.auto-badge { background: #0A2510; border: 1px solid #1A5020; color: #22D47B; }
.manual-badge { background: #251A0A; border: 1px solid #50380A; color: #FFB830; }
.skip-badge { background: #1A1A2A; border: 1px solid #3A3A5A; color: #667799; }
div[data-testid="stTabs"] button { color: #6688AA !important; font-size: 13px !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #4A9EFF !important; }
hr { border-color: #1A2A45 !important; }
span[data-baseweb="tag"] { background-color: #1A3A6A !important; border: 1px solid #2A5099 !important; }
span[data-baseweb="tag"] span { color: #7ABAFF !important; }
span[data-baseweb="tag"] button svg { fill: #7ABAFF !important; }
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

MONTH_ORDER = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
]

# ==========================================================
# GENERIC SEMANTIC ROLES
# These are not fixed file types. They are meanings the user can assign
# to any uploaded column so the app knows which analyses are possible.
# ==========================================================
ROLE_INFO = {
    "skip":                 ("Skip / not used", "Leave this column out of the analysis"),
    "date":                 ("Date", "Booking, stay, arrival, transaction, or observation date"),
    "year":                 ("Year", "Year value"),
    "month":                ("Month", "Month name or number"),
    "property":             ("Property / Hotel", "Hotel name, property, branch, or accommodation"),
    "room_type":            ("Room Type", "Room/category type"),
    "country":              ("Market / Country", "Guest origin, market, or nationality"),
    "segment":              ("Segment", "Market segment, business segment, or booking segment"),
    "channel":              ("Channel", "Distribution channel, sales channel, source, or OTA"),
    "customer_type":        ("Customer Type", "Guest type, customer type, group/contract/transient"),
    "revenue":              ("Revenue", "Total sales, booking revenue, room revenue, or gross revenue"),
    "adr":                  ("ADR / Rate", "Average daily rate, room rate, price per night"),
    "room_nights":          ("Room Nights / Stay Nights", "Number of nights, room nights, LOS"),
    "bookings":             ("Bookings / Orders", "Booking count or reservation count"),
    "cancellation":         ("Cancellation Status", "Cancelled flag or booking status"),
    "lead_time":            ("Lead Time", "Days booked before arrival/stay"),
    "occupancy_rate":       ("Occupancy Rate", "Occupancy percentage"),
    "guests":               ("Guests / Pax", "Number of guests, pax, adults + children"),
    "demand":               ("Demand / Visitors / Arrivals", "Tourism arrivals, visitors, searches, demand volume"),
    "event_date":           ("Event / Holiday Date", "Public holiday, event, campaign, or local event date"),
    "event_name":           ("Event / Holiday Name", "Name of holiday, event, campaign, or occasion"),
    "rating":               ("Rating / Satisfaction", "Review score, satisfaction, NPS, rating"),
    "cost":                 ("Cost / Expense", "Cost, commission, campaign spend, or operating expense"),
    "profit":               ("Profit / Margin", "Profit, contribution, margin, or net revenue"),
}

ROLE_OPTIONS = list(ROLE_INFO.keys())
ROLE_LABELS = {k: v[0] for k, v in ROLE_INFO.items()}
ROLE_SELECT_OPTIONS = [f"{ROLE_LABELS[k]}  ·  {k}" for k in ROLE_OPTIONS]
ROLE_OPTION_TO_KEY = {f"{ROLE_LABELS[k]}  ·  {k}": k for k in ROLE_OPTIONS}

ROLE_ALIASES = {
    "date": ["date", "arrival_date", "arrival", "check_in", "checkin", "check_in_date", "stay_date", "booking_date", "reservation_date", "transaction_date", "created_date"],
    "year": ["year", "yr", "arrival_year", "booking_year", "stay_year", "period_year"],
    "month": ["month", "mo", "arrival_month", "booking_month", "stay_month", "month_name", "period_month"],
    "property": ["hotel", "property", "property_name", "hotel_name", "branch", "resort", "accommodation", "accommodation_type"],
    "room_type": ["room_type", "reserved_room_type", "assigned_room_type", "room", "room_category", "unit_type"],
    "country": ["country", "market", "nationality", "origin", "guest_country", "country_of_origin", "source_market", "market_country"],
    "segment": ["market_segment", "segment", "booking_segment", "business_segment", "customer_segment"],
    "channel": ["channel", "distribution_channel", "booking_channel", "sales_channel", "source", "ota", "agent", "travel_agent"],
    "customer_type": ["customer_type", "guest_type", "traveller_type", "traveler_type", "booker_type", "customer_group"],
    "revenue": ["revenue", "total_revenue", "estimated_revenue", "booking_revenue", "room_revenue", "sales", "amount", "gross_revenue", "net_revenue"],
    "adr": ["adr", "average_daily_rate", "avg_daily_rate", "daily_rate", "room_rate", "rate", "price_per_night", "avg_rate"],
    "room_nights": ["room_nights", "stay_nights", "total_stay_nights", "nights", "los", "length_of_stay", "stays_in_week_nights", "stays_in_weekend_nights"],
    "bookings": ["bookings", "booking_count", "reservations", "reservation_count", "orders", "transactions", "count", "volume"],
    "cancellation": ["is_canceled", "is_cancelled", "cancelled", "canceled", "cancellation", "booking_status", "status", "cancel_status"],
    "lead_time": ["lead_time", "leadtime", "days_in_advance", "booking_lead_time", "advance_days", "days_before_arrival"],
    "occupancy_rate": ["occupancy", "occupancy_rate", "occ", "occ_rate", "room_occupancy"],
    "guests": ["guests", "pax", "adults", "children", "total_guests", "guest_count", "people"],
    "demand": ["demand", "arrivals", "tourist_arrivals", "international_arrivals", "visitors", "tourists", "searches", "impressions", "visitor_volume"],
    "event_date": ["holiday_date", "event_date", "public_holiday", "campaign_date", "festivity_date", "occasion_date"],
    "event_name": ["holiday_name", "event_name", "campaign_name", "event", "holiday", "occasion", "festivity", "name"],
    "rating": ["rating", "review_score", "score", "satisfaction", "nps", "guest_rating", "review_rating"],
    "cost": ["cost", "expense", "commission", "spend", "campaign_spend", "operating_cost"],
    "profit": ["profit", "margin", "gross_profit", "net_profit", "contribution", "contribution_margin"],
}

BOOKING_LIKE_ROLES = {
    "revenue", "adr", "room_nights", "bookings", "cancellation", "lead_time",
    "property", "room_type", "country", "segment", "channel", "customer_type", "guests", "occupancy_rate", "rating", "cost", "profit"
}

# ==========================================================
# HELPERS
# ==========================================================
def merged_layout(height: int, **overrides) -> Dict[str, Any]:
    layout = dict(**CHART_LAYOUT)
    layout.update(overrides)
    layout["height"] = height
    return layout


def chart(fig, height=340):
    fig.update_layout(**merged_layout(height))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def norm_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm_text(a), norm_text(b)).ratio()


def month_to_number(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        try:
            month_num = int(value)
            return month_num if 1 <= month_num <= 12 else np.nan
        except Exception:
            return np.nan
    text = str(value).strip()
    if text.isdigit():
        month_num = int(text)
        return month_num if 1 <= month_num <= 12 else np.nan
    lookup = {m.lower(): i for i, m in enumerate(MONTH_ORDER, start=1)}
    lookup.update({m[:3].lower(): i for i, m in enumerate(MONTH_ORDER, start=1)})
    return lookup.get(text.lower(), lookup.get(text.lower()[:3], np.nan))


def month_number_to_name(value):
    try:
        value = int(value)
        if 1 <= value <= 12:
            return MONTH_ORDER[value - 1]
    except Exception:
        pass
    return np.nan


def get_season(month_name):
    if pd.isna(month_name):
        return "Unknown"
    m = str(month_name).strip()
    if m in ["June", "July", "August"]:
        return "☀️ Summer"
    if m in ["March", "April", "May"]:
        return "🌸 Spring"
    if m in ["September", "October", "November"]:
        return "🍂 Autumn"
    if m in ["December", "January", "February"]:
        return "❄️ Winter"
    return "Unknown"


def to_number(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype=float)
    if series.dtype == "object":
        cleaned = (
            series.astype(str)
            .str.replace(r"[$€,]", "", regex=True)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        return pd.to_numeric(cleaned, errors="coerce")
    return pd.to_numeric(series, errors="coerce")


def normalize_cancel_flag(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() >= 0.70:
        return (numeric.fillna(0) > 0).astype(int)

    text = series.astype(str).str.strip().str.lower()
    not_cancelled = text.str.contains(
        r"not cancelled|not canceled|not cancel|no cancellation|confirmed|active|booked|checked.?in|stayed|completed",
        regex=True,
        na=False,
    )
    cancelled = text.str.contains(
        r"cancelled|canceled|cancel|no.?show|noshow|void|refunded",
        regex=True,
        na=False,
    ) & ~not_cancelled
    return cancelled.astype(int)


def money(value: float) -> str:
    if pd.isna(value):
        return "$0"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:,.1f}K"
    return f"${value:,.0f}"


def pct(value: float) -> str:
    if pd.isna(value):
        return "0.0%"
    return f"{value:,.1f}%"


def short_num(value: float) -> str:
    if pd.isna(value):
        return "0"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:,.1f}K"
    return f"{value:,.0f}"


def safe_div(n, d):
    return n / d if d not in [0, None] and not pd.isna(d) else np.nan


def first_existing(df: pd.DataFrame, roles: List[str]):
    for role in roles:
        if role in df.columns:
            return role
    return None


def get_role_label(role_key: str) -> str:
    return ROLE_INFO.get(role_key, (role_key, ""))[0]

# ==========================================================
# FILE READING
# ==========================================================
@st.cache_data(show_spinner=False)
def read_uploaded_file(file_bytes: bytes, file_name: str) -> Dict[str, pd.DataFrame]:
    lower_name = file_name.lower()
    if lower_name.endswith(".csv"):
        return {file_name: pd.read_csv(io.BytesIO(file_bytes))}

    if lower_name.endswith((".xlsx", ".xls")):
        sheets = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        clean_sheets = {}
        for sheet_name, df in sheets.items():
            if df is not None and not df.empty:
                dataset_name = file_name if len(sheets) == 1 else f"{file_name} / {sheet_name}"
                clean_sheets[dataset_name] = df
        return clean_sheets

    raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS files.")


def load_all_uploaded_files(uploaded_files) -> Tuple[List[Dict[str, Any]], List[str]]:
    datasets = []
    errors = []
    if not uploaded_files:
        return datasets, errors

    for uploaded in uploaded_files:
        try:
            read_result = read_uploaded_file(uploaded.getvalue(), uploaded.name)
            for dataset_name, df in read_result.items():
                # remove fully empty columns
                df = df.dropna(axis=1, how="all")
                datasets.append({
                    "key": dataset_name,
                    "name": dataset_name,
                    "source_file": uploaded.name,
                    "data": df,
                    "rows": len(df),
                    "cols": len(df.columns),
                })
        except Exception as exc:
            errors.append(f"{uploaded.name}: {exc}")
    return datasets, errors


def file_signature(datasets: List[Dict[str, Any]]) -> str:
    parts = []
    for item in datasets:
        df = item["data"]
        parts.append(f"{item['name']}|{len(df)}|{len(df.columns)}|{','.join(map(str, df.columns))}")
    return "||".join(parts)

# ==========================================================
# COLUMN ROLE GUESSING + MAPPING UI
# ==========================================================
def guess_column_role(column_name: str, series: pd.Series) -> Tuple[str, str]:
    col_norm = norm_text(column_name)

    # direct alias and contains matching
    for role, aliases in ROLE_ALIASES.items():
        alias_norms = [norm_text(a) for a in aliases]
        if col_norm in alias_norms:
            return role, "auto"
        if any(a and (a in col_norm or col_norm in a) for a in alias_norms if len(a) >= 4):
            return role, "auto"

    # data-type hints
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date", "auto"

    numeric = to_number(series)
    numeric_ratio = numeric.notna().mean() if len(series) else 0

    if numeric_ratio >= 0.80:
        lower_col = col_norm
        if "rate" in lower_col or "price" in lower_col or lower_col == "adr":
            return "adr", "fuzzy"
        if "revenue" in lower_col or "sales" in lower_col or "amount" in lower_col:
            return "revenue", "fuzzy"
        if "occup" in lower_col:
            return "occupancy_rate", "fuzzy"
        if "rating" in lower_col or "score" in lower_col:
            return "rating", "fuzzy"

    # fuzzy score
    best_role = "skip"
    best_score = 0.0
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            score = similarity(column_name, alias)
            if score > best_score:
                best_score = score
                best_role = role
    if best_score >= 0.78:
        return best_role, "fuzzy"

    return "skip", "none"


def render_mapping_form(datasets: List[Dict[str, Any]]):
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>🗂️ Confirm Column Meaning</h1>
        <p style='color:#5577AA;font-size:14px;'>
            The app does not assume your file structure. For each uploaded dataset, confirm what each column means.
            Columns can be skipped. The analysis will only use the meanings you confirm.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "working_mappings" not in st.session_state:
        st.session_state["working_mappings"] = {}

    with st.form("dynamic_mapping_form"):
        all_mappings = {}
        duplicate_role_warnings = []

        for dataset_idx, item in enumerate(datasets):
            df = item["data"]
            dataset_key = item["key"]

            if dataset_key not in st.session_state["working_mappings"]:
                st.session_state["working_mappings"][dataset_key] = {}
                for col in df.columns:
                    guessed_role, _ = guess_column_role(col, df[col])
                    st.session_state["working_mappings"][dataset_key][col] = guessed_role

            with st.expander(f"📄 {item['name']}  ·  {len(df):,} rows  ·  {len(df.columns)} columns", expanded=(dataset_idx == 0)):
                st.dataframe(df.head(8), use_container_width=True)

                st.markdown("<div class='section-header'>Column mapping</div>", unsafe_allow_html=True)
                st.caption("Choose a meaning for each column. Leave unrelated columns as 'Skip / not used'.")

                dataset_mapping = {}
                used_roles = []

                for col in df.columns:
                    guessed_role, confidence = guess_column_role(col, df[col])
                    current_role = st.session_state["working_mappings"][dataset_key].get(col, guessed_role)
                    current_label = f"{ROLE_LABELS.get(current_role, 'Skip / not used')}  ·  {current_role}"
                    default_index = ROLE_SELECT_OPTIONS.index(current_label) if current_label in ROLE_SELECT_OPTIONS else 0

                    c1, c2, c3 = st.columns([1.25, 1.5, 1.2])
                    with c1:
                        badge = ""
                        if confidence == "auto" and guessed_role != "skip":
                            badge = "<span class='auto-badge'>✅ suggested</span>"
                        elif confidence == "fuzzy" and guessed_role != "skip":
                            badge = "<span class='manual-badge'>⚠️ verify</span>"
                        else:
                            badge = "<span class='skip-badge'>manual</span>"
                        st.markdown(
                            f"<div style='padding-top:10px;color:#C8D8F0;font-size:13px;font-weight:600;'>{col}</div>{badge}",
                            unsafe_allow_html=True,
                        )
                    with c2:
                        selected = st.selectbox(
                            "Role",
                            ROLE_SELECT_OPTIONS,
                            index=default_index,
                            key=f"role_{dataset_key}_{col}",
                            label_visibility="collapsed",
                        )
                        role_key = ROLE_OPTION_TO_KEY[selected]
                        st.session_state["working_mappings"][dataset_key][col] = role_key
                        dataset_mapping[col] = role_key
                        if role_key != "skip":
                            used_roles.append(role_key)
                    with c3:
                        samples = df[col].dropna().head(3).astype(str).tolist()
                        sample_text = " · ".join(samples) if samples else "No sample"
                        st.markdown(
                            f"<div style='padding-top:10px;color:#5577AA;font-size:11px;'>Sample: {sample_text[:90]}</div>",
                            unsafe_allow_html=True,
                        )

                duplicated = sorted({r for r in used_roles if used_roles.count(r) > 1})
                if duplicated:
                    duplicate_role_warnings.append(
                        f"{item['name']}: duplicate mapped roles found ({', '.join(get_role_label(r) for r in duplicated)}). Please map each meaning only once per dataset."
                    )
                all_mappings[dataset_key] = dataset_mapping

        st.markdown("---")
        submitted = st.form_submit_button("✅ Confirm Mapping & Generate Analysis", use_container_width=True, type="primary")

        if submitted:
            if duplicate_role_warnings:
                for warning in duplicate_role_warnings:
                    st.error(warning)
                st.stop()
            total_mapped = sum(
                1 for mapping in all_mappings.values() for role in mapping.values() if role != "skip"
            )
            if total_mapped == 0:
                st.warning("Please map at least one column meaning before generating the dashboard.")
                st.stop()
            st.session_state["confirmed_mappings"] = all_mappings
            st.session_state["mapping_confirmed"] = True
            st.rerun()

    st.stop()

# ==========================================================
# DATA NORMALISATION BASED ON USER-CONFIRMED ROLES
# ==========================================================
def infer_dataset_type(roles: List[str]) -> str:
    role_set = set(roles)
    if role_set & BOOKING_LIKE_ROLES:
        return "commercial / booking-like"
    if "demand" in role_set:
        return "demand / market signal"
    if "event_date" in role_set or "event_name" in role_set:
        return "event / calendar signal"
    return "general hospitality data"


def standardise_dataset(item: Dict[str, Any], mapping: Dict[str, str]) -> pd.DataFrame:
    raw = item["data"].copy()
    roles_used = [role for role in mapping.values() if role != "skip"]
    dataset_type = infer_dataset_type(roles_used)

    std = pd.DataFrame(index=raw.index)
    std["_source_dataset"] = item["name"]
    std["_source_file"] = item["source_file"]
    std["_dataset_type"] = dataset_type

    # Map confirmed columns into role columns
    for col, role in mapping.items():
        if role == "skip" or col not in raw.columns:
            continue
        std[role] = raw[col]

    # Normalise dates
    for date_col in ["date", "event_date"]:
        if date_col in std.columns:
            std[date_col] = pd.to_datetime(std[date_col], errors="coerce")

    # Build analysis date from main date, then event date
    if "date" in std.columns:
        std["analysis_date"] = std["date"]
    elif "event_date" in std.columns:
        std["analysis_date"] = std["event_date"]
    else:
        std["analysis_date"] = pd.NaT

    # Normalise year / month
    if "year" in std.columns:
        std["year"] = pd.to_numeric(std["year"], errors="coerce")
    else:
        std["year"] = std["analysis_date"].dt.year

    if "month" in std.columns:
        std["month"] = std["month"].apply(month_to_number)
    else:
        std["month"] = std["analysis_date"].dt.month

    std["month_name"] = std["month"].apply(month_number_to_name)
    std["season"] = std["month_name"].apply(get_season)

    # Numeric roles
    numeric_roles = ["revenue", "adr", "room_nights", "bookings", "lead_time", "occupancy_rate", "guests", "demand", "rating", "cost", "profit"]
    for role in numeric_roles:
        if role in std.columns:
            std[role] = to_number(std[role])

    # Cancellation role
    if "cancellation" in std.columns:
        std["cancelled_flag"] = normalize_cancel_flag(std["cancellation"])
    else:
        std["cancelled_flag"] = np.nan

    # Record count: used for general row volume only
    std["record_count"] = 1

    # Booking count: only if mapped, otherwise row count for booking-like data
    if "bookings" in std.columns:
        std["booking_count"] = std["bookings"].fillna(0)
    elif dataset_type == "commercial / booking-like":
        std["booking_count"] = 1
    else:
        std["booking_count"] = np.nan

    # Estimate revenue when ADR and room nights are available but revenue is not
    if "revenue" not in std.columns and {"adr", "room_nights"}.issubset(std.columns):
        std["revenue"] = std["adr"].fillna(0) * std["room_nights"].fillna(1).clip(lower=1)

    if "revenue" in std.columns:
        std["confirmed_revenue"] = np.where(std["cancelled_flag"].fillna(0).eq(1), 0, std["revenue"].fillna(0))
        std["lost_revenue"] = np.where(std["cancelled_flag"].fillna(0).eq(1), std["revenue"].fillna(0), 0)
    else:
        std["confirmed_revenue"] = np.nan
        std["lost_revenue"] = np.nan

    return std


def build_standardised_data(datasets: List[Dict[str, Any]], mappings: Dict[str, Dict[str, str]]) -> pd.DataFrame:
    frames = []
    for item in datasets:
        mapping = mappings.get(item["key"], {})
        frames.append(standardise_dataset(item, mapping))
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()

# ==========================================================
# ANALYSIS DATASETS
# ==========================================================
def get_commercial_df(std: pd.DataFrame) -> pd.DataFrame:
    if std.empty:
        return std
    cdf = std[std["_dataset_type"].eq("commercial / booking-like")].copy()
    return cdf if not cdf.empty else std.copy()


def monthly_rollup(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "year" not in df.columns or "month" not in df.columns:
        return pd.DataFrame()
    valid = df[df["year"].notna() & df["month"].notna()].copy()
    if valid.empty:
        return pd.DataFrame()

    agg = {
        "records": ("record_count", "sum"),
    }
    if "booking_count" in valid.columns:
        agg["bookings"] = ("booking_count", "sum")
    if "revenue" in valid.columns:
        agg["revenue"] = ("revenue", "sum")
        agg["confirmed_revenue"] = ("confirmed_revenue", "sum")
        agg["lost_revenue"] = ("lost_revenue", "sum")
    if "adr" in valid.columns:
        agg["avg_adr"] = ("adr", "mean")
    if "demand" in valid.columns:
        agg["demand"] = ("demand", "sum")
    if "cancelled_flag" in valid.columns and valid["cancelled_flag"].notna().any():
        agg["cancelled"] = ("cancelled_flag", "sum")

    monthly = valid.groupby(["year", "month", "month_name"], dropna=False).agg(**agg).reset_index()
    monthly["sort_key"] = monthly["year"].fillna(0).astype(int) * 100 + monthly["month"].fillna(0).astype(int)
    if "bookings" in monthly.columns and "cancelled" in monthly.columns:
        monthly["cancel_rate"] = np.where(monthly["bookings"] > 0, monthly["cancelled"] / monthly["bookings"] * 100, np.nan)
    return monthly.sort_values("sort_key")


def quality_by_group(df: pd.DataFrame, group_col: str, min_records: int = 5) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame()
    valid = df[df[group_col].notna()].copy()
    if valid.empty:
        return pd.DataFrame()

    agg = {
        "records": ("record_count", "sum"),
    }
    if "booking_count" in valid.columns:
        agg["bookings"] = ("booking_count", "sum")
    if "revenue" in valid.columns:
        agg["revenue"] = ("revenue", "sum")
        agg["confirmed_revenue"] = ("confirmed_revenue", "sum")
        agg["lost_revenue"] = ("lost_revenue", "sum")
    if "adr" in valid.columns:
        agg["avg_adr"] = ("adr", "mean")
    if "cancelled_flag" in valid.columns and valid["cancelled_flag"].notna().any():
        agg["cancelled"] = ("cancelled_flag", "sum")
    if "demand" in valid.columns:
        agg["demand"] = ("demand", "sum")
    if "rating" in valid.columns:
        agg["avg_rating"] = ("rating", "mean")

    out = valid.groupby(group_col).agg(**agg).reset_index()
    out = out[out["records"] >= min_records]
    if "bookings" in out.columns and "cancelled" in out.columns:
        out["cancel_rate"] = np.where(out["bookings"] > 0, out["cancelled"] / out["bookings"] * 100, np.nan)
    if "revenue" in out.columns:
        out["revenue_m"] = out["revenue"] / 1_000_000
    return out.sort_values(out.columns[1], ascending=False)

# ==========================================================
# RENDER FUNCTIONS
# ==========================================================
def render_landing():
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem;'>
        <div style='font-size:64px;margin-bottom:1rem;'>🏨</div>
        <h1 style='color:#E0E6F0;font-size:36px;font-weight:800;margin-bottom:0.5rem;'>
            Hospitality Intelligence Studio
        </h1>
        <p style='color:#5577AA;font-size:18px;margin-bottom:2rem;'>
            Upload any hospitality-related data file. The dashboard will adapt based on the columns you confirm.
        </p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, desc in zip(
        [c1, c2, c3, c4],
        ["📁", "🗂️", "📊", "💡"],
        ["Any file count", "Any column names", "Dynamic analysis", "Auto insights"],
        ["Upload one or many files", "You confirm meaning", "Only relevant charts appear", "Based on uploaded data"]
    ):
        with col:
            st.markdown(f"""
            <div class='panel-card' style='text-align:center;min-height:130px;'>
                <div style='font-size:34px;margin-bottom:8px;'>{icon}</div>
                <div style='font-size:14px;color:#E0E6F0;font-weight:700;margin-bottom:6px;'>{title}</div>
                <div style='font-size:12px;color:#5577AA;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.info("Start by uploading one or more CSV / Excel files from the sidebar.")


def render_header(std: pd.DataFrame, datasets: List[Dict[str, Any]], mappings: Dict[str, Dict[str, str]]):
    commercial = get_commercial_df(std)
    mapped_roles = sorted({role for m in mappings.values() for role in m.values() if role != "skip"})
    date_min = std["analysis_date"].min() if "analysis_date" in std.columns else pd.NaT
    date_max = std["analysis_date"].max() if "analysis_date" in std.columns else pd.NaT

    st.markdown(
        f"<div style='margin-bottom:1.5rem;'>"
        f"<h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>🏨 Hospitality Intelligence Studio</h1>"
        f"<p style='color:#5577AA;font-size:14px;'>"
        f"<strong style='color:#7ABAFF'>{len(std):,}</strong> rows analysed from "
        f"<strong style='color:#7ABAFF'>{len(datasets)}</strong> uploaded dataset{'s' if len(datasets) != 1 else ''} · "
        f"<strong style='color:#22D47B'>{len(mapped_roles)}</strong> confirmed data meaning{'s' if len(mapped_roles) != 1 else ''}"
        f"</p></div>",
        unsafe_allow_html=True,
    )

    total_revenue = commercial["revenue"].sum(skipna=True) if "revenue" in commercial.columns else np.nan
    avg_adr = commercial["adr"].mean(skipna=True) if "adr" in commercial.columns else np.nan
    total_bookings = commercial["booking_count"].sum(skipna=True) if "booking_count" in commercial.columns else np.nan
    cancel_rate = np.nan
    if "cancelled_flag" in commercial.columns and commercial["cancelled_flag"].notna().any():
        denom = commercial["booking_count"].sum(skipna=True) if "booking_count" in commercial.columns else len(commercial)
        cancel_rate = safe_div(commercial["cancelled_flag"].sum(skipna=True), denom) * 100

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📁 Uploaded Datasets", f"{len(datasets):,}", f"{len(std):,} total rows")
    k2.metric("💰 Revenue", money(total_revenue) if not pd.isna(total_revenue) else "Not mapped")
    k3.metric("💳 ADR / Rate", f"${avg_adr:,.0f}" if not pd.isna(avg_adr) else "Not mapped")
    k4.metric("📋 Booking Volume", short_num(total_bookings) if not pd.isna(total_bookings) else "Not mapped")
    k5.metric("📉 Cancel Rate", pct(cancel_rate) if not pd.isna(cancel_rate) else "Not mapped")

    if pd.notna(date_min) and pd.notna(date_max):
        st.caption(f"Date range detected: **{date_min.date()}** to **{date_max.date()}**")


def render_overview(std: pd.DataFrame, datasets: List[Dict[str, Any]]):
    st.markdown('<div class="section-header">📁 Uploaded Data Overview</div>', unsafe_allow_html=True)
    file_rows = []
    for item in datasets:
        subset = std[std["_source_dataset"].eq(item["name"])]
        roles_present = [c for c in subset.columns if c in ROLE_INFO and subset[c].notna().any()]
        file_rows.append({
            "Dataset": item["name"],
            "Rows": f"{item['rows']:,}",
            "Columns": f"{item['cols']:,}",
            "Detected type": subset["_dataset_type"].iloc[0] if not subset.empty else "Unknown",
            "Confirmed meanings": ", ".join(get_role_label(r) for r in roles_present[:8]) + ("..." if len(roles_present) > 8 else ""),
        })
    st.dataframe(pd.DataFrame(file_rows), use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🧩 Dataset Type Mix</div>', unsafe_allow_html=True)
        type_df = std.groupby("_dataset_type").size().reset_index(name="rows")
        fig = px.pie(type_df, values="rows", names="_dataset_type", hole=0.55, color_discrete_sequence=COLORS)
        fig.update_traces(textinfo="percent+label", textfont_color="white")
        chart(fig, 320)

    with col2:
        st.markdown('<div class="section-header">🗂️ Confirmed Column Meanings</div>', unsafe_allow_html=True)
        role_counts = []
        for role in ROLE_INFO:
            if role != "skip" and role in std.columns:
                non_missing = int(std[role].notna().sum())
                if non_missing > 0:
                    role_counts.append({"Meaning": get_role_label(role), "Rows with value": non_missing})
        if role_counts:
            role_df = pd.DataFrame(role_counts).sort_values("Rows with value", ascending=True)
            fig = px.bar(role_df, x="Rows with value", y="Meaning", orientation="h", color="Rows with value", color_continuous_scale=[[0, "#0D1628"], [1, BLUE]])
            fig.update_layout(**merged_layout(320, coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No confirmed column meanings were found.")


def render_time_trends(std: pd.DataFrame):
    st.markdown('<div class="section-header">📅 Time-Based Trends</div>', unsafe_allow_html=True)
    monthly = monthly_rollup(std)
    if monthly.empty:
        st.info("Map a Date column, or Year and Month columns, to enable time-based analysis.")
        return

    monthly["month_label"] = monthly["month_name"].astype(str).str[:3] + " " + monthly["year"].astype(int).astype(str)

    y_candidates = [c for c in ["revenue", "bookings", "demand", "records", "avg_adr"] if c in monthly.columns]
    selected_metric = st.selectbox(
        "Choose trend metric",
        y_candidates,
        format_func=lambda c: {
            "revenue": "Revenue",
            "bookings": "Bookings / volume",
            "demand": "Demand / visitors",
            "records": "Record count",
            "avg_adr": "Average ADR / rate",
        }.get(c, c),
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month_label"],
        y=monthly[selected_metric],
        mode="lines+markers",
        line=dict(color=BLUE, width=3),
        marker=dict(size=8),
        name=selected_metric,
    ))
    if selected_metric == "revenue":
        fig.update_layout(**merged_layout(380, yaxis=dict(tickprefix="$", gridcolor="#1A2A45")))
    else:
        fig.update_layout(**merged_layout(380))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🌞 Season Mix</div>', unsafe_allow_html=True)
        season_metric = selected_metric if selected_metric in monthly.columns else "records"
        season_df = monthly.groupby("month_name", dropna=False)[season_metric].sum().reset_index()
        season_df["season"] = season_df["month_name"].apply(get_season)
        season_sum = season_df.groupby("season")[season_metric].sum().reset_index()
        fig2 = px.pie(season_sum, values=season_metric, names="season", hole=0.55, color_discrete_sequence=COLORS)
        fig2.update_traces(textinfo="percent+label", textfont_color="white")
        chart(fig2, 320)
    with col2:
        st.markdown('<div class="section-header">📊 Monthly Summary</div>', unsafe_allow_html=True)
        display = monthly[[c for c in ["year", "month_name", "records", "bookings", "demand", "revenue", "avg_adr", "cancel_rate"] if c in monthly.columns]].copy()
        for c in ["revenue"]:
            if c in display.columns:
                display[c] = display[c].map(money)
        if "avg_adr" in display.columns:
            display["avg_adr"] = display["avg_adr"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
        if "cancel_rate" in display.columns:
            display["cancel_rate"] = display["cancel_rate"].map(pct)
        st.dataframe(display, use_container_width=True, hide_index=True)


def render_revenue_pricing(std: pd.DataFrame):
    commercial = get_commercial_df(std)
    has_revenue = "revenue" in commercial.columns and commercial["revenue"].notna().any()
    has_adr = "adr" in commercial.columns and commercial["adr"].notna().any()
    if not has_revenue and not has_adr:
        st.info("Map Revenue or ADR / Rate columns to enable commercial analysis.")
        return

    st.markdown('<div class="section-header">💰 Revenue & Pricing Analysis</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    if has_revenue:
        cols[0].metric("Total Revenue", money(commercial["revenue"].sum(skipna=True)))
        cols[1].metric("Avg Revenue / Row", money(commercial["revenue"].mean(skipna=True)))
    if has_adr:
        cols[2].metric("Average ADR / Rate", f"${commercial['adr'].mean(skipna=True):,.0f}")
        cols[3].metric("Median ADR / Rate", f"${commercial['adr'].median(skipna=True):,.0f}")

    group_options = [c for c in ["property", "room_type", "country", "segment", "channel", "customer_type", "season", "_source_dataset"] if c in commercial.columns]
    if group_options and has_revenue:
        selected_group = st.selectbox("Break revenue down by", group_options, format_func=lambda c: get_role_label(c) if c in ROLE_INFO else "Uploaded dataset")
        grouped = quality_by_group(commercial, selected_group, min_records=1).head(15)
        if not grouped.empty:
            grouped = grouped.sort_values("revenue", ascending=True)
            fig = px.bar(
                grouped,
                x="revenue",
                y=selected_group,
                orientation="h",
                color="revenue",
                color_continuous_scale=[[0, "#0D1628"], [1, BLUE]],
                text=grouped["revenue"].map(money),
            )
            fig.update_traces(textposition="outside", textfont=dict(color="#8899BB", size=11))
            fig.update_layout(**merged_layout(420, xaxis=dict(tickprefix="$", gridcolor="#1A2A45"), coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if has_adr and has_revenue and "booking_count" in commercial.columns:
        st.markdown('<div class="section-header">📌 Pricing vs Volume</div>', unsafe_allow_html=True)
        group_col = first_existing(commercial, ["property", "room_type", "segment", "channel", "country", "_source_dataset"])
        if group_col:
            scatter_df = quality_by_group(commercial, group_col, min_records=2)
            if not scatter_df.empty and "avg_adr" in scatter_df.columns:
                fig = px.scatter(
                    scatter_df,
                    x="avg_adr",
                    y="revenue_m",
                    size="records",
                    color="records",
                    hover_name=group_col,
                    color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, PURPLE]],
                    labels={"avg_adr": "Average ADR / Rate", "revenue_m": "Revenue ($M)", "records": "Rows"},
                )
                chart(fig, 420)


def render_booking_risk(std: pd.DataFrame):
    commercial = get_commercial_df(std)
    if "cancelled_flag" not in commercial.columns or not commercial["cancelled_flag"].notna().any():
        st.info("Map a Cancellation Status column to enable cancellation/risk analysis.")
        return

    st.markdown('<div class="section-header">📉 Cancellation & Booking Risk</div>', unsafe_allow_html=True)
    total_rows = len(commercial)
    cancelled = commercial["cancelled_flag"].sum(skipna=True)
    cancel_rate = safe_div(cancelled, total_rows) * 100
    lost_revenue = commercial["lost_revenue"].sum(skipna=True) if "lost_revenue" in commercial.columns else np.nan

    a, b, c = st.columns(3)
    a.metric("Cancelled Rows", f"{cancelled:,.0f}")
    b.metric("Cancellation Rate", pct(cancel_rate))
    c.metric("Revenue at Risk", money(lost_revenue) if not pd.isna(lost_revenue) else "Revenue not mapped")

    group_options = [c for c in ["property", "country", "segment", "channel", "customer_type", "room_type", "season", "_source_dataset"] if c in commercial.columns]
    if group_options:
        selected_group = st.selectbox("Compare cancellation by", group_options, format_func=lambda c: get_role_label(c) if c in ROLE_INFO else "Uploaded dataset")
        risk_df = quality_by_group(commercial, selected_group, min_records=1)
        if not risk_df.empty and "cancel_rate" in risk_df.columns:
            risk_df = risk_df.sort_values("cancel_rate", ascending=True).tail(15)
            fig = px.bar(
                risk_df,
                x="cancel_rate",
                y=selected_group,
                orientation="h",
                color="cancel_rate",
                color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]],
                text=risk_df["cancel_rate"].map(pct),
            )
            fig.update_traces(textposition="outside", textfont=dict(color="#E0E6F0"))
            fig.update_layout(**merged_layout(420, xaxis=dict(ticksuffix="%", gridcolor="#1A2A45"), coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_market_guest(std: pd.DataFrame):
    commercial = get_commercial_df(std)
    group_options = [c for c in ["property", "country", "segment", "channel", "customer_type", "room_type", "season", "_source_dataset"] if c in commercial.columns]
    if not group_options:
        st.info("Map categorical columns such as Property, Country/Market, Segment, Channel, Room Type, or Customer Type to enable this analysis.")
        return

    st.markdown('<div class="section-header">🌍 Market, Guest & Channel Analysis</div>', unsafe_allow_html=True)
    selected_group = st.selectbox("Choose category to analyse", group_options, format_func=lambda c: get_role_label(c) if c in ROLE_INFO else "Uploaded dataset")
    group_df = quality_by_group(commercial, selected_group, min_records=1).head(15)

    if group_df.empty:
        st.warning("No values available for the selected category.")
        return

    metric_options = [c for c in ["revenue", "records", "bookings", "demand", "avg_adr", "avg_rating", "cancel_rate"] if c in group_df.columns]
    metric = st.selectbox("Choose metric", metric_options, format_func=lambda c: {
        "revenue": "Revenue",
        "records": "Record count",
        "bookings": "Bookings / volume",
        "demand": "Demand / visitors",
        "avg_adr": "Average ADR / rate",
        "avg_rating": "Average rating",
        "cancel_rate": "Cancellation rate",
    }.get(c, c))

    chart_df = group_df.sort_values(metric, ascending=True).tail(15)
    fig = px.bar(
        chart_df,
        x=metric,
        y=selected_group,
        orientation="h",
        color=metric,
        color_continuous_scale=[[0, "#0D1628"], [1, BLUE]],
    )
    if metric == "revenue":
        fig.update_layout(**merged_layout(440, xaxis=dict(tickprefix="$", gridcolor="#1A2A45"), coloraxis_showscale=False))
    elif metric == "cancel_rate":
        fig.update_layout(**merged_layout(440, xaxis=dict(ticksuffix="%", gridcolor="#1A2A45"), coloraxis_showscale=False))
    else:
        fig.update_layout(**merged_layout(440, coloraxis_showscale=False))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header">📋 Category Summary</div>', unsafe_allow_html=True)
    display_cols = [selected_group] + [c for c in ["records", "bookings", "revenue", "avg_adr", "cancel_rate", "demand", "avg_rating"] if c in group_df.columns]
    display = group_df[display_cols].copy()
    if "revenue" in display.columns:
        display["revenue"] = display["revenue"].map(money)
    if "avg_adr" in display.columns:
        display["avg_adr"] = display["avg_adr"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
    if "cancel_rate" in display.columns:
        display["cancel_rate"] = display["cancel_rate"].map(pct)
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_demand_events(std: pd.DataFrame):
    st.markdown('<div class="section-header">📊 Demand & Event Signals</div>', unsafe_allow_html=True)

    has_demand = "demand" in std.columns and std["demand"].notna().any()
    has_events = ("event_date" in std.columns and std["event_date"].notna().any()) or ("event_name" in std.columns and std["event_name"].notna().any())

    if not has_demand and not has_events:
        st.info("Map Demand / Visitors / Arrivals or Event / Holiday columns to enable this analysis.")
        return

    if has_demand:
        demand_df = std[std["demand"].notna()].copy()
        monthly = monthly_rollup(demand_df)
        if not monthly.empty and "demand" in monthly.columns:
            monthly["month_label"] = monthly["month_name"].astype(str).str[:3] + " " + monthly["year"].astype(int).astype(str)
            fig = px.bar(monthly, x="month_label", y="demand", color="demand", color_continuous_scale=[[0, "#0D1628"], [1, CYAN]])
            fig.update_layout(**merged_layout(380, coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if has_events:
        st.markdown('<div class="section-header">🎉 Event / Calendar Data</div>', unsafe_allow_html=True)
        event_df = std[(std.get("event_date", pd.Series(index=std.index)).notna()) | (std.get("event_name", pd.Series(index=std.index)).notna())].copy()
        display_cols = [c for c in ["event_date", "event_name", "_source_dataset"] if c in event_df.columns]
        st.dataframe(event_df[display_cols].head(50), use_container_width=True, hide_index=True)

        commercial = get_commercial_df(std)
        if "date" in commercial.columns and commercial["date"].notna().any() and "event_date" in event_df.columns:
            st.markdown('<div class="section-header">📌 Commercial Rows Near Events</div>', unsafe_allow_html=True)
            days = st.slider("Event window days", min_value=1, max_value=30, value=7)
            events = event_df[[c for c in ["event_date", "event_name"] if c in event_df.columns]].dropna(subset=["event_date"]).sort_values("event_date")
            commercial_sorted = commercial[commercial["date"].notna()].sort_values("date").copy()
            if not events.empty and not commercial_sorted.empty:
                merged = pd.merge_asof(
                    commercial_sorted,
                    events,
                    left_on="date",
                    right_on="event_date",
                    direction="nearest",
                    tolerance=pd.Timedelta(days=days),
                )
                merged["near_event"] = merged["event_date"].notna()
                compare_metric = "revenue" if "revenue" in merged.columns else "record_count"
                compare = merged.groupby("near_event").agg(
                    rows=("record_count", "sum"),
                    metric=(compare_metric, "sum"),
                ).reset_index()
                compare["date_type"] = np.where(compare["near_event"], f"Within ±{days} days of event", "Other dates")
                fig = px.bar(compare, x="date_type", y="metric", color="date_type", color_discrete_sequence=[BLUE, AMBER])
                yaxis = dict(tickprefix="$", gridcolor="#1A2A45") if compare_metric == "revenue" else dict(gridcolor="#1A2A45")
                fig.update_layout(**merged_layout(320, yaxis=yaxis, showlegend=False))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_data_quality(std: pd.DataFrame, datasets: List[Dict[str, Any]]):
    st.markdown('<div class="section-header">🧪 Data Quality & Profiling</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(std):,}")
    c2.metric("Uploaded datasets", f"{len(datasets):,}")
    c3.metric("Mapped columns", f"{len([c for c in std.columns if c in ROLE_INFO]):,}")
    c4.metric("Date rows", f"{int(std['analysis_date'].notna().sum()):,}" if "analysis_date" in std.columns else "0")

    st.markdown('<div class="section-header">Missing Values by Confirmed Meaning</div>', unsafe_allow_html=True)
    quality_rows = []
    for role in [c for c in std.columns if c in ROLE_INFO]:
        missing_pct = std[role].isna().mean() * 100
        quality_rows.append({
            "Meaning": get_role_label(role),
            "Non-null rows": int(std[role].notna().sum()),
            "Missing %": f"{missing_pct:.1f}%",
        })
    if quality_rows:
        st.dataframe(pd.DataFrame(quality_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No mapped columns to profile.")

    st.markdown('<div class="section-header">Raw Dataset Preview</div>', unsafe_allow_html=True)
    selected = st.selectbox("Select uploaded dataset", [d["name"] for d in datasets])
    raw_df = next(d["data"] for d in datasets if d["name"] == selected)
    st.dataframe(raw_df.head(50), use_container_width=True)


def render_insights(std: pd.DataFrame):
    st.markdown('<div class="section-header">💡 Auto-Generated Insights</div>', unsafe_allow_html=True)
    commercial = get_commercial_df(std)
    insights = []

    if "revenue" in commercial.columns and commercial["revenue"].notna().any():
        total_revenue = commercial["revenue"].sum(skipna=True)
        insights.append((BLUE, "Revenue Base", f"Total mapped revenue is **{money(total_revenue)}** across uploaded commercial rows."))

        for group_col in ["property", "country", "segment", "channel", "room_type", "customer_type"]:
            if group_col in commercial.columns:
                q = quality_by_group(commercial, group_col, min_records=1)
                if not q.empty and "revenue" in q.columns:
                    top = q.sort_values("revenue", ascending=False).iloc[0]
                    insights.append((GREEN, f"Top {get_role_label(group_col)}", f"**{top[group_col]}** contributes the highest mapped revenue at **{money(top['revenue'])}**."))
                    break

    if "cancelled_flag" in commercial.columns and commercial["cancelled_flag"].notna().any():
        cancel_rate = commercial["cancelled_flag"].sum(skipna=True) / max(len(commercial), 1) * 100
        insights.append((RED if cancel_rate >= 30 else AMBER, "Cancellation Signal", f"Mapped cancellation rate is **{pct(cancel_rate)}**. Review high-risk segments/channels if this is above your business tolerance."))

    if "adr" in commercial.columns and commercial["adr"].notna().any():
        avg_adr = commercial["adr"].mean(skipna=True)
        high_adr = commercial["adr"].quantile(0.90)
        insights.append((AMBER, "Pricing Range", f"Average mapped ADR/rate is **${avg_adr:,.0f}**; top 10% rate level starts around **${high_adr:,.0f}**."))

    if "demand" in std.columns and std["demand"].notna().any():
        monthly = monthly_rollup(std[std["demand"].notna()])
        if not monthly.empty and "demand" in monthly.columns:
            top_demand = monthly.sort_values("demand", ascending=False).iloc[0]
            insights.append((CYAN, "Demand Peak", f"Highest mapped demand appears in **{top_demand['month_name']} {int(top_demand['year'])}** with **{short_num(top_demand['demand'])}** demand volume."))

    if "event_name" in std.columns and std["event_name"].notna().any():
        event_count = std["event_name"].dropna().nunique()
        insights.append((PURPLE, "Event Calendar", f"The uploaded data contains **{event_count}** unique mapped events/holidays/campaigns that can support calendar-based planning."))

    if not insights:
        st.info("Map more column meanings to generate richer automated insights.")
        return

    for color, title, text in insights:
        st.markdown(f"""
        <div class='insight-card' style='border-left:4px solid {color};'>
            <div class='insight-title'>{title}</div>
            <div class='insight-desc' style='font-size:13px;color:#C8D8F0;'>{text}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# SIDEBAR + APP FLOW
# ==========================================================
with st.sidebar:
    st.markdown("## 🏨 Hospitality\nIntelligence Studio")
    st.markdown("---")
    st.markdown("### 📂 Upload Data")
    st.caption("Upload one or more hospitality-related CSV / Excel files. No file name or file type is fixed.")

    uploaded_files = st.file_uploader(
        "Upload your files",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="You can upload one or many files. The app will ask you to confirm column meanings before analysis.",
    )

# Empty initial page
if not uploaded_files:
    render_landing()
    st.stop()

# Read user-uploaded files only
datasets, load_errors = load_all_uploaded_files(uploaded_files)
if load_errors:
    for err in load_errors:
        st.sidebar.warning(err)

if not datasets:
    render_landing()
    st.warning("No valid data was loaded. Please upload CSV, XLSX, or XLS files.")
    st.stop()

# Reset mapping if the uploaded data changes
current_signature = file_signature(datasets)
if st.session_state.get("file_signature") != current_signature:
    st.session_state["file_signature"] = current_signature
    st.session_state["mapping_confirmed"] = False
    st.session_state.pop("confirmed_mappings", None)
    st.session_state.pop("working_mappings", None)

with st.sidebar:
    st.markdown("---")
    st.markdown("### ✅ Uploaded")
    for item in datasets:
        st.markdown(f"<span class='file-badge'>📄 {item['name']}</span>", unsafe_allow_html=True)
    st.success(f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} loaded")

    if st.button("🗂️ Re-confirm Column Meanings", use_container_width=True):
        st.session_state["mapping_confirmed"] = False
        st.session_state.pop("confirmed_mappings", None)
        st.rerun()

# Mapping screen before any analysis
if not st.session_state.get("mapping_confirmed", False):
    render_mapping_form(datasets)

mappings = st.session_state.get("confirmed_mappings", {})
std = build_standardised_data(datasets, mappings)

if std.empty:
    st.warning("No data available after applying your mapping.")
    st.stop()

# Sidebar filters, generated only from available mapped roles
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎛 Dynamic Filters")

    filtered = std.copy()

    if "year" in filtered.columns and filtered["year"].notna().any():
        years = sorted(filtered["year"].dropna().astype(int).unique().tolist())
        selected_years = st.multiselect("Year", years, default=years)
        if selected_years:
            filtered = filtered[filtered["year"].astype("Int64").isin(selected_years)]

    for role in ["_source_dataset", "property", "country", "segment", "channel", "customer_type", "room_type", "season"]:
        if role in filtered.columns and filtered[role].notna().any():
            values = sorted(filtered[role].dropna().astype(str).unique().tolist())
            if 1 < len(values) <= 80:
                selected_values = st.multiselect(
                    get_role_label(role) if role in ROLE_INFO else "Uploaded dataset",
                    values,
                    default=values,
                )
                if selected_values:
                    filtered = filtered[filtered[role].astype(str).isin(selected_values)]

    st.markdown("---")
    st.markdown("<p style='font-size:11px;color:#334466;text-align:center;'>Dynamic hospitality analytics · upload-based only</p>", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No data available after applying filters.")
    st.stop()

render_header(filtered, datasets, mappings)
st.markdown("---")

# Create tabs only when relevant
modules = [("📁 Overview", lambda: render_overview(filtered, datasets))]

if filtered["analysis_date"].notna().any() or ("year" in filtered.columns and "month" in filtered.columns):
    modules.append(("📅 Trends", lambda: render_time_trends(filtered)))

if any(c in filtered.columns and filtered[c].notna().any() for c in ["revenue", "adr", "profit", "cost"]):
    modules.append(("💰 Commercial", lambda: render_revenue_pricing(filtered)))

if "cancelled_flag" in filtered.columns and filtered["cancelled_flag"].notna().any():
    modules.append(("📉 Risk", lambda: render_booking_risk(filtered)))

if any(c in filtered.columns and filtered[c].notna().any() for c in ["property", "country", "segment", "channel", "customer_type", "room_type"]):
    modules.append(("🌍 Categories", lambda: render_market_guest(filtered)))

if any(c in filtered.columns and filtered[c].notna().any() for c in ["demand", "event_date", "event_name"]):
    modules.append(("📊 Signals", lambda: render_demand_events(filtered)))

modules.append(("🧪 Data Quality", lambda: render_data_quality(filtered, datasets)))
modules.append(("💡 Insights", lambda: render_insights(filtered)))

tabs = st.tabs([title for title, _ in modules])
for tab, (_, render_func) in zip(tabs, modules):
    with tab:
        render_func()
