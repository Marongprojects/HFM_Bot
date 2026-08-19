import streamlit as st
import pytz
from datetime import datetime
import time

st.set_page_config(page_title="STOIC HFM", page_icon="⚔️", layout="wide")

SAST = pytz.timezone("Africa/Johannesburg")

st.markdown("""
<style>
.stApp { background-color: #0A0A0B; }
h1 { color: #FFD700 !important; text-align: center; }
div[data-testid="metric-container"] {
 background: #1A1A1A;
 border-left: 4px solid #FFD700;
 border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ STOIC HFM LIVE")

# Live clock (updates every second)
clock = st.empty()
while True:
    clock.write(f"SAST Time: {datetime.now(SAST).strftime('%H:%M:%S')}")
    time.sleep(1)

# Metrics
st.metric("GOLD", "$ 4,391.50", "LIVE")
st.success("✅ APP FIXED - READY")

# User's Edge browser tabs metadata
edge_all_open_tabs = [
    {
        "pageTitle": "Editing HFM_Bot/app.py at main · Marongprojects/HFM_Bot",
        "pageUrl": "https://github.com/Marongprojects/HFM_Bot/edit/main/app.py",
        "tabId": 1176020989,
        "isCurrent": True
    },
    {
        "pageTitle": "STOIC HFM LIVE",
        "pageUrl": "http://127.0.0.1",
        "tabId": 1176020871,
        "isCurrent": False
    }
]
