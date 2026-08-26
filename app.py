import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf, base64
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from pathlib import Path

# ── Page config ──────────────────────────────────────────────
_LOGO_PATH = Path(__file__).parent / "logo.png"
_logo_b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode() if _LOGO_PATH.exists() else ""
_page_icon = f"data:image/png;base64,{_logo_b64}" if _logo_b64 else "⚔️"

st.set_page_config(
    page_title="MARONG STOIC BOT",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://hfmbot-8hxcdrycoldue48qs2eoxy.streamlit.app/",
        "Report a bug": None,
        "About": "**MARONG STOIC BOT**\nPowered by yfinance & TradingView",
    },
)

SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }

/* KPI card — cleaned */
.kpi {
    background: #000;
    border-radius: 16px;
    padding: 18px;
    border: 2px solid #FFD700;
    transition: transform 0.2s ease-in-out;
}
.kpi:hover { transform: scale(1.02); }
.kpi-val { font-size: 24px; font-weight: 800; color: #FFD700; }
.kpi-label { font-size: 10px; color: #888; text-transform: uppercase; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Safe default content ─────────────────────────────────────
st.title("MARONG STOIC BOT")
st.write("✅ Dashboard is running. If you see this, the app is rendering correctly.")

# Example KPI section (always visible)
k1, k2, k3 = st.columns(3)
k1.markdown('<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">$1234.56</div></div>', unsafe_allow_html=True)
k2.markdown('<div class="kpi"><div class="kpi-label">EURUSD CONFIRM</div><div class="kpi-val">1.09876</div></div>', unsafe_allow_html=True)
k3.markdown('<div class="kpi"><div class="kpi-label">USDZAR HOME</div><div class="kpi-val">R18.50</div></div>', unsafe_allow_html=True)

# ── Continue with your trading logic below ──
