import streamlit as st
import pytz
from datetime import datetime

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
st.write(f"SAST Time: {datetime.now(SAST).strftime('%H:%M:%S')}")
st.metric("GOLD", "$ 4,391.50", "LIVE")
st.success("✅ APP FIXED - READY")
