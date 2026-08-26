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

# ── Global CSS / Shell ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace !important; }
.stApp { background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #000 !important;
    border-right: 1px solid #FFD700 !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* Topbar */
.topbar {
    background: #000;
    border-bottom: 2px solid #FFD700;
    padding: 14px 24px;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 18px;
}

/* Logo */
.logo-img { height: 52px; border-radius: 50%; border: 2px solid #FFD700; }
.logo-sm  { height: 100px; border-radius: 50%; border: 3px solid #FFD700; display: block; margin: 0 auto 10px; }

/* Gold shimmer text */
.gold-text {
    background: linear-gradient(90deg, #FFD700 0%, #FFA500 30%, #FFD700 60%, #FFEC6E 80%, #FFD700 100%);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 5s linear infinite;
}
@keyframes shine { to { background-position: 300% center; } }

/* Glass card */
.glass {
    background: rgba(0,0,0,0.8);
    border: 1px solid #FFD700;
    border-radius: 18px;
    padding: 18px;
}

/* KPI card — cleaned */
.kpi {
    background: #000;
    border-radius: 16px;
    padding: 18px;
    border: 2px solid #FFD700;
    transition: transform 0.2s ease-in-out;
}
.kpi:hover { transform: scale(1.02); }
.kpi-val { font-size: 24px; font-weight: 800; color: #FFD700; letter-spacing: -0.5px; }
.kpi-label { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 4px; }

/* Signals */
.buy-signal { background:#001a00; border:2px solid #00e676; border-radius:18px; padding:24px; text-align:center; font-weight:900; font-size:22px; color:#00ff87; }
.sell-signal { background:#1a0000; border:2px solid #ff1744; border-radius:18px; padding:24px; text-align:center; font-weight:900; font-size:22px; color:#ff6b6b; }
.wait-signal { background:#0a0a0a; border:2px dashed #333; border-radius:18px; padding:24px; text-align:center; color:#666; }

/* Confidence badges */
.conf-high { background:linear-gradient(90deg,#00c853,#00e676); color:#000; padding:8px 16px; border-radius:22px; font-weight:900; }
.conf-mid { background:#1a1a00; color:#FFD700; padding:8px 16px; border-radius:22px; font-weight:900; border:1px solid #FFD700; }
.conf-low { background:#1a1a1a; color:#888; padding:8px 16px; border-radius:22px; border:1px solid #333; }
.conf-verylow { background:#1a0505; color:#ff5252; padding:8px 16px; border-radius:22px; border:1px solid #ff5252; }

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #B8860B, #FFD700, #B8860B) !important;
    color: #000 !important; font-weight: 900 !important;
    border-radius: 12px !important; border: none !important;
    transition: background-position 0.4s !important;
}
.stButton > button:hover { background-position: right center !important; }
</style>
""", unsafe_allow_html=True)

# ── Your Python logic continues below (unchanged) ──
