import streamlit as st
import pytz, requests, pandas as pd, yfinance as yf, base64
from datetime import datetime
import xml.etree.ElementTree as ET
from streamlit_autorefresh import st_autorefresh
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
_LOGO_PATH = Path(__file__).parent / "logo.png"
_logo_b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode() if _LOGO_PATH.exists() else ""
_page_icon = f"data:image/png;base64,{_logo_b64}" if _logo_b64 else "⚔️"

st.set_page_config(
    page_title="MARONG STOIC BOT SA",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://hfmbot-8hxcdrycoldue48qs2eoxy.streamlit.app/",
        "Report a bug": None,
        "About": "**MARONG STOIC BOT** — SA Edition 🇿🇦\nPowered by yfinance & TradingView",
    },
)
SAST = pytz.timezone("Africa/Johannesburg")
st_autorefresh(interval=1000, key="clock")

# ── Global CSS / Shell ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&display=swap');

/* ── Base ──────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace !important; }
.stApp {
    background: radial-gradient(ellipse at top, #0d0d12 0%, #08080a 60%);
    color: #e0e0e0;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Sidebar shell ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c0c10 0%, #111116 100%) !important;
    border-right: 1px solid rgba(255,215,0,0.18) !important;
    box-shadow: 4px 0 24px rgba(255,215,0,0.06);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── Top navigation bar ─────────────────────────────────── */
.topbar {
    background: linear-gradient(90deg, #0a0a0d 0%, #111116 50%, #0a0a0d 100%);
    border-bottom: 2px solid;
    border-image: linear-gradient(90deg, transparent, #FFD700, #FFA500, #FFD700, transparent) 1;
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
}
.topbar::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 40px,
        rgba(255,215,0,0.015) 40px,
        rgba(255,215,0,0.015) 41px
    );
    pointer-events: none;
}

/* ── Logo in header ─────────────────────────────────────── */
.logo-img { height: 52px; border-radius: 50%; border: 2px solid rgba(255,215,0,0.5); box-shadow: 0 0 16px rgba(255,215,0,0.3); }
.logo-sm  { height: 100px; border-radius: 50%; border: 3px solid rgba(255,215,0,0.6); box-shadow: 0 0 30px rgba(255,215,0,0.25); display: block; margin: 0 auto 10px; }

/* ── Gold shimmer text ──────────────────────────────────── */
.gold-text {
    background: linear-gradient(90deg, #FFD700 0%, #FFA500 30%, #FFD700 60%, #FFEC6E 80%, #FFD700 100%);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shine 5s linear infinite;
}
@keyframes shine { to { background-position: 300% center; } }

/* ── Glass card ─────────────────────────────────────────── */
.glass {
    background: rgba(18,18,22,0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,215,0,0.14);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
}

/* ── KPI card ───────────────────────────────────────────── */
.kpi {
    background: linear-gradient(145deg, #1a1a1e, #101012);
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #1e1e22;
    border-top: 2px solid rgba(255,215,0,0.35);
    box-shadow: 0 0 18px rgba(255,215,0,0.07), 0 4px 12px rgba(0,0,0,0.6);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 0 28px rgba(255,215,0,0.18); }
.kpi-val { font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
.kpi-label { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 4px; }

/* ── Signal boxes ───────────────────────────────────────── */
.buy-signal {
    background: linear-gradient(135deg, #004d1f, #007a33);
    border: 2px solid #00e676;
    border-radius: 18px; padding: 24px; text-align: center;
    font-weight: 900; font-size: 22px; color: #00ff87;
    box-shadow: 0 0 30px rgba(0,198,83,0.3);
    animation: pulse-green 2s ease-in-out infinite;
}
@keyframes pulse-green { 0%,100%{box-shadow:0 0 30px rgba(0,198,83,0.3)} 50%{box-shadow:0 0 50px rgba(0,230,118,0.5)} }

.sell-signal {
    background: linear-gradient(135deg, #4d0010, #8b0020);
    border: 2px solid #ff1744;
    border-radius: 18px; padding: 24px; text-align: center;
    font-weight: 900; font-size: 22px; color: #ff6b6b;
    box-shadow: 0 0 30px rgba(255,23,68,0.3);
    animation: pulse-red 2s ease-in-out infinite;
}
@keyframes pulse-red { 0%,100%{box-shadow:0 0 30px rgba(255,23,68,0.3)} 50%{box-shadow:0 0 50px rgba(255,82,82,0.5)} }

.wait-signal {
    background: linear-gradient(135deg, #0e0e12, #16161c);
    border: 2px dashed #2a2a32;
    border-radius: 18px; padding: 24px; text-align: center;
    color: #666;
}

.locked {
    background: linear-gradient(135deg, #2a0a0a, #1a0a0a);
    border: 1px solid #ff1744; border-radius: 18px; padding: 20px; text-align: center;
}

.killswitch {
    background: linear-gradient(135deg, #3d0000, #8b0000);
    border: 2px solid #ff1744; border-radius: 18px; padding: 28px; text-align: center;
    font-weight: 900; font-size: 18px; color: white;
    animation: ks-pulse 1s ease-in-out infinite;
    box-shadow: 0 0 40px rgba(255,23,68,0.4);
}
@keyframes ks-pulse { 0%,100%{opacity:1} 50%{opacity:0.75} }

/* ── Confidence badges ──────────────────────────────────── */
.conf-high    { background: linear-gradient(90deg,#00c853,#00e676); color:black; padding:8px 16px; border-radius:22px; font-weight:900; box-shadow:0 0 12px rgba(0,200,83,0.35); }
.conf-mid     { background: #1e1e00; color:#FFD700; padding:8px 16px; border-radius:22px; font-weight:900; border:1px solid #FFD700; }
.conf-low     { background: #1a1a1a; color:#888; padding:8px 16px; border-radius:22px; border:1px solid #333; }
.conf-verylow { background: #1a0505; color:#ff5252; padding:8px 16px; border-radius:22px; border:1px solid #ff5252; }

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(90deg, #B8860B, #D4AF37, #FFD700, #D4AF37, #B8860B) !important;
    background-size: 200% auto !important;
    color: #000 !important;
    font-weight: 900 !important;
    font-family: 'JetBrains Mono', monospace !important;
    height: 54px !important;
    border-radius: 12px !important;
    width: 100% !important;
    border: none !important;
    letter-spacing: 1px !important;
    transition: background-position 0.4s, box-shadow 0.3s !important;
    box-shadow: 0 2px 12px rgba(212,175,55,0.35) !important;
}
.stButton > button:hover {
    background-position: right center !important;
    box-shadow: 0 0 22px rgba(255,215,0,0.55) !important;
}

/* ── Sidebar nav items ──────────────────────────────────── */
.sb-nav-item {
    background: rgba(255,215,0,0.04);
    border: 1px solid rgba(255,215,0,0.1);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 12px;
    color: #ccc;
    cursor: default;
}
.sb-nav-item:hover { background: rgba(255,215,0,0.09); color: #FFD700; }
.sb-section { font-size: 10px; color: #555; text-transform: uppercase; letter-spacing: 2px; margin: 16px 0 6px; }
.sb-divider  { border: none; border-top: 1px solid rgba(255,215,0,0.12); margin: 14px 0; }
.status-dot-green { display:inline-block; width:8px; height:8px; background:#00e676; border-radius:50%; margin-right:6px; box-shadow:0 0 6px #00e676; }
.status-dot-red   { display:inline-block; width:8px; height:8px; background:#ff1744; border-radius:50%; margin-right:6px; box-shadow:0 0 6px #ff1744; }

/* ── Hide Streamlit default chrome ──────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Streamlit tab styling ──────────────────────────────── */
[data-baseweb="tab-list"] { background: transparent !important; gap: 4px; }
[data-baseweb="tab"] {
    background: rgba(255,215,0,0.04) !important;
    border-radius: 10px 10px 0 0 !important;
    color: #888 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(255,215,0,0.12) !important;
    color: #FFD700 !important;
    border-bottom: 2px solid #FFD700 !important;
}

/* ── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0a0a0c; }
::-webkit-scrollbar-thumb { background: #2a2a2e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a3e; }

/* ── Input widgets ──────────────────────────────────────── */
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select {
    background: #111116 !important;
    border: 1px solid rgba(255,215,0,0.2) !important;
    color: #e0e0e0 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

if "trades" not in st.session_state: st.session_state.trades=[]
if "trade_history" not in st.session_state: st.session_state.trade_history = []
if "losses" not in st.session_state: st.session_state.losses = 0
if "last_reset" not in st.session_state: st.session_state.last_reset=datetime.now(SAST).date()
if datetime.now(SAST).date()!=st.session_state.last_reset:
    st.session_state.trades=[]; st.session_state.losses = 0; st.session_state.last_reset=datetime.now(SAST).date()

@st.cache_data(ttl=60)
def get_gold():
    try:
        df=yf.Ticker("GC=F").history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1])
        atr=float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        ema50=float(df['Close'].ewm(50).mean().iloc[-1])
        ema200=float(df['Close'].ewm(200).mean().iloc[-1])
        rsi=float(100 - (100/(1 + (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().clip(upper=0).abs().rolling(14).mean()))))
        macd_line = df['Close'].ewm(12).mean() - df['Close'].ewm(26).mean()
        macd_signal = macd_line.ewm(9).mean()
        macd = float(macd_line.iloc[-1] - macd_signal.iloc[-1])
        momentum = float(df['Close'].iloc[-1] - df['Close'].iloc[-15])
        volatility = float(df['Close'].rolling(20).std().iloc[-1])
        return df, price, atr, ema50, ema200, rsi, macd, momentum, volatility
    except:
        return None, 4407.0, 5.5, 4400.0, 4385.0, 50.0, 0.0, 0.0, 5.0

@st.cache_data(ttl=60)
def get_forex(ticker, invert=False):
    try:
        df=yf.Ticker(ticker).history(period="5d", interval="15m")
        price=float(df['Close'].iloc[-1])
        ema20=float(df['Close'].ewm(20).mean().iloc[-1])
        ema100=float(df['Close'].ewm(100).mean().iloc[-1])
        ema50=float(df['Close'].ewm(50).mean().iloc[-1])
        rsi=float(100 - (100/(1 + (df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().clip(upper=0).abs().rolling(14).mean()))))
        atr = float((df['High']-df['Low']).rolling(14).mean().iloc[-1])
        momentum = float(df['Close'].iloc[-1] - df['Close'].iloc[-10])
        
        # Enhanced signal with momentum and volatility confirmation
        trend_bull = ema20 > ema100 and price > ema20 and ema50 > ema100
        trend_bear = ema20 < ema100 and price < ema20 and ema50 < ema100
        momentum_bull = momentum > 0 and rsi < 70
        momentum_bear = momentum < 0 and rsi > 30
        
        if trend_bull and momentum_bull:
            sig = "BUY"
        elif trend_bear and momentum_bear:
            sig = "SELL"
        else:
            sig = "WAIT"
        
        return price, sig, ema20, ema100, rsi, atr, momentum
    except:
        default = 18.5 if "ZAR" in ticker else 1.08
        return default, "WAIT", default, default, 50.0, 0.005, 0.0

@st.cache_data(ttl=60)
def get_dxy():
    try:
        dxy_df=yf.Ticker("DX-Y.NYB").history(period="2d")
        dxy=float(dxy_df['Close'].iloc[-1])
        chg=float(dxy_df['Close'].pct_change().iloc[-1]*100)
        ema20_dxy=float(dxy_df['Close'].ewm(20).mean().iloc[-1])
        dxy_momentum = float(dxy_df['Close'].iloc[-1] - dxy_df['Close'].iloc[-5])
        return dxy, chg, ema20_dxy, dxy_momentum
    except:
        return 99.5, -0.15, 99.5, 0.0

def send_alert(msg):
    token=st.secrets.get("TELEGRAM_TOKEN","")
    chat=st.secrets.get("TELEGRAM_CHAT_ID","")
    if token and chat:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=5)
        except:
            pass

def get_conf_label(conf):
    """Generate confidence label with enhanced styling"""
    if conf >= 85:
        return f'<span class="conf-high">⚡ CONF {conf}% ELITE 🇿🇦</span>'
    elif conf >= 75:
        return f'<span class="conf-high">✅ CONF {conf}% HIGH 🇿🇦</span>'
    elif conf >= 60:
        return f'<span class="conf-mid">⚠️ CONF {conf}% MED</span>'
    elif conf >= 50:
        return f'<span class="conf-mid">🟡 CONF {conf}% FAIR</span>'
    elif conf >= 30:
        return f'<span class="conf-low">❓ CONF {conf}% LOW</span>'
    else:
        return f'<span class="conf-verylow">🔴 CONF {conf}% DANGER</span>'

def get_conf_breakdown(conf, base, eur_add, eur_mom, zar_add, zar_mom, vol_adj):
    """Detailed confidence breakdown for debugging"""
    return f"""
    <div style="background:#0a0a0c;border:1px solid #333;border-radius:8px;padding:10px;font-size:11px;margin-top:8px;">
    <div style="color:#FFD700;margin-bottom:5px;">📊 CONF BREAKDOWN:</div>
    <div>🥇 Base Setup: +{base}%</div>
    <div>🇪🇺 EUR Signal: +{eur_add}% | Momentum: +{eur_mom}%</div>
    <div>🇿🇦 ZAR Signal: +{zar_add}% | Momentum: +{zar_mom}%</div>
    <div>🌪️ Volatility Adj: +{vol_adj:.1f}%</div>
    <div style="border-top:1px solid #333;margin-top:5px;padding-top:5px;color:#00e676;font-weight:bold;">TOTAL: {conf}%</div>
    </div>
    """

def calculate_levels(price, atr, agree_buy, rr_v):
    """Calculate SL & TP based on direction and RR"""
    sl = price - atr*1.5 if agree_buy else price + atr*1.5
    tp = price + (abs(price-sl) * rr_v) if agree_buy else price - (abs(sl-price) * rr_v)
    return sl, tp

def check_trade_outcome(current_price, sl, tp, direction):
    """
    Check if trade hit SL (loss) or TP (win)
    direction: "BUY" or "SELL"
    Returns: "WIN", "LOSS", or None (still open)
    """
    if direction == "BUY":
        if current_price <= sl:
            return "LOSS"
        elif current_price >= tp:
            return "WIN"
    else:  # SELL
        if current_price >= sl:
            return "LOSS"
        elif current_price <= tp:
            return "WIN"
    return None

def record_trade_outcome(direction, entry, sl, tp, outcome, conf):
    """Record trade outcome and update loss counter"""
    timestamp = datetime.now(SAST).strftime("%H:%M:%S")
    
    if outcome == "LOSS":
        st.session_state.losses += 1
        trade_record = f"❌ {direction} @ {entry:.2f} | SL HIT | Loss {st.session_state.losses}/2 | CONF {conf}%"
        send_alert(f"❌ *TRADE CLOSED - LOSS*\n{direction} XAUUSD @ {entry:.2f}\nSL {sl:.2f} | TP {tp:.2f}\nLoss recorded: {st.session_state.losses}/2\nCONF {conf}%")
        
        if st.session_state.losses >= 2:
            send_alert(f"🔒 *KILL-SWITCH TRIGGERED!*\n2 consecutive losses - Trading disabled for today.")
    else:  # WIN
        st.session_state.losses = 0  # Reset loss counter on win
        trade_record = f"✅ {direction} @ {entry:.2f} | TP HIT | WIN! | Losses reset to 0 | CONF {conf}%"
        send_alert(f"✅ *TRADE CLOSED - WIN*\n{direction} XAUUSD @ {entry:.2f}\nTP {tp:.2f}\nLoss counter reset to 0!\nCONF {conf}%")
    
    st.session_state.trade_history.append({
        "timestamp": timestamp,
        "record": trade_record
    })
    
    return trade_record

# DATA COLLECTION
df_gold, price, atr, ema50, ema200, gold_rsi, gold_macd, gold_momentum, gold_volatility = get_gold()
eur_price, eur_sig, eur20, eur100, eur_rsi, eur_atr, eur_momentum = get_forex("EURUSD=X")
zar_price, zar_sig, zar20, zar100, zar_rsi, zar_atr, zar_momentum = get_forex("USDZAR=X")  # SA PAIR
dxy, dxy_chg, dxy_ema20, dxy_momentum = get_dxy()
now = datetime.now(SAST)

# ENHANCED CORE LOGIC (must be before sidebar)
setup_bull = ema50>ema200 and price>ema50 and gold_rsi < 70 and gold_macd > 0
setup_bear = ema50<ema200 and price<ema50 and gold_rsi > 30 and gold_macd < 0
fund_bull = dxy_chg < -0.08 and dxy_momentum < 0
fund_bear = dxy_chg > 0.08 and dxy_momentum > 0
session_ok = 10 <= now.hour < 20
agree_buy = setup_bull and fund_bull and session_ok
agree_sell = setup_bear and fund_bear and session_ok

# SA CONFIDENCE
base_conf = 50 if (agree_buy or agree_sell) else 0
eur_signal_bonus = 15 if ((eur_sig=="BUY" and agree_buy) or (eur_sig=="SELL" and agree_sell)) else 0
eur_momentum_bonus = 10 if ((eur_momentum > 0 and agree_buy) or (eur_momentum < 0 and agree_sell)) else 0
zar_signal_bonus = 15 if ((zar_sig=="SELL" and agree_buy) or (zar_sig=="BUY" and agree_sell)) else 0
zar_momentum_bonus = 10 if ((zar_momentum < 0 and agree_buy) or (zar_momentum > 0 and agree_sell)) else 0
vol_adjustment = min(gold_volatility / 5.0, 5)
conf = min(int(base_conf + eur_signal_bonus + eur_momentum_bonus + zar_signal_bonus + zar_momentum_bonus + vol_adjustment), 100)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if _logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{_logo_b64}" class="logo-sm" />', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><span class="gold-text" style="font-size:18px;font-weight:800;">MARONG STOIC BOT</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;margin-top:4px;"><span style="background:#007A4B;color:white;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;">🇿🇦 SA EDITION</span></div>', unsafe_allow_html=True)
    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # Live status
    live_dot = "status-dot-green" if session_ok else "status-dot-red"
    st.markdown(f'<div class="sb-nav-item"><span class="{live_dot}"></span>{"LIVE — Session Active" if session_ok else "OUT OF SESSION"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sb-nav-item">🕒 {now.strftime("%H:%M:%S")} SAST</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sb-nav-item">📅 {now.strftime("%a %d %b %Y")}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider"><div class="sb-section">📊 Markets</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sb-nav-item">🥇 XAUUSD &nbsp;<b style="color:#FFD700">${price:,.2f}</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sb-nav-item">🇪🇺 EURUSD &nbsp;<b style="color:#aaa">{eur_price:.5f}</b> <span style="color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#666"}">{eur_sig}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sb-nav-item">🇿🇦 USDZAR &nbsp;<b style="color:#aaa">R{zar_price:.4f}</b> <span style="color:{"#00e676" if zar_sig=="SELL" else "#ff5252" if zar_sig=="BUY" else "#666"}">{zar_sig}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sb-nav-item">💵 DXY &nbsp;<b style="color:#aaa">{dxy:.2f}</b> <span style="color:{"#00e676" if dxy_chg<0 else "#ff5252"}">{dxy_chg:+.2f}%</span></div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider"><div class="sb-section">⚠️ Risk State</div>', unsafe_allow_html=True)
    loss_color = "#ff1744" if st.session_state.losses >= 2 else "#FFD700" if st.session_state.losses == 1 else "#00e676"
    st.markdown(f'<div class="sb-nav-item">Consecutive Losses: <b style="color:{loss_color}">{st.session_state.losses}/2</b></div>', unsafe_allow_html=True)
    if st.session_state.losses >= 2:
        st.markdown('<div class="sb-nav-item" style="border-color:#ff1744;color:#ff5252;">🔒 KILL-SWITCH ACTIVE</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider"><div class="sb-section">🔗 Links</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-nav-item"><a href="https://hfmbot-8hxcdrycoldue48qs2eoxy.streamlit.app/" target="_blank" style="color:#FFD700;text-decoration:none;">🌐 Live App ↗</a></div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:9px;color:#333;margin-top:8px;">MARONG STOIC BOT v2.0<br>Powered by yfinance · TradingView</div>', unsafe_allow_html=True)

# ── TOP BAR HEADER ─────────────────────────────────────────────────────────────
_signal_color = "#00e676" if agree_buy else "#ff1744" if agree_sell else "#888"
_signal_label = "🟢 BUY BIAS" if agree_buy else "🔴 SELL BIAS" if agree_sell else "⚪ WAITING"
st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:center;gap:14px;">
    {"<img src='data:image/png;base64," + _logo_b64 + "' class='logo-img' />" if _logo_b64 else ""}
    <div>
      <span class="gold-text" style="font-size:26px;font-weight:800;letter-spacing:-0.5px;">MARONG STOIC BOT</span>
      <span style="background:#007A4B;color:white;padding:3px 10px;border-radius:6px;margin-left:10px;font-size:12px;font-weight:700;vertical-align:middle;">🇿🇦 SA EDITION</span>
    </div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:22px;font-weight:800;color:#FFD700;font-variant-numeric:tabular-nums;">{now.strftime('%H:%M:%S')}</div>
    <div style="font-size:10px;color:#555;letter-spacing:1px;">SOUTH AFRICA STANDARD TIME</div>
    <div style="margin-top:4px;"><span style="color:{_signal_color};font-size:12px;font-weight:700;">{_signal_label}</span>&nbsp;&nbsp;<span style="font-size:10px;color:#444;">CONF&nbsp;<b style="color:#FFD700">{conf}%</b></span></div>
  </div>
</div>
""", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">${price:,.2f}</div><div style="font-size:12px;color:#888;">{ema50:.0f}/{ema200:.0f} | RSI {gold_rsi:.0f}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><div class="kpi-label">EURUSD CONFIRM</div><div class="kpi-val">{eur_price:.5f}</div><div style="font-size:12px;color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#999"};">{eur_sig} | RSI {eur_rsi:.0f}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><div class="kpi-label">USDZAR HOME 🇿🇦</div><div class="kpi-val">R{zar_price:.4f}</div><div style="font-size:12px;color:{"#00e676" if zar_sig=="SELL" else "#ff5252" if zar_sig=="BUY" else "#999"};">{zar_sig} | RSI {zar_rsi:.0f}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi"><div class="kpi-label">DXY FUND</div><div class="kpi-val">{dxy:.2f}</div><div style="font-size:12px;color:{"#00e676" if dxy_chg<0 else "#ff5252"}>{dxy_chg:+.2f}% | MOM {dxy_momentum:+.1f}</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi"><div class="kpi-label">LOSSES</div><div class="kpi-val">{st.session_state.losses}/2</div><div style="font-size:12px;color:{"#ff1744" if st.session_state.losses >= 2 else "#00e676"};">{"🔒 KILL-SWITCH" if st.session_state.losses >= 2 else "Status OK"}</div></div>', unsafe_allow_html=True)

# Confidence labels (computed once above, used here)
conf_label = get_conf_label(conf)
conf_breakdown = get_conf_breakdown(conf, base_conf, eur_signal_bonus, eur_momentum_bonus, zar_signal_bonus, zar_momentum_bonus, vol_adjustment)

# KILL-SWITCH CHECK
if st.session_state.losses >= 2:
    st.markdown(f"""
    <div class="killswitch">
    🚨 KILL-SWITCH ACTIVATED 🚨<br>
    <span style="font-size:14px;">2/2 Consecutive Losses Recorded<br>TRADING DISABLED FOR TODAY</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

left, right = st.columns([1.7,1])
with left:
    tab1, tab2, tab3 = st.tabs(["⚔️ GOLD CORE", "🇪🇺 EURUSD", "🇿🇦 USDZAR - YOUR RAND"])
    with tab1:
        st.markdown(f'<div class="glass"> <div style="display:flex;justify-content:space-between;"><div class="kpi-label">SA SMART LOGIC</div><div>{conf_label}</div></div>', unsafe_allow_html=True)
        st.markdown(conf_breakdown, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        html="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AXAUUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg&hide_side_toolbar=1" style="width: 100%; height: 100%; border: none;"></iframe></div>"""
        st.components.v1.html(html, height=380)
        st.markdown('</div>', unsafe_allow_html=True)
        # Gold metrics
        st.markdown(f"""
        <div class="glass">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>🥇 Price: ${price:,.2f}<br>📊 EMA50/200: {ema50:.0f}/{ema200:.0f}<br>💪 RSI: {gold_rsi:.1f}</div>
        <div>📈 Momentum: {gold_momentum:+.2f}<br>🎯 MACD: {gold_macd:+.5f}<br>🌪️ Volatility: {gold_volatility:.4f}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        html2="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AEURUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg&hide_side_toolbar=1" style="width: 100%; height: 100%; border: none;"></iframe></div>"""
        st.components.v1.html(html2, height=380)
        st.markdown(f"""
        <div class="glass">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>💶 Price: {eur_price:.5f}<br>📊 EMA20/100: {eur20:.5f}/{eur100:.5f}<br>💪 RSI: {eur_rsi:.1f}</div>
        <div>📈 Momentum: {eur_momentum:+.5f}<br>🎯 Signal: {eur_sig}<br>⚡ Trend: {"BULLISH" if eur_sig=="BUY" else "BEARISH" if eur_sig=="SELL" else "NEUTRAL"}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    with tab3:
        html3="""<div style="height:360px;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AUSDZAR&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg&hide_side_toolbar=1" style="width: 100%; height: 100%; border: none;"></iframe></div>"""
        st.components.v1.html(html3, height=380)
        st.markdown(f"""
        <div class="glass">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>🇿🇦 Price: R{zar_price:.4f}<br>📊 EMA20/100: {zar20:.4f}/{zar100:.4f}<br>💪 RSI: {zar_rsi:.1f}</div>
        <div>📈 Momentum: {zar_momentum:+.6f}<br>🎯 Signal: {zar_sig}<br>💰 (SELL=Strong Rand=Good)</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if len(st.session_state.trades)>=4:
        st.markdown(f'<div class="locked"><h3>🔒 SA PORTFOLIO LOCKED 4/4</h3><p>{", ".join(st.session_state.trades)}</p></div>', unsafe_allow_html=True)
    elif agree_buy:
        sl, tp = calculate_levels(price, atr, True, rr_v if "rr_v" in locals() else 2.5)
        badge = "HIGH CONVICTION 🇿🇦" if conf>=75 else "MEDIUM"
        st.markdown(f'<div class="buy-signal">🟢 ELITE BUY - {badge}<br><span style="font-size:13px;">{price:.2f} SL {sl:.2f} TP {tp:.2f} | {conf}% CONF | ZAR {zar_price:.4f}</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE BUY - SA EDITION"):
            st.session_state.trades.append(f"BUY {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *SA EDITION EXECUTED*\n🟢 BUY XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} USDZAR:{zar_sig} R{zar_price:.4f}\n{len(st.session_state.trades)}/4 TRADES")
            st.rerun()
    elif agree_sell:
        sl, tp = calculate_levels(price, atr, False, rr_v if "rr_v" in locals() else 2.5)
        badge = "HIGH CONVICTION 🇿🇦" if conf>=75 else "MEDIUM"
        st.markdown(f'<div class="sell-signal">🔴 ELITE SELL - {badge}<br><span style="font-size:13px;">{price:.2f} SL {sl:.2f} TP {tp:.2f} | {conf}% CONF | ZAR {zar_price:.4f}</span></div>', unsafe_allow_html=True)
        if st.button("✅ EXECUTE SELL - SA EDITION"):
            st.session_state.trades.append(f"SELL {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *SA EDITION EXECUTED*\n🔴 SELL XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} USDZAR:{zar_sig} R{zar_price:.4f}\n{len(st.session_state.trades)}/4 TRADES")
            st.rerun()
    else:
        st.markdown(f'<div class="wait-signal"><h3>⚪ STOIC WAIT - SA CHECK</h3><p>Gold {setup_bull or setup_bear} | DXY {fund_bull or fund_bear} | EUR {eur_sig} | ZAR {zar_sig} (Need SELL for BUY) | VOL {gold_volatility:.4f}</p></div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass"><div class="kpi-label">🇿🇦 RAND CALCULATOR</div>', unsafe_allow_html=True)
    bal_usd = st.number_input("Balance $ (Cent)", 10.0, 50000.0, 500.0)
    st.caption(f"≈ R{bal_usd*zar_price:,.2f} at R{zar_price:.2f}/$")
    risk = st.slider("Risk %", 0.5, 2.0, 1.0)
    rr = st.selectbox("RR", ["1:2","1:2.5","1:3"], index=1)
    rr_v = float(rr.split(":")[1])
    risk_amt = bal_usd * risk/100
    lots = max(0.01, min(risk_amt/((atr*1.5)*10), 2.0))
    st.markdown(f'<div style="margin-top:12px;background:#111;border-radius:10px;padding:12px;">USD Risk <span class="gold-text">${risk_amt:.2f}</span> ≈ R{risk_amt*zar_price:.2f}<br>Reward ${risk_amt*rr_v:.2f} ≈ R{risk_amt*rr_v*zar_price:.2f}<br>Lots {lots:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">SA VOTE SYSTEM</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🥇 GOLD: {"BUY" if agree_buy else "SELL" if agree_sell else "WAIT"} (50%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🇪🇺 EURUSD: {eur_sig} (25%) - Must match Gold</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">🇿🇦 USDZAR: {zar_sig} - Need <b>SELL</b> for Gold BUY (Rand Strong = Good)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">📊 SIGNAL STRENGTH</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">Gold RSI: {gold_rsi:.1f} {"⚡ Overbought" if gold_rsi>70 else "⚠️ Oversold" if gold_rsi<30 else "✅ Neutral"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">EUR RSI: {eur_rsi:.1f} {"⚡ Overbought" if eur_rsi>70 else "⚠️ Oversold" if eur_rsi<30 else "✅ Neutral"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">ZAR RSI: {zar_rsi:.1f} {"⚡ Overbought" if zar_rsi>70 else "⚠️ Oversold" if zar_rsi<30 else "✅ Neutral"}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">⚠️ LOSS TRACKER</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#111;padding:10px;border-radius:8px;margin:5px 0;">Consecutive Losses: <span style="color:{"#ff1744" if st.session_state.losses >= 2 else "#00e676"};font-weight:bold;">{st.session_state.losses}/2</span></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Log Loss"):
            # Example: if trade outcome was a loss
            st.session_state.losses += 1
            send_alert(f"⚠️ Loss recorded: {st.session_state.losses}/2\n{st.session_state.losses}/2 consecutive losses.")
            if st.session_state.losses >= 2:
                send_alert(f"🔒 KILL-SWITCH TRIGGERED!\n2 consecutive losses - Trading disabled for today.")
            st.rerun()
    with col2:
        if st.button("✅ Log Win"):
            # Example: if trade outcome was a win, reset losses
            st.session_state.losses = 0
            send_alert(f"✅ Win recorded! Loss counter reset to 0.")
            st.rerun()
    
    if st.button("🔄 Reset Losses"):
        st.session_state.losses = 0
        send_alert(f"🔄 Loss counter manually reset to 0.")
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Trade History
    if st.session_state.trade_history:
        st.markdown('<div class="glass" style="margin-top:15px;"><div class="kpi-label">📝 TRADE HISTORY</div>', unsafe_allow_html=True)
        for trade in reversed(st.session_state.trade_history[-5:]):  # Show last 5 trades
            st.markdown(f'<div style="background:#111;padding:8px;border-radius:6px;margin:5px 0;font-size:10px;">{trade["timestamp"]} | {trade["record"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
