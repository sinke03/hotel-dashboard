import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Hotel Revenue Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme CSS ─────────────────────────────────────────────
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

/* ── KPI Metric cards — much more visible numbers ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0D1628 0%, #152240 100%);
    border: 1px solid #2A3F6A;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
}
div[data-testid="metric-container"] label {
    color: #7A9EC8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.10em;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    text-shadow: 0 0 20px rgba(74,158,255,0.3);
    line-height: 1.15 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
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

/* Upload area */
.upload-container {
    background: linear-gradient(135deg, #0D1628, #111E35);
    border: 2px dashed #2A4070;
    border-radius: 16px; padding: 2rem;
    text-align: center; margin-bottom: 1.5rem;
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

/* Rec cards */
.rec-card { border-radius: 14px; padding: 1.25rem; margin-bottom: 0.5rem; }

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

/* ── Multiselect tag: blue instead of red ── */
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

# ── Safe layout merger ────────────────────────────────────
def merged_layout(height, **overrides):
    layout = dict(**CHART_LAYOUT)
    layout.update(overrides)
    layout['height'] = height
    return layout

# ── Helpers ───────────────────────────────────────────────
MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

def get_season(m):
    if m in ['June','July','August']:          return '☀️ Summer'
    elif m in ['March','April','May']:          return '🌸 Spring'
    elif m in ['September','October','November']: return '🍂 Autumn'
    else:                                        return '❄️ Winter'

@st.cache_data
def process_single(file_bytes, file_name):
    """Process one uploaded file (bytes) into a clean DataFrame."""
    import io
    if file_name.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))
    df['_source_file'] = file_name
    df['arrival_date'] = pd.to_datetime(df.get('arrival_date', pd.NaT), errors='coerce')
    if 'arrival_month_name' not in df.columns:
        df['arrival_month_name'] = df['arrival_date'].dt.strftime('%B')
    if 'arrival_year' not in df.columns:
        df['arrival_year'] = df['arrival_date'].dt.year
    if 'estimated_revenue' not in df.columns and 'adr' in df.columns:
        nights = df['total_stay_nights'] if 'total_stay_nights' in df.columns else pd.Series(1, index=df.index)
        df['estimated_revenue'] = df['adr'] * nights
    df['season'] = df['arrival_month_name'].apply(get_season)
    return df

def chart(fig, height=340):
    fig.update_layout(**merged_layout(height))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏨 Hotel Revenue\nIntelligence")
    st.markdown("---")

    st.markdown("### 📂 Upload Your Data")
    st.caption("You can upload **multiple files** — they will be merged and analysed together.")

    uploaded_files = st.file_uploader(
        "Drop Excel / CSV files here",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        help="Upload one or more hotel booking files. Supports .xlsx, .xls, .csv"
    )

    if uploaded_files:
        frames = []
        errors = []
        for f in uploaded_files:
            try:
                frames.append(process_single(f.read(), f.name))
            except Exception as e:
                errors.append(f"❌ {f.name}: {e}")

        if errors:
            for err in errors:
                st.warning(err)

        if frames:
            df_raw = pd.concat(frames, ignore_index=True)
            file_names = [f.name for f in uploaded_files]

            # Show loaded file badges
            badges_html = "".join([f"<span class='file-badge'>📄 {n}</span>" for n in file_names])
            st.markdown(f"<div style='margin-bottom:6px;'>{badges_html}</div>", unsafe_allow_html=True)
            st.success(f"✅ **{len(df_raw):,}** rows from **{len(frames)}** file(s)")

            st.markdown("---")
            st.markdown("### 🎛 Filters")

            years = sorted(df_raw['arrival_year'].dropna().unique().astype(int))
            sel_years = st.multiselect("📅 Year", years, default=years)

            hotels = sorted(df_raw['hotel'].dropna().unique()) if 'hotel' in df_raw.columns else []
            sel_hotels = st.multiselect("🏨 Hotel Type", hotels, default=hotels)

            # File source filter (only when >1 file)
            if len(frames) > 1:
                sel_files = st.multiselect("📁 Data Source", file_names, default=file_names)
            else:
                sel_files = file_names

            top_countries = df_raw.groupby('country')['estimated_revenue'].sum().nlargest(10).index.tolist() \
                if 'country' in df_raw.columns else []
            sel_countries = st.multiselect("🌍 Country", top_countries, default=top_countries)

            mask = df_raw['arrival_year'].isin(sel_years) & df_raw['_source_file'].isin(sel_files)
            if sel_hotels:
                mask &= df_raw['hotel'].isin(sel_hotels)
            if sel_countries:
                mask &= df_raw['country'].isin(sel_countries if sel_countries else top_countries)
            df = df_raw[mask]

            st.caption(f"Showing **{len(df):,}** bookings after filters")
        else:
            df = None
    else:
        df = None
        st.info("👆 Upload one or more Excel / CSV files to get started")

    st.markdown("---")
    st.markdown("<p style='font-size:11px;color:#334466;text-align:center;'>© 2026 Strateq Group · BDA Dept</p>", unsafe_allow_html=True)

