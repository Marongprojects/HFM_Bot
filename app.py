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
st_autorefresh(interval=1000, key="clock
