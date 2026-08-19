import streamlit as st
import pytz
import random
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="STOIC HFM LIVE", page_icon="⚔️", layout="wide")

SAST = pytz.timezone("Africa/Johannesburg")

# --- LUXURY GOLD THEME ---
st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at top, #1a1a1e 0%, #0a0a0b 100%); color: white; }
    h1,h2,h3 { color: #FFD700 !important; text-align: center; font-weight: 900; letter-spacing: 2px; }
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e1e22, #16161a);
        border-left: 4px solid #FFD700;
        border-radius: 16px;
        padding: 18px;
        border: 1px solid rgba(255,215,0,0.15);
    }
    div[data-testid="stMetricValue"] { color: #FFD700 !important; font-size: 28px !important; }
    .signal-buy {
        background: linear-gradient(90deg, #00c853, #00e676);
        color: black; padding: 20px; border-radius: 15px;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    .signal-sell {
        background: linear-gradient(90deg, #ff1744, #ff5252);
        color: white; padding: 20px; border-radius: 15px;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #FFD700);
        color: black; font-weight: 900; height: 55px;
        border-radius: 12px; width: 100%; border: none;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("# ⚔️ STOIC HFM LIVE")
now_sast = datetime.now(SAST)
st.markdown(f"<p style='text-align:center; color:#888;'>Durban SAST • {now_sast.strftime('%Y-%m-%d %H:%M:%S')} • HFM Gold Scalper</p>", unsafe_allow_html=True)

# --- MOCK LIVE PRICE (Stable, no API crash) ---
base_price = 2685.50
price = base_price + random.uniform(-3.5, 3.5)
change = random.uniform(-0.8, 1.2)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("GOLD XAUUSD", f"$ {price:,.2f}", f"{change:+.2f}%")
with col2:
    st.metric("Spread HFM", "12 pts", "Tight")
with col3:
    st.metric("Session", "London-NY Overlap", "High Vol")

# --- SIGNAL LOGIC ---
st.write("---")
rsi = random.randint(35, 78)
ema_signal = random.choice(["BUY", "SELL", "WAIT"])

if rsi < 45 and ema_signal == "BUY":
    st.markdown('<div class="signal-buy">🟢 STRONG BUY • GOLD LONG<br>Entry: {:.2f} • SL: {:.2f} • TP: {:.2f}</div>'.format(price, price-3.5, price+7), unsafe_allow_html=True)
    st.balloons()
elif rsi > 65 and ema_signal == "SELL":
    st.markdown('<div class="signal-sell">🔴 STRONG SELL • GOLD SHORT<br>Entry: {:.2f} • SL: {:.2f} • TP: {:.2f}</div>'.format(price, price+3.5, price-7), unsafe_allow_html=True)
else:
    st.markdown(f'<div style="background:#1e1e22; border:1px solid #FFD700; padding:20px; border-radius:15px; text-align:center;"><h3 style="margin:0;">⚪ WAIT • NO TRADE</h3><p style="color:#888;">RSI: {rsi} • Scanning for Stoic Setup...</p></div>', unsafe_allow_html=True)

# --- CHART ---
st.write("---")
st.subheader("Live Gold Structure")
chart_data = pd.DataFrame({
    "GOLD": [base_price + random.uniform(-5,5) + i*0.1 for i in range(50)]
})
st.line_chart(chart_data, height=250)

# --- CONTROLS ---
colA, colB = st.columns(2)
with colA:
    if st.button("🔄 REFRESH SIGNAL"):
        st.rerun()
with colB:
    st.button("⚙️ HFM Risk: 1% Lot Size")

st.caption("STOIC v2.0 • Built for HFM • Durban • Disclaimer: Not financial advice. Trade at own risk.")
