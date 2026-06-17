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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #F0F4FF; color: #1A1F36; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

section[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E2E8F0; }

div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.08);
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] p,
div[data-testid="metric-container"] label {
    color: #6B7280 !important; font-size: 11px !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.08em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1A1F36 !important; font-size: 28px !important; font-weight: 800 !important;
}
div[data-testid="stTabs"] button {
    color: #6B7280 !important; font-size: 13px !important; font-weight: 500 !important;
    background: transparent;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #4F46E5 !important; border-bottom-color: #4F46E5 !important;
    font-weight: 700 !important;
}
div[data-testid="stTabs"] { border-bottom: 1px solid #E2E8F0; }
hr { border-color: #E2E8F0 !important; margin: 1.2rem 0 !important; }

.sechdr {
    font-size: 12px; font-weight: 700; color: #9CA3AF; text-transform: uppercase;
    letter-spacing: 0.08em; margin: 1.4rem 0 0.8rem;
    display: flex; align-items: center; gap: 8px;
}
.sechdr::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,#E2E8F0,transparent); }

.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 4px; }
.card-body { font-size: 13px; color: #374151; line-height: 1.65; }

.hero-banner {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.4rem;
    color: white;
}
.hero-banner * { color: white !important; }

.rec-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── COLORS ────────────────────────────────────────────────────────────────────
BLUE   = "#4F46E5"   # indigo
GREEN  = "#10B981"   # emerald
RED    = "#EF4444"   # red
AMBER  = "#F59E0B"   # amber
PURPLE = "#7C3AED"   # violet
CYAN   = "#06B6D4"   # cyan
PINK   = "#EC4899"   # pink
TEAL   = "#0D9488"   # teal

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FAFBFF",
    font=dict(family="Inter", color="#6B7280", size=12),
    margin=dict(t=30, b=10, l=10, r=10),
    xaxis=dict(gridcolor="#F3F4F6", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#F3F4F6", showline=False, zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#E2E8F0", font=dict(color="#374151")),
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E2E8F0", font=dict(color="#1A1F36")),
)

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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏨 Hotel Revenue Intelligence")
    st.markdown("---")
    st.markdown("### 📂 Upload Data Files")
    st.caption("Upload both Excel files to generate the analysis.")
    hotel_file    = st.file_uploader("Hotel data (cleaned_hotel_data.xlsx)",
                                     type=["xlsx","xls","csv"], key="hotel")
    arrivals_file = st.file_uploader("Arrivals data (cleaned_portugal_arrivals.xlsx)",
                                     type=["xlsx","xls","csv"], key="arrivals")

if not hotel_file or not arrivals_file:
    st.markdown("""
    <div class='hero-banner' style='text-align:center;padding:3.5rem 2rem'>
      <div style='font-size:52px;margin-bottom:1rem'>🏨</div>
      <div style='font-size:26px;font-weight:900;margin-bottom:8px'>Hotel Revenue Intelligence</div>
      <div style='font-size:15px;opacity:0.85;margin-bottom:2rem'>
        Revenue Optimization Analysis — Portugal Hospitality Market
      </div>
      <div style='font-size:13px;opacity:0.75;line-height:2;background:rgba(255,255,255,0.15);
           border-radius:10px;padding:1rem 1.5rem;display:inline-block'>
        👈 Open the <strong>sidebar</strong> and upload both files to begin:<br>
        1. cleaned_hotel_data.xlsx<br>
        2. cleaned_portugal_arrivals.xlsx
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

with st.spinner("Loading data…"):
    hotel, arrivals = load_data(hotel_file.getvalue(), arrivals_file.getvalue())

# ── PRE-COMPUTE GLOBALS ───────────────────────────────────────────────────────
conf_rev    = hotel['confirmed_rev'].sum()
lost_rev    = hotel['lost_rev'].sum()
cancel_rate = hotel['is_canceled'].mean() * 100
avg_adr     = hotel['adr'].mean()

nonref_cr       = hotel.loc[hotel['deposit_type']=='Non Refund','is_canceled'].mean()*100
direct_repeat_cr= hotel.loc[(hotel['distribution_channel']=='Direct') & (hotel['is_repeated_guest']==1),'is_canceled'].mean()*100
repeat_share    = hotel['is_repeated_guest'].mean()*100

bridge_tmp = hotel.groupby(['arrival_month','arrival_month_name']).agg(
    bookings=('is_canceled','count'), avg_adr=('adr','mean')
).reset_index()
arr_tmp = arrivals.groupby(['month','month_name']).agg(
    arrivals=('international_arrivals','mean')
).reset_index()
_bridge = bridge_tmp.merge(arr_tmp, left_on='arrival_month', right_on='month').sort_values('arrival_month')
mar_adr = _bridge.loc[_bridge['arrival_month']==3,'avg_adr'].values[0]
jun_adr = _bridge.loc[_bridge['arrival_month']==6,'avg_adr'].values[0]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-banner'>
  <div style='font-size:24px;font-weight:900;margin-bottom:4px'>🏨 Hotel Revenue Intelligence</div>
  <div style='font-size:13px;opacity:0.85'>Revenue Optimization Analysis — Portugal Hospitality Market · 2015–2017</div>
</div>""", unsafe_allow_html=True)

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

# ════════════════════════════════════════════════════════════════
# TAB 1 — OBJECTIVE
# ════════════════════════════════════════════════════════════════
with t1:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#4F46E5,#7C3AED);border-radius:14px;
         padding:1.5rem 2rem;margin-bottom:1.2rem;color:white'>
      <div style='font-size:20px;font-weight:800;margin-bottom:6px'>
        "Are we maximizing revenue… or just maximizing booking volume?"
      </div>
      <div style='font-size:13px;opacity:0.85'>
        Portugal's hospitality market is growing. But revenue isn't staying.
      </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col, num, color, bg, title, desc in zip(
        [c1,c2,c3], ["01","02","03"],
        [GREEN, BLUE, PINK],
        ["#ECFDF5","#EEF2FF","#FDF2F8"],
        ["Reduce Cancellation Revenue Loss",
         "Price for Real Demand Year-Round",
         "Acquire Reliable, Retain Loyal Guest"],
        ["Stop losing $1 for every $2 earned to booking cancellations.",
         "Extend dynamic pricing beyond the summer peak period only.",
         "Shift focus from booking volume to reliable, low-risk guest quality."],
    ):
        with col:
            st.markdown(f"""
            <div class='card' style='border-left:5px solid {color};background:{bg};min-height:130px'>
              <div style='font-size:32px;font-weight:900;color:{color};margin-bottom:6px'>{num}</div>
              <div style='font-size:14px;font-weight:700;color:#1A1F36;margin-bottom:6px'>{title}</div>
              <div style='font-size:12px;color:#6B7280;line-height:1.6'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    sechdr("Agenda")
    for n, label in [("01","Objective"),("02","Pain Points"),
                     ("03","Data-Driven Insights"),("04","Strategic Recommendations"),("05","Key Takeaway")]:
        st.markdown(
            f"<p style='color:#374151;font-size:13px;margin-bottom:6px;padding:6px 12px;"
            f"background:#F9FAFB;border-radius:6px;display:inline-block;margin-right:8px'>"
            f"<span style='color:{BLUE};font-weight:700'>{n}</span> &nbsp; {label}</p>",
            unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — CANCELLATION
# ════════════════════════════════════════════════════════════════
with t2:
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#FEF2F2,#FFF1F2);border:1px solid #FCA5A5;
         border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem'>
      <div style='font-size:18px;font-weight:800;color:{RED}'>🚨 Pain Point 1 — Money Out the Door</div>
      <div style='font-size:13px;color:#6B7280;margin-top:2px'>$11.31M lost from booking cancellations</div>
    </div>""", unsafe_allow_html=True)

    k1,k2,k3 = st.columns(3)
    k1.metric("✅ Confirmed Revenue", money(conf_rev))
    k2.metric("❌ Revenue Lost",      money(lost_rev))
    k3.metric("📉 Cancellation Rate", pct(cancel_rate))

    sechdr("Confirmed Revenue vs Cancellation Loss — monthly (2015–2017)")

    monthly = hotel.groupby(['arrival_month','arrival_month_name']).agg(
        conf=('confirmed_rev','sum'), lost=('lost_rev','sum')
    ).reset_index().sort_values('arrival_month')

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Confirmed Revenue", x=monthly['arrival_month_name'],
                         y=monthly['conf'], marker_color=BLUE, opacity=0.9))
    fig.add_trace(go.Bar(name="Revenue Lost", x=monthly['arrival_month_name'],
                         y=monthly['lost'], marker_color=RED, opacity=0.85))
    fig.update_layout(**{**CHART,"height":370,"barmode":"group",
                         "yaxis":{"tickprefix":"$","gridcolor":"#F3F4F6"}})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    c1,c2,c3 = st.columns(3)
    with c1:
        card(RED, "$11.31M lost — every $2 earned, $1 lost",
             "The revenue loss ratio is structural and consistent across all 12 months, not a seasonal spike.")
    with c2:
        card(AMBER, "28% cancellation rate runs year-round",
             "The rate stays between 25–33% every month. Seasonal policy changes alone won't fix it.")
    with c3:
        aug_conf = monthly.loc[monthly['arrival_month_name']=='August','conf'].values[0]
        aug_lost = monthly.loc[monthly['arrival_month_name']=='August','lost'].values[0]
        card(RED, "August: highest revenue AND highest loss",
             f"August generates the most revenue ({money(aug_conf)}) but also the most loss ({money(aug_lost)}).")

    st.markdown("---")
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
        fig2.update_traces(textposition='outside', textfont=dict(color='#374151'))
        fig2.update_layout(**{**CHART,"height":340,
                               "yaxis":{"ticksuffix":"%","range":[0,110],"gridcolor":"#F3F4F6"},
                               "coloraxis_showscale":False})
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
    with col_right:
        display_dep = dep[['deposit_type','cancel_rate','revenue_lost','total_bookings','avg_adr']].copy()
        display_dep['cancel_rate']   = display_dep['cancel_rate'].map(pct)
        display_dep['revenue_lost']  = display_dep['revenue_lost'].map(money)
        display_dep['avg_adr']       = display_dep['avg_adr'].map(lambda x: f"${x:,.2f}")
        display_dep.columns = ['Deposit Type','Cancel Rate','Revenue Lost','Bookings','Avg ADR']
        st.dataframe(display_dep, use_container_width=True, hide_index=True)

    card(RED, "Non-refundable bookings cancel at nearly 95%",
         f"<strong>{pct(dep.loc[dep['deposit_type']=='Non Refund','cancel_rate'].values[0])}</strong> of "
         "non-refundable bookings cancel. The label does not protect revenue.")
    card(AMBER, "No-deposit bookings create the largest revenue exposure",
         f"79,100 no-deposit bookings lost <strong>"
         f"{money(dep.loc[dep['deposit_type']=='No Deposit','revenue_lost'].values[0])}</strong> — "
         "the biggest absolute risk pool.")
    card(GREEN, "The label 'non-refundable' does not mean confirmed revenue",
         "Treat OTA non-refundable bookings as unconfirmed until a pre-arrival deposit is physically collected.")

    st.markdown(f"""
    <div class='rec-card' style='border-left:5px solid {GREEN};background:#ECFDF5'>
      <div style='font-size:13px;font-weight:700;color:{GREEN};margin-bottom:8px'>
        💡 Strategic Recommendation 1 — Flag high-risk bookings before they confirm
      </div>
      <div style='font-size:13px;color:#065F46;line-height:1.7'>
        • <strong>Prior cancellers → mandatory deposit</strong> before confirmation is accepted<br>
        • <strong>OTA non-refundable → treat as unconfirmed</strong> until deposit is verified<br>
        • Flag data in PMS and apply stricter deposit terms automatically
      </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 3 — PRICING / DEMAND
# ════════════════════════════════════════════════════════════════
with t3:
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FCD34D;
         border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem'>
      <div style='font-size:18px;font-weight:800;color:#92400E'>💰 Pain Point 2 — Missing the Moment</div>
      <div style='font-size:13px;color:#6B7280;margin-top:2px'>Rooms sold below peak demand value</div>
    </div>""", unsafe_allow_html=True)

    sechdr("Market Capture Rate vs Average Daily Rate (Jan–Dec, 2015–2017 avg)")

    hotel_avg = hotel.groupby(['arrival_month','arrival_month_name']).agg(
        bookings=('is_canceled','count'), avg_adr=('adr','mean')
    ).reset_index()
    arr_avg = arrivals.groupby(['month','month_name']).agg(
        arrivals=('international_arrivals','mean')
    ).reset_index()
    bridge = hotel_avg.merge(arr_avg, left_on='arrival_month', right_on='month')
    bridge['capture_rate'] = bridge['bookings'] / bridge['arrivals'] * 100
    bridge['arrival_month_name'] = pd.Categorical(bridge['arrival_month_name'], MONTH_ORDER, ordered=True)
    bridge = bridge.sort_values('arrival_month_name')

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(name="Market Capture Rate (%)", x=bridge['arrival_month_name'],
                         y=bridge['capture_rate'], marker_color=CYAN, opacity=0.7), secondary_y=False)
    fig.add_trace(go.Scatter(name="Avg ADR ($)", x=bridge['arrival_month_name'],
                             y=bridge['avg_adr'], mode='lines+markers',
                             line=dict(color=AMBER,width=3), marker=dict(size=8, color=AMBER)),
                  secondary_y=True)
    fig.update_yaxes(title_text="Market Capture Rate (%)", ticksuffix="%", secondary_y=False)
    fig.update_yaxes(title_text="Avg ADR ($)", tickprefix="$", secondary_y=True)
    fig.update_layout(**{**CHART,"height":390})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    mar_cap = bridge.loc[bridge['arrival_month_name']=='March','capture_rate'].values[0]
    jun_cap = bridge.loc[bridge['arrival_month_name']=='June','capture_rate'].values[0]
    mar_adr = bridge.loc[bridge['arrival_month_name']=='March','avg_adr'].values[0]
    jun_adr = bridge.loc[bridge['arrival_month_name']=='June','avg_adr'].values[0]

    card(RED, "March–April capture rate matches June, but ADR is $30–40 lower",
         f"March capture rate: <strong>{mar_cap:.2f}%</strong> vs June: <strong>{jun_cap:.2f}%</strong>. "
         f"But March ADR is <strong>${mar_adr:,.0f}</strong> vs June <strong>${jun_adr:,.0f}</strong> — "
         f"a gap of <strong>${jun_adr-mar_adr:,.0f}</strong>.")
    card(AMBER, "Dynamic pricing responds to summer only, not the full year",
         "ADR only rises materially from July–August. Spring and autumn demand signals are ignored by pricing logic.")
    card(GREEN, "Sufficient demand in shoulder season — revenue not being captured",
         "March and April have strong capture rates comparable to June. Pricing isn't reflecting this.")

    st.markdown("---")
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
        fig2.update_traces(textinfo='percent+label', textfont_color='white',
                           textfont_size=13)
        fig2.update_layout(**{**CHART,"height":340})
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
    with col_right:
        disp = season.copy()
        disp['revenue']      = disp['revenue'].map(money)
        disp['share']        = disp['share'].map(pct)
        disp['cancel_rate']  = disp['cancel_rate'].map(pct)
        disp['avg_adr']      = disp['avg_adr'].map(lambda x: f"${x:,.0f}")
        disp.columns = ['Season','Revenue','Cancel Rate','Avg ADR','Bookings','Share']
        st.dataframe(disp[['Season','Revenue','Share','Avg ADR','Cancel Rate','Bookings']],
                     use_container_width=True, hide_index=True)

    summer       = season.loc[season['season']=='Summer','revenue'].values[0]
    autumn       = season.loc[season['season']=='Autumn','revenue'].values[0]
    winter       = season.loc[season['season']=='Winter','revenue'].values[0]
    summer_share = season.loc[season['season']=='Summer','share'].values[0]
    total_rev    = hotel['confirmed_rev'].sum()

    card(CYAN, f"Summer generates {pct(summer_share)} of annual revenue in just 3 months",
         f"{money(summer)} from Jun–Aug alone. Revenue is heavily concentrated.")
    card(RED, "Autumn + Winter combined contribute less than 30%",
         f"{money(autumn)} + {money(winter)} = {money(autumn+winter)} "
         f"({pct((autumn+winter)/total_rev*100)}). Both seasons are under-priced relative to demand.")

    st.markdown(f"""
    <div class='rec-card' style='border-left:5px solid {AMBER};background:#FFFBEB'>
      <div style='font-size:13px;font-weight:700;color:#92400E;margin-bottom:8px'>
        💡 Strategic Recommendation 2 — Reprice March–April to match real demand
      </div>
      <div style='font-size:13px;color:#78350F;line-height:1.7'>
        • <strong>Extend dynamic pricing beyond summer</strong> — activate rate logic for Mar–Jun and Sep–Oct<br>
        • <strong>Match ADR to capture rate, not season assumption</strong> — let demand signal pricing<br>
        • <strong>Package off-season as experience bundles, not discounts</strong> — protect rate integrity
      </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — GUEST / MARKET MIX
# ════════════════════════════════════════════════════════════════
with t4:
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1px solid #C4B5FD;
         border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem'>
      <div style='font-size:18px;font-weight:800;color:{PURPLE}'>🎯 Pain Point 3 — Aiming at the Wrong Guests</div>
      <div style='font-size:13px;color:#6B7280;margin-top:2px'>Ignoring the guests who actually stay</div>
    </div>""", unsafe_allow_html=True)

    sechdr("Top 8 Source Markets — Confirmed Revenue vs Cancellation Rate")

    country = hotel.groupby('country').agg(
        conf_rev=('confirmed_rev','sum'), cancel_rate=('is_canceled','mean'),
        bookings=('is_canceled','count')
    ).reset_index()
    country['cancel_rate'] *= 100
    top8 = country.nlargest(8, 'conf_rev').reset_index(drop=True)

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(name="Confirmed Revenue ($M)", x=top8['country'],
                         y=top8['conf_rev']/1e6, marker_color=BLUE, opacity=0.85),
                  secondary_y=False)
    fig.add_trace(go.Scatter(name="Cancellation Rate (%)", x=top8['country'],
                             y=top8['cancel_rate'], mode='lines+markers',
                             line=dict(color=RED,width=3), marker=dict(size=9,color=RED)),
                  secondary_y=True)
    fig.update_yaxes(title_text="Confirmed Revenue ($M)", tickprefix="$", ticksuffix="M", secondary_y=False)
    fig.update_yaxes(title_text="Cancellation Rate (%)", ticksuffix="%", secondary_y=True)
    fig.update_layout(**{**CHART,"height":390})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    disp_c = top8[['country','conf_rev','cancel_rate','bookings']].copy()
    disp_c['conf_rev']    = disp_c['conf_rev'].map(money)
    disp_c['cancel_rate'] = disp_c['cancel_rate'].map(pct)
    disp_c.columns = ['Country','Confirmed Revenue','Cancel Rate','Bookings']
    st.dataframe(disp_c, use_container_width=True, hide_index=True)

    prt_cancel = top8.loc[top8['country']=='PRT','cancel_rate'].values[0]
    deu_cancel = top8.loc[top8['country']=='DEU','cancel_rate'].values[0]
    bel_cancel = top8.loc[top8['country']=='BEL','cancel_rate'].values[0]

    card(RED, f"Portugal: top revenue source, highest cancel rate at {pct(prt_cancel)}",
         "PRT generates the most confirmed revenue but cancels at 38% — the highest of all markets. High volume masks high risk.")
    card(GREEN, f"Germany & Belgium cancel at only {pct(deu_cancel)} / {pct(bel_cancel)} — most reliable",
         "DEU and BEL are far more reliable. Lower volume but stronger effective revenue per completed booking.")
    card(AMBER, "Shifting investment toward low-cancellation markets improves net revenue",
         "Investing more in DEU, BEL and GBR acquisition reduces leakage without needing to grow total booking volume.")

    st.markdown("---")
    sechdr("Highest-Risk Guest Segments by Cancellation Rate")

    hotel['prior_canceller'] = hotel['previous_cancellations'] > 0
    segments = {
        "Prior canceller · Any channel":      hotel['prior_canceller'],
        "Online TA · Non-refundable":         hotel['deposit_type'] == 'Non Refund',
        "Online TA · No deposit · Lead >90d": (hotel['market_segment']=='Online TA') & (hotel['deposit_type']=='No Deposit') & (hotel['lead_time']>90),
        "Groups · Holiday month":             (hotel['market_segment']=='Groups'),
        "Corp / GDS · Short lead":            (hotel['market_segment']=='Corporate') & (hotel['lead_time']<=7),
        "Online TA · General":                (hotel['market_segment']=='Online TA'),
        "Direct · Repeat guest":              (hotel['distribution_channel']=='Direct') & (hotel['is_repeated_guest']==1),
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
                  color_continuous_scale=[[0,GREEN],[0.15,GREEN],[0.4,AMBER],[0.7,RED],[1,'#B91C1C']],
                  text=seg_df['Cancel Rate (%)'].map(pct))
    fig2.update_traces(textposition='outside', textfont=dict(color='#374151'))
    fig2.update_layout(**{**CHART,"height":400,
                           "xaxis":{"ticksuffix":"%","range":[0,115],"gridcolor":"#F3F4F6"},
                           "coloraxis_showscale":False})
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    direct_repeat_cr = hotel.loc[(hotel['distribution_channel']=='Direct') & (hotel['is_repeated_guest']==1),'is_canceled'].mean()*100
    repeat_share     = hotel['is_repeated_guest'].mean()*100
    nonref_cr        = hotel.loc[hotel['deposit_type']=='Non Refund','is_canceled'].mean()*100

    card(RED, "Prior cancellers and OTA non-refundable bookings cancel at nearly 95%",
         f"OTA non-refundable: <strong>{pct(nonref_cr)}</strong> cancel rate. "
         "Both high-risk groups are identifiable before booking confirms.")
    card(GREEN, f"Direct repeat guests cancel at only {pct(direct_repeat_cr)} but represent {pct(repeat_share)} of the base",
         "The most reliable segment is the most under-invested. Growing this group is the highest-leverage action available.")

    st.markdown(f"""
    <div class='rec-card' style='border-left:5px solid {PURPLE};background:#F5F3FF'>
      <div style='font-size:13px;font-weight:700;color:{PURPLE};margin-bottom:8px'>
        💡 Strategic Recommendation 3 — Shift acquisition toward guests who actually stay
      </div>
      <div style='font-size:13px;color:#4C1D95;line-height:1.7'>
        • <strong>Reduce Portugal OTA spend</strong> — highest cancel rate, lowest net revenue per booking<br>
        • <strong>Increase Germany &amp; Belgium acquisition</strong> — most reliable at 19–22% cancel rate<br>
        • <strong>Create direct repeat guest incentive</strong> (rate priority, upgrade, recognition) — 
          grow the {pct(repeat_share)} base that cancels at only {pct(direct_repeat_cr)}
      </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 5 — RECOMMENDATIONS & TAKEAWAY
# ════════════════════════════════════════════════════════════════
with t5:
    sechdr("Strategic Recommendations")

    for color, bg, text_color, num, obj, tagline, actions in [
        (GREEN, "#ECFDF5", "#065F46", "01",
         "Reduce Cancellation Revenue Loss",
         "Flag high-risk bookings before they confirm",
         ["Prior cancellers → mandatory deposit before confirmation",
          "OTA non-refundable → treat as unconfirmed until deposit verified",
          "Flag data in PMS and apply stricter deposit terms automatically"]),
        (AMBER, "#FFFBEB", "#78350F", "02",
         "Price for Real Demand Year-Round",
         "Reprice March–April to match real demand",
         ["Extend dynamic pricing beyond summer — activate for Mar–Jun and Sep–Oct",
          "Match ADR to capture rate, not season assumption",
          "Package off-season as experience bundles, not discounts"]),
        (PURPLE, "#F5F3FF", "#4C1D95", "03",
         "Acquire Reliable, Retain Loyal Guest",
         "Shift acquisition toward guests who actually stay",
         ["Reduce Portugal OTA spend — highest cancel rate, lowest net revenue per booking",
          "Increase Germany & Belgium acquisition — most reliable at 19–22% cancel rate",
          "Create direct repeat guest incentive (rate, upgrade, recognition)"]),
    ]:
        actions_html = "".join(f"<div style='margin-bottom:5px'>• {a}</div>" for a in actions)
        st.markdown(f"""
        <div class='rec-card' style='border-left:5px solid {color};background:{bg}'>
          <div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:10px'>
            <span style='font-size:30px;font-weight:900;color:{color};line-height:1'>{num}</span>
            <div>
              <div style='font-size:15px;font-weight:700;color:#1A1F36'>{obj}</div>
              <div style='font-size:12px;color:{color};font-style:italic;margin-top:3px'>"{tagline}"</div>
            </div>
          </div>
          <div style='font-size:13px;color:{text_color};line-height:1.75'>{actions_html}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    sechdr("🏁 Key Takeaway")

    for color, bg, text_color, bullet, text in [
        (RED, "#FEF2F2", "#991B1B",
         "A confirmed booking is NOT confirmed revenue",
         f"Every booking marked 'non-refundable' carries real risk — {pct(nonref_cr)} cancel. "
         "Revenue is only real after the guest checks out."),
        (AMBER, "#FFFBEB", "#92400E",
         "Our pricing is not applied beyond summer",
         f"March–April demand matches June but ADR is ${jun_adr-mar_adr:,.0f} lower. "
         "Pricing logic ignores actual capture signals in spring and autumn."),
        (PURPLE, "#F5F3FF", "#5B21B6",
         "Our best guests are being ignored",
         f"Direct repeat guests cancel at only {pct(direct_repeat_cr)} but represent just {pct(repeat_share)} of the base. "
         "The most reliable segment is the least invested in."),
    ]:
        st.markdown(f"""
        <div class='rec-card' style='border-left:4px solid {color};background:{bg}'>
          <div style='font-size:13px;font-weight:700;color:{color};margin-bottom:4px'>{bullet}</div>
          <div style='font-size:13px;color:{text_color};line-height:1.65'>{text}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:linear-gradient(135deg,#4F46E5,#7C3AED,#EC4899);
         border-radius:16px;padding:2rem 2.5rem;margin-top:1.5rem;text-align:center'>
      <div style='font-size:19px;font-weight:900;color:white;line-height:1.8'>
        "We are not losing to the market.<br>
         We are losing to our own decisions &amp; strategy."
      </div>
    </div>""", unsafe_allow_html=True)
