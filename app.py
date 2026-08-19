import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf
from datetime import datetime
import xml.etree.ElementTree as ET

st.set_page_config(page_title="STOIC v5 DISCIPLINED", page_icon="⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")

st.markdown("""
<style>
.stApp { background:#0a0a0b; color:white; }
h1 { color:#FFD700!important; text-align:center; font-weight:900; letter-spacing:2px; }
.card { background:#16161a; border:1px solid #222; border-left:4px solid #FFD700; border-radius:12px; padding:16px; }
.locked { background:#2a0a0a; border:2px solid #ff1744; padding:20px; border-radius:12px; text-align:center; }
.buy-box { background:linear-gradient(90deg,#00c853,#00e676); color:black; padding:22px; border-radius:14px; text-align:center; font-weight:900; font-size:20px; }
.sell-box { background:linear-gradient(90deg,#ff1744,#ff5252); color:white; padding:22px; border-radius:14px; text-align:center; font-weight:900; font-size:20px; }
.stButton>button { background:linear-gradient(90deg,#D4AF37,#FFD700); color:black; font-weight:900; height:55px; border-radius:12px; width:100%; border:none; }
</style>
""", unsafe_allow_html=True)

# --- DISCIPLINE STATE ---
if "trades_today" not in st.session_state:
    st.session_state.trades_today = []
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now(SAST).date()

# Auto reset at midnight SAST
today = datetime.now(SAST).date()
if st.session_state.last_reset != today:
    st.session_state.trades_today = []
    st.session_state.last_reset = today

# --- SIDEBAR RISK ---
st.sidebar.title("⚔️ DISCIPLINE")
balance = st.sidebar.number_input("Balance ($)", 100.0, 100000.0, 500.0)
risk_pct = st.sidebar.slider("Risk %", 0.5, 2.0, 1.0)
rr_choice = st.sidebar.selectbox("RR", ["1:2", "1:2.5", "1:3"], index=1)
rr_val = float(rr_choice.split(":")[1])

st.sidebar.markdown("---")
st.sidebar.metric("Trades Today", f"{len(st.session_state.trades_today)}/2")
if len(st.session_state.trades_today)>=2:
    st.sidebar.error("🔒 DAILY LIMIT HIT - No more trades today")
else:
    st.sidebar.success(f"✅ {2-len(st.session_state.trades_today)} trades left")

if st.sidebar.button("Reset Daily Counter"):
    st.session_state.trades_today = []
    st.rerun()

@st.cache_data(ttl=60)
def get_market():
    try:
        df = yf.Ticker("GC=F").history(period="5d", interval="15m")
        price = float(df['Close'].iloc[-1])
        atr = float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        ema50 = float(df['Close'].ewm(50).mean().iloc[-1])
        ema200 = float(df['Close'].ewm(200).mean().iloc[-1])
        dxy_chg = float(yf.Ticker("DX-Y.NYB").history(period="2d")['Close'].pct_change().iloc[-1]*100)
        dxy = float(yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1])
        return price, atr, ema50, ema200, dxy, dxy_chg
    except:
        return 4407.0, 5.0, 4400.0, 4380.0, 99.5, -0.15

