import streamlit as st
import datetime
import pytz
import random
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="STOIC HFM LIVE", page_icon="⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")

st.markdown("""
<style>
.stApp { background-color: #0e0e0e; color: #D4AF37; }
h1,h2,h3 { color: #D4AF37!important; }
div[data-testid="stMetricValue"] { color: #D4AF37; font-size: 32px; }
.stButton>button { background: linear-gradient(90deg, #D4AF37, #FFD700); color: black; font-weight: bold; width: 100%; height: 50px; border: none; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_gold_price():
    try:
        gold = yf.Ticker("GC=F")
        hist = gold.history(period="1d", interval="1m")
        if hist.empty:
            raise ValueError("No data")
        price = float(hist["Close"].iloc[-1])
        prev = float(hist["Open"].iloc[0])
        change = ((price - prev) / prev) * 100 if prev else 0.0
        return round(price, 2), round(change, 2), hist
    except Exception:
        fallback = pd.DataFrame({"Close": [2650.0, 2651.5, 2649.8, 2653.1, 2652.4]})
        return 2650.0, 0.0, fallback

if 'bot_data' not in st.session_state:
    st.session_state.bot_data = {
        "daily_pnl": 0.0,
        "winrate": 0,
        "bias": "ANALYZING...",
        "status": "DISCIPLINE LOCK",
        "trades": [],
        "equity": [10000],
    }

def get_sast():
    return datetime.datetime.now(SAST)

def take_trade(signal):
    win = random.random() < 0.55
    r = round(random.uniform(1.5, 2.5) if win else random.uniform(-1.2, -0.5), 2)
    st.session_state.bot_data["trades"].append({
        "time": get_sast().strftime("%H:%M"),
        "signal": signal,
        "result": "WIN" if win else "LOSS",
        "r": r,
    })
    total = len(st.session_state.bot_data["trades"])
    wins = len([t for t in st.session_state.bot_data["trades"] if t["result"] == "WIN"])
    st.session_state.bot_data["winrate"] = round((wins / total) * 100, 1)
    st.session_state.bot_data["daily_pnl"] = round(sum([t["r"] for t in st.session_state.bot_data["trades"]]), 2)
    st.session_state.bot_data["equity"].append(st.session_state.bot_data["equity"][-1] + (r * 10))
    st.session_state.bot_data["bias"] = "BUY GOLD" if signal == "BUY" else "SELL GOLD"
    st.session_state.bot_data["status"] = "TRADE EXECUTED"

gold_price, gold_change, hist = get_gold_price()
data = st.session_state.bot_data
now = get_sast()

st.markdown(f"<h1 style='text-align:center;'>⚔️ YOU ARE WHAT YOU THINK - LIVE GOLD</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#888;'> {now.strftime('%A, %d %b %Y %H:%M:%S')} SAST | HFM GOLD BOT | DISCIPLINE > EMOTION </p>", unsafe_allow_html=True)
st.divider()

c1, c2, c3, c4 = st.columns(4)
c1.metric("LIVE GOLD", f"${gold_price:,.2f}", f"{gold_change:+.2f}%")
c2.metric("Daily P&L", f"{data['daily_pnl']}R", f"{data['trades'][-1]['r']}R" if data['trades'] else "0R")
c3.metric("Winrate", f"{data['winrate']}%", "55% TARGET")
c4.metric("Equity", f"${data['equity'][-1]:,.2f}")

left, right = st.columns([2, 1])

with left:
    st.subheader("📈 LIVE GOLD PRICE")
    st.line_chart(hist[["Close"]], height=260)
    signal = "BUY" if gold_change >= 0 else "SELL"
    st.info(f"**CURRENT SIGNAL:** {signal}")

    buy_col, sell_col = st.columns(2)
    with buy_col:
        st.button("BUY GOLD", on_click=take_trade, args=("BUY",), type="primary")
    with sell_col:
        st.button("SELL GOLD", on_click=take_trade, args=("SELL",), type="secondary")

    if len(data["trades"]) >= 5:
        st.warning("⛔ DAILY LIMIT HIT - PROTECT CAPITAL.")

with right:
    st.subheader("🧠 STOIC LOG")
    st.write("**Marcus Aurelius:** _'You have power over your mind - not outside events. Realize this, and you will find strength.'_")
    st.divider()
    if data["trades"]:
        df = pd.DataFrame(data["trades"][::-1])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No trades yet. Waiting for the next setup.")
    st.divider()
    st.caption("Account: HFM Demo | Symbol: XAUUSD | Risk: 1% per trade")

st.divider()
st.markdown("<p style='text-align:center; color:#555;'>Built with Discipline in Durban, SA 🇿🇦 | v1.0 Stoic</p>", unsafe_allow_html=True)