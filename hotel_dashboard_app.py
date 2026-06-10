import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Hotel Revenue Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; color: #e0e6f0; }
    .block-container { padding: 2rem 2rem 2rem 2rem; }
    
    .metric-card {
        background: #0d1220;
        border: 1px solid #1e2740;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }
    .metric-label {
        font-size: 12px;
        color: #5577aa;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .metric-value-green { font-size: 28px; font-weight: 700; color: #22c55e; }
    .metric-value-red   { font-size: 28px; font-weight: 700; color: #ef4444; }
    .metric-value-amber { font-size: 28px; font-weight: 700; color: #f59e0b; }
    .metric-sub { font-size: 12px; color: #5577aa; margin-top: 6px; }

    .section-title {
        font-size: 13px;
        font-weight: 600;
        color: #8899bb;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
    .insight-box {
        background: #0d1220;
        border: 1px solid #1e2740;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .rec-card-red    { border-top: 3px solid #ef4444; background: #0d1220; border-radius: 10px; padding: 1rem; }
    .rec-card-amber  { border-top: 3px solid #f59e0b; background: #0d1220; border-radius: 10px; padding: 1rem; }
    .rec-card-green  { border-top: 3px solid #22c55e; background: #0d1220; border-radius: 10px; padding: 1rem; }
    
    div[data-testid="metric-container"] {
        background: #0d1220;
        border: 1px solid #1e2740;
        border-radius: 12px;
        padding: 1rem;
    }
    div[data-testid="stSidebarContent"] { background: #0d1220; }
    .stSelectbox label, .stMultiSelect label { color: #8899bb !important; }
    h1, h2, h3 { color: #e0e6f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])

    def get_season(m):
        if m in ['June','July','August']: return 'Summer'
        elif m in ['March','April','May']: return 'Spring'
        elif m in ['September','October','November']: return 'Autumn'
        else: return 'Winter'

    df['season'] = df['arrival_month_name'].apply(get_season)
    return df

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏨 STRATEQ BDA")
    st.markdown("---")

    st.markdown("#### 📂 Upload Data")
    uploaded = st.file_uploader("Upload hotel Excel file", type=['xlsx'])

    st.markdown("---")
    st.markdown("#### 🔍 Filters")

    if uploaded:
        df_raw = load_data(uploaded)
    else:
        st.info("Using demo data. Upload your Excel file above.")
        # Demo data based on your PPT
        df_raw = pd.DataFrame({
            'hotel': ['Resort Hotel']*50 + ['City Hotel']*50,
            'is_canceled': [0]*35 + [1]*15 + [0]*30 + [1]*20,
            'country': ['PRT']*20 + ['GBR']*15 + ['FRA']*10 + ['DEU']*10 + ['ESP']*10 + ['IRL']*10 + ['ITA']*15 + ['BEL']*10,
            'arrival_month_name': (['January','February','March','April','May','June','July','August','September','October'] * 10),
            'arrival_year': [2015]*33 + [2016]*34 + [2017]*33,
            'deposit_type': ['No Deposit']*60 + ['Non Refund']*25 + ['Refundable']*15,
            'market_segment': ['Online TA']*40 + ['Direct']*25 + ['Corporate']*20 + ['Groups']*15,
            'customer_type': ['Transient']*60 + ['Contract']*20 + ['Group']*20,
            'adr': [75 + i*2 for i in range(100)],
            'estimated_revenue': [100 + i*3 for i in range(100)],
            'total_stay_nights': [2 + (i % 5) for i in range(100)],
            'lead_time': [10 + i*2 for i in range(100)],
            'season': ['Summer']*25 + ['Spring']*25 + ['Autumn']*25 + ['Winter']*25,
        })

    years = sorted(df_raw['arrival_year'].unique())
    selected_years = st.multiselect("Year", years, default=years)

    hotels = sorted(df_raw['hotel'].unique())
    selected_hotels = st.multiselect("Hotel", hotels, default=hotels)

    countries_list = sorted(df_raw['country'].unique())
    selected_countries = st.multiselect("Country (top markets)", countries_list[:10], default=countries_list[:10])

    # Apply filters
    df = df_raw[
        (df_raw['arrival_year'].isin(selected_years)) &
        (df_raw['hotel'].isin(selected_hotels)) &
        (df_raw['country'].isin(selected_countries if selected_countries else countries_list))
    ]

    st.markdown("---")
    st.markdown(f"**{len(df):,}** bookings loaded")

# ── Main Content ──────────────────────────────────────────
st.markdown("## 🏨 Hotel Revenue Intelligence Dashboard")
st.markdown("*Revenue Optimization Analysis · Portugal Hospitality Market*")
st.markdown("---")

# ── Key Metrics ───────────────────────────────────────────
confirmed = df[df['is_canceled'] == 0]['estimated_revenue'].sum()
lost = df[df['is_canceled'] == 1]['estimated_revenue'].sum()
total = len(df)
cancelled = df['is_canceled'].sum()
cancel_rate = cancelled / total * 100 if total > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("✅ Confirmed Revenue", f"${confirmed/1e6:.2f}M")
with col2:
    st.metric("❌ Revenue Lost", f"${lost/1e6:.2f}M")
with col3:
    st.metric("📉 Cancellation Rate", f"{cancel_rate:.1f}%")
with col4:
    st.metric("📋 Total Bookings", f"{total:,}")
with col5:
    ratio = lost / confirmed if confirmed > 0 else 0
    st.metric("💸 Loss Ratio", f"{ratio:.2f}x", help="For every $1 confirmed, this much is lost")

st.markdown("---")

# ── Monthly Revenue Chart ─────────────────────────────────
st.markdown("### 📅 Monthly Revenue vs Cancellation Loss")

month_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
monthly = df.groupby('arrival_month_name').agg(
    confirmed=('estimated_revenue', lambda x: x[df.loc[x.index, 'is_canceled'] == 0].sum() / 1e6),
    lost=('estimated_revenue', lambda x: x[df.loc[x.index, 'is_canceled'] == 1].sum() / 1e6)
).reindex([m for m in month_order if m in df['arrival_month_name'].unique()]).reset_index()

fig_monthly = go.Figure()
fig_monthly.add_trace(go.Bar(name='Confirmed Revenue', x=monthly['arrival_month_name'], y=monthly['confirmed'], marker_color='#4a9eff', text=monthly['confirmed'].apply(lambda x: f'${x:.2f}M'), textposition='outside'))
fig_monthly.add_trace(go.Bar(name='Revenue Lost', x=monthly['arrival_month_name'], y=monthly['lost'], marker_color='#ef4444', text=monthly['lost'].apply(lambda x: f'${x:.2f}M'), textposition='outside'))
fig_monthly.update_layout(
    barmode='group', plot_bgcolor='#0d1220', paper_bgcolor='#0d1220',
    font_color='#8899bb', height=380,
    legend=dict(bgcolor='#0d1220', bordercolor='#1e2740'),
    yaxis=dict(tickprefix='$', ticksuffix='M', gridcolor='#1e2740'),
    xaxis=dict(gridcolor='#1e2740'),
    margin=dict(t=20, b=20)
)
st.plotly_chart(fig_monthly, use_container_width=True)

# ── Season + Deposit ──────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.markdown("### 🌞 Season Performance")
    season_df = df[df['is_canceled'] == 0].groupby('season')['estimated_revenue'].sum().reset_index()
    season_df.columns = ['season', 'revenue']
    season_df['revenue_m'] = season_df['revenue'] / 1e6

    fig_season = px.pie(season_df, values='revenue_m', names='season',
        color_discrete_sequence=['#4a9eff','#22c55e','#f59e0b','#8899bb'],
        hole=0.5)
    fig_season.update_layout(plot_bgcolor='#0d1220', paper_bgcolor='#0d1220', font_color='#8899bb', height=320, margin=dict(t=20,b=20), legend=dict(bgcolor='#0d1220'))
    fig_season.update_traces(textinfo='percent+label', textfont_color='white')
    st.plotly_chart(fig_season, use_container_width=True)

with col_r:
    st.markdown("### 💳 Deposit Type — Cancellation Risk")
    deposit_df = df.groupby('deposit_type').agg(
        total=('is_canceled', 'count'),
        cancelled=('is_canceled', 'sum'),
        revenue_lost=('estimated_revenue', lambda x: x[df.loc[x.index, 'is_canceled'] == 1].sum() / 1e6)
    ).reset_index()
    deposit_df['cancel_rate'] = deposit_df['cancelled'] / deposit_df['total'] * 100

    fig_dep = go.Figure(go.Bar(
        x=deposit_df['cancel_rate'],
        y=deposit_df['deposit_type'],
        orientation='h',
        marker_color=deposit_df['cancel_rate'].apply(lambda x: '#ef4444' if x > 50 else '#f59e0b'),
        text=deposit_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside'
    ))
    fig_dep.update_layout(
        plot_bgcolor='#0d1220', paper_bgcolor='#0d1220', font_color='#8899bb',
        height=320, margin=dict(t=20, b=20, l=10, r=60),
        xaxis=dict(ticksuffix='%', gridcolor='#1e2740', range=[0, 110]),
        yaxis=dict(gridcolor='#1e2740')
    )
    st.plotly_chart(fig_dep, use_container_width=True)
    st.caption("⚠️ Non-refundable does NOT mean confirmed revenue — 94.6% of these cancel")

st.markdown("---")

# ── Top Countries ─────────────────────────────────────────
st.markdown("### 🌍 Top 8 Source Markets — Revenue vs Cancellation Rate")

country_df = df.groupby('country').agg(
    confirmed_rev=('estimated_revenue', lambda x: x[df.loc[x.index, 'is_canceled'] == 0].sum() / 1e6),
    total=('is_canceled', 'count'),
    cancelled=('is_canceled', 'sum')
).reset_index()
country_df['cancel_rate'] = country_df['cancelled'] / country_df['total'] * 100
country_df = country_df.nlargest(8, 'confirmed_rev')

fig_country = make_subplots(specs=[[{"secondary_y": True}]])
fig_country.add_trace(go.Bar(name='Revenue ($M)', x=country_df['country'], y=country_df['confirmed_rev'], marker_color='#4a9eff', text=country_df['confirmed_rev'].apply(lambda x: f'${x:.2f}M'), textposition='outside'), secondary_y=False)
fig_country.add_trace(go.Scatter(name='Cancel Rate (%)', x=country_df['country'], y=country_df['cancel_rate'], mode='lines+markers', line=dict(color='#ef4444', width=2), marker=dict(size=8, color='#ef4444')), secondary_y=True)
fig_country.update_layout(plot_bgcolor='#0d1220', paper_bgcolor='#0d1220', font_color='#8899bb', height=380, margin=dict(t=20,b=20), legend=dict(bgcolor='#0d1220', bordercolor='#1e2740'))
fig_country.update_yaxes(tickprefix='$', ticksuffix='M', gridcolor='#1e2740', secondary_y=False)
fig_country.update_yaxes(ticksuffix='%', gridcolor='#1e2740', secondary_y=True)
st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# ── Market Segment + Customer Type ───────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📦 Revenue by Market Segment")
    seg_df = df[df['is_canceled'] == 0].groupby('market_segment')['estimated_revenue'].sum().reset_index()
    fig_seg = px.bar(seg_df.sort_values('estimated_revenue'), x='estimated_revenue', y='market_segment', orientation='h', color_discrete_sequence=['#4a9eff'])
    fig_seg.update_layout(plot_bgcolor='#0d1220', paper_bgcolor='#0d1220', font_color='#8899bb', height=300, margin=dict(t=20,b=20), xaxis=dict(tickprefix='$', gridcolor='#1e2740'), yaxis=dict(gridcolor='#1e2740'))
    st.plotly_chart(fig_seg, use_container_width=True)

with col2:
    st.markdown("### 👥 Cancellation by Customer Type")
    cust_df = df.groupby('customer_type').agg(total=('is_canceled','count'), cancelled=('is_canceled','sum')).reset_index()
    cust_df['cancel_rate'] = cust_df['cancelled'] / cust_df['total'] * 100
    fig_cust = px.bar(cust_df, x='customer_type', y='cancel_rate', color_discrete_sequence=['#f59e0b'], text=cust_df['cancel_rate'].apply(lambda x: f'{x:.1f}%'))
    fig_cust.update_layout(plot_bgcolor='#0d1220', paper_bgcolor='#0d1220', font_color='#8899bb', height=300, margin=dict(t=20,b=20), yaxis=dict(ticksuffix='%', gridcolor='#1e2740'), xaxis=dict(gridcolor='#1e2740'))
    fig_cust.update_traces(textposition='outside')
    st.plotly_chart(fig_cust, use_container_width=True)

st.markdown("---")

# ── Key Takeaway ──────────────────────────────────────────
st.markdown("""
<div style="background:#0d1220;border:1px solid #1e2740;border-radius:12px;padding:1.5rem;text-align:center;margin-bottom:1.5rem;">
    <p style="font-size:20px;font-weight:600;color:#4a9eff;font-style:italic;">
        "We are not losing to the market. We are losing to our own decisions & strategy."
    </p>
    <p style="font-size:13px;color:#5577aa;margin-top:8px;">
        A confirmed booking is NOT confirmed revenue &nbsp;·&nbsp; 
        Pricing does not apply beyond summer &nbsp;·&nbsp; 
        Our best guests are being ignored
    </p>
</div>
""", unsafe_allow_html=True)

# ── Recommendations ───────────────────────────────────────
st.markdown("### 🎯 Strategic Recommendations")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="rec-card-red">
        <p style="font-size:11px;font-weight:700;color:#ef4444;letter-spacing:0.08em;">01 — REDUCE CANCELLATION LOSS</p>
        <p style="font-size:14px;font-weight:600;color:#e0e6f0;margin:8px 0;">Flag high-risk bookings</p>
        <p style="font-size:12px;color:#5577aa;line-height:1.6;">Require mandatory deposits for prior cancellers. Treat OTA non-refundable as unconfirmed. Flag in PMS.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="rec-card-amber">
        <p style="font-size:11px;font-weight:700;color:#f59e0b;letter-spacing:0.08em;">02 — PRICE FOR REAL DEMAND</p>
        <p style="font-size:14px;font-weight:600;color:#e0e6f0;margin:8px 0;">Reprice March–April</p>
        <p style="font-size:12px;color:#5577aa;line-height:1.6;">Extend dynamic pricing beyond summer. Match ADR to capture rate. Package off-season with experience bundles.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="rec-card-green">
        <p style="font-size:11px;font-weight:700;color:#22c55e;letter-spacing:0.08em;">03 — ACQUIRE RELIABLE GUESTS</p>
        <p style="font-size:14px;font-weight:600;color:#e0e6f0;margin:8px 0;">Shift acquisition strategy</p>
        <p style="font-size:12px;color:#5577aa;line-height:1.6;">Reduce Portugal OTA spend. Increase Germany & Belgium. Create direct repeat guest incentives.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#5577aa;font-size:12px;'>© 2026 Strateq Group of Companies · Hotel Revenue Intelligence · Big Data Analytics Dept</p>", unsafe_allow_html=True)
