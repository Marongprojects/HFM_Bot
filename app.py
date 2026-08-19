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
    .stApp {
        background: radial-gradient(ellipse at top, #1a1a1e 0%, #0a0a0b 100%);
        color: #fff;
    }
    h1,h2,h3 { 
        color: #FFD700 !important; 
        font-weight: 900;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(255,215,0,0.4);
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e1e22, #16161a);
        border: 1px solid rgba(255,215,0,0.15);
        border-left: 4px solid #FFD700;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    div[data-testid="stMetricValue"] { 
        color: #FFD700 !important; 
        font-size: 30px !important; 
        font-weight: 800;
    }
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #FFD700);
        color: #000;
        font-weight: 900;
        border-radius: 12px;
        border: none;
        height: 55px;
        width: 100%;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

SAST = pytz.timezone("Africa/Johannesburg")        padding: 25px;
        text-align: center;
        box-shadow: 0 0 40px rgba(255,215,0,0.2);
    }
</style>
""", unsafe_allow_html=True)