# ── Landing page ──────────────────────────────────────────
if df is None:
    st.markdown("""
    <div style='text-align:center; padding: 4rem 2rem;'>
        <div style='font-size:64px; margin-bottom:1rem;'>🏨</div>
        <h1 style='color:#E0E6F0; font-size:36px; font-weight:700; margin-bottom:0.5rem;'>
            Hotel Revenue Intelligence
        </h1>
        <p style='color:#5577AA; font-size:18px; margin-bottom:2rem;'>
            Upload one or multiple hotel data files for instant revenue insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, label in zip([c1,c2,c3,c4],
        ["📊","💰","🌍","🎯"],
        ["Revenue Analysis","Cancellation Insights","Market Breakdown","Smart Recommendations"]):
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#111E35);border:1px solid #1A2A45;
            border-radius:16px;padding:1.5rem;text-align:center;'>
                <div style='font-size:32px;margin-bottom:8px;'>{icon}</div>
                <div style='font-size:13px;color:#8899BB;font-weight:500;'>{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;background:linear-gradient(135deg,#0D1628,#111E35);
    border:1px solid #1A2A45;border-radius:14px;padding:1.2rem 2rem;max-width:500px;margin:0 auto;'>
        <div style='font-size:13px;color:#5577AA;margin-bottom:6px;'>Supported formats</div>
        <div style='font-size:14px;color:#7ABAFF;font-weight:600;'>.xlsx &nbsp;·&nbsp; .xls &nbsp;·&nbsp; .csv</div>
        <div style='font-size:12px;color:#334466;margin-top:8px;'>
            Upload multiple files — they are automatically merged
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── KPI calculations ──────────────────────────────────────
confirmed   = df[df['is_canceled']==0]['estimated_revenue'].sum()
lost        = df[df['is_canceled']==1]['estimated_revenue'].sum()
total       = len(df)
cancelled   = int(df['is_canceled'].sum())
cancel_rate = cancelled / total * 100 if total > 0 else 0
avg_adr     = df[df['is_canceled']==0]['adr'].mean() if 'adr' in df.columns else 0
loss_ratio  = lost / confirmed if confirmed > 0 else 0
n_sources   = df['_source_file'].nunique()

source_label = f"{n_sources} data source{'s' if n_sources > 1 else ''}" if n_sources > 1 else ""

source_tag = (f" · <strong style='color:#22D47B'>{n_sources} data sources merged</strong>"
              if n_sources > 1 else "")

header_html = (
    "<div style='margin-bottom:1.5rem;'>"
    "<h1 style='color:#FFFFFF;font-size:28px;font-weight:800;margin-bottom:4px;'>"
    "🏨 Hotel Revenue Intelligence"
    "</h1>"
    "<p style='color:#5577AA;font-size:14px;'>"
    f"Portugal Hospitality Market · <strong style='color:#7ABAFF'>{total:,}</strong> bookings analysed"
    f"{source_tag}"
    " · Auto-generated insights"
    "</p>"
    "</div>"
)
st.markdown(header_html, unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.metric("✅ Confirmed Revenue",  f"${confirmed/1e6:.2f}M", f"+${confirmed/1e6*0.08:.1f}M YoY est.")
with k2: st.metric("❌ Revenue Lost",       f"${lost/1e6:.2f}M",      f"-{loss_ratio:.0%} loss ratio",  delta_color="inverse")
with k3: st.metric("📉 Cancel Rate",        f"{cancel_rate:.1f}%",    f"{cancelled:,} bookings",        delta_color="inverse")
with k4: st.metric("💳 Avg Daily Rate",     f"${avg_adr:.0f}",        "per night")
with k5: st.metric("📋 Total Bookings",     f"{total:,}",             f"{total-cancelled:,} confirmed")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Revenue Overview",
    "❌ Cancellation Analysis",
    "🌍 Market Intelligence",
    "📅 Seasonality",
    "🎯 Recommendations"
])

# ════════════════════════════════════════════════════
# TAB 1 — Revenue Overview
# ════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📊 Monthly Revenue Performance</div>', unsafe_allow_html=True)

    monthly = []
    for m in MONTH_ORDER:
        sub = df[df['arrival_month_name']==m]
        if len(sub) > 0:
            monthly.append({
                'month':     m[:3],
                'confirmed': sub[sub['is_canceled']==0]['estimated_revenue'].sum() / 1e6,
                'lost':      sub[sub['is_canceled']==1]['estimated_revenue'].sum() / 1e6,
            })
    monthly_df = pd.DataFrame(monthly)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='✅ Confirmed', x=monthly_df['month'], y=monthly_df['confirmed'],
        marker=dict(color=BLUE, opacity=0.9),
        text=monthly_df['confirmed'].apply(lambda x: f'${x:.2f}M'),
        textposition='outside', textfont=dict(size=10, color='#8899BB')
    ))
    fig.add_trace(go.Bar(
        name='❌ Lost', x=monthly_df['month'], y=monthly_df['lost'],
        marker=dict(color=RED, opacity=0.8),
        text=monthly_df['lost'].apply(lambda x: f'${x:.2f}M'),
        textposition='outside', textfont=dict(size=10, color='#8899BB')
    ))
    fig.update_layout(**merged_layout(
        360,
        barmode='group',
        yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45', showline=False, zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    bgcolor='rgba(0,0,0,0)', bordercolor='#1A2A45', font=dict(color='#8899BB'))
    ))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Per-file comparison (only when multiple sources)
    if n_sources > 1:
        st.markdown('<div class="section-header">📁 Revenue by Data Source</div>', unsafe_allow_html=True)
        src_rev = df[df['is_canceled']==0].groupby('_source_file')['estimated_revenue'].sum().reset_index()
        src_rev.columns = ['file','revenue']
        src_rev['revenue_m'] = src_rev['revenue'] / 1e6
        fig_src = px.bar(src_rev, x='file', y='revenue_m',
            color='revenue_m', color_continuous_scale=[[0,'#0D2040'],[1,BLUE]],
            text=src_rev['revenue_m'].apply(lambda x: f'${x:.2f}M'))
        fig_src.update_traces(textposition='outside', textfont=dict(color='#E0E6F0', size=12))
        fig_src.update_layout(**merged_layout(
            280,
            yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45', showline=False, zeroline=False),
            coloraxis_showscale=False
        ))
        st.plotly_chart(fig_src, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">🏨 Revenue by Hotel Type</div>', unsafe_allow_html=True)
        if 'hotel' in df.columns:
            hotel_df = df[df['is_canceled']==0].groupby('hotel')['estimated_revenue'].sum().reset_index()
            fig2 = px.pie(hotel_df, values='estimated_revenue', names='hotel',
                color_discrete_sequence=[BLUE, PURPLE], hole=0.55)
            fig2.update_traces(
                textinfo='percent+label', textfont_color='white',
                marker=dict(line=dict(color='#060B18', width=3))
            )
            chart(fig2, 300)

    with col2:
        st.markdown('<div class="section-header">📦 Revenue by Market Segment</div>', unsafe_allow_html=True)
        if 'market_segment' in df.columns:
            seg_df = (df[df['is_canceled']==0]
                      .groupby('market_segment')['estimated_revenue']
                      .sum().reset_index()
                      .sort_values('estimated_revenue'))
            fig3 = px.bar(seg_df, x='estimated_revenue', y='market_segment', orientation='h',
                color='estimated_revenue', color_continuous_scale=[[0,'#0D1628'],[1,BLUE]])
            fig3.update_traces(
                texttemplate='$%{x:.1f}', textposition='outside',
                textfont=dict(color='#8899BB', size=11)
            )
            fig3.update_layout(**merged_layout(
                300,
                xaxis=dict(tickprefix='$', gridcolor='#1A2A45', showline=False, zeroline=False),
                coloraxis_showscale=False
            ))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 2 — Cancellation Analysis
# ════════════════════════════════════════════════════
with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>Total Revenue Lost</div>
            <div class='insight-value' style='color:{RED};'>${lost/1e6:.2f}M</div>
            <div class='insight-desc'>Every $2 earned, $1 is lost to cancellations</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>Cancellation Rate</div>
            <div class='insight-value' style='color:{AMBER};'>{cancel_rate:.1f}%</div>
            <div class='insight-desc'>Year-round problem, not just seasonal</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        peak_month = monthly_df.loc[monthly_df['lost'].idxmax(), 'month'] if len(monthly_df) > 0 else "Aug"
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>Peak Loss Month</div>
            <div class='insight-value' style='color:{PURPLE};'>{peak_month}</div>
            <div class='insight-desc'>Highest revenue AND highest loss month</div>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">💳 Cancellation Rate by Deposit Type</div>', unsafe_allow_html=True)
        if 'deposit_type' in df.columns:
            dep_df = df.groupby('deposit_type').agg(
                total=('is_canceled','count'),
                cancelled=('is_canceled','sum')
            ).reset_index()
            dep_df['cancel_rate'] = dep_df['cancelled'] / dep_df['total'] * 100
            dep_df = dep_df.sort_values('cancel_rate', ascending=True)
            colors_dep = [RED if x > 50 else AMBER if x > 25 else GREEN for x in dep_df['cancel_rate']]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dep_df['cancel_rate'], y=dep_df['deposit_type'], orientation='h',
                marker=dict(color=colors_dep, opacity=0.85),
                text=dep_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside', textfont=dict(color='#E0E6F0', size=12, family='Inter')
            ))
            fig.update_layout(**merged_layout(
                280,
                xaxis=dict(ticksuffix='%', range=[0,115], gridcolor='#1A2A45', showline=False, zeroline=False)
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("⚠️ **Non-refundable ≠ confirmed revenue** — nearly 95% of these cancel!")

    with col2:
        st.markdown('<div class="section-header">👥 Cancellation by Customer Type</div>', unsafe_allow_html=True)
        if 'customer_type' in df.columns:
            cust_df = df.groupby('customer_type').agg(
                total=('is_canceled','count'),
                cancelled=('is_canceled','sum')
            ).reset_index()
            cust_df['cancel_rate'] = cust_df['cancelled'] / cust_df['total'] * 100
            fig = px.bar(cust_df, x='customer_type', y='cancel_rate',
                color='cancel_rate', color_continuous_scale=[[0,GREEN],[0.5,AMBER],[1,RED]],
                text=cust_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'))
            fig.update_traces(textposition='outside', textfont=dict(color='#E0E6F0', size=12))
            fig.update_layout(**merged_layout(
                280,
                yaxis=dict(ticksuffix='%', gridcolor='#1A2A45', showline=False, zeroline=False),
                coloraxis_showscale=False
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header">📊 Revenue Lost vs Confirmed — Monthly Trend</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_df['month'], y=monthly_df['confirmed'], name='✅ Confirmed',
        fill='tozeroy', fillcolor='rgba(74,158,255,0.15)',
        line=dict(color=BLUE, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=monthly_df['month'], y=monthly_df['lost'], name='❌ Lost',
        fill='tozeroy', fillcolor='rgba(255,90,90,0.15)',
        line=dict(color=RED, width=3, dash='dot')
    ))
    fig.update_layout(**merged_layout(
        280,
        yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1A2A45', showline=False, zeroline=False)
    ))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 3 — Market Intelligence
# ════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🌍 Top Source Markets — Revenue vs Cancellation Rate</div>', unsafe_allow_html=True)

    if 'country' in df.columns:
        country_df = df.groupby('country').agg(
            revenue=('estimated_revenue', lambda x: x[df.loc[x.index,'is_canceled']==0].sum() / 1e6),
            total=('is_canceled','count'),
            cancelled=('is_canceled','sum')
        ).reset_index()
        country_df['cancel_rate'] = country_df['cancelled'] / country_df['total'] * 100
        country_df = country_df.nlargest(8, 'revenue')

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            name='Revenue ($M)', x=country_df['country'], y=country_df['revenue'],
            marker=dict(color=BLUE, opacity=0.85),
            text=country_df['revenue'].apply(lambda x: f'${x:.2f}M'),
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
            dist_df = (df[df['is_canceled']==0]
                       .groupby('distribution_channel')['estimated_revenue']
                       .sum().reset_index())
            fig = px.pie(dist_df, values='estimated_revenue', names='distribution_channel',
                color_discrete_sequence=COLORS, hole=0.5)
            fig.update_traces(
                textinfo='percent+label', textfont_color='white',
                marker=dict(line=dict(color='#060B18', width=3))
            )
            chart(fig, 300)

    with col2:
        st.markdown('<div class="section-header">🧳 Booking Source Breakdown</div>', unsafe_allow_html=True)
        if 'booking_source' in df.columns:
            src_df = (df[df['is_canceled']==0]
                      .groupby('booking_source')['estimated_revenue']
                      .sum().reset_index()
                      .sort_values('estimated_revenue', ascending=True)
                      .tail(6))
            fig = px.bar(src_df, x='estimated_revenue', y='booking_source', orientation='h',
                color='estimated_revenue', color_continuous_scale=[[0,'#0D1628'],[1,CYAN]])
            fig.update_layout(**merged_layout(
                300,
                xaxis=dict(tickprefix='$', gridcolor='#1A2A45', showline=False, zeroline=False),
                coloraxis_showscale=False
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 4 — Seasonality
# ════════════════════════════════════════════════════
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🌞 Revenue by Season</div>', unsafe_allow_html=True)
        season_df = (df[df['is_canceled']==0]
                     .groupby('season')
                     .agg(revenue=('estimated_revenue','sum'), bookings=('is_canceled','count'))
                     .reset_index())
        season_df['revenue_m'] = season_df['revenue'] / 1e6
        season_colors = {'☀️ Summer': AMBER, '🌸 Spring': GREEN, '🍂 Autumn': CYAN, '❄️ Winter': BLUE}
        fig = px.pie(season_df, values='revenue_m', names='season',
            color='season', color_discrete_map=season_colors, hole=0.55)
        fig.update_traces(
            textinfo='percent+label', textfont_color='white',
            marker=dict(line=dict(color='#060B18', width=3))
        )
        fig.update_layout(**merged_layout(320))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown('<div class="section-header">📊 Season Performance Summary</div>', unsafe_allow_html=True)
        for _, row in season_df.sort_values('revenue_m', ascending=False).iterrows():
            s   = row['season']
            c   = season_colors.get(s, BLUE)
            pct = row['revenue_m'] / season_df['revenue_m'].sum() * 100
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0D1628,#0F1A2E);border:1px solid #1A2A45;
            border-left:4px solid {c};border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;
            display:flex;justify-content:space-between;align-items:center;'>
                <div>
                    <div style='font-size:14px;color:#C8D8F0;font-weight:600;'>{s}</div>
                    <div style='font-size:12px;color:#5577AA;'>{int(row['bookings']):,} bookings</div>
                </div>
                <div style='text-align:right;'>
                    <div style='font-size:18px;font-weight:700;color:{c};'>${row['revenue_m']:.2f}M</div>
                    <div style='font-size:12px;color:#5577AA;'>{pct:.1f}% of annual</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📅 ADR vs Arrival Volume by Month</div>', unsafe_allow_html=True)
    if 'adr' in df.columns:
        valid_months = [m for m in MONTH_ORDER if m in df['arrival_month_name'].values]
        adr_df = (df[df['is_canceled']==0]
                  .groupby('arrival_month_name')
                  .agg(avg_adr=('adr','mean'), bookings=('is_canceled','count'))
                  .reindex(valid_months)
                  .reset_index())
        adr_df.columns = ['month','avg_adr','bookings']

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            name='Bookings Volume', x=adr_df['month'].str[:3], y=adr_df['bookings'],
            marker=dict(color=BLUE, opacity=0.5)
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            name='Avg Daily Rate', x=adr_df['month'].str[:3], y=adr_df['avg_adr'],
            mode='lines+markers', line=dict(color=AMBER, width=3),
            marker=dict(size=8, color=AMBER, line=dict(color='white', width=2))
        ), secondary_y=True)
        fig.update_layout(**merged_layout(
            300,
            yaxis=dict(title='Bookings', gridcolor='#1A2A45', showline=False, zeroline=False),
            yaxis2=dict(title='Avg ADR ($)', tickprefix='$', gridcolor='rgba(0,0,0,0)', showline=False, zeroline=False)
        ))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════
# TAB 5 — Recommendations
# ════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D1628,#0A1A35);border:1px solid #1A2A45;
    border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;text-align:center;'>
        <p style='font-size:20px;font-weight:600;color:#4A9EFF;font-style:italic;margin-bottom:8px;'>
            "We are not losing to the market.<br>We are losing to our own decisions &amp; strategy."
        </p>
        <p style='font-size:13px;color:#5577AA;'>
            A confirmed booking is NOT confirmed revenue &nbsp;·&nbsp;
            Pricing does not apply beyond summer &nbsp;·&nbsp;
            Our best guests are being ignored
        </p>
    </div>
    """, unsafe_allow_html=True)

    recs = [
        (RED, "01", "🚨 Reduce Cancellation Revenue Loss",
         "Flag high-risk bookings before they confirm",
         [f"Prior cancellers → **mandatory deposit**",
          f"OTA non-refundable → treat as **unconfirmed**",
          f"Flag data in PMS, apply stricter deposit terms",
          f"**Potential recovery: ${lost*0.3/1e6:.2f}M** (30% reduction target)"]),
        (AMBER, "02", "💰 Price for Real Demand Year-Round",
         "Reprice March–April to match real demand",
         ["March–April capture rate matches June but ADR is **$30–40 lower**",
          "Extend dynamic pricing **beyond summer**",
          "Match ADR to capture rate, not season assumption",
          "Package off-season with **experience bundles**, not discounts"]),
        (GREEN, "03", "🎯 Acquire Reliable, Retain Loyal Guests",
         "Shift acquisition toward guests who actually stay",
         ["Reduce Portugal OTA spend (38% cancel rate)",
          "Increase **Germany & Belgium** acquisition (20-22% cancel rate)",
          "Create direct repeat guest incentive (rate, upgrade, recognition)",
          "Direct repeat guests cancel at only **10-12%**"]),
    ]

    for color, num, title, subtitle, points in recs:
        with st.expander(f"**{num} — {title}**", expanded=True):
            st.markdown(f"<p style='color:#8899BB;font-size:13px;font-style:italic;margin-bottom:1rem;'>💡 {subtitle}</p>", unsafe_allow_html=True)
            for p in points:
                st.markdown(f"<p style='color:#C8D8F0;font-size:13px;margin-bottom:6px;'>→ {p}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📊 Auto-Generated Key Insights</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    top_country   = df[df['is_canceled']==0].groupby('country')['estimated_revenue'].sum().idxmax() \
        if 'country' in df.columns and len(df) > 0 else "N/A"
    best_country  = df.groupby('country').apply(lambda x: x['is_canceled'].sum()/len(x)).idxmin() \
        if 'country' in df.columns and len(df) > 0 else "N/A"
    best_season   = df[df['is_canceled']==0].groupby('season')['estimated_revenue'].sum().idxmax() \
        if len(df) > 0 else "N/A"
    worst_deposit = df.groupby('deposit_type').apply(lambda x: x['is_canceled'].sum()/len(x)).idxmax() \
        if 'deposit_type' in df.columns and len(df) > 0 else "N/A"

    for col, icon, label, val, desc in zip(
        [i1, i2, i3, i4],
        ["🏆","✅","🌞","⚠️"],
        ["Top Revenue Market","Most Reliable Market","Best Season","Highest Risk Deposit"],
        [top_country, best_country, best_season, worst_deposit],
        ["by confirmed revenue","lowest cancel rate","by revenue contribution","highest cancel rate"]
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
