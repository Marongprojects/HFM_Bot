import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf
from datetime import datetime
import xml.etree.ElementTree as ET
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="MARONG STOIC BOT SA", page_icon="🇿🇦", layout="wide")
SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
.stApp { background: #08080a; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
.glass { background: rgba(22,22,26,0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,215,0,0.15); border-radius: 16px; padding: 18px; }
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); box-shadow: 0 0 12px rgba(255,215,0,0.15); transition: transform 0.2s; }
.kpi:hover { transform: scale(1.02); }
.kpi-val { font-size: 24px; font-weight: 800; color: white; }
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

@st.cache_data(ttl=60)
def get_gold():
    try:
        df=yf.Ticker("GC=F").history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1]); atr=float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        ema50=float(df['Close'].ewm(50).mean().iloc[-1]); ema200=float(df['Close'].ewm(200).mean().iloc[-1])
        return df, price, atr, ema50, ema200
    except: return None, 4407.0, 5.5, 4400.0, 4385.0

@st.cache_data(ttl=60)
def get_forex(ticker, invert=False):
    try:
        df=yf.Ticker(ticker).history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1]); ema20=float(df['Close'].ewm(20).mean().iloc[-1]); ema100=float(df['Close'].ewm(100).mean().iloc[-1])
        sig = "BUY" if ema20>ema100 and price>ema20 else "SELL" if ema20<ema100 and price<ema20 else "WAIT"
        return price, sig, ema20, ema100
    except: 
        default = 18.5 if "ZAR" in ticker else 1.08
        return default, "WAIT", default, default

@st.cache_data(ttl=60)
def get_dxy():
    try:
        dxy_df=yf.Ticker("DX-Y.NYB").history(period="2d")
        dxy=float(dxy_df['Close'].iloc[-1]); chg=float(dxy_df['Close'].pct_change().iloc[-1]*100)
        return dxy, chg
    except: return 99.5, -0.15

def send_alert(msg):
    token=st.secrets.get("TELEGRAM_TOKEN",""); chat=st.secrets.get("TELEGRAM_CHAT_ID","")
    if token and chat:
        try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=5)
        except: pass

df_gold, price, atr, ema50, ema200 = get_gold()
eur_price, eur_sig, eur20, eur100 = get_forex("EURUSD=X")
zar_price, zar_sig, zar20, zar100 = get_forex("USDZAR=X") # SA PAIR
dxy, dxy_chg = get_dxy()
now = datetime.now(SAST)

# HEADER SA
st.markdown(f"""
<div class="glass" style="display:flex;justify-content:space-between;align-items:center;">
<div><span class="gold-text" style="font-size:22px;">⚔️ MARONG STOIC BOT</span> <span style="background:#007A4B;color:white;padding:3px 8px;border-radius:4px;margin-left:8px;">🇿🇦 SA EDITION</span></div>
<div style="text-align:right;"><span style="color:#FFD700;font-weight:700;">{now.strftime('%H:%M:%S')}</span> SAST<br><span style="font-size:11px;color:#00e676;">● RAND SMART ACTIVE</span></div>
</div>
""", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">${price:,.2f}</div><div style="font-size:12px;color:#888;">{ema50:.0f}/{ema200:.0f}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><div class="kpi-label">EURUSD CONFIRM</div><div class="kpi-val">{eur_price:.5f}</div><div style="font-size:12px;color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#888"}>{eur_sig}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><div class="kpi-label">USDZAR HOME 🇿🇦</div><div class="kpi-val">R{zar_price:.4f}</div><div style="font-size:12px;color:{"#00e676" if zar_sig=="SELL" else "#ff5252" if zar_sig=="BUY" else "#888"}>{zar_sig} {"= RAND STRONG" if zar_sig=="SELL" else ""}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi"><div class="kpi-label">DXY FUND</div><div class="kpi-val">{dxy:.2f}</div><div style="font-size:12px;color:{"#00e676" if dxy_chg<0 else "#ff5252"}>{dxy_chg:+.2f}%</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi"><div class="kpi-label">DISCIPLINE</div><div class="kpi-val">{len(st.session_state.trades)}/4</div><div style="font-size:12px;color:{"#ff5252" if len(st.session_state.trades)>=4 else "#00e676"}>{"LOCKED" if len(st.session_state.trades)>=4 else "READY"}</div></div>', unsafe_allow_html=True)

# CORE LOGIC UNCHANGED
setup_bull = ema50>ema200 and price>ema50
setup_bear = ema50<ema200 and price<ema50
fund_bull = dxy_chg < -0.08
fund_bear = dxy_chg > 0.08
session_ok = 10 <= now.hour < 20
agree_buy = setup_bull and fund_bull and session_ok
agree_sell = setup_bear and fund_bear and session_ok

# SA CONFIDENCE - ZAR SELL = GOLD BUY
conf = 0
if agree_buy or agree_sell: conf+=50
if eur_sig=="BUY" and agree_buy: conf+=25
if eur_sig=="SELL" and agree_sell: conf+=25
if zar_sig=="SELL" and agree_buy: conf+=25 # RAND STRONG = Dollar weak = Gold BUY
if zar_sig=="BUY" and agree_sell: conf+=25 # RAND WEAK = Dollar strong = Gold SELL

conf_label = f'<span class="conf-high">CONF {conf}% HIGH 🇿🇦</span>' if conf>=75 else f'<span class="conf-mid">CONF {conf}% MED</span>' if conf>=50 else f'<span class="conf-low">CONF {conf}% LOW</span>'

left, right = st.columns([1.7,1])
with left:
    tab1, tab2, tab3 = st.tabs(["⚔️ GOLD CORE", "🇪🇺 EURUSD", "🇿🇦 USDZAR - YOUR RAND"])
    with tab1:
        st.markdown(f'<div class="glass"> <div style="display:flex;justify-content:space-between;"><div class="kpi-label">SA SMART LOGIC</div><div>{conf_label}</div></div>', unsafe_allow_html=True)
        html="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AXAUUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe></div>"""
        st.components.v1.html(html, height=380)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        html2="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AEURUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe></div>"""
        st.components.v1.html(html2, height=380)
    with tab3:
        html3="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AUSDZAR&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg" style="width:100%;height:100%;border:0;border-radius:12px;"></iframe></div>"""
        st.components.v1.html(html3, height=380)

    st.write("")
    if len(st.session_state.trades)>=4:
        st.markdown(f'<div class="locked"><h3>🔒 SA PORTFOLIO LOCKED 4/4</h3><p>{", ".join(st.session_state.trades)}</p></div>', unsafe_allow_html=True)
    elif agree_buy:
        sl=price-atr*1.5; tp=price+(abs(price-sl)*2.5)
        badge = "HIGH CONVICTION 🇿🇦" if conf>=75 else "MEDIUM"
        st.markdown(f'<div class="buy-signal">🟢 ELITE BUY - {badge}<br><span style="font-size:13px;">{price:.2f} SL {sl:.2f} TP {tp:.2f} | {conf}% CONF | ZAR {zar_price:.4f}</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE BUY - SA EDITION"):
            st.session_state.trades.append(f"BUY {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *SA EDITION EXECUTED*\n🟢 BUY XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} USDZAR:{zar_sig} R{zar_price:.4f}\n{len(st.session_state.trades)}/4")
            st.rerun()
    elif agree_sell:
        sl=price+atr*1.5; tp=price-(abs(sl-price)*2.5)
        badge = "HIGH CONVICTION 🇿🇦" if conf>=75 else "MEDIUM"
        st.markdown(f'<div class="sell-signal">🔴 ELITE SELL - {badge}<br><span style="font-size:13px;">{price:.2f} SL {sl:.2f} TP {tp:.2f} | {conf}% CONF | ZAR {zar_price:.4f}</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE SELL - SA EDITION"):
            st.session_state.trades.append(f"SELL {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *SA EDITION EXECUTED*\n🔴 SELL XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} USDZAR:{zar_sig} R{zar_price:.4f}\n{len(st.session_state.trades)}/4")
            st.rerun()
    else:
        st.markdown(f'<div class="wait-signal"><h3>⚪ STOIC WAIT - SA CHECK</h3><p>Gold {setup_bull or setup_bear} | DXY {fund_bull or fund_bear} | EUR {eur_sig} | ZAR {zar_sig} (Need SELL for BUY) | Conf {conf}%</p></div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass"><div class="kpi-label">🇿🇦 RAND CALCULATOR</div>', unsafe_allow_html=True)
    bal_usd = st.number_input("Balance $ (Cent)", 10.0, 50000.0, 500.0)
    st.caption(f"≈ R{bal_usd*zar_price:,.2f} at R{zar_price:.2f}/$")
    risk = st.slider("Risk %", 0.5, 2.0, 1.0)
    rr = st.selectbox("RR", ["1:2","1:2.5","1:3"], index=1)
    rr_v = float(rr.split(":")[1])
    risk_amt = bal_usd * risk/100
    lots = max(0.01, min(risk_amt/((atr*1.5)*10), 2.0))
    st.markdown(f'<div style="margin-top:12px;background:#111;border-radius:10px;padding:12px;">USD Risk <span class="gold-text">${risk_amt:.2f}</span> ≈ R{risk_amt*zar_price:.2f}<br>Reward ${risk_amt*rr_v:.2f} ≈ R{risk_amt*rr_v*zar_price:.2f}<br>Lot <span class="gold-text">{lots:.2f}</span><br>CONF {conf}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">SA VOTE SYSTEM</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🥇 GOLD: {"BUY" if agree_buy else "SELL" if agree_sell else "WAIT"} (50%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🇪🇺 EURUSD: {eur_sig} (25%) - Must match Gold</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🇿🇦 USDZAR: {zar_sig} - Need <b>SELL</b> for Gold BUY (Rand Strong = Good)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
