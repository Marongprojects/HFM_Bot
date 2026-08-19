import streamlit as st
import pytz, requests, yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="MARONG STOIC BOT SA", page_icon="🇿🇦", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

# --- Styling ---
st.markdown("""
<style>
.stApp { background: #08080a; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
.glass { background: rgba(22,22,26,0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,215,0,0.15); border-radius: 16px; padding: 18px; }
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); box-shadow: 0 0 12px rgba(255,215,0,0.15); }
.kpi-val { font-size: 24px; font-weight: 800; color: white; }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }
.gold-text { background: linear-gradient(90deg,#FFD700,#FFA500,#FFD700); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine
