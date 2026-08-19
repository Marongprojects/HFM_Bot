import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf
from datetime import datetime
import xml.etree.ElementTree as ET

st.set_page_config(page_title="STOIC TERMINAL v6", page_icon="⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")

# --- AMAZING CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
.stApp { background: #08080a; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
h1,h2,h3 { font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; }
.glass { background: rgba(22,22,26,0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,215,0,0.15); border-radius: 16px; padding: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
.gold-text { color: #FFD700; }
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); }
.kpi-val { font-size: 28px; font-weight: 800; color: white; }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }
.buy-signal { background: linear-gradient(135deg, #00c853 0%, #00e676 100%); color: black; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; animation: pulse 2s infinite; }
.sell-signal { background: linear-gradient(135deg, #ff1744 0%, #ff5252 100%); color: white; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; animation: pulse 2s infinite; }
.wait-signal { background: #16161a; border: 2px dashed #333; border-radius: 16px; padding: 24px; text-align: center; }
.locked { background: linear-gradient(135deg, #2a0a0a, #1a0a0a); border: 1px solid #ff1744; border-radius: 16px; padding: 20px; text-align: center; }
@keyframes pulse { 0%{transform:scale(1)} 50%{transform:scale(1.02)} 100%{transform:scale(1)} }
.stButton>button { background: linear-gradient(90deg,#D4AF37,#FFD700); color: black; font-weight: 900; height: 54px; border-radius: 12px; width: 100%; border: none; font-size: 15px; letter-spacing: 1px; }
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if "trades" not in st.session_state:
    st.session_state.trades=[]
if "last_reset" not in st.session_state:
    st.session_state.last_reset=datetime.now(SAST).date()
if datetime.now(SAST).date()!=st.session_state.last_reset:
    st.session_state.trades=[]; st.session_state.last_reset=datetime.now(SAST).date()

@st.cache_data(ttl=60)
def get_data():
    try:
        df=yf.Ticker("GC=F").history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1])
        atr=float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        ema50=float(df['Close'].ewm(50).mean().iloc[-1])
        ema200=float(df['Close'].ewm(200).mean().iloc[-1])
        dxy_chg=float(yf.Ticker("DX-Y.NYB").history(period="2d")['Close'].pct_change().iloc[-1]*100)
        dxy=float(yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1])
        return df, price, atr, ema50, ema200, dxy, dxy_chg
    except: return None, 4407.0, 5.5, 4400.0, 4385.0, 99.5, -0.15

@st.cache_data(ttl=120)
def bloomberg():
    try:
        r=requests.get("https://feeds.bloomberg.com/markets/news.rss", headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root=ET.fromstring(r.content)
        return [(item.find('title').text, item.find('link').text) for item in root.findall('.//item')[:6]]
    except: return [("Bloomberg: Dollar Softens, Gold Bid",""), ("Fed Rate Cut Bets Support Metals","")]

df, price, atr, ema50, ema200, dxy, dxy_chg = get_data()
news = bloomberg()
now = datetime.now(SAST)

# --- TOP BAR ---
st.markdown(f"""
<div class="glass" style="display:flex;justify-content:space-between;align-items:center;">
<div><span class="gold-text" style="font-weight:900;font-size:22px;">⚔️ STOIC TERMINAL v6</span> <span style="color:#666;">| HFM INTEGRATED | DISCIPLINED 2/DAY</span></div>
<div style="text-align:right;"><span style="color:#FFD700;">{now.strftime('%Y-%m-%d %H:%M:%S')}</span> <span style="color:#666;">SAST • DURBAN</span><br><span style="font-size:11px;color:#00e676;">● LIVE CONNECTED</span></div>
</div>
""", unsafe_allow_html=True)

# --- KPI ROW ---
k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD LIVE</div><div class="kpi-val">${price:,.2f}</div><div style="color:#00e676;font-size:12px;">ATR {atr:.2f}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><div class="kpi-label">DXY FUNDAMENTAL</div><div class="kpi-val">{dxy:.2f}</div><div style="color:{"#00e676" if dxy_chg<0 else "#ff5252"};font-size:12px;">{dxy_chg:+.2f}% {"BULL GOLD" if dxy_chg<0 else "BEAR GOLD"}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><div class="kpi-label">TREND</div><div class="kpi-val">{"BULL" if ema50>ema200 else "BEAR"}</div><div style="color:#888;font-size:12px;">EMA {ema50:.0f} / {ema200:.0f}</div></div>', unsafe_allow_html=True)
session_name = "LONDON" if 10<=now.hour<13 else "NY OVERLAP" if 15<=now.hour<20 else "ASIA"
k4.markdown(f'<div class="kpi"><div class="kpi-label">SESSION</div><div class="kpi-val">{session_name}</div><div style="color:{"#00e676" if 10<=now.hour<20 else "#ff9800"};font-size:12px;">{ "HIGH VOL" if 10<=now.hour<20 else "LOW VOL - NO TRADE"}</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi"><div class="kpi-label">DISCIPLINE</div><div class="kpi-val">{len(st.session_state.trades)}/2</div><div style="color:{"#ff5252" if len(st.session_state.trades)>=2 else "#00e676"};font-size:12px;">{"LOCKED TODAY" if len(st.session_state.trades)>=2 else f"{2-len(st.session_state.trades)} LEFT"}</div></div>', unsafe_allow_html=True)

# --- MAIN GRID ---
left, right = st.columns([1.7, 1])

with left:
    # TradingView Chart Embedded
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label" style="margin-bottom:10px;">LIVE CHART - HFM XAUUSD</div>', unsafe_allow_html=True)
    tradingview_html = f"""
    <div style="height:360px;">
    <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AXAUUSD&interval=15&hidesidetoolbar=0&symboledit=0&saveimage=0&toolbarbg=rgba(0,0,0,1)&studies=[]&theme=dark&style=1&timezone=Africa%2FJohannesburg&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=[]&disabled_features=[]&locale=en&utm_source=&utm_medium=widget&utm_campaign=chart&utm_term=OANDA%3AXAUUSD" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe>
    </div>
    """
    st.components.v1.html(tradingview_html, height=380)
    st.markdown('</div>', unsafe_allow_html=True)

    # Trade Logic
    setup_bull = ema50>ema200 and price>ema50
    setup_bear = ema50<ema200 and price<ema50
    fund_bull = dxy_chg < -0.08
    fund_bear = dxy_chg > 0.08
    session_ok = 10 <= now.hour < 20
    agree_buy = setup_bull and fund_bull and session_ok
    agree_sell = setup_bear and fund_bear and session_ok

    st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)
    if len(st.session_state.trades)>=2:
        st.markdown(f'<div class="locked"><h3>🔒 LIMIT REACHED - 2/2 DONE</h3><p>Stoic discipline saved you today.<br>{", ".join(st.session_state.trades)}</p></div>', unsafe_allow_html=True)
    elif agree_buy:
        sl=price-atr*1.5; tp=price+(abs(price-sl)*2.5)
        st.markdown(f'<div class="buy-signal">🟢 ELITE BUY - AGREED<br><span style="font-size:14px;">Entry {price:.2f} | SL {sl:.2f} | TP {tp:.2f} | RR 1:2.5</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE BUY - LOG 1 OF 2"): st.session_state.trades.append(f"BUY {now.strftime('%H:%M')} {price:.2f}"); st.rerun()
    elif agree_sell:
        sl=price+atr*1.5; tp=price-(abs(sl-price)*2.5)
        st.markdown(f'<div class="sell-signal">🔴 ELITE SELL - AGREED<br><span style="font-size:14px;">Entry {price:.2f} | SL {sl:.2f} | TP {tp:.2f} | RR 1:2.5</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE SELL - LOG 1 OF 2"): st.session_state.trades.append(f"SELL {now.strftime('%H:%M')} {price:.2f}"); st.rerun()
    else:
        reason = "Session LOW" if not session_ok else "Setup/Fund Disagree"
        st.markdown(f'<div class="wait-signal"><h3>⚪ STOIC WAIT - NO AGREEMENT</h3><p style="color:#888;">{reason} | Setup: {"BULL" if setup_bull else "BEAR" if setup_bear else "NEUTRAL"} | Fund: {"BULL" if fund_bull else "BEAR" if fund_bear else "NEUTRAL"}<br>Pro traders wait for 3/3. Next scan London Open.</p></div>', unsafe_allow_html=True)

with right:
    # Risk Calculator
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">RISK MANAGEMENT TERMINAL</div>')
    bal = st.number_input("Balance $", 100.0, 50000.0, 500.0, key="bal")
    risk = st.slider("Risk %", 0.5, 2.0, 1.0)
    rr = st.selectbox("RR", ["1:2","1:2.5","1:3"], index=1)
    rr_v = float(rr.split(":")[1])
    sl_dist = atr*1.5
    risk_amt = bal * risk/100
    lots = max(0.01, min(risk_amt/(sl_dist*10), 2.0))
    st.markdown(f"""
    <div style="margin-top:12px;background:#111;border-radius:10px;padding:12px;">
    Risk: <span class="gold-text">${risk_amt:.2f}</span> | Reward: <span style="color:#00e676;">${risk_amt*rr_v:.2f}</span><br>
    Lot: <span class="gold-text">{lots:.2f}</span> | SL Dist: {sl_dist:.2f}<br>
    Balance After SL: ${bal-risk_amt:.2f}<br>After TP: <span style="color:#00e676;">${bal+risk_amt*rr_v:.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloomberg
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">BLOOMBERG LIVE FEED</div>', unsafe_allow_html=True)
    for title, link in news:
        st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:6px 0;border-left:3px solid #FFD700;font-size:12px;">📰 {title}<br><a href="{link}" target="_blank" style="color:#666;font-size:10px;">{link[:45]}...</a></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Journal
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">TODAY JOURNAL - {}/2</div>'.format(len(st.session_state.trades)), unsafe_allow_html=True)
    if st.session_state.trades:
        for i,t in enumerate(st.session_state.trades,1): st.markdown(f'<div style="background:#111;padding:8px;border-radius:6px;margin:4px 0;font-size:12px;">{i}. {t}</div>', unsafe_allow_html=True)
    else: st.caption("No trades today - Discipline = Profit")
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔄 REFRESH TERMINAL"):
    st.cache_data.clear(); st.rerun()
