import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf, os
from datetime import datetime
import xml.etree.ElementTree as ET
from streamlit_autorefresh import st_autorefresh

LOGO_FILE = "logo.png"
logo_exists = os.path.exists(LOGO_FILE)

st.set_page_config(page_title="MARONG STOIC BOT", page_icon=LOGO_FILE if logo_exists else "⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
.stApp { background: #08080a; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
.glass { background: rgba(22,22,26,0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,215,0,0.15); border-radius: 16px; padding: 18px; }
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); box-shadow: 0 0 12px rgba(255,215,0,0.15); }
.kpi-val { font-size: 28px; font-weight: 800; color: white; }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }
.gold-text { background: linear-gradient(90deg,#FFD700,#FFA500,#FFD700); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 6s linear infinite; font-weight: 900; }
@keyframes shine { 0% { background-position: 0% } 100% { background-position: 200% } }
.buy-signal { background: linear-gradient(135deg, #00c853, #00e676); color: black; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; }
.sell-signal { background: linear-gradient(135deg, #ff1744, #ff5252); color: white; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; }
.wait-signal { background: #16161a; border: 2px dashed #333; border-radius: 16px; padding: 24px; text-align: center; }
.locked { background: linear-gradient(135deg, #2a0a0a, #1a0a0a); border: 1px solid #ff1744; border-radius: 16px; padding: 20px; text-align: center; }
.conf-high { background: linear-gradient(90deg,#00c853,#00e676); color:black; padding:8px 14px; border-radius:20px; font-weight:900; }
.conf-mid { background: #333; color:#FFD700; padding:8px 14px; border-radius:20px; font-weight:900; border:1px solid #FFD700; }
.conf-low { background: #222; color:#888; padding:8px 14px; border-radius:20px; }
.stButton>button { background: linear-gradient(90deg,#D4AF37,#FFD700); color: black; font-weight: 900; height: 54px; border-radius: 12px; width: 100%; border: none; }
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "trades" not in st.session_state: st.session_state.trades=[]
if "last_reset" not in st.session_state: st.session_state.last_reset=datetime.now(SAST).date()
if datetime.now(SAST).date()!=st.session_state.last_reset:
    st.session_state.trades=[]; st.session_state.last_reset=datetime.now(SAST).date()

@st.cache_data(ttl=60)
def get_gold():
    try:
        df=yf.Ticker("GC=F").history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1]); atr=float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        ema50=float(df['Close'].ewm(50).mean().iloc[-1]); ema200=float(df['Close'].ewm(200).mean().iloc[-1])
        return df, price, atr, ema50, ema200
    except: return None, 4407.0, 5.5, 4400.0, 4385.0

@st.cache_data(ttl=60)
def get_forex(ticker):
    try:
        df=yf.Ticker(ticker).history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1]); ema20=float(df['Close'].ewm(20).mean().iloc[-1]); ema100=float(df['Close'].ewm(100).mean().iloc[-1])
        sig = "BUY" if ema20>ema100 and price>ema20 else "SELL" if ema20<ema100 and price<ema20 else "WAIT"
        return price, sig, ema20, ema100
    except: return 1.08, "WAIT", 1.08, 1.08

@st.cache_data(ttl=60)
def get_dxy():
    try:
        dxy_df=yf.Ticker("DX-Y.NYB").history(period="2d")
        dxy=float(dxy_df['Close'].iloc[-1]); chg=float(dxy_df['Close'].pct_change().iloc[-1]*100)
        return dxy, chg
    except: return 99.5, -0.15

def send_alert(msg):
    token=st.secrets.get("TELEGRAM_TOKEN",""); chat=st.secrets.get("TELEGRAM_CHAT_ID","")
    if token and chat:
        try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=5)
        except: pass

df_gold, price, atr, ema50, ema200 = get_gold()
eur_price, eur_sig, eur20, eur100 = get_forex("EURUSD=X")
gbp_price, gbp_sig, gbp20, gbp100 = get_forex("GBPUSD=X")
dxy, dxy_chg = get_dxy()
now = datetime.now(SAST)

# HEADER
c1, c2, c3 = st.columns([0.15, 0.60, 0.25])
with c1:
    if logo_exists:
        st.image(LOGO_FILE, width=75)
    else:
        st.markdown('<div style="font-size:40px">⚔️</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="margin-top:5px"><span class="gold-text" style="font-size:24px;">MARONG STOIC BOT</span><br><span style="color:#666;font-size:10px;letter-spacing:3px;">FINANCE • PROTECTION • STOIC</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="text-align:right;margin-top:8px"><span style="color:#FFD700;font-weight:700;">{now.strftime("%H:%M:%S")}</span> SAST<br><span style="font-size:11px;color:#00e676;">● VAULT SECURED</span></div>', unsafe_allow_html=True)

# KPIs - FIXED (no nested quotes)
k1,k2,k3,k4,k5 = st.columns(5)

with k1:
    st.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">${price:,.2f}</div><div style="font-size:12px;color:#888;">{ema50:.0f}/{ema200:.0f}</div></div>', unsafe_allow_html=True)

eur_color = "#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#888"
with k2:
    st.markdown(f'<div class="kpi"><div class="kpi-label">EURUSD WING</div><div class="kpi-val">{eur_price:.5f}</div><div style="font-size:12px;color:{eur_color}">{eur_sig}</div></div>', unsafe_allow_html=True)

gbp_color = "#00e676" if gbp_sig=="BUY" else "#ff5252" if gbp_sig=="SELL" else "#888"
with k3:
    st.markdown(f'<div class="kpi"><div class="kpi-label">GBPUSD WING</div><div class="kpi-val">{gbp_price:.5f}</div><div style="font-size:12px;color:{gbp_color}">{gbp_sig}</div></div>', unsafe_allow_html=True)

dxy_color = "#00e676" if dxy_chg<0 else "#ff5252"
with k4:
    st.markdown(f'<div class="kpi"><div class="kpi-label">DXY FUND</div><div class="kpi-val">{dxy:.2f}</div><div style="font-size:12px;color:{dxy_color}">{dxy_chg:+.2f}%</div></div>', unsafe_allow_html=True)

disc_color = "#ff5252" if len(st.session_state.trades)>=4 else "#00e676"
disc_text = "LOCKED" if len(st.session_state.trades)>=4 else "READY"
with k5:
    st.markdown(f'<div class="kpi"><div class="kpi-label">DISCIPLINE</div><div class="kpi-val">{len(st.session_state.trades)}/4</div><div style="font-size:12px;color:{disc_color}">{disc_text}</div></div>', unsafe_allow_html=True)

# CORE LOGIC
setup_bull = ema50>ema200 and price>ema50
setup_bear = ema50<ema200 and price<ema50
fund_bull = dxy_chg < -0.08
fund_bear = dxy_chg > 0.08
session_ok = 10 <= now.hour < 20
agree_buy = setup_bull and fund_bull and session_ok
agree_sell = setup_bear and fund_bear and session_ok

conf = 0
if agree_buy or agree_sell: conf+=50
if eur_sig=="BUY" and agree_buy: conf+=25
if eur_sig=="SELL" and agree_sell: conf+=25
if gbp_sig=="BUY" and agree_buy: conf+=25
if gbp_sig=="SELL" and agree_sell: conf+=25
if eur_sig=="WAIT": conf+=10
if gbp_sig=="WAIT": conf+=10

conf_label = f'<span class="conf-high">CONF {conf}% HIGH</span>' if conf>=75 else f'<span class="conf-mid">CONF {conf}% MED</span>' if conf>=50 else f'<span class="conf-low">CONF {conf}% LOW</span>'

left, right = st.columns([1.7,1])
with left:
    tab1, tab2, tab3 = st.tabs(["GOLD CORE", "EURUSD WING", "GBPUSD WING"])
    with tab1:
        st.markdown(f'<div class="glass"><div style="display:flex;justify-content:space-between;"><div class="kpi
