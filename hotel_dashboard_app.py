import io
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(
    page_title="Hotel Revenue Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── THEME ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #060B18; color: #E0E6F0; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0D1628, #152240);
    border: 1px solid #2A3F6A; border-radius: 14px;
    padding: 1.2rem 1.4rem;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] p,
div[data-testid="metric-container"] label {
    color: #8899BB !important; font-size: 11px !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.08em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important; font-size: 28px !important; font-weight: 800 !important;
}
div[data-testid="stTabs"] button { color: #5577AA !important; font-size: 13px !important; font-weight: 500 !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #4A9EFF !important; border-bottom-color: #4A9EFF !important; }
.stDataFrame { background: #0D1628 !important; }
hr { border-color: #1A2A45 !important; margin: 1.2rem 0 !important; }
.sechdr {
    font-size: 13px; font-weight: 700; color: #8899BB; text-transform: uppercase;
    letter-spacing: 0.08em; margin: 1.4rem 0 0.8rem; display: flex; align-items: center; gap: 8px;
}
.sechdr::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,#1A2A45,transparent); }
.card {
    background: linear-gradient(135deg,#0D1628,#0F1A2E);
    border: 1px solid #1A2A45; border-radius: 12px;
    padding: 1rem 1.2rem; margin-bottom: 0.75rem;
}
.card-title { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 4px; }
.card-body { font-size: 13px; color: #C8D8F0; line-height: 1.65; }
.hero-banner {
    background: linear-gradient(135deg,#0D1628,#0A1A35);
    border: 1px solid #1A2A45; border-radius: 16px;
    padding: 1.4rem 1.8rem; margin-bottom: 1.4rem;
}
</style>
""", unsafe_allow_html=True)

# ── COLORS ────────────────────────────────────────────────────────────────────
BLUE="#4A9EFF"; GREEN="#22D47B"; RED="#FF5A5A"; AMBER="#FFB830"
PURPLE="#A855F7"; CYAN="#06B6D4"; PINK="#EC4899"

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,22,40,0.6)",
    font=dict(family="Inter", color="#8899BB", size=12),
    margin=dict(t=30,b=10,l=10,r=10),
    xaxis=dict(gridcolor="#1A2A45", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#1A2A45", showline=False, zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1A2A45", font=dict(color="#8899BB")),
    hoverlabel=dict(bgcolor="#0D1628", bordercolor="#1A2A45", font=dict(color="#E0E6F0")),
)

def ch(fig, h=360):
    fig.update_layout(**{**CHART, "height": h})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def money(v):
    if pd.isna(v): return "$0"
    v = float(v)
    if abs(v) >= 1e6: return f"${v/1e6:,.2f}M"
    if abs(v) >= 1e3: return f"${v/1e3:,.1f}K"
    return f"${v:,.0f}"

def pct(v): return f"{float(v):,.1f}%"

def card(color, title, body):
    st.markdown(f"""
    <div class='card' style='border-left:4px solid {color}'>
        <div class='card-title' style='color:{color}'>{title}</div>
        <div class='card-body'>{body}</div>
    </div>""", unsafe_allow_html=True)

def sechdr(text):
    st.markdown(f"<div class='sechdr'>{text}</div>", unsafe_allow_html=True)

MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
SEASON_MAP = {m: s for m,s in zip(MONTH_ORDER,
    ['Winter','Winter','Spring','Spring','Spring','Summer',
     'Summer','Summer','Autumn','Autumn','Autumn','Winter'])}

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(hotel_bytes, arrivals_bytes):
    hotel    = pd.read_excel(io.BytesIO(hotel_bytes))
    arrivals = pd.read_excel(io.BytesIO(arrivals_bytes))

    hotel['confirmed_rev'] = hotel['estimated_revenue'] * (1 - hotel['is_canceled'])
    hotel['lost_rev']      = hotel['estimated_revenue'] * hotel['is_canceled']
    hotel['season']        = hotel['arrival_month_name'].map(SEASON_MAP)
    hotel['arrival_month_name'] = pd.Categorical(
        hotel['arrival_month_name'], MONTH_ORDER, ordered=True)

    return hotel, arrivals

# ── SIDEBAR FILE UPLOAD ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏨 Hotel Revenue Intelligence")
    st.markdown("---")
    st.markdown("### 📂 Upload Data Files")
    st.caption("Upload the two required Excel files to generate the analysis.")
    hotel_file    = st.file_uploader("Hotel data (cleaned_hotel_data.xlsx)",
                                     type=["xlsx","xls","csv"], key="hotel")
    arrivals_file = st.file_uploader("Arrivals data (cleaned_portugal_arrivals.xlsx)",
                                     type=["xlsx","xls","csv"], key="arrivals")

if not hotel_file or not arrivals_file:
    st.markdown("""
    <div class='hero-banner' style='text-align:center;padding:3rem 2rem'>
      <div style='font-size:48px;margin-bottom:1rem'>🏨</div>
      <div style='font-size:22px;font-weight:800;color:#E0E6F0;margin-bottom:8px'>
        Hotel Revenue Intelligence
      </div>
      <div style='font-size:14px;color:#5577AA;margin-bottom:1.5rem'>
        Revenue Optimization Analysis — Portugal Hospitality Market
      </div>
      <div style='font-size:13px;color:#8899BB;line-height:1.8'>
        👈 Upload both files from the <strong style='color:#4A9EFF'>sidebar</strong> to begin:<br>
        <strong style='color:#E0E6F0'>1.</strong> cleaned_hotel_data.xlsx<br>
        <strong style='color:#E0E6F0'>2.</strong> cleaned_portugal_arrivals.xlsx
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

with st.spinner("Loading data…"):
    hotel, arrivals = load_data(hotel_file.getvalue(), arrivals_file.getvalue())

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-banner'>
  <div style='font-size:22px;font-weight:800;color:#E0E6F0;margin-bottom:3px'>
    🏨 Hotel Revenue Intelligence
  </div>
  <div style='font-size:13px;color:#5577AA'>
    Revenue Optimization Analysis — Portugal Hospitality Market · 2015–2017
  </div>
</div>
""", unsafe_allow_html=True)

# top KPIs
conf_rev   = hotel['confirmed_rev'].sum()
lost_rev   = hotel['lost_rev'].sum()
cancel_rate = hotel['is_canceled'].mean() * 100
avg_adr    = hotel['adr'].mean()

k1,k2,k3,k4 = st.columns(4)
k1.metric("✅ Confirmed Revenue", money(conf_rev))
k2.metric("❌ Revenue Lost",      money(lost_rev))
k3.metric("📉 Cancellation Rate", pct(cancel_rate))
k4.metric("💳 Avg ADR",          f"${avg_adr:,.0f}")
st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs([
    "📋 Objective",
    "🚨 Pain Point 1 — Cancellation",
    "💰 Pain Point 2 — Pricing",
    "🎯 Pain Point 3 — Guest Mix",
    "🏁 Recommendations & Takeaway",
])

# ════════════════════════════════════════════════════════
# TAB 1 — OBJECTIVE
# ════════════════════════════════════════════════════════
with t1:
    st.markdown("""
    <div class='hero-banner'>
      <div style='font-size:18px;font-weight:800;color:#E0E6F0;margin-bottom:6px'>
        "Are we maximizing revenue… or just maximizing booking volume?"
      </div>
      <div style='font-size:13px;color:#5577AA'>
        Portugal's hospitality market is growing. But revenue isn't staying.
      </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col, num, color, title, desc in zip(
        [c1,c2,c3], ["01","02","03"], [GREEN,CYAN,PINK],
        ["Reduce Cancellation Revenue Loss",
         "Price for Real Demand Year-Round",
         "Acquire Reliable, Retain Loyal Guest"],
        ["Stop losing $1 for every $2 earned to booking cancellations.",
         "Extend dynamic pricing beyond the summer peak period only.",
         "Shift focus from booking volume to reliable, low-risk guest quality."],
    ):
        with col:
            st.markdown(f"""
            <div class='card' style='border-left:4px solid {color};min-height:130px'>
              <div style='font-size:28px;font-weight:900;color:{color};margin-bottom:6px'>{num}</div>
              <div style='font-size:14px;font-weight:700;color:#E0E6F0;margin-bottom:8px'>{title}</div>
              <div style='font-size:12px;color:#8899BB;line-height:1.6'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    sechdr("Agenda")
    for n,t in [("01","Objective"),("02","Pain Points"),
                ("03","Data-Driven Insights"),("04","Strategic Recommendations"),("05","Key Takeaway")]:
        st.markdown(f"<p style='color:#C8D8F0;font-size:13px;margin-bottom:5px'>"
                    f"<span style='color:#4A9EFF;font-weight:700'>{n}</span> &nbsp; {t}</p>",
                    unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2 — PAIN POINT 1: CANCELLATION
# ════════════════════════════════════════════════════════
with t2:
    st.markdown(f"""
    <div style='font-size:18px;font-weight:800;color:{RED};margin-bottom:4px'>
      🚨 Pain Point 1 — Money Out the Door
    </div>
    <p style='color:#5577AA;font-size:13px;margin-bottom:1.2rem'>
      $11.31M lost from booking cancellations
    </p>""", unsafe_allow_html=True)

    k1,k2,k3 = st.columns(3)
    k1.metric("✅ Confirmed Revenue", money(conf_rev))
    k2.metric("❌ Revenue Lost",      money(lost_rev))
    k3.metric("📉 Cancellation Rate", pct(cancel_rate))

    # ── Chart 1: Monthly confirmed vs lost ───────────────────────
    sechdr("Confirmed Revenue vs Cancellation Loss — monthly (2015–2017 avg)")

    monthly = hotel.groupby(['arrival_month','arrival_month_name']).agg(
        conf=('confirmed_rev','sum'), lost=('lost_rev','sum')
    ).reset_index().sort_values('arrival_month')

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Confirmed Revenue", x=monthly['arrival_month_name'],
                         y=monthly['conf'], marker_color=BLUE, opacity=0.85))
    fig.add_trace(go.Bar(name="Revenue Lost", x=monthly['arrival_month_name'],
                         y=monthly['lost'], marker_color=RED, opacity=0.80))
    fig.update_layout(**{**CHART,"height":370,"barmode":"group",
                         "yaxis":{"tickprefix":"$","gridcolor":"#1A2A45"}})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    c1,c2,c3 = st.columns(3)
    with c1:
        card(RED, "$11.31M lost — every $2 earned, $1 lost",
             "The revenue loss ratio is structural and consistent across all 12 months, not a seasonal spike.")
    with c2:
        card(AMBER, "28% cancellation rate runs year-round",
             "The rate stays between 25–33% every month. Seasonal policy changes alone won't fix it.")
    with c3:
        card(RED, "August: highest revenue AND highest loss",
             f"August generates the most revenue ({money(monthly.loc[monthly['arrival_month_name']=='August','conf'].values[0])}) "
             f"but also the most loss ({money(monthly.loc[monthly['arrival_month_name']=='August','lost'].values[0])}).")

    st.markdown("---")

    # ── Chart 2: Cancel rate by deposit type ─────────────────────
    sechdr("Cancel Rate by Deposit Type vs Revenue Exposure")

    dep = hotel.groupby('deposit_type').agg(
        cancel_rate=('is_canceled','mean'),
        revenue_lost=('lost_rev','sum'),
        total_bookings=('is_canceled','count'),
        avg_adr=('adr','mean')
    ).reset_index()
    dep['cancel_rate'] *= 100

    col_left, col_right = st.columns([3,2])
    with col_left:
        fig2 = px.bar(dep, x='deposit_type', y='cancel_rate',
                      color='cancel_rate',
                      color_continuous_scale=[[0,GREEN],[0.3,AMBER],[1,RED]],
                      text=dep['cancel_rate'].map(pct))
        fig2.update_traces(textposition='outside', textfont=dict(color='#E0E6F0'))
        fig2.update_layout(**{**CHART,"height":340,
                               "yaxis":{"ticksuffix":"%","range":[0,110],"gridcolor":"#1A2A45"},
                               "coloraxis_showscale":False})
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    with col_right:
        display_dep = dep[['deposit_type','cancel_rate','revenue_lost','total_bookings','avg_adr']].copy()
        display_dep['cancel_rate'] = display_dep['cancel_rate'].map(pct)
        display_dep['revenue_lost'] = display_dep['revenue_lost'].map(money)
        display_dep['avg_adr'] = display_dep['avg_adr'].map(lambda x: f"${x:,.2f}")
        display_dep.columns = ['Deposit Type','Cancel Rate','Revenue Lost','Bookings','Avg ADR']
        st.dataframe(display_dep, use_container_width=True, hide_index=True)

    card(RED, "Non-refundable bookings cancel at nearly 95%",
         f"<strong>{pct(dep.loc[dep['deposit_type']=='Non Refund','cancel_rate'].values[0])}</strong> of non-refundable bookings cancel. "
         "The label does not protect revenue.")
    card(AMBER, "No-deposit bookings create the largest revenue exposure",
         f"79,100 no-deposit bookings lost <strong>{money(dep.loc[dep['deposit_type']=='No Deposit','revenue_lost'].values[0])}</strong> — the biggest absolute risk pool.")
    card(GREEN, "The label 'non-refundable' does not mean confirmed revenue",
         "Treat OTA non-refundable bookings as unconfirmed until a pre-arrival deposit is physically collected.")

    st.markdown(f"""
    <div class='card' style='background:linear-gradient(135deg,#0A1E10,#0D2818);border:1px solid #1A5020;margin-top:0.5rem'>
      <div style='font-size:13px;font-weight:700;color:{GREEN};margin-bottom:8px'>
        💡 Strategic Recommendation 1 — Flag high-risk bookings before they confirm
      </div>
      <div class='card-body'>
        • <strong>Prior cancellers → mandatory deposit</strong> before confirmation<br>
        • <strong>OTA non-refundable → treat as unconfirmed</strong> until deposit verified<br>
        • Flag data in PMS and apply stricter deposit terms automatically
      </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 3 — PAIN POINT 2: PRICING / DEMAND
# ════════════════════════════════════════════════════════
with t3:
    st.markdown(f"""
    <div style='font-size:18px;font-weight:800;color:{AMBER};margin-bottom:4px'>
      💰 Pain Point 2 — Missing the Moment
    </div>
    <p style='color:#5577AA;font-size:13px;margin-bottom:1.2rem'>
      Rooms sold below peak demand value
    </p>""", unsafe_allow_html=True)

    # ── Chart 1: Market Capture Rate vs ADR ──────────────────────
    sechdr("Market Capture Rate vs Average Daily Rate (Jan–Dec, 2015–2017 avg)")

    hotel_avg = hotel.groupby(['arrival_month','arrival_month_name']).agg(
        bookings=('is_canceled','count'), avg_adr=('adr','mean')
    ).reset_index()
    arr_avg = arrivals.groupby(['month','month_name']).agg(
        arrivals=('international_arrivals','mean')
    ).reset_index()
    bridge = hotel_avg.merge(arr_avg, left_on='arrival_month', right_on='month')
    bridge['capture_rate'] = bridge['bookings'] / bridge['arrivals'] * 100
    bridge = bridge.sort_values('arrival_month')
    bridge['arrival_month_name'] = pd.Categorical(bridge['arrival_month_name'], MONTH_ORDER, ordered=True)
    bridge = bridge.sort_values('arrival_month_name')

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(name="Market Capture Rate (%)", x=bridge['arrival_month_name'],
                         y=bridge['capture_rate'], marker_color=CYAN, opacity=0.55), secondary_y=False)
    fig.add_trace(go.Scatter(name="Avg ADR ($)", x=bridge['arrival_month_name'],
                             y=bridge['avg_adr'], mode='lines+markers',
                             line=dict(color=AMBER,width=3), marker=dict(size=8)), secondary_y=True)
    fig.update_yaxes(title_text="Market Capture Rate (%)", ticksuffix="%", secondary_y=False)
    fig.update_yaxes(title_text="Avg ADR ($)", tickprefix="$", secondary_y=True)
    fig.update_layout(**{**CHART,"height":390})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # find march-april vs june ADR gap
    mar_adr = bridge.loc[bridge['arrival_month_name']=='March','avg_adr'].values[0]
    apr_adr = bridge.loc[bridge['arrival_month_name']=='April','avg_adr'].values[0]
    jun_adr = bridge.loc[bridge['arrival_month_name']=='June','avg_adr'].values[0]
    mar_cap = bridge.loc[bridge['arrival_month_name']=='March','capture_rate'].values[0]
    jun_cap = bridge.loc[bridge['arrival_month_name']=='June','capture_rate'].values[0]

    card(RED, "March–April capture rate matches June, but ADR is $30–40 lower",
         f"March capture rate: <strong>{mar_cap:.2f}%</strong> vs June: <strong>{jun_cap:.2f}%</strong>. "
         f"But March ADR is <strong>${mar_adr:,.0f}</strong> vs June <strong>${jun_adr:,.0f}</strong> — "
         f"a gap of <strong>${jun_adr-mar_adr:,.0f}</strong>.")
    card(AMBER, "Dynamic pricing responds to summer only, not the full year",
         "ADR only rises materially from July–August. Spring and early autumn demand signals are ignored by pricing logic.")
    card(GREEN, "Sufficient demand in shoulder season — revenue not being captured",
         "March and April have strong market capture rates comparable to June. The pricing system isn't reflecting this.")

    st.markdown("---")

    # ── Chart 2: Season performance ───────────────────────────────
    sechdr("Season Performance — Revenue Distribution")

    season = hotel.groupby('season').agg(
        revenue=('confirmed_rev','sum'), cancel_rate=('is_canceled','mean'),
        avg_adr=('adr','mean'), bookings=('is_canceled','count')
    ).reset_index()
    season['cancel_rate'] *= 100
    season['share'] = season['revenue'] / season['revenue'].sum() * 100

    col_left, col_right = st.columns([2,3])
    with col_left:
        fig2 = px.pie(season, values='revenue', names='season', hole=0.52,
                      color_discrete_map={'Summer':CYAN,'Spring':PINK,'Autumn':AMBER,'Winter':BLUE})
        fig2.update_traces(textinfo='percent+label', textfont_color='white')
        fig2.update_layout(**{**CHART,"height":340})
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    with col_right:
        disp = season.copy()
        disp['revenue'] = disp['revenue'].map(money)
        disp['share'] = disp['share'].map(pct)
        disp['cancel_rate'] = disp['cancel_rate'].map(pct)
        disp['avg_adr'] = disp['avg_adr'].map(lambda x: f"${x:,.0f}")
        disp.columns = ['Season','Revenue','Cancel Rate','Avg ADR','Bookings','Share']
        st.dataframe(disp[['Season','Revenue','Share','Avg ADR','Cancel Rate','Bookings']],
                     use_container_width=True, hide_index=True)

    summer = season.loc[season['season']=='Summer','revenue'].values[0]
    autumn = season.loc[season['season']=='Autumn','revenue'].values[0]
    winter = season.loc[season['season']=='Winter','revenue'].values[0]
    summer_share = season.loc[season['season']=='Summer','share'].values[0]

    card(CYAN, f"Summer generates {pct(summer_share)} of annual revenue in just 3 months",
         f"{money(summer)} from Jun–Aug alone. Revenue is heavily concentrated and vulnerable to any demand shift.")
    card(RED, "Autumn + Winter combined contribute less than 30%",
         f"{money(autumn)} + {money(winter)} = {money(autumn+winter)} ({pct((autumn+winter)/(hotel['confirmed_rev'].sum())*100)}). "
         "Both seasons are under-priced relative to actual visitor demand.")

    st.markdown(f"""
    <div class='card' style='background:linear-gradient(135deg,#1A1205,#251A05);border:1px solid #503A05;margin-top:0.5rem'>
      <div style='font-size:13px;font-weight:700;color:{AMBER};margin-bottom:8px'>
        💡 Strategic Recommendation 2 — Reprice March–April to match real demand
      </div>
      <div class='card-body'>
        • <strong>Extend dynamic pricing beyond summer</strong> — activate rate logic for Mar–Jun and Sep–Oct<br>
        • <strong>Match ADR to capture rate, not season assumption</strong> — let demand signal pricing<br>
        • <strong>Package off-season as experience bundles, not discounts</strong> — protect rate integrity
      </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 4 — PAIN POINT 3: GUEST / MARKET MIX
# ════════════════════════════════════════════════════════
with t4:
    st.markdown(f"""
    <div style='font-size:18px;font-weight:800;color:{PURPLE};margin-bottom:4px'>
      🎯 Pain Point 3 — Aiming at the Wrong Guests
    </div>
    <p style='color:#5577AA;font-size:13px;margin-bottom:1.2rem'>
      Ignoring the guests who actually stay
    </p>""", unsafe_allow_html=True)

    # ── Chart 1: Top 8 markets ────────────────────────────────────
    sechdr("Top 8 Source Markets — Confirmed Revenue vs Cancellation Rate")

    country = hotel.groupby('country').agg(
        conf_rev=('confirmed_rev','sum'), cancel_rate=('is_canceled','mean'),
        bookings=('is_canceled','count')
    ).reset_index()
    country['cancel_rate'] *= 100
    top8 = country.nlargest(8, 'conf_rev').reset_index(drop=True)

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(name="Confirmed Revenue ($M)", x=top8['country'],
                         y=top8['conf_rev']/1e6, marker_color=CYAN, opacity=0.75), secondary_y=False)
    fig.add_trace(go.Scatter(name="Cancellation Rate (%)", x=top8['country'],
                             y=top8['cancel_rate'], mode='lines+markers',
                             line=dict(color=RED,width=3), marker=dict(size=9)), secondary_y=True)
    fig.update_yaxes(title_text="Confirmed Revenue ($M)", tickprefix="$", ticksuffix="M", secondary_y=False)
    fig.update_yaxes(title_text="Cancellation Rate (%)", ticksuffix="%", secondary_y=True)
    fig.update_layout(**{**CHART,"height":390})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    disp_c = top8[['country','conf_rev','cancel_rate','bookings']].copy()
    disp_c['conf_rev'] = disp_c['conf_rev'].map(money)
    disp_c['cancel_rate'] = disp_c['cancel_rate'].map(pct)
    disp_c.columns = ['Country','Confirmed Revenue','Cancel Rate','Bookings']
    st.dataframe(disp_c, use_container_width=True, hide_index=True)

    prt_cancel = top8.loc[top8['country']=='PRT','cancel_rate'].values[0]
    deu_cancel = top8.loc[top8['country']=='DEU','cancel_rate'].values[0]
    bel_cancel = top8.loc[top8['country']=='BEL','cancel_rate'].values[0]

    card(RED, f"Portugal: top revenue source, highest cancel rate at {pct(prt_cancel)}",
         "PRT generates the most confirmed revenue but also cancels at 38% — the highest of all markets. High volume masks high risk.")
    card(GREEN, f"Germany & Belgium cancel at only {pct(deu_cancel)} / {pct(bel_cancel)} — most reliable",
         "DEU and BEL are far more reliable. Lower volume but stronger effective revenue per completed booking.")
    card(AMBER, "Shifting investment toward low-cancellation markets improves net revenue",
         "Investing more in DEU, BEL and GBR acquisition reduces leakage without needing to increase total booking volume.")

    st.markdown("---")

    # ── Chart 2: Risk segments ────────────────────────────────────
    sechdr("Highest-Risk Guest Segments by Cancellation Rate")

    hotel['prior_canceller'] = hotel['previous_cancellations'] > 0
    segments = {
        "Prior canceller · Any channel":          hotel['prior_canceller'],
        "Online TA · Non-refundable":             hotel['deposit_type'] == 'Non Refund',
        "Online TA · No deposit · Lead >90d":     (hotel['market_segment']=='Online TA') & (hotel['deposit_type']=='No Deposit') & (hotel['lead_time']>90),
        "Groups · Holiday month":                 (hotel['market_segment']=='Groups'),
        "Corp / GDS · Short lead":                (hotel['market_segment']=='Corporate') & (hotel['lead_time']<=7),
        "Online TA · General":                    (hotel['market_segment']=='Online TA'),
        "Direct · Repeat guest":                  (hotel['distribution_channel']=='Direct') & (hotel['is_repeated_guest']==1),
    }

    seg_rows = []
    for label, mask in segments.items():
        sub = hotel[mask]
        if len(sub) >= 5:
            seg_rows.append({"Risk Segment": label,
                             "Cancel Rate (%)": sub['is_canceled'].mean()*100,
                             "Count": len(sub)})
    seg_df = pd.DataFrame(seg_rows).sort_values("Cancel Rate (%)")

    fig2 = px.bar(seg_df, x='Cancel Rate (%)', y='Risk Segment', orientation='h',
                  color='Cancel Rate (%)',
                  color_continuous_scale=[[0,GREEN],[0.15,GREEN],[0.4,AMBER],[0.7,RED],[1,'#FF0000']],
                  text=seg_df['Cancel Rate (%)'].map(pct))
    fig2.update_traces(textposition='outside', textfont=dict(color='#E0E6F0'))
    fig2.update_layout(**{**CHART,"height":400,
                           "xaxis":{"ticksuffix":"%","range":[0,115],"gridcolor":"#1A2A45"},
                           "coloraxis_showscale":False})
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    direct_repeat_cr = hotel.loc[(hotel['distribution_channel']=='Direct') & (hotel['is_repeated_guest']==1),'is_canceled'].mean()*100
    repeat_share = hotel['is_repeated_guest'].mean()*100
    nonref_cr = hotel.loc[hotel['deposit_type']=='Non Refund','is_canceled'].mean()*100

    card(RED, f"Prior cancellers and OTA non-refundable bookings cancel at nearly 95%",
         f"OTA non-refundable: <strong>{pct(nonref_cr)}</strong> cancel rate. Both high-risk groups are identifiable before booking confirms.")
    card(GREEN, f"Direct repeat guests cancel at only {pct(direct_repeat_cr)} but represent only {pct(repeat_share)} of the base",
         "The most reliable segment is the most under-invested. Growing this group is the highest-leverage loyalty action available.")

    st.markdown(f"""
    <div class='card' style='background:linear-gradient(135deg,#160A25,#1E0F35);border:1px solid #4A1A7A;margin-top:0.5rem'>
      <div style='font-size:13px;font-weight:700;color:{PURPLE};margin-bottom:8px'>
        💡 Strategic Recommendation 3 — Shift acquisition toward guests who actually stay
      </div>
      <div class='card-body'>
        • <strong>Reduce Portugal OTA spend</strong> — highest cancel rate, lowest effective revenue per booking<br>
        • <strong>Increase Germany & Belgium acquisition</strong> — most reliable at 20–22% cancel rate<br>
        • <strong>Create direct repeat guest incentive</strong> (rate priority, upgrade, recognition) — grow the {pct(repeat_share)} base that cancels at only {pct(direct_repeat_cr)}
      </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 5 — RECOMMENDATIONS & KEY TAKEAWAY
# ════════════════════════════════════════════════════════
with t5:
    sechdr("Strategic Recommendations")

    for color, num, obj, tagline, actions in [
        (GREEN, "01", "Reduce Cancellation Revenue Loss",
         "Flag high-risk bookings before they confirm",
         ["Prior cancellers → mandatory deposit before confirmation",
          "OTA non-refundable → treat as unconfirmed until deposit verified",
          "Flag data in PMS and apply stricter deposit terms automatically"]),
        (AMBER, "02", "Price for Real Demand Year-Round",
         "Reprice March–April to match real demand",
         ["Extend dynamic pricing beyond summer — activate for Mar–Jun and Sep–Oct",
          "Match ADR to capture rate, not season assumption",
          "Package off-season as experience bundles, not discounts"]),
        (PURPLE, "03", "Acquire Reliable, Retain Loyal Guest",
         "Shift acquisition toward guests who actually stay",
         ["Reduce Portugal OTA spend — highest cancel rate, lowest net revenue per booking",
          "Increase Germany & Belgium acquisition — most reliable at 19–22% cancel rate",
          "Create direct repeat guest incentive (rate, upgrade, recognition)"]),
    ]:
        actions_html = "".join(f"<div style='margin-bottom:4px'>• {a}</div>" for a in actions)
        st.markdown(f"""
        <div class='card' style='border-left:5px solid {color};margin-bottom:1rem'>
          <div style='display:flex;align-items:flex-start;gap:12px;margin-bottom:8px'>
            <span style='font-size:26px;font-weight:900;color:{color};line-height:1'>{num}</span>
            <div>
              <div style='font-size:14px;font-weight:700;color:#E0E6F0'>{obj}</div>
              <div style='font-size:12px;color:{color};font-style:italic;margin-top:2px'>"{tagline}"</div>
            </div>
          </div>
          <div class='card-body'>{actions_html}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    sechdr("🏁 Key Takeaway")

    for color, bullet, text in [
        (RED,    "A confirmed booking is NOT confirmed revenue",
                 f"Every booking marked 'non-refundable' carries real risk — {pct(nonref_cr)} cancel. "
                 "Revenue is only real after the guest checks out."),
        (AMBER,  "Our pricing is not applied beyond summer",
                 f"March–April demand matches June but ADR is ${jun_adr-mar_adr:,.0f} lower. "
                 "Pricing logic ignores actual capture signals in spring and autumn."),
        (PURPLE, "Our best guests are being ignored",
                 f"Direct repeat guests cancel at only {pct(direct_repeat_cr)} but represent just {pct(repeat_share)} of the base. "
                 "The most reliable segment is the least invested in."),
    ]:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {color}'>
          <div style='font-size:13px;font-weight:700;color:{color};margin-bottom:4px'>{bullet}</div>
          <div class='card-body'>{text}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='card' style='background:linear-gradient(135deg,#0A1020,#0D1A35);
         border:2px solid #2A3F6A;padding:1.5rem 2rem;margin-top:1rem;text-align:center'>
      <div style='font-size:17px;font-weight:800;color:#22D47B;line-height:1.75'>
        "We are not losing to the market.<br>
         We are losing to our own decisions &amp; strategy."
      </div>
    </div>""", unsafe_allow_html=True)