@st.cache_data(ttl=180)
def get_bloomberg():
    try:
        r=requests.get("https://feeds.bloomberg.com/markets/news.rss", headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root=ET.fromstring(r.content)
        return [item.find('title').text for item in root.findall('.//item')[:5]]
    except:
        return ["Bloomberg: Fed Watch", "Dollar Weakness Supports Gold"]

price, atr, ema50, ema200, dxy, dxy_chg = get_market()
news = get_bloomberg()
now = datetime.now(SAST)

# --- HEADER ---
st.markdown("# ⚔️ STOIC v5 - DISCIPLINED 2x DAILY")
st.markdown(f"<p style='text-align:center;color:#888;'>{now.strftime('%Y-%m-%d %H:%M:%S SAST')} | Max 2 Trades/Day | Setup + Fundamentals Must Agree</p>", unsafe_allow_html=True)

c1,c2,c3 = st.columns(3)
c1.metric("GOLD LIVE", f"${price:,.2f}")
c2.metric("FUNDAMENTAL", f"DXY {dxy:.2f} ({dxy_chg:+.2f}%)", "BULL GOLD" if dxy_chg<-0.1 else "BEAR GOLD")
c3.metric("DISCIPLINE", f"{len(st.session_state.trades_today)}/2 Taken", "LOCKED" if len(st.session_state.trades_today)>=2 else "READY")

# --- ELITE AGREEMENT CHECK ---
st.write("---")
st.subheader("🔍 Setup + Fundamentals Agreement (Must BOTH Agree)")

setup_bull = ema50 > ema200 and price > ema50
setup_bear = ema50 < ema200 and price < ema50
fund_bull = dxy_chg < -0.1
fund_bear = dxy_chg > 0.1
session_ok = 10 <= now.hour < 20

st.markdown(f"""
<div class="card">
<b>TECHNICAL SETUP:</b> {'🟢 BULLISH' if setup_bull else '🔴 BEARISH' if setup_bear else '⚪ NEUTRAL'} (EMA50 {ema50:.1f} vs EMA200 {ema200:.1f})<br>
<b>FUNDAMENTAL:</b> {'🟢 BULLISH GOLD' if fund_bull else '🔴 BEARISH GOLD' if fund_bear else '⚪ NEUTRAL'} (DXY {dxy_chg:+.2f}%)<br>
<b>SESSION:</b> {'✅ London/NY' if session_ok else '❌ Asia/Off-Hours - WAIT'}<br>
<b>AGREEMENT:</b> {'✅ <span style="color:#00e676;">SETUP + FUNDAMENTAL AGREE</span>' if (setup_bull and fund_bull) or (setup_bear and fund_bear) else '❌ NO AGREEMENT - NO TRADE'}
</div>
""", unsafe_allow_html=True)

agree_buy = setup_bull and fund_bull and session_ok
agree_sell = setup_bear and fund_bear and session_ok

# --- TRADE LOGIC WITH 2 MAX ---
if len(st.session_state.trades_today) >= 2:
    st.markdown(f'<div class="locked"><h2>🔒 DAILY LIMIT REACHED - 2/2 TRADES DONE</h2><p>Stoic discipline: No more trades today. Protect capital.<br>Trades taken: {", ".join(st.session_state.trades_today)}<br>Reset at midnight SAST</p></div>', unsafe_allow_html=True)
else:
    if agree_buy or agree_sell:
        direction = "BUY" if agree_buy else "SELL"
        sl = price - atr*1.5 if direction=="BUY" else price + atr*1.5
        tp = price + abs(price-sl)*rr_val if direction=="BUY" else price - abs(price-sl)*rr_val
        risk_amt = balance * risk_pct/100
        lots = max(0.01, min(risk_amt / (abs(price-sl)*10), 2.0))
        profit = risk_amt * rr_val

        box_class = "buy-box" if direction=="BUY" else "sell-box"
        st.markdown(f'<div class="{box_class}">⚔️ ELITE {direction} - CONFLUENCE AGREED<br>Entry {price:.2f} | SL {sl:.2f} | TP {tp:.2f}<br>RISK ${risk_amt:.2f} ({risk_pct}%) → REWARD ${profit:.2f} | RR {rr_choice}<br>LOT {lots:.2f} | Trades {len(st.session_state.trades_today)+1}/2</div>', unsafe_allow_html=True)
        
        if st.button(f"✅ CONFIRM TAKE {direction} TRADE - Count as 1 of 2"):
            st.session_state.trades_today.append(f"{direction} {now.strftime('%H:%M')} @ {price:.2f} RR {rr_choice}")
            st.success(f"Trade logged! {len(st.session_state.trades_today)}/2 used today.")
            st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center;"><h3>⚪ NO AGREEMENT - NO TRADE</h3><p style="color:#888;">Pro rule: Setup and Fundamentals must point SAME direction.<br>Currently they disagree or session bad. Waiting = Winning.</p></div>')

# --- TODAY'S LOG ---
st.write("---")
st.subheader(f"📓 Today's Trades ({len(st.session_state.trades_today)}/2 Max)")
if st.session_state.trades_today:
    for i,t in enumerate(st.session_state.trades_today,1):
        st.markdown(f"<div class='card'>{i}. {t}</div>", unsafe_allow_html=True)
else:
    st.caption("No trades taken today yet. Discipline.")

st.write("Bloomberg Context:")
for t in news[:3]:
    st.caption(f"📰 {t}")

if st.button("🔄 RE-SCAN MARKET"):
    st.cache_data.clear()
    st.rerun()
