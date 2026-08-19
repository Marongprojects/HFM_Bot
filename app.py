import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf, os
from datetime import datetime
import xml.etree.ElementTree as ET
from streamlit_autorefresh import st_autorefresh

# --- LOGO PATH ---
LOGO = "logo.png" if os.path.exists("logo.png") else "⚔️"

st.set_page_config(page_title="MARONG STOIC BOT", page_icon=LOGO if os.path.exists("logo.png") else "⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

# --- CSS SHINE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
.stApp { background: #08080a; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
.glass { background: rgba(22,22,26,0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,215,0,0.15); border-radius: 16px; padding: 18px; }
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); box-shadow: 0 0 12px rgba(255,215,0,0.15); transition: transform 0.2s ease-in-out; }
.kpi:hover { transform: scale(1.02); }
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

@st.cache_data(ttl=120)
def bloomberg():
    try:
        r=requests.get("https://feeds.bloomberg.com/markets/news.rss", headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root=ET.fromstring(r.content)
        return [(item.find('title').text, item.find('link').text) for item in root.findall('.//item')[:6]]
    except: return [("Bloomberg: Dollar Softens","")]

def send_alert(msg):
    token=st.secrets.get("TELEGRAM_TOKEN",""); chat=st.secrets.get("TELEGRAM_CHAT_ID","")
    if token and chat:
        try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=5)
        except: pass

df_gold, price, atr, ema50, ema200 = get_gold()
eur_price, eur_sig, eur20, eur100 = get_forex("EURUSD=X")
gbp_price, gbp_sig, gbp20, gbp100 = get_forex("GBPUSD=X")
dxy, dxy_chg = get_dxy()
news = bloomberg()
now = datetime.now(SAST)

# --- HEADER WITH MARONG LOGO ---
c1, c2, c3 = st.columns([0.15, 0.60, 0.25])
with c1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=75)
    else:
        st.markdown('<div style="font-size:40px">⚔️</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="margin-top:5px"><span class="gold-text" style="font-size:24px;letter-spacing:1px;">MARONG STOIC BOT</span><br><span style="color:#666;font-size:10px;letter-spacing:3px;">FINANCE • PROTECTION • STOIC</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="text-align:right;margin-top:8px"><span style="color:#FFD700;font-weight:700;">{now.strftime("%H:%M:%S")}</span> SAST<br><span style="font-size:11px;color:#00e676;">● VAULT SECURED</span></div>', unsafe_allow_html=True)

# --- KPIs ---
k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">${price:,.2f}</div><div style="font-size
