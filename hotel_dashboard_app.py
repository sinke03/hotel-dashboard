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
    "deposit_policy":       ("Deposit / Refund Policy", "Deposit type, refund policy, prepaid / non-refundable indicator"),
    "repeat_guest":         ("Repeat Guest", "Returning guest, loyalty guest, repeat customer flag"),
    "previous_cancellations": ("Previous Cancellations", "Past cancellation count or prior cancellation indicator"),
    "booking_status":       ("Reservation Status", "Check-out / cancelled / no-show / reservation status"),
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
    "deposit_policy": ["deposit_type", "deposit", "refund_policy", "payment_policy", "cancellation_policy", "prepayment", "non_refund", "non_refundable", "non refund"],
    "repeat_guest": ["is_repeated_guest", "repeat_guest", "repeated_guest", "returning_guest", "loyal_guest", "loyalty_guest", "guest_repeat"],
    "previous_cancellations": ["previous_cancellations", "prior_cancellations", "past_cancellations", "historic_cancellations", "cancellation_history"],
    "booking_status": ["reservation_status", "booking_status", "status", "reservation_state", "booking_state"],
}

BOOKING_LIKE_ROLES = {
    "revenue", "adr", "room_nights", "bookings", "cancellation", "lead_time",
    "property", "room_type", "country", "segment", "channel", "customer_type", "guests", "occupancy_rate", "rating", "cost", "profit",
    "deposit_policy", "repeat_guest", "previous_cancellations", "booking_status"
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
    tokens = set(col_norm.split("_"))

    # Guardrails: these are historical counters, not current booking volume.
    # They should not be confused with “Bookings / Orders”.
    if col_norm in {"previous_bookings_not_canceled", "previous_bookings_not_cancelled", "past_bookings_not_canceled", "past_bookings_not_cancelled"}:
        return "skip", "none"

    # 1) Exact aliases across ALL roles first. This prevents broad words such as
    # "arrival" or "date" from stealing columns like international_arrivals or holiday_date.
    for role, aliases in ROLE_ALIASES.items():
        alias_norms = [norm_text(a) for a in aliases]
        if col_norm in alias_norms:
            return role, "auto"

    # 2) High-confidence role-specific patterns.
    if "demand_tier" in col_norm or col_norm.endswith("_tier"):
        return "skip", "none"
    if "international_arrivals" in col_norm or "tourist_arrivals" in col_norm or col_norm in {"arrivals", "visitors", "tourists"}:
        return "demand", "auto"
    if col_norm.startswith("holiday_") or col_norm.endswith("_holiday_date") or col_norm in {"event_date", "campaign_date"}:
        return "event_date", "auto"
    if col_norm.startswith("holiday_name") or col_norm in {"event_name", "campaign_name"}:
        return "event_name", "auto"
    if "deposit" in tokens or "deposit" in col_norm or "refund" in col_norm:
        return "deposit_policy", "auto"
    if "previous" in tokens and "cancellation" in col_norm:
        return "previous_cancellations", "auto"
    if ("repeat" in col_norm or "repeated" in col_norm or "returning" in col_norm) and "guest" in col_norm:
        return "repeat_guest", "auto"

    # 3) Careful contains matching. Only match on meaningful whole tokens or
    # role-safe substrings, not broad words like date/arrival/name/year/month.
    unsafe_contains_aliases = {"date", "arrival", "name", "year", "month", "booking", "bookings", "count", "status", "source", "demand"}
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            alias_norm = norm_text(alias)
            if len(alias_norm) < 4 or alias_norm in unsafe_contains_aliases:
                continue
            if alias_norm in tokens or col_norm.endswith("_" + alias_norm) or col_norm.startswith(alias_norm + "_"):
                return role, "auto"

    # data-type hints
    if pd.api.types.is_datetime64_any_dtype(series):
        # Holiday/event-looking datetime columns become event dates; otherwise general dates.
        if "holiday" in col_norm or "event" in col_norm or "campaign" in col_norm:
            return "event_date", "auto"
        return "date", "auto"

    numeric = to_number(series)
    numeric_ratio = numeric.notna().mean() if len(series) else 0

    if numeric_ratio >= 0.80:
        lower_col = col_norm
        if lower_col in {"year", "yr"} or lower_col.endswith("_year"):
            return "year", "auto"
        if lower_col in {"month", "mo"} or lower_col.endswith("_month"):
            return "month", "auto"
        if "arrival" in lower_col or "visitor" in lower_col or "tourist" in lower_col or lower_col == "demand":
            return "demand", "auto"
        if "rate" in lower_col or "price" in lower_col or lower_col == "adr":
            return "adr", "fuzzy"
        if "revenue" in lower_col or "sales" in lower_col or "amount" in lower_col:
            return "revenue", "fuzzy"
        if "occup" in lower_col:
            return "occupancy_rate", "fuzzy"
        if "rating" in lower_col or "score" in lower_col:
            return "rating", "fuzzy"
        if "night" in lower_col or lower_col in {"los", "length_of_stay"}:
            return "room_nights", "fuzzy"

    # fuzzy score, but reject weak broad matches.
    best_role = "skip"
    best_score = 0.0
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            alias_norm = norm_text(alias)
            if alias_norm in unsafe_contains_aliases:
                continue
            score = similarity(column_name, alias)
            if score > best_score:
                best_score = score
                best_role = role
    if best_score >= 0.82:
        return best_role, "fuzzy"

    return "skip", "none"


def raw_upload_signature(uploaded_files) -> str:
    """Create a lightweight signature before reading file contents."""
    if not uploaded_files:
        return ""
    return "||".join(
        f"{getattr(file, 'name', '')}|{getattr(file, 'size', 0)}|{getattr(file, 'type', '')}"
        for file in uploaded_files
    )


def render_upload_confirmation(uploaded_files):
    """Show uploaded file list first, then ask user to confirm before processing."""
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>📂 Confirm Uploaded Files</h1>
        <p style='color:#5577AA;font-size:14px;'>
            The app will only start reading and processing the files after you confirm.
            Make sure the uploaded files are hospitality-related and the column names are already prepared.
        </p>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for file in uploaded_files:
        rows.append({
            "File name": file.name,
            "File type": file.type or "Unknown",
            "Size": f"{getattr(file, 'size', 0) / 1024:,.1f} KB",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.info("After confirmation, the app will process the files and show a column preview for your final check.")
    if st.button("✅ Confirm Uploaded Files", use_container_width=True, type="primary"):
        st.session_state["upload_confirmed"] = True
        st.session_state["columns_confirmed"] = False
        st.session_state.pop("confirmed_mappings", None)
        st.rerun()

    st.stop()


def build_auto_mappings(datasets: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    """
    Automatically detect the meaning of each column based only on the uploaded column names and values.
    Users do not manually map or rename inside the app.
    """
    all_mappings = {}

    for item in datasets:
        df = item["data"]
        dataset_mapping = {}
        used_roles = set()

        for col in df.columns:
            guessed_role, confidence = guess_column_role(col, df[col])

            # Keep only one column per role per dataset to prevent accidental overwriting.
            # If a duplicate role is detected, the later column is skipped.
            if guessed_role != "skip" and guessed_role in used_roles:
                dataset_mapping[col] = "skip"
                continue

            dataset_mapping[col] = guessed_role
            if guessed_role != "skip":
                used_roles.add(guessed_role)

        all_mappings[item["key"]] = dataset_mapping

    return all_mappings


def render_column_preview_confirmation(datasets: List[Dict[str, Any]], auto_mappings: Dict[str, Dict[str, str]]):
    """
    Preview uploaded data and detected column meanings.
    No manual column mapping is shown; users only confirm that their uploaded column names are correct.
    """
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>🗂️ Preview Data Columns</h1>
        <p style='color:#5577AA;font-size:14px;'>
            Check the uploaded columns below. The app will analyse the data using the detected hospitality meanings.
            If something looks wrong, rename the column in your file and upload again.
        </p>
    </div>
    """, unsafe_allow_html=True)

    total_detected = 0

    for dataset_idx, item in enumerate(datasets):
        df = item["data"]
        mapping = auto_mappings.get(item["key"], {})

        with st.expander(f"📄 {item['name']}  ·  {len(df):,} rows  ·  {len(df.columns)} columns", expanded=(dataset_idx == 0)):
            st.markdown("<div class='section-header'>Data preview</div>", unsafe_allow_html=True)
            st.dataframe(df.head(8), use_container_width=True)

            st.markdown("<div class='section-header'>Column preview</div>", unsafe_allow_html=True)
            column_rows = []
            for col in df.columns:
                guessed_role, confidence = guess_column_role(col, df[col])
                final_role = mapping.get(col, "skip")
                if final_role != "skip":
                    total_detected += 1

                samples = df[col].dropna().head(3).astype(str).tolist()
                sample_text = " · ".join(samples) if samples else "No sample"

                column_rows.append({
                    "Column name": col,
                    "Detected meaning": get_role_label(final_role) if final_role != "skip" else "Not used / not recognised",
                    "Status": "Suggested" if final_role != "skip" and confidence in ["auto", "fuzzy"] else "Ignored",
                    "Sample values": sample_text[:120],
                })

            st.dataframe(pd.DataFrame(column_rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    if total_detected == 0:
        st.error(
            "No hospitality-related columns were recognised. Please rename the columns in your file "
            "using clearer names such as date, revenue, ADR, bookings, channel, country, occupancy, rating, or demand, then upload again."
        )
        st.stop()

    st.success(f"✅ {total_detected} column meaning{'s' if total_detected != 1 else ''} detected across the uploaded data.")

    if st.button("✅ Confirm Columns & Generate Analysis", use_container_width=True, type="primary"):
        st.session_state["confirmed_mappings"] = auto_mappings
        st.session_state["columns_confirmed"] = True
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
    numeric_roles = ["revenue", "adr", "room_nights", "bookings", "lead_time", "occupancy_rate", "guests", "demand", "rating", "cost", "profit", "previous_cancellations"]
    for role in numeric_roles:
        if role in std.columns:
            std[role] = to_number(std[role])

    # Cancellation role
    if "cancellation" in std.columns:
        std["cancelled_flag"] = normalize_cancel_flag(std["cancellation"])
    elif "booking_status" in std.columns:
        std["cancelled_flag"] = normalize_cancel_flag(std["booking_status"])
    else:
        std["cancelled_flag"] = np.nan

    if "repeat_guest" in std.columns:
        # Re-use cancellation normalizer only for numeric/text yes-no behaviour by interpreting >0/yes/true as repeat.
        num_repeat = pd.to_numeric(std["repeat_guest"], errors="coerce")
        if num_repeat.notna().mean() >= 0.70:
            std["repeat_guest_flag"] = num_repeat.fillna(0).gt(0).astype(int)
        else:
            std["repeat_guest_flag"] = std["repeat_guest"].astype(str).str.lower().str.strip().isin(["1", "yes", "y", "true", "repeat", "repeated", "returning", "loyal"]).astype(int)
    else:
        std["repeat_guest_flag"] = np.nan

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
# MORE ADAPTIVE DATASET-BASED ANALYSIS
# ==========================================================
def get_raw_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Detect usable column groups directly from the uploaded data, not only from mapped roles."""
    numeric_cols, date_cols, categorical_cols = [], [], []
    for col in df.columns:
        s = df[col]
        if s.dropna().empty:
            continue
        numeric = to_number(s)
        numeric_ratio = numeric.notna().mean()
        parsed_date = pd.to_datetime(s, errors="coerce")
        date_ratio = parsed_date.notna().mean()
        unique_count = s.nunique(dropna=True)
        non_null = int(s.notna().sum())

        if date_ratio >= 0.70 and unique_count > 1:
            date_cols.append(col)
        elif numeric_ratio >= 0.70:
            numeric_cols.append(col)
        elif unique_count <= min(80, max(20, non_null * 0.30)):
            categorical_cols.append(col)
    return {"numeric": numeric_cols, "date": date_cols, "categorical": categorical_cols}


def get_detected_role_columns(mapping: Dict[str, str]) -> Dict[str, str]:
    """Convert mapping from raw column -> role into role -> raw column for display."""
    role_cols = {}
    for raw_col, role in mapping.items():
        if role != "skip" and role not in role_cols:
            role_cols[role] = raw_col
    return role_cols


def readable_dataset_name(name: str, max_len: int = 24) -> str:
    name = str(name)
    return name if len(name) <= max_len else name[:max_len-3] + "..."


def render_adaptive_dataset_profile(item: Dict[str, Any], mapping: Dict[str, str]):
    df = item["data"].copy()
    col_types = get_raw_column_types(df)
    role_cols = get_detected_role_columns(mapping)

    st.markdown(f"<div class='section-header'>🧠 Analysis plan for {item['name']}</div>", unsafe_allow_html=True)
    plan_rows = []
    if col_types["date"]:
        plan_rows.append({"Detected data feature": "Date/time columns", "What the app will analyse": "Time trend, seasonality, month-by-month movement", "Columns used": ", ".join(map(str, col_types["date"][:5]))})
    if col_types["numeric"]:
        plan_rows.append({"Detected data feature": "Numeric columns", "What the app will analyse": "KPI totals, averages, distribution, ranking, correlation", "Columns used": ", ".join(map(str, col_types["numeric"][:8]))})
    if col_types["categorical"]:
        plan_rows.append({"Detected data feature": "Categorical columns", "What the app will analyse": "Top categories, contribution mix, segment comparison", "Columns used": ", ".join(map(str, col_types["categorical"][:8]))})
    if role_cols:
        plan_rows.append({"Detected data feature": "Hospitality meanings", "What the app will analyse": "Hospitality-specific revenue, pricing, risk or demand logic", "Columns used": ", ".join(f"{get_role_label(r)} = {c}" for r, c in list(role_cols.items())[:8])})
    if plan_rows:
        st.dataframe(pd.DataFrame(plan_rows), use_container_width=True, hide_index=True)
    else:
        st.warning("The app could not confidently detect numeric/date/category patterns. It will show profiling only.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{len(df.columns):,}")
    c3.metric("Numeric fields", f"{len(col_types['numeric']):,}")
    c4.metric("Category fields", f"{len(col_types['categorical']):,}")

    with st.expander("👀 Raw data preview", expanded=False):
        st.dataframe(df.head(50), use_container_width=True)

    return col_types, role_cols


def render_adaptive_time_analysis(df: pd.DataFrame, col_types: Dict[str, List[str]], role_cols: Dict[str, str], dataset_key: str):
    if not col_types["date"]:
        return
    numeric_cols = col_types["numeric"]
    if not numeric_cols:
        return

    st.markdown("<div class='section-header'>📅 Time movement based on uploaded date columns</div>", unsafe_allow_html=True)
    default_date = role_cols.get("date") if role_cols.get("date") in col_types["date"] else col_types["date"][0]
    default_metric = None
    for preferred_role in ["revenue", "adr", "bookings", "demand", "occupancy_rate", "rating", "cost", "profit"]:
        candidate = role_cols.get(preferred_role)
        if candidate in numeric_cols:
            default_metric = candidate
            break
    if default_metric is None:
        default_metric = numeric_cols[0]

    date_col = st.selectbox("Date column", col_types["date"], index=col_types["date"].index(default_date), key=f"adaptive_date_{dataset_key}")
    metric_col = st.selectbox("Metric to trend", numeric_cols, index=numeric_cols.index(default_metric), key=f"adaptive_metric_time_{dataset_key}")

    temp = df[[date_col, metric_col]].copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp[metric_col] = to_number(temp[metric_col])
    temp = temp.dropna(subset=[date_col, metric_col])
    if temp.empty:
        st.info("No valid date + metric values available for trend analysis.")
        return
    temp["period"] = temp[date_col].dt.to_period("M").dt.to_timestamp()
    monthly = temp.groupby("period", as_index=False)[metric_col].sum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["period"], y=monthly[metric_col], mode="lines+markers", line=dict(color=BLUE, width=3), marker=dict(size=8)))
    yaxis = dict(tickprefix="$", gridcolor="#1A2A45") if any(word in norm_text(metric_col) for word in ["revenue", "sales", "amount", "rate", "price", "adr", "cost", "profit"]) else dict(gridcolor="#1A2A45")
    fig.update_layout(**merged_layout(380, yaxis=yaxis))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Auto insight based on actual chosen metric
    if len(monthly) >= 2:
        peak = monthly.loc[monthly[metric_col].idxmax()]
        low = monthly.loc[monthly[metric_col].idxmin()]
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Time trend insight</div>
            <div class='insight-desc' style='font-size:13px;color:#C8D8F0;'>
                <strong>{metric_col}</strong> peaks in <strong>{peak['period'].strftime('%b %Y')}</strong> and is lowest in <strong>{low['period'].strftime('%b %Y')}</strong>.
                This is generated from the uploaded column <strong>{date_col}</strong>, not from a fixed template.
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_adaptive_category_analysis(df: pd.DataFrame, col_types: Dict[str, List[str]], role_cols: Dict[str, str], dataset_key: str):
    if not col_types["categorical"]:
        return
    st.markdown("<div class='section-header'>🧩 Category contribution based on uploaded category columns</div>", unsafe_allow_html=True)

    numeric_cols = col_types["numeric"]
    default_cat = None
    for preferred_role in ["property", "country", "segment", "channel", "customer_type", "room_type", "event_name"]:
        candidate = role_cols.get(preferred_role)
        if candidate in col_types["categorical"]:
            default_cat = candidate
            break
    if default_cat is None:
        default_cat = col_types["categorical"][0]

    cat_col = st.selectbox("Category to analyse", col_types["categorical"], index=col_types["categorical"].index(default_cat), key=f"adaptive_cat_{dataset_key}")

    if numeric_cols:
        default_metric = None
        for preferred_role in ["revenue", "adr", "bookings", "demand", "occupancy_rate", "rating", "cost", "profit", "guests"]:
            candidate = role_cols.get(preferred_role)
            if candidate in numeric_cols:
                default_metric = candidate
                break
        if default_metric is None:
            default_metric = numeric_cols[0]
        metric_col = st.selectbox("Metric for category comparison", numeric_cols, index=numeric_cols.index(default_metric), key=f"adaptive_metric_cat_{dataset_key}")
        temp = df[[cat_col, metric_col]].copy()
        temp[metric_col] = to_number(temp[metric_col])
        temp = temp.dropna(subset=[cat_col, metric_col])
        if temp.empty:
            st.info("No valid category + metric values available.")
            return
        grouped = temp.groupby(cat_col, dropna=False)[metric_col].sum().reset_index().sort_values(metric_col, ascending=True).tail(15)
        fig = px.bar(grouped, x=metric_col, y=cat_col, orientation="h", color=metric_col, color_continuous_scale=[[0, "#0D1628"], [1, BLUE]])
        fig.update_layout(**merged_layout(430, coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        top = grouped.sort_values(metric_col, ascending=False).iloc[0]
        total = grouped[metric_col].sum()
        share = safe_div(top[metric_col], total) * 100 if total else np.nan
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Category insight</div>
            <div class='insight-desc' style='font-size:13px;color:#C8D8F0;'>
                <strong>{top[cat_col]}</strong> is the strongest category for <strong>{metric_col}</strong>
                {f'with {pct(share)} of the displayed top-category total' if not pd.isna(share) else ''}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        counts = df[cat_col].dropna().astype(str).value_counts().head(15).reset_index()
        counts.columns = [cat_col, "rows"]
        fig = px.bar(counts.sort_values("rows"), x="rows", y=cat_col, orientation="h", color="rows", color_continuous_scale=[[0, "#0D1628"], [1, CYAN]])
        fig.update_layout(**merged_layout(430, coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_adaptive_numeric_analysis(df: pd.DataFrame, col_types: Dict[str, List[str]], role_cols: Dict[str, str], dataset_key: str):
    if not col_types["numeric"]:
        return
    st.markdown("<div class='section-header'>📊 Numeric profile from uploaded measures</div>", unsafe_allow_html=True)
    numeric_cols = col_types["numeric"]
    profile_rows = []
    for col in numeric_cols[:20]:
        s = to_number(df[col])
        if s.notna().any():
            profile_rows.append({
                "Column": col,
                "Total": short_num(s.sum(skipna=True)),
                "Average": short_num(s.mean(skipna=True)),
                "Median": short_num(s.median(skipna=True)),
                "Min": short_num(s.min(skipna=True)),
                "Max": short_num(s.max(skipna=True)),
                "Missing %": f"{s.isna().mean()*100:.1f}%",
            })
    if profile_rows:
        st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)

    selected_num = st.selectbox("View distribution for", numeric_cols, key=f"adaptive_dist_{dataset_key}")
    s = to_number(df[selected_num]).dropna()
    if not s.empty:
        fig = px.histogram(s.to_frame(name=selected_num), x=selected_num, nbins=30)
        fig.update_layout(**merged_layout(330, yaxis=dict(gridcolor="#1A2A45")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if len(numeric_cols) >= 2:
        st.markdown("<div class='section-header'>🔗 Relationship between numeric columns</div>", unsafe_allow_html=True)
        corr_df = pd.DataFrame({col: to_number(df[col]) for col in numeric_cols[:12]}).dropna(how="all")
        corr = corr_df.corr(numeric_only=True)
        if not corr.empty:
            fig = px.imshow(corr, text_auto='.2f', aspect="auto", color_continuous_scale="RdBu", zmin=-1, zmax=1)
            fig.update_layout(**merged_layout(430))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_hospitality_specific_analysis(df: pd.DataFrame, role_cols: Dict[str, str], dataset_key: str):
    """Only appears when hospitality meanings are detected. Content changes based on available roles."""
    available_roles = set(role_cols.keys())
    if not available_roles:
        return

    sections = []
    if {"revenue", "adr"} & available_roles:
        sections.append("commercial performance")
    if "cancellation" in available_roles:
        sections.append("booking risk")
    if {"country", "segment", "channel", "customer_type", "property", "room_type"} & available_roles:
        sections.append("market/category mix")
    if {"demand", "event_date", "event_name"} & available_roles:
        sections.append("demand/event signal")
    if {"rating", "guests", "occupancy_rate"} & available_roles:
        sections.append("guest/operation signal")
    if not sections:
        return

    st.markdown("<div class='section-header'>🏨 Hospitality-specific interpretation</div>", unsafe_allow_html=True)
    st.caption("This section is generated only from hospitality meanings detected in the uploaded columns.")

    cards = []
    if "revenue" in role_cols:
        revenue_col = role_cols["revenue"]
        revenue = to_number(df[revenue_col]).sum(skipna=True)
        cards.append((BLUE, "Revenue detected", f"The file contains a revenue-like column <strong>{revenue_col}</strong> with total value <strong>{money(revenue)}</strong>."))
    if "adr" in role_cols:
        adr_col = role_cols["adr"]
        avg_adr = to_number(df[adr_col]).mean(skipna=True)
        cards.append((AMBER, "Rate / ADR detected", f"Average value of <strong>{adr_col}</strong> is <strong>${avg_adr:,.0f}</strong>, useful for pricing and rate comparison."))
    if "cancellation" in role_cols:
        can_col = role_cols["cancellation"]
        flags = normalize_cancel_flag(df[can_col])
        cards.append((RED if flags.mean() >= 0.30 else GREEN, "Cancellation signal", f"Column <strong>{can_col}</strong> suggests a cancellation/no-show rate of <strong>{pct(flags.mean()*100)}</strong>."))
    if "demand" in role_cols:
        demand_col = role_cols["demand"]
        demand = to_number(df[demand_col]).sum(skipna=True)
        cards.append((CYAN, "Demand signal", f"Column <strong>{demand_col}</strong> provides demand/visitor volume with total <strong>{short_num(demand)}</strong>."))
    if "rating" in role_cols:
        rating_col = role_cols["rating"]
        avg_rating = to_number(df[rating_col]).mean(skipna=True)
        cards.append((PURPLE, "Guest experience signal", f"Column <strong>{rating_col}</strong> has average score <strong>{avg_rating:,.2f}</strong>, useful for service quality analysis."))

    for color, title, desc in cards:
        st.markdown(f"""
        <div class='insight-card' style='border-left:4px solid {color};'>
            <div class='insight-title'>{title}</div>
            <div class='insight-desc' style='font-size:13px;color:#C8D8F0;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)


def render_dataset_adaptive_analysis(item: Dict[str, Any], mappings: Dict[str, Dict[str, str]]):
    """One genuinely adaptive analysis page per uploaded dataset."""
    df = item["data"].copy()
    mapping = mappings.get(item["key"], {})
    col_types, role_cols = render_adaptive_dataset_profile(item, mapping)

    render_hospitality_specific_analysis(df, role_cols, item["key"])
    render_adaptive_time_analysis(df, col_types, role_cols, item["key"])
    render_adaptive_category_analysis(df, col_types, role_cols, item["key"])
    render_adaptive_numeric_analysis(df, col_types, role_cols, item["key"])

    st.markdown("<div class='section-header'>🧪 Data quality based on this file</div>", unsafe_allow_html=True)
    missing = df.isna().mean().mul(100).sort_values(ascending=False).reset_index()
    missing.columns = ["Column", "Missing %"]
    missing = missing[missing["Missing %"] > 0].head(20)
    if not missing.empty:
        fig = px.bar(missing.sort_values("Missing %"), x="Missing %", y="Column", orientation="h", color="Missing %", color_continuous_scale=[[0, GREEN], [1, RED]])
        fig.update_layout(**merged_layout(360, xaxis=dict(ticksuffix="%", gridcolor="#1A2A45"), coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.success("No missing values detected in this dataset.")


def render_cross_dataset_adaptive_analysis(std: pd.DataFrame, datasets: List[Dict[str, Any]], mappings: Dict[str, Dict[str, str]]):
    st.markdown("<div class='section-header'>🔗 Cross-dataset adaptive comparison</div>", unsafe_allow_html=True)
    st.caption("This page compares only metrics that are actually detected across the uploaded files.")

    rows = []
    for item in datasets:
        subset = std[std["_source_dataset"].eq(item["name"])]
        mapping = mappings.get(item["key"], {})
        role_cols = get_detected_role_columns(mapping)
        row = {
            "Dataset": item["name"],
            "Rows": len(subset),
            "Detected type": subset["_dataset_type"].iloc[0] if not subset.empty and "_dataset_type" in subset.columns else "Unknown",
            "Detected meanings": ", ".join(get_role_label(r) for r in role_cols.keys()) or "No recognised hospitality meaning",
        }
        for metric in ["revenue", "adr", "bookings", "demand", "rating", "occupancy_rate", "cost", "profit"]:
            if metric in subset.columns and subset[metric].notna().any():
                if metric in ["adr", "rating", "occupancy_rate"]:
                    row[get_role_label(metric)] = subset[metric].mean(skipna=True)
                else:
                    row[get_role_label(metric)] = subset[metric].sum(skipna=True)
        rows.append(row)
    compare = pd.DataFrame(rows)
    st.dataframe(compare, use_container_width=True, hide_index=True)

    numeric_compare_cols = [c for c in compare.columns if c not in ["Dataset", "Detected type", "Detected meanings"] and pd.api.types.is_numeric_dtype(compare[c])]
    if numeric_compare_cols:
        metric = st.selectbox("Choose detected cross-dataset metric", numeric_compare_cols, key="cross_dataset_metric")
        fig = px.bar(compare, x="Dataset", y=metric, color=metric, color_continuous_scale=[[0, "#0D1628"], [1, BLUE]])
        fig.update_layout(**merged_layout(380, coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No common numeric hospitality metrics were detected for cross-dataset comparison.")


# ==========================================================
# ADAPTIVE HOSPITALITY PLAYBOOK ENGINE
# ----------------------------------------------------------
# This is the “training” layer. It does not hardcode file names or require
# exactly 3 files. It watches for business patterns in the uploaded columns
# and only activates analyses when the needed signals exist.
# ==========================================================
def role_available(df: pd.DataFrame, role: str) -> bool:
    return role in df.columns and df[role].notna().any()


def commercial_rows(std: pd.DataFrame) -> pd.DataFrame:
    if std.empty:
        return std
    mask = std["_dataset_type"].eq("commercial / booking-like") if "_dataset_type" in std.columns else pd.Series(False, index=std.index)
    if mask.any():
        return std[mask].copy()
    # Fallback: any rows with booking/revenue/ADR/category signals are commercial-like
    cols = [c for c in ["revenue", "adr", "booking_count", "cancelled_flag", "property", "country", "segment", "channel"] if c in std.columns]
    if cols:
        return std[std[cols].notna().any(axis=1)].copy()
    return pd.DataFrame()


def monthly_business_bridge(std: pd.DataFrame) -> pd.DataFrame:
    """Build a month-level bridge across uploaded files: commercial metrics + demand signals."""
    pieces = []
    comm = commercial_rows(std)
    if not comm.empty and {"year", "month"}.issubset(comm.columns):
        valid = comm[comm["year"].notna() & comm["month"].notna()].copy()
        if not valid.empty:
            agg = {"records": ("record_count", "sum")}
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
            comm_m = valid.groupby(["year", "month", "month_name"], dropna=False).agg(**agg).reset_index()
            pieces.append(comm_m)

    if "demand" in std.columns and {"year", "month"}.issubset(std.columns):
        demand_valid = std[std["demand"].notna() & std["year"].notna() & std["month"].notna()].copy()
        if not demand_valid.empty:
            dem_m = demand_valid.groupby(["year", "month"], dropna=False).agg(demand=("demand", "sum")).reset_index()
            if pieces:
                out = pieces[0].merge(dem_m, on=["year", "month"], how="outer")
            else:
                out = dem_m.copy()
                out["month_name"] = out["month"].apply(month_number_to_name)
            out["month_name"] = out["month_name"].where(out["month_name"].notna(), out["month"].apply(month_number_to_name))
            out["sort_key"] = out["year"].fillna(0).astype(int) * 100 + out["month"].fillna(0).astype(int)
            if "bookings" in out.columns and "demand" in out.columns:
                out["capture_index"] = np.where(out["demand"] > 0, out["bookings"] / out["demand"] * 100, np.nan)
            if "avg_adr" in out.columns and "demand" in out.columns:
                out["demand_rank"] = out["demand"].rank(pct=True) * 100
                out["adr_rank"] = out["avg_adr"].rank(pct=True) * 100
                out["pricing_gap"] = out["demand_rank"] - out["adr_rank"]
            if "bookings" in out.columns and "cancelled" in out.columns:
                out["cancel_rate"] = np.where(out["bookings"] > 0, out["cancelled"] / out["bookings"] * 100, np.nan)
            return out.sort_values("sort_key")

    if pieces:
        out = pieces[0]
        out["sort_key"] = out["year"].fillna(0).astype(int) * 100 + out["month"].fillna(0).astype(int)
        if "bookings" in out.columns and "cancelled" in out.columns:
            out["cancel_rate"] = np.where(out["bookings"] > 0, out["cancelled"] / out["bookings"] * 100, np.nan)
        return out.sort_values("sort_key")

    return pd.DataFrame()


def group_quality(df: pd.DataFrame, group_col: str, min_rows: int = 5) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame()
    valid = df[df[group_col].notna()].copy()
    if valid.empty:
        return pd.DataFrame()
    agg = {"rows": ("record_count", "sum")}
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
    if "repeat_guest_flag" in valid.columns and valid["repeat_guest_flag"].notna().any():
        agg["repeat_guests"] = ("repeat_guest_flag", "sum")
    if "previous_cancellations" in valid.columns:
        agg["avg_previous_cancellations"] = ("previous_cancellations", "mean")

    out = valid.groupby(group_col, dropna=False).agg(**agg).reset_index()
    out = out[out["rows"] >= min_rows]
    if "bookings" in out.columns and "cancelled" in out.columns:
        out["cancel_rate"] = np.where(out["bookings"] > 0, out["cancelled"] / out["bookings"] * 100, np.nan)
    elif "cancelled" in out.columns:
        out["cancel_rate"] = np.where(out["rows"] > 0, out["cancelled"] / out["rows"] * 100, np.nan)
    if "revenue" in out.columns:
        out["revenue_m"] = out["revenue"] / 1_000_000
        denom = out["bookings"] if "bookings" in out.columns else out["rows"]
        out["effective_revenue_per_booking"] = np.where(denom > 0, out.get("confirmed_revenue", out["revenue"]) / denom, np.nan)
    return out


def story_card(color: str, title: str, text: str):
    st.markdown(f"""
    <div class='insight-card' style='border-left:4px solid {color};'>
        <div class='insight-title'>{title}</div>
        <div class='insight-desc' style='font-size:13px;color:#C8D8F0;'>{text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_playbook_cancellation(std: pd.DataFrame):
    comm = commercial_rows(std)
    if comm.empty or not role_available(comm, "cancelled_flag"):
        return False
    st.markdown('<div class="section-header">🚨 Revenue Leakage & Cancellation Risk</div>', unsafe_allow_html=True)
    total_rows = len(comm)
    cancelled = comm["cancelled_flag"].sum(skipna=True)
    cancel_rate = safe_div(cancelled, total_rows) * 100
    lost = comm["lost_revenue"].sum(skipna=True) if role_available(comm, "lost_revenue") else np.nan
    confirmed = comm["confirmed_revenue"].sum(skipna=True) if role_available(comm, "confirmed_revenue") else np.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cancelled rows", f"{cancelled:,.0f}")
    c2.metric("Cancel rate", pct(cancel_rate))
    c3.metric("Revenue lost", money(lost) if pd.notna(lost) else "Revenue not mapped")
    c4.metric("Confirmed revenue", money(confirmed) if pd.notna(confirmed) else "Revenue not mapped")

    monthly = monthly_business_bridge(std)
    if not monthly.empty and {"confirmed_revenue", "lost_revenue"}.issubset(monthly.columns):
        monthly = monthly.dropna(subset=["year", "month"]).copy()
        monthly["month_label"] = monthly["month_name"].astype(str).str[:3] + " " + monthly["year"].astype(int).astype(str)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Confirmed revenue", x=monthly["month_label"], y=monthly["confirmed_revenue"], marker=dict(color=BLUE, opacity=0.85)))
        fig.add_trace(go.Bar(name="Lost revenue", x=monthly["month_label"], y=monthly["lost_revenue"], marker=dict(color=RED, opacity=0.80)))
        fig.update_layout(**merged_layout(390, barmode="group", yaxis=dict(tickprefix="$", gridcolor="#1A2A45")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        peak = monthly.sort_values("lost_revenue", ascending=False).iloc[0]
        story_card(RED, "Peak exposure month", f"The highest cancellation revenue exposure appears in <strong>{peak['month_name']} {int(peak['year'])}</strong> with <strong>{money(peak['lost_revenue'])}</strong> in mapped lost revenue.")

    risk_groups = [g for g in ["deposit_policy", "channel", "segment", "country", "customer_type", "property", "room_type"] if g in comm.columns]
    if risk_groups:
        group_col = st.selectbox("Find high-risk groups by", risk_groups, format_func=lambda c: get_role_label(c), key="playbook_cancel_group")
        q = group_quality(comm, group_col, min_rows=5)
        if not q.empty and "cancel_rate" in q.columns:
            q = q.sort_values("cancel_rate", ascending=True).tail(12)
            fig = px.bar(q, x="cancel_rate", y=group_col, orientation="h", color="cancel_rate", color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]], text=q["cancel_rate"].map(pct))
            fig.update_traces(textposition="outside", textfont=dict(color="#E0E6F0"))
            fig.update_layout(**merged_layout(380, xaxis=dict(ticksuffix="%", gridcolor="#1A2A45"), coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            worst = q.sort_values("cancel_rate", ascending=False).iloc[0]
            story_card(AMBER, "Action trigger", f"<strong>{worst[group_col]}</strong> has the highest detected cancellation rate at <strong>{pct(worst['cancel_rate'])}</strong>. Apply stricter confirmation, deposit, or pre-arrival follow-up rules to this group.")
    return True


def render_playbook_pricing_demand(std: pd.DataFrame):
    bridge = monthly_business_bridge(std)
    if bridge.empty or not ({"avg_adr", "demand"}.issubset(bridge.columns) or {"revenue", "demand"}.issubset(bridge.columns)):
        return False
    st.markdown('<div class="section-header">💰 Pricing vs Real Demand</div>', unsafe_allow_html=True)
    bridge = bridge.dropna(subset=["year", "month"]).copy()
    bridge["month_label"] = bridge["month_name"].astype(str).str[:3] + " " + bridge["year"].astype(int).astype(str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(name="Demand / arrivals", x=bridge["month_label"], y=bridge["demand"], marker=dict(color=CYAN, opacity=0.45)), secondary_y=False)
    y_metric = "avg_adr" if "avg_adr" in bridge.columns else "revenue"
    fig.add_trace(go.Scatter(name="ADR" if y_metric == "avg_adr" else "Revenue", x=bridge["month_label"], y=bridge[y_metric], mode="lines+markers", line=dict(color=AMBER if y_metric == "avg_adr" else BLUE, width=3)), secondary_y=True)
    fig.update_yaxes(title_text="Demand / arrivals", secondary_y=False)
    fig.update_yaxes(title_text="ADR" if y_metric == "avg_adr" else "Revenue", tickprefix="$" if y_metric in ["avg_adr", "revenue"] else "", secondary_y=True)
    fig.update_layout(**merged_layout(410))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if "pricing_gap" in bridge.columns and bridge["pricing_gap"].notna().any():
        opp = bridge.sort_values("pricing_gap", ascending=False).head(5)
        best = opp.iloc[0]
        story_card(AMBER, "Underpriced demand window", f"<strong>{best['month_name']} {int(best['year'])}</strong> shows demand ranking higher than ADR ranking. This suggests a pricing or packaging review opportunity, not just a volume opportunity.")
        show = opp[[c for c in ["year", "month_name", "demand", "avg_adr", "pricing_gap", "capture_index"] if c in opp.columns]].copy()
        if "avg_adr" in show.columns:
            show["avg_adr"] = show["avg_adr"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
        if "capture_index" in show.columns:
            show["capture_index"] = show["capture_index"].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
        if "pricing_gap" in show.columns:
            show["pricing_gap"] = show["pricing_gap"].map(lambda x: f"{x:.1f}" if pd.notna(x) else "")
        st.dataframe(show, use_container_width=True, hide_index=True)
    return True


def render_playbook_market_quality(std: pd.DataFrame):
    comm = commercial_rows(std)
    if comm.empty:
        return False
    available_groups = [g for g in ["country", "channel", "segment", "customer_type", "property", "room_type"] if g in comm.columns]
    if not available_groups:
        return False
    st.markdown('<div class="section-header">🎯 Reliable Market, Guest & Channel Quality</div>', unsafe_allow_html=True)
    group_col = st.selectbox("Evaluate quality by", available_groups, format_func=lambda c: get_role_label(c), key="playbook_quality_group")
    q = group_quality(comm, group_col, min_rows=5)
    if q.empty:
        st.info("Not enough rows to compare this category.")
        return True

    if "revenue_m" in q.columns and "cancel_rate" in q.columns:
        fig = px.scatter(q, x="cancel_rate", y="revenue_m", size="rows", color="effective_revenue_per_booking" if "effective_revenue_per_booking" in q.columns else "rows", hover_name=group_col, color_continuous_scale=[[0, RED], [0.5, AMBER], [1, GREEN]], labels={"cancel_rate": "Cancellation rate (%)", "revenue_m": "Revenue ($M)"})
        fig.add_vline(x=q["cancel_rate"].median(), line_dash="dash", line_color="#5577AA")
        fig.add_hline(y=q["revenue_m"].median(), line_dash="dash", line_color="#5577AA")
        chart(fig, 430)
        reliable = q.dropna(subset=["cancel_rate", "revenue_m"]).sort_values(["cancel_rate", "revenue_m"], ascending=[True, False]).iloc[0]
        story_card(GREEN, "Reliable revenue target", f"<strong>{reliable[group_col]}</strong> combines lower cancellation risk with meaningful revenue contribution. This is a stronger target than looking at booking volume alone.")
    else:
        metric = "revenue" if "revenue" in q.columns else "rows"
        q2 = q.sort_values(metric, ascending=True).tail(15)
        fig = px.bar(q2, x=metric, y=group_col, orientation="h", color=metric, color_continuous_scale=[[0, "#0D1628"], [1, BLUE]])
        fig.update_layout(**merged_layout(390, coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    return True


def render_playbook_events(std: pd.DataFrame):
    comm = commercial_rows(std)
    if comm.empty or not role_available(comm, "date") or "event_date" not in std.columns or not std["event_date"].notna().any():
        return False
    st.markdown('<div class="section-header">🎉 Event / Holiday Impact</div>', unsafe_allow_html=True)
    days = st.slider("Event window days", min_value=1, max_value=30, value=7, key="playbook_event_days")
    events = std[std["event_date"].notna()][[c for c in ["event_date", "event_name"] if c in std.columns]].dropna(subset=["event_date"]).sort_values("event_date")
    commercial_sorted = comm[comm["date"].notna()].sort_values("date").copy()
    if events.empty or commercial_sorted.empty:
        st.info("Event dates or commercial dates are not available after filtering.")
        return True
    merged = pd.merge_asof(commercial_sorted, events, left_on="date", right_on="event_date", direction="nearest", tolerance=pd.Timedelta(days=days))
    merged["near_event"] = merged["event_date"].notna()
    metric = "revenue" if "revenue" in merged.columns else "record_count"
    compare = merged.groupby("near_event").agg(rows=("record_count", "sum"), metric=(metric, "sum")).reset_index()
    compare["date_type"] = np.where(compare["near_event"], f"Within ±{days} days of event", "Other dates")
    fig = px.bar(compare, x="date_type", y="metric", color="date_type", color_discrete_sequence=[BLUE, AMBER], text=compare["metric"].map(money if metric == "revenue" else short_num))
    fig.update_layout(**merged_layout(340, yaxis=dict(tickprefix="$" if metric == "revenue" else "", gridcolor="#1A2A45"), showlegend=False))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if "event_name" in merged.columns:
        near = merged[merged["near_event"]].copy()
        if not near.empty:
            top = near.groupby("event_name").agg(rows=("record_count", "sum"), metric=(metric, "sum")).reset_index().sort_values("rows", ascending=False).head(8)
            st.dataframe(top.rename(columns={"rows": "Rows near event", "metric": "Revenue" if metric == "revenue" else "Rows"}), use_container_width=True, hide_index=True)
    return True


def render_playbook_loyalty(std: pd.DataFrame):
    comm = commercial_rows(std)
    if comm.empty or not (role_available(comm, "repeat_guest_flag") or role_available(comm, "previous_cancellations")):
        return False
    st.markdown('<div class="section-header">🤝 Loyalty & Prior Behaviour</div>', unsafe_allow_html=True)
    if role_available(comm, "repeat_guest_flag"):
        temp = comm.copy()
        temp["guest_status"] = np.where(temp["repeat_guest_flag"].fillna(0).eq(1), "Repeat guest", "New / non-repeat guest")
        q = group_quality(temp, "guest_status", min_rows=1)
        if not q.empty:
            metric = "cancel_rate" if "cancel_rate" in q.columns else "rows"
            fig = px.bar(q, x="guest_status", y=metric, color=metric, color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]])
            fig.update_layout(**merged_layout(330, yaxis=dict(ticksuffix="%" if metric == "cancel_rate" else "", gridcolor="#1A2A45"), coloraxis_showscale=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if role_available(comm, "previous_cancellations") and role_available(comm, "cancelled_flag"):
        comm["prior_cancel_flag"] = np.where(comm["previous_cancellations"].fillna(0).gt(0), "Has previous cancellations", "No previous cancellations")
        q = group_quality(comm, "prior_cancel_flag", min_rows=1)
        if not q.empty and "cancel_rate" in q.columns:
            risky = q.sort_values("cancel_rate", ascending=False).iloc[0]
            story_card(RED, "Prior behaviour warning", f"<strong>{risky['prior_cancel_flag']}</strong> has cancellation rate of <strong>{pct(risky['cancel_rate'])}</strong>. Use this as an operational risk flag when available.")
    return True


def render_adaptive_hospitality_playbook(std: pd.DataFrame, datasets: List[Dict[str, Any]], mappings: Dict[str, Dict[str, str]]):
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D1628,#0A1A35);border:1px solid #1A2A45;
    border-radius:16px;padding:1.4rem 1.8rem;margin-bottom:1rem;'>
        <div style='font-size:20px;font-weight:800;color:#E0E6F0;margin-bottom:6px;'>🧠 Adaptive Hospitality Playbook</div>
        <div style='font-size:13px;color:#5577AA;line-height:1.6;'>
            The app chooses business questions based on the uploaded columns. It uses the same thinking pattern as a revenue-optimization deck — loss, demand, pricing, market quality, and recommendations — but it only shows sections that the current data can support.
        </div>
    </div>
    """, unsafe_allow_html=True)

    mapped_roles = sorted({role for m in mappings.values() for role in m.values() if role != "skip"})
    questions = []
    if "cancellation" in mapped_roles or "booking_status" in mapped_roles:
        questions.append("Are bookings turning into revenue, or leaking through cancellations?")
    if "adr" in mapped_roles and "demand" in mapped_roles:
        questions.append("Are rates aligned with real demand, or only with season assumptions?")
    if any(r in mapped_roles for r in ["country", "segment", "channel", "customer_type"]):
        questions.append("Which markets, channels, or guests are reliable instead of just high-volume?")
    if "event_date" in mapped_roles:
        questions.append("Do holidays/events create measurable pressure on booking or revenue behaviour?")
    if "repeat_guest" in mapped_roles or "previous_cancellations" in mapped_roles:
        questions.append("Does past guest behaviour explain current booking risk?")
    if not questions:
        questions.append("What are the strongest trends, categories, and outliers available in this uploaded data?")

    st.markdown('<div class="section-header">Business questions detected</div>', unsafe_allow_html=True)
    for q in questions:
        st.markdown(f"<p style='color:#C8D8F0;font-size:13px;margin-bottom:4px;'>→ {q}</p>", unsafe_allow_html=True)

    shown = []
    for title, fn in [
        ("Cancellation", render_playbook_cancellation),
        ("Pricing vs demand", render_playbook_pricing_demand),
        ("Market quality", render_playbook_market_quality),
        ("Events", render_playbook_events),
        ("Loyalty", render_playbook_loyalty),
    ]:
        try:
            if fn(std):
                shown.append(title)
        except Exception as exc:
            st.warning(f"Skipped {title} playbook due to data issue: {exc}")

    if not shown:
        st.info("The uploaded files do not contain enough recognised hospitality signals for the executive playbook yet. The dataset-level analysis tabs below will still profile the data dynamically.")

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

# Reset confirmation steps whenever the uploaded file set changes.
upload_signature = raw_upload_signature(uploaded_files)
if st.session_state.get("upload_signature") != upload_signature:
    st.session_state["upload_signature"] = upload_signature
    st.session_state["upload_confirmed"] = False
    st.session_state["columns_confirmed"] = False
    st.session_state.pop("confirmed_mappings", None)

# Step 1: user confirms uploaded files before the app reads/processes them.
if not st.session_state.get("upload_confirmed", False):
    render_upload_confirmation(uploaded_files)

# Step 2: read and process user-uploaded files only, with visible loading feedback.
with st.spinner("⏳ Processing uploaded files... please wait."):
    datasets, load_errors = load_all_uploaded_files(uploaded_files)

if load_errors:
    for err in load_errors:
        st.sidebar.warning(err)

if not datasets:
    render_landing()
    st.warning("No valid data was loaded. Please upload CSV, XLSX, or XLS files.")
    st.stop()

# Reset column confirmation if file content/columns changed after processing.
current_signature = file_signature(datasets)
if st.session_state.get("file_signature") != current_signature:
    st.session_state["file_signature"] = current_signature
    st.session_state["columns_confirmed"] = False
    st.session_state.pop("confirmed_mappings", None)

with st.sidebar:
    st.markdown("---")
    st.markdown("### ✅ Uploaded")
    for item in datasets:
        st.markdown(f"<span class='file-badge'>📄 {item['name']}</span>", unsafe_allow_html=True)
    st.success(f"{len(datasets)} dataset{'s' if len(datasets) != 1 else ''} loaded")

    if st.button("🔄 Re-check Uploaded Columns", use_container_width=True):
        st.session_state["columns_confirmed"] = False
        st.session_state.pop("confirmed_mappings", None)
        st.rerun()

# Step 3: preview columns only. No manual mapping or column fixing inside the app.
auto_mappings = build_auto_mappings(datasets)
if not st.session_state.get("columns_confirmed", False):
    render_column_preview_confirmation(datasets, auto_mappings)

mappings = st.session_state.get("confirmed_mappings", auto_mappings)

# Step 4: build standardised analysis data with loading feedback.
with st.spinner("📊 Generating dynamic hospitality analysis..."):
    std = build_standardised_data(datasets, mappings)

if std.empty:
    st.warning("No data available after processing your uploaded files.")
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

    for role in ["_source_dataset", "property", "country", "segment", "channel", "customer_type", "room_type", "deposit_policy", "season"]:
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

# Create tabs from the uploaded datasets, not from a fixed analysis template.
modules = [("📁 Overview", lambda: render_overview(filtered, datasets))]
modules.append(("🧠 Playbook", lambda: render_adaptive_hospitality_playbook(filtered, datasets, mappings)))

for item in datasets:
    title = "📄 " + readable_dataset_name(item["name"], 20)
    modules.append((title, lambda item=item: render_dataset_adaptive_analysis(item, mappings)))

if len(datasets) > 1:
    modules.append(("🔗 Cross-Dataset", lambda: render_cross_dataset_adaptive_analysis(filtered, datasets, mappings)))

# These final two are still dynamic because they are generated from the mapped/detected columns.
modules.append(("💡 Smart Insights", lambda: render_insights(filtered)))
modules.append(("🧪 Data Quality", lambda: render_data_quality(filtered, datasets)))

tabs = st.tabs([title for title, _ in modules])
for tab, (_, render_func) in zip(tabs, modules):
    with tab:
        render_func()
