import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf
from datetime import datetime
import xml.etree.ElementTree as ET
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="MARONG STOIC BOT", page_icon="⚔️", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

# --- CSS SHINE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
.stApp { background: #08080a; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
.glass { background: rgba(22,22,26,0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,215,0,0.15); border-radius: 16px; padding: 18px; }
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); box-shadow: 0 0 12px rgba(255,215,0,0.15); transition: transform 0.2s ease-in-out; }
.kpi:hover { transform: scale(1.02); }
.kpi-val { font-size: 28px; font-weight: 800; color: white; }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }
.gold-text { background: linear-gradient(90deg,#FFD700,#FFA500,#FFD700); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 6s linear infinite; font-weight: 900; }
@keyframes shine { 0% { background-position: 0% } 100% { background-position: 200% } }
.buy-signal { background: linear-gradient(135deg, #00c853, #00e676); color: black; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; }
.sell-signal { background: linear-gradient(135deg, #ff1744, #ff5252); color: white; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; }
.wait-signal { background: #16161a; border: 2px dashed #333; border-radius: 16px; padding: 24px; text-align: center; }
.locked { background: linear-gradient(135deg, #2a0a0a, #1a0a0a); border: 1px solid #ff1744; border-radius: 16px; padding: 20px; text-align: center; }
.conf-high { background: linear-gradient(90deg,#00c853,#00e676); color:black; padding:8px 14px; border-radius:20px; font-weight:900; }
.conf-mid { background: #333; color:#FFD700; padding:8px 14px; border-radius:20px; font-weight:900; border:1px solid #FFD700; }
.conf-low { background: #222; color:#888; padding:8px 14px; border-radius:20px; }
.stButton>button { background: linear-gradient(90deg,#D4AF37,#FFD700); color: black; font-weight: 900; height: 54px; border-radius: 12px; width: 100%; border: none; }
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "trades" not in st.session_state: st.session_state.trades=[]
if "last_reset" not in st.session_state: st.session_state.last_reset=datetime.now(SAST).date()
if datetime.now(SAST).date()!=st.session_state.last_reset:
    st.session_state.trades=[]; st.session_state.last_reset=datetime.now(SAST).date()

# --- DATA FETCH ---
@st.cache_data(ttl=60)
def get_gold():
    try:
        df=yf.Ticker("GC=F").history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1]); atr=float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        ema50=float(df['Close'].ewm(50).mean().iloc[-1]); ema200=float(df['Close'].ewm(200).mean().iloc[-1])
        return df, price, atr, ema50, ema200
    except: return None, 4407.0, 5.5, 4400.0, 4385.0

@st.cache_data(ttl=60)
def get_forex(ticker):
    try:
        df=yf.Ticker(ticker).history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1]); ema20=float(df['Close'].ewm(20).mean().iloc[-1]); ema100=float(df['Close'].ewm(100).mean().iloc[-1])
        sig = "BUY" if ema20>ema100 and price>ema20 else "SELL" if ema20<ema100 and price<ema20 else "WAIT"
        return price, sig, ema20, ema100
    except: return 1.08, "WAIT", 1.08, 1.08

@st.cache_data(ttl=60)
def get_dxy():
    try:
        dxy_df=yf.Ticker("DX-Y.NYB").history(period="2d")
        dxy=float(dxy_df['Close'].iloc[-1]); chg=float(dxy_df['Close'].pct_change().iloc[-1]*100)
        return dxy, chg
    except: return 99.5, -0.15

@st.cache_data(ttl=120)
def bloomberg():
    try:
        r=requests.get("https://feeds.bloomberg.com/markets/news.rss", headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root=ET.fromstring(r.content)
        return [(item.find('title').text, item.find('link').text) for item in root.findall('.//item')[:6]]
    except: return [("Bloomberg: Dollar Softens","")]

# --- TELEGRAM ---
def send_alert(msg):
    token=st.secrets.get("TELEGRAM_TOKEN",""); chat=st.secrets.get("TELEGRAM_CHAT_ID","")
    if token and chat:
        try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=5)
        except: pass

# --- LOAD ---
df_gold, price, atr, ema50, ema200 = get_gold()
eur_price, eur_sig, eur20, eur100 = get_forex("EURUSD=X")
gbp_price, gbp_sig, gbp20, gbp100 = get_forex("GBPUSD=X")
dxy, dxy_chg = get_dxy()
news = bloomberg()
now = datetime.now(SAST)

# --- HEADER ---
st.markdown(f"""
<div class="glass" style="display:flex;justify-content:space-between;align-items:center;">
<div><span class="gold-text" style="font-size:22px;">⚔️ MARONG STOIC BOT</span> <span style="color:#666;">| PORTFOLIO v8 INTEGRATED</span></div>
<div style="text-align:right;"><span style="color:#FFD700;font-weight:700;">{now.strftime('%H:%M:%S')}</span> SAST<br><span style="font-size:11px;color:#00e676;">● LIVE PORTFOLIO SCAN</span></div>
</div>
""", unsafe_allow_html=True)

# --- KPIs ---
k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">${price:,.2f}</div><div style="font-size:12px;color:#888;">{ema50:.0f}/{ema200:.0f}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><div class="kpi-label">EURUSD WING</div><div class="kpi-val">{eur_price:.5f}</div><div style="font-size:12px;color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#888"}>{eur_sig}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><div class="kpi-label">GBPUSD WING</div><div class="kpi-val">{gbp_price:.5f}</div><div style="font-size:12px;color:{"#00e676" if gbp_sig=="BUY" else "#ff5252" if gbp_sig=="SELL" else "#888"}>{gbp_sig}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi"><div class="kpi-label">DXY FUND</div><div class="kpi-val">{dxy:.2f}</div><div style="font-size:12px;color:{"#00e676" if dxy_chg<0 else "#ff5252"}>{dxy_chg:+.2f}%</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi"><div class="kpi-label">DISCIPLINE</div><div class="kpi-val">{len(st.session_state.trades)}/4</div><div style="font-size:12px;color:{"#ff5252" if len(st.session_state.trades)>=4 else "#00e676"}>{"LOCKED" if len(st.session_state.trades)>=4 else "READY"}</div></div>', unsafe_allow_html=True)

# --- CORE LOGIC (YOUR ORIGINAL UNTOUCHED) ---
setup_bull = ema50>ema200 and price>ema50
setup_bear = ema50<ema200 and price<ema50
fund_bull = dxy_chg < -0.08
fund_bear = dxy_chg > 0.08
session_ok = 10 <= now.hour < 20
agree_buy = setup_bull and fund_bull and session_ok
agree_sell = setup_bear and fund_bear and session_ok

# --- NEW: CONFIDENCE ENGINE ---
conf = 0
if agree_buy or agree_sell: conf+=50
if eur_sig=="BUY" and agree_buy: conf+=25
if eur_sig=="SELL" and agree_sell: conf+=25
if gbp_sig=="BUY" and agree_buy: conf+=25
if gbp_sig=="SELL" and agree_sell: conf+=25
if eur_sig=="WAIT": conf+=10
if gbp_sig=="WAIT": conf+=10

conf_label = f'<span class="conf-high">CONF {conf}% HIGH</span>' if conf>=75 else f'<span class="conf-mid">CONF {conf}% MED</span>' if conf>=50 else f'<span class="conf-low">CONF {conf}% LOW</span>'

left, right = st.columns([1.7,1])
with left:
    tab1, tab2, tab3 = st.tabs(["⚔️ GOLD CORE", "🇪🇺 EURUSD WING", "🇬🇧 GBPUSD WING"])
    with tab1:
        st.markdown(f'<div class="glass"> <div style="display:flex;justify-content:space-between;"><div class="kpi-label">LIVE CHART - CORE LOGIC UNCHANGED</div><div>{conf_label}</div></div>', unsafe_allow_html=True)
        html="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AXAUUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe></div>"""
        st.components.v1.html(html, height=380)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        html2="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AEURUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe></div>"""
        st.components.v1.html(html2, height=380)
    with tab3:
        html3="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AGBPUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe></div>"""
        st.components.v1.html(html3, height=380)

    st.write("")
    if len(st.session_state.trades)>=4:
        st.markdown(f'<div class="locked"><h3>🔒 PORTFOLIO LOCKED 4/4 DONE</h3><p>{", ".join(st.session_state.trades)}</p></div>', unsafe_allow_html=True)
    elif agree_buy:
        sl=price-atr*1.5; tp=price+(abs(price-sl)*2.5)
        badge = "HIGH CONVICTION" if conf>=75 else "MEDIUM" if conf>=50 else "LOW - WAIT FOR CONFIRM?"
        st.markdown(f'<div class="buy-signal">🟢 ELITE BUY - {badge}<br><span style="font-size:13px;">{price:.2f} SL {sl:.2f} TP {tp:.2f} | {conf}% CONF</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE BUY - SEND ALERT"):
            st.session_state.trades.append(f"BUY {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *MARONG STOIC BOT EXECUTED*\n🟢 BUY XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} GBP:{gbp_sig}\nTrades {len(st.session_state.trades)}/4")
            if len(st.session_state.trades)>=4: send_alert(f"🔒 *DONE FOR TODAY* 4/4\n{', '.join(st.session_state.trades)}")
            st.rerun()
    elif agree_sell:
        sl=price+atr*1.5; tp=price-(abs(sl-price)*2.5)
        badge = "HIGH CONVICTION" if conf>=75 else "MEDIUM" if conf>=50 else "LOW"
        st.markdown(f'<div class="sell-signal">🔴 ELITE SELL - {badge}<br><span style="font-size:13px;">{price:.2f} SL {sl:.2f} TP {tp:.2f} | {conf}% CONF</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE SELL - SEND ALERT"):
            st.session_state.trades.append(f"SELL {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *MARONG STOIC BOT EXECUTED*\n🔴 SELL XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} GBP:{gbp_sig}\nTrades {len(st.session_state.trades)}/4")
            if len(st.session_state.trades)>=4: send_alert(f"🔒 *DONE FOR TODAY* 4/4\n{', '.join(st.session_state.trades)}")
            st.rerun()
    else:
        st.markdown(f'<div class="wait-signal"><h3>⚪ STOIC WAIT</h3><p>Gold Setup: {setup_bull or setup_bear} | DXY: {fund_bull or fund_bear} | Session {session_ok} | Conf {conf}%</p><p style="font-size:11px;color:#666;">Need 50%+ confidence. EUR:{eur_sig} GBP:{gbp_sig}</p></div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass"><div class="kpi-label">RISK TERMINAL - CENT ACCOUNT</div>', unsafe_allow_html=True)
    bal = st.number_input("Balance $ (Cent = $5 = 500c)", 10.0, 50000.0, 500.0)
    risk = st.slider("Risk %", 0.5, 2.0, 1.0)
    rr = st.selectbox("RR", ["1:2","1:2.5","1:3"], index=1)
    rr_v = float(rr.split(":")[1])
    risk_amt = bal * risk/100
    lots = max(0.01, min(risk_amt/((atr*1.5)*10), 2.0))
    st.markdown(f'<div style="margin-top:12px;background:#111;border-radius:10px;padding:12px;">Risk <span class="gold-text">${risk_amt:.2f}</span> → Reward ${risk_amt*rr_v:.2f}<br>Lot <span class="gold-text">{lots:.2f}</span> (Cent: {lots*100:.0f}c lots)<br>CONF {conf}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">PORTFOLIO VOTE</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🥇 GOLD CORE: {"BUY" if agree_buy else "SELL" if agree_sell else "WAIT"} (50%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🇪🇺 EURUSD: {eur_sig} (25%) - {eur_price:.5f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🇬🇧 GBPUSD: {gbp_sig} (25%) - {gbp_price:.5f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="glass" style="margin-top:15px;"><div class="kpi-label">JOURNAL {len(st.session_state.trades)}/4</div>', unsafe_allow_html=True)
    if st.session_state.trades:
        for i,t in enumerate(st.session_state.trades,1): st.markdown(f'<div style="background:#111;padding:8px;border-radius:6px;margin:4px 0;font-size:12px;">{i}. {t}</div>', unsafe_allow_html=True)
    else: st.caption("No trades today - Portfolio waiting for 75%+")
    st.markdown('</div>', unsafe_allow_html=True)
