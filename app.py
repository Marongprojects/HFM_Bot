import streamlit as st
import pytz
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import xml.etree.ElementTree as ET
from datetime import timedelta

st.set_page_config(page_title="STOIC HFM ELITE v3", page_icon="⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")

st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at top, #1a1a1e 0%, #0a0a0b 100%); color:white; }
h1 { color:#FFD700 !important; text-align:center; font-weight:900; letter-spacing:2px; }
.metric-card { background: linear-gradient(145deg,#1e1e22,#16161a); border:1px solid rgba(255,215,0,0.15); border-left:4px solid #FFD700; border-radius:16px; padding:15px; }
.news-bull { border-left:4px solid #00e676; background:#111; padding:10px; border-radius:8px; margin:5px 0; }
.news-bear { border-left:4px solid #ff1744; background:#111; padding:10px; border-radius:8px; margin:5px 0; }
.news-neutral { border-left:4px solid #888; background:#111; padding:10px; border-radius:8px; margin:5px 0; }
.stButton>button { background: linear-gradient(90deg,#D4AF37,#FFD700); color:black; font-weight:900; height:50px; border-radius:12px; width:100%; border:none; }
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
@st.cache_data(ttl=60)
def get_live_gold():
    try:
        data = yf.Ticker("GC=F").history(period="1d", interval="1m")
        price = data['Close'].iloc[-1]
        return float(price)
    except:
        return 2686.10

@st.cache_data(ttl=300)
def get_dxy_fundamental():
    try:
        dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
        dxy_change = yf.Ticker("DX-Y.NYB").history(period="2d")['Close'].pct_change().iloc[-1]*100
        bias = "BEARISH GOLD" if dxy_change > 0.1 else "BULLISH GOLD" if dxy_change < -0.1 else "NEUTRAL"
        return dxy, dxy_change, bias
    except:
        return 104.5, 0.0, "NEUTRAL"

@st.cache_data(ttl=180)
def get_bloomberg_news():
    news_list = []
    try:
        # Bloomberg Markets RSS
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://feeds.bloomberg.com/markets/news.rss"
        r = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(r.content)
        for item in root.findall('.//item')[:6]:
            title = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            # Sentiment
            bull_words = ["rally","gain","surge","up","bull","safe haven","rate cut"]
            bear_words = ["fall","drop","down","bear","hawkish","rate hike","strong dollar"]
            score = sum(1 for w in bull_words if w.lower() in title.lower()) - sum(1 for w in bear_words if w.lower() in title.lower())
            sentiment = "BULLISH" if score>0 else "BEARISH" if score<0 else "NEUTRAL"
            news_list.append({"title": title, "link": link, "sent": sentiment})
    except Exception as e:
        # Fallback to Yahoo Gold news if Bloomberg blocks
        try:
            ticker = yf.Ticker("GC=F")
            for n in ticker.news[:5]:
                title = n.get('title','')
                news_list.append({"title": f"[Yahoo Finance] {title}", "link": n.get('link',''), "sent": "NEUTRAL"})
        except:
            news_list.append({"title": "Bloomberg Feed Temporarily Blocked - Using DXY Bias Only", "link":"", "sent":"NEUTRAL"})
    return news_list

# --- HEADER ---
st.markdown("# ⚔️ STOIC HFM ELITE v3")
now_sast = datetime.now(SAST)
st.markdown(f"<p style='text-align:center;color:#888;'>Durban SAST {now_sast.strftime('%Y-%m-%d %H:%M:%S')} • Bloomberg Linked • Fundamentals + Sessions</p>", unsafe_allow_html=True)

# --- LIVE DATA ---
gold_price = get_live_gold()
dxy_price, dxy_chg, fund_bias = get_dxy_fundamental()
news = get_bloomberg_news()

# --- SESSION LOGIC ---
hour_sast = now_sast.hour
if 10 <= hour_sast < 13:
    session, session_ok, vol = "LONDON OPEN", True, "🔥 HIGH"
elif 15 <= hour_sast < 20:
    session, session_ok, vol = "NY / LONDON OVERLAP", True, "🔥🔥 EXTREME"
elif 3 <= hour_sast < 10:
    session, session_ok, vol = "ASIA / SYDNEY", False, "⚠️ LOW"
else:
    session, session_ok, vol = "OFF-HOURS", False, "LOW"

# --- METRICS ---
c1,c2,c3,c4 = st.columns(4)
c1.metric("GOLD XAUUSD LIVE", f"$ {gold_price:,.2f}", f"DXY {dxy_chg:+.2f}%")
c2.metric("FUNDAMENTAL BIAS", fund_bias, f"DXY {dxy_price:.2f}")
c3.metric("SESSION", session, vol)
c4.metric("BLOOMBERG SENTIMENT", f"{sum(1 for n in news if n['sent']=='BULLISH')} Bull / {sum(1 for n in news if n['sent']=='BEARISH')} Bear", "Live")

# --- ELITE DECISION ENGINE ---
st.write("---")
st.subheader("ELITE SETUP ENGINE - Pro Confluence")

bull_news = sum(1 for n in news if n['sent']=='BULLISH')
bear_news = sum(1 for n in news if n['sent']=='BEARISH')

if fund_bias == "BULLISH GOLD" and session_ok and bull_news >= bear_news:
    st.markdown(f'<div style="background:linear-gradient(90deg,#00c853,#00e676);color:black;padding:25px;border-radius:15px;text-align:center;font-weight:900;font-size:24px;">🟢 ELITE BUY • CONFLUENCE 3/3<br><span style="font-size:16px;">Price: {gold_price:.2f} | Fund: Bull | Session: {session} | Bloomberg: Bullish</span><br>Entry {gold_price:.2f} | SL {gold_price-4:.2f} | TP {gold_price+9:.2f}</div>', unsafe_allow_html=True)
    st.balloons()
elif fund_bias == "BEARISH GOLD" and session_ok and bear_news >= bull_news:
    st.markdown(f'<div style="background:linear-gradient(90deg,#ff1744,#ff5252);color:white;padding:25px;border-radius:15px;text-align:center;font-weight:900;font-size:24px;">🔴 ELITE SELL • CONFLUENCE 3/3<br><span style="font-size:16px;">Price: {gold_price:.2f} | Fund: Bear | Session: {session} | Bloomberg: Bearish</span><br>Entry {gold_price:.2f} | SL {gold_price+4:.2f} | TP {gold_price-9:.2f}</div>', unsafe_allow_html=True)
else:
    reason = []
    if not session_ok: reason.append(f"Bad Session ({session})")
    if fund_bias=="NEUTRAL": reason.append("Fundamentals Neutral")
    if bull_news==bear_news: reason.append("Bloomberg Mixed")
    st.markdown(f'<div style="background:#1e1e22;border:2px solid #FFD700;padding:20px;border-radius:15px;text-align:center;"><h3>⚪ NO TRADE - STOIC WAIT</h3><p style="color:#888;">Reason: {", ".join(reason) if reason else "Waiting for 3/3 confluence"}</p><p>Gold {gold_price:.2f} | {fund_bias} | {session}</p></div>', unsafe_allow_html=True)

# --- BLOOMBERG FEED ---
st.write("---")
st.subheader("📰 Bloomberg Live Feed - Gold / Dollar / Rates")
for n in news:
    css = "news-bull" if n['sent']=="BULLISH" else "news-bear" if n['sent']=="BEARISH" else "news-neutral"
    st.markdown(f'<div class="{css}"><b>{n["sent"]}</b> • {n["title"]}<br><a href="{n["link"]}" style="color:#FFD700;font-size:12px;">{n["link"][:60]}</a></div>', unsafe_allow_html=True)

# --- CHART ---
st.write("---")
chart = yf.Ticker("GC=F").history(period="1d", interval="5m")['Close'] if True else pd.DataFrame()
try:
    st.line_chart(chart, height=250)
except:
    st.info("Chart loading...")

if st.button("🔄 REFRESH ELITE SCAN"):
    st.cache_data.clear()
    st.rerun()
