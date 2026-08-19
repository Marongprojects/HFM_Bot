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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* ── BASE ── */
.stApp { background: #050508; color: #d8d8e8; font-family: 'JetBrains Mono', monospace; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0.5rem !important; }

/* ── ANIMATIONS ── */
@keyframes shine       { 0%   { background-position: 0% }   100% { background-position: 200% } }
@keyframes pulse-glow  { 0%,100% { box-shadow: 0 0 12px rgba(255,215,0,0.4); } 50% { box-shadow: 0 0 28px rgba(255,215,0,0.9); } }
@keyframes pulse-green { 0%,100% { box-shadow: 0 0 10px rgba(0,230,118,0.4); } 50% { box-shadow: 0 0 26px rgba(0,230,118,0.9); } }
@keyframes pulse-red   { 0%,100% { box-shadow: 0 0 10px rgba(255,23,68,0.4);  } 50% { box-shadow: 0 0 26px rgba(255,23,68,0.9);  } }
@keyframes float-up    { 0%,100% { transform: translateY(0);   } 50% { transform: translateY(-6px); } }
@keyframes ticker-dot  { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.7); } }
@keyframes bar-fill    { from { width: 0; } to { width: var(--w); } }
@keyframes hero-fade   { from { opacity: 0; transform: translateY(-18px); } to { opacity: 1; transform: translateY(0); } }

/* ── GOLD TEXT ── */
.gold-text {
  background: linear-gradient(90deg, #FFD700, #FFA500, #FFE566, #FFD700);
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 5s linear infinite;
}

/* ── HERO HEADER ── */
.hero-header {
  background: linear-gradient(135deg, #0a0a10 0%, #111118 40%, #0d0d14 100%);
  border: 1px solid rgba(255,215,0,0.25);
  border-radius: 20px;
  padding: 28px 32px 22px;
  margin-bottom: 18px;
  position: relative;
  overflow: hidden;
  animation: hero-fade 0.8s ease;
}
.hero-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(255,215,0,0.07) 0%, transparent 70%);
  pointer-events: none;
}
.hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  font-weight: 900;
  letter-spacing: 4px;
  background: linear-gradient(90deg, #FFD700, #FFA500, #FFE566, #FFD700);
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 5s linear infinite;
  margin: 0 0 4px;
}
.hero-sub {
  font-size: 12px;
  color: #8888aa;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.hero-quote {
  font-style: italic;
  color: rgba(255,215,0,0.6);
  font-size: 12px;
  border-left: 2px solid rgba(255,215,0,0.35);
  padding-left: 10px;
  margin-top: 8px;
}
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-right: 6px;
}
.badge-active  { background: rgba(0,230,118,0.15); border: 1px solid rgba(0,230,118,0.5); color: #00e676; }
.badge-sa      { background: rgba(0,122,75,0.25);  border: 1px solid rgba(0,122,75,0.6);  color: #00e676; }
.badge-time    { background: rgba(255,215,0,0.12); border: 1px solid rgba(255,215,0,0.35); color: #FFD700; }
.dot-pulse {
  width: 7px; height: 7px; border-radius: 50%;
  display: inline-block;
  animation: ticker-dot 1.4s ease-in-out infinite;
}
.dot-green { background: #00e676; }
.dot-gold  { background: #FFD700; }
.dot-red   { background: #ff1744; }

/* ── GLASS CARDS ── */
.glass {
  background: rgba(16,16,22,0.88);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,215,0,0.12);
  border-radius: 18px;
  padding: 18px 20px;
  transition: border-color 0.3s;
}
.glass:hover { border-color: rgba(255,215,0,0.28); }

/* ── KPI CARDS ── */
.kpi {
  background: linear-gradient(160deg, #131318, #0c0c12);
  border-radius: 16px;
  padding: 18px 16px;
  border: 1px solid #1c1c26;
  border-top: 2px solid rgba(255,215,0,0.35);
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  transition: transform 0.25s, box-shadow 0.25s;
  animation: pulse-glow 3s ease-in-out infinite;
}
.kpi:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 8px 30px rgba(255,215,0,0.15); }
.kpi-val   { font-size: 22px; font-weight: 800; color: #ffffff; font-family: 'Orbitron', sans-serif; }
.kpi-label { font-size: 10px; color: #6666aa; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; }
.kpi-sub   { font-size: 11px; color: #555577; margin-top: 5px; }

/* ── SIGNAL PANELS ── */
.buy-signal {
  background: linear-gradient(135deg, #002818, #00451a);
  border: 2px solid #00c853;
  border-radius: 18px;
  padding: 26px;
  text-align: center;
  font-weight: 900;
  font-size: 24px;
  color: #00e676;
  animation: pulse-green 2s ease-in-out infinite;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
}
.sell-signal {
  background: linear-gradient(135deg, #280005, #450009);
  border: 2px solid #ff1744;
  border-radius: 18px;
  padding: 26px;
  text-align: center;
  font-weight: 900;
  font-size: 24px;
  color: #ff5252;
  animation: pulse-red 2s ease-in-out infinite;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
}
.wait-signal {
  background: linear-gradient(135deg, #0e0e14, #13131a);
  border: 2px dashed #2a2a40;
  border-radius: 18px;
  padding: 26px;
  text-align: center;
  color: #55557a;
}
.locked {
  background: linear-gradient(135deg, #200008, #180005);
  border: 2px solid #ff1744;
  border-radius: 18px;
  padding: 22px;
  text-align: center;
  animation: pulse-red 1.5s ease-in-out infinite;
}
.killswitch {
  background: linear-gradient(135deg, #5c0000, #8b0000, #c00000);
  border: 2px solid #ff1744;
  border-radius: 20px;
  padding: 30px;
  text-align: center;
  font-weight: 900;
  font-size: 20px;
  color: white;
  animation: pulse-red 1s ease-in-out infinite;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
}

/* ── CONFIDENCE BADGES ── */
.conf-high     { background: linear-gradient(90deg,#003d1a,#006628); color:#00e676; padding:7px 16px; border-radius:20px; font-weight:900; border:1px solid #00c853; font-size:13px; }
.conf-mid      { background: rgba(255,215,0,0.12); color:#FFD700; padding:7px 16px; border-radius:20px; font-weight:900; border:1px solid rgba(255,215,0,0.4); font-size:13px; }
.conf-low      { background: #1a1a24; color:#7777aa; padding:7px 16px; border-radius:20px; border:1px solid #333; font-size:13px; }
.conf-verylow  { background: rgba(255,23,68,0.12); color:#ff5252; padding:7px 16px; border-radius:20px; border:1px solid rgba(255,23,68,0.4); font-size:13px; }

/* ── ANIMATED CONF BAR ── */
.conf-bar-wrap { background:#1a1a24; border-radius:8px; height:8px; margin:6px 0; overflow:hidden; }
.conf-bar {
  height:8px; border-radius:8px;
  animation: bar-fill 1.2s ease-out forwards;
}
.conf-bar-green  { background: linear-gradient(90deg,#00c853,#00e676); }
.conf-bar-gold   { background: linear-gradient(90deg,#D4AF37,#FFD700); }
.conf-bar-gray   { background: #444460; }
.conf-bar-red    { background: linear-gradient(90deg,#c62828,#ff5252); }

/* ── DISCIPLINE TRACKER ── */
.discipline-ring-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(16,16,22,0.9);
  border: 1px solid rgba(255,215,0,0.15);
  border-radius: 16px;
  padding: 14px 18px;
}
.disc-label { font-size: 11px; color: #6666aa; text-transform: uppercase; letter-spacing: 2px; }
.disc-count { font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900; color: #FFD700; }

/* ── LOSS PROGRESS ── */
.loss-progress-wrap { background: #1a1a24; border-radius: 10px; height: 12px; margin: 8px 0; overflow: hidden; }
.loss-progress-bar  {
  height: 12px; border-radius: 10px;
  transition: width 0.6s ease;
}
.loss-0  { background: #00e676; width: 2%;  }
.loss-25 { background: #FFD700; width: 25%; }
.loss-50 { background: #ff9800; width: 50%; }
.loss-75 { background: #ff5722; width: 75%; }
.loss-100{ background: linear-gradient(90deg,#c62828,#ff1744); width:100%; animation: pulse-red 0.8s infinite; }

/* ── TRADE HISTORY CARD ── */
.trade-card {
  background: linear-gradient(135deg,#0f0f18,#131320);
  border: 1px solid #222236;
  border-radius: 12px;
  padding: 10px 14px;
  margin: 6px 0;
  font-size: 11px;
  transition: border-color 0.2s;
}
.trade-card:hover { border-color: rgba(255,215,0,0.3); }
.trade-win  { border-left: 3px solid #00e676; }
.trade-loss { border-left: 3px solid #ff1744; }

/* ── VOTE ROW ── */
.vote-row {
  background: linear-gradient(135deg,#0f0f18,#121220);
  border: 1px solid #1c1c2e;
  border-radius: 10px;
  padding: 10px 14px;
  margin: 5px 0;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ── BUTTONS ── */
.stButton > button {
  background: linear-gradient(90deg, #B8860B, #D4AF37, #FFD700, #D4AF37, #B8860B) !important;
  background-size: 300% auto !important;
  color: #050508 !important;
  font-weight: 900 !important;
  font-family: 'Orbitron', sans-serif !important;
  letter-spacing: 1.5px !important;
  height: 52px !important;
  border-radius: 12px !important;
  width: 100% !important;
  border: none !important;
  font-size: 13px !important;
  animation: shine 4s linear infinite !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 22px rgba(255,215,0,0.4) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: #0d0d14;
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  color: #6666aa;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 1px;
}
.stTabs [aria-selected="true"] {
  background: rgba(255,215,0,0.12) !important;
  color: #FFD700 !important;
}

/* ── INPUTS ── */
.stSlider .st-emotion-cache-1n5bne7 { color: #FFD700; }
input[type="number"], .stSelectbox select {
  background: #0f0f18 !important;
  border: 1px solid #2a2a40 !important;
  color: #e0e0f0 !important;
  border-radius: 8px !important;
}

/* ── SECTION HEADER ── */
.section-hdr {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: rgba(255,215,0,0.7);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255,215,0,0.12);
}

/* ── METRIC GRID ── */
.metric-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.metric-item { background:#0d0d16; border-radius:10px; padding:10px 12px; border:1px solid #1c1c2e; }
.metric-lbl  { font-size:10px; color:#55557a; text-transform:uppercase; letter-spacing:1.5px; }
.metric-val  { font-size:14px; font-weight:700; color:#d0d0f0; margin-top:2px; }
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

STOIC_QUOTES = [
    "The obstacle is the way. — Marcus Aurelius",
    "You have power over your mind, not outside events. Realise this, and you will find strength.",
    "Waste no more time arguing what a good trader should be. Be one.",
    "He who is brave is free. Trade with conviction, not fear.",
    "First say to yourself what you would be; and then do what you have to do.",
    "Difficulty is what wakes up the genius. — Nassim Taleb",
    "Discipline is the bridge between goals and accomplishment.",
    "A smooth sea never made a skilled sailor — nor a skilled trader.",
]

def get_stoic_quote():
    idx = datetime.now().minute % len(STOIC_QUOTES)
    return STOIC_QUOTES[idx]

def get_conf_label(conf):
    """Generate confidence label with enhanced styling"""
    if conf >= 85:
        return f'<span class="conf-high">⚡ ELITE {conf}% 🇿🇦</span>'
    elif conf >= 75:
        return f'<span class="conf-high">✅ HIGH {conf}% 🇿🇦</span>'
    elif conf >= 60:
        return f'<span class="conf-mid">⚠️ MED {conf}%</span>'
    elif conf >= 50:
        return f'<span class="conf-mid">🟡 FAIR {conf}%</span>'
    elif conf >= 30:
        return f'<span class="conf-low">❓ LOW {conf}%</span>'
    else:
        return f'<span class="conf-verylow">🔴 DANGER {conf}%</span>'

def _bar_color(pct):
    if pct >= 75: return "conf-bar-green"
    if pct >= 50: return "conf-bar-gold"
    if pct >= 25: return "conf-bar-gray"
    return "conf-bar-red"

def get_conf_breakdown(conf, base, eur_add, eur_mom, zar_add, zar_mom, vol_adj):
    """Detailed animated confidence breakdown"""
    rows = [
        ("🥇 Base Setup",      base,    100),
        ("🇪🇺 EUR Signal",     eur_add,  15),
        ("🇪🇺 EUR Momentum",   eur_mom,  10),
        ("🇿🇦 ZAR Signal",     zar_add,  15),
        ("🇿🇦 ZAR Momentum",   zar_mom,  10),
        (f"🌪️ Vol Adj",        round(vol_adj), 5),
    ]
    bars_html = ""
    for label, val, max_val in rows:
        pct = int(min(val / max_val * 100, 100)) if max_val else 0
        color = _bar_color(pct)
        bars_html += f"""
        <div style="margin:6px 0;">
          <div style="display:flex;justify-content:space-between;font-size:10px;color:#7777aa;margin-bottom:2px;">
            <span>{label}</span><span style="color:#d0d0f0;font-weight:700;">+{val}%</span>
          </div>
          <div class="conf-bar-wrap">
            <div class="conf-bar {color}" style="--w:{pct}%;width:{pct}%;"></div>
          </div>
        </div>"""
    return f"""
    <div style="background:#08080f;border:1px solid rgba(255,215,0,0.12);border-radius:12px;padding:14px 16px;margin-top:10px;">
      <div class="section-hdr" style="margin-bottom:12px;">📊 Confidence Breakdown</div>
      {bars_html}
      <div style="border-top:1px solid rgba(255,215,0,0.15);margin-top:10px;padding-top:8px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:11px;color:#6666aa;">TOTAL CONFIDENCE</span>
        <span style="font-family:'Orbitron',sans-serif;font-size:20px;font-weight:900;color:#FFD700;">{conf}%</span>
      </div>
    </div>"""

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

# ── HERO HEADER ──────────────────────────────────────────────────────────────
session_active = 10 <= now.hour < 20
session_status = '<span class="status-badge badge-active"><span class="dot-pulse dot-green"></span>SESSION LIVE</span>' if session_active else '<span class="status-badge" style="background:rgba(255,23,68,0.12);border:1px solid rgba(255,23,68,0.4);color:#ff5252;"><span class="dot-pulse dot-red"></span>OFF HOURS</span>'
st.markdown(f"""
<div class="hero-header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
    <div>
      <div class="hero-title">⚔ I AM A STOIC TRADER</div>
      <div class="hero-sub">MARONG STOIC BOT &nbsp;·&nbsp; SA EDITION &nbsp;·&nbsp; XAUUSD COMMAND CENTER</div>
      <div class="hero-quote">"{get_stoic_quote()}"</div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'Orbitron',sans-serif;font-size:26px;font-weight:900;color:#FFD700;letter-spacing:3px;">{now.strftime('%H:%M:%S')}</div>
      <div style="font-size:10px;color:#55557a;letter-spacing:2px;margin-bottom:8px;">SAST — JOHANNESBURG</div>
      <div>
        {session_status}
        <span class="status-badge badge-sa"><span class="dot-pulse dot-green"></span>🇿🇦 RAND SMART</span>
        <span class="status-badge badge-time"><span class="dot-pulse dot-gold"></span>BOT ONLINE</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.markdown(f'''<div class="kpi">
  <div class="kpi-label">XAUUSD CORE</div>
  <div class="kpi-val">${price:,.2f}</div>
  <div class="kpi-sub">EMA50 {ema50:.0f} · EMA200 {ema200:.0f}</div>
  <div class="kpi-sub">RSI <span style="color:{"#ff9800" if gold_rsi>70 else "#00e676" if gold_rsi<30 else "#aaaacc"};">{gold_rsi:.0f}</span></div>
</div>''', unsafe_allow_html=True)
k2.markdown(f'''<div class="kpi">
  <div class="kpi-label">EURUSD CONFIRM</div>
  <div class="kpi-val">{eur_price:.5f}</div>
  <div class="kpi-sub" style="color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#666688"};">{eur_sig}</div>
  <div class="kpi-sub">RSI {eur_rsi:.0f} · MOM {eur_momentum:+.4f}</div>
</div>''', unsafe_allow_html=True)
k3.markdown(f'''<div class="kpi">
  <div class="kpi-label">USDZAR HOME 🇿🇦</div>
  <div class="kpi-val">R{zar_price:.4f}</div>
  <div class="kpi-sub" style="color:{"#00e676" if zar_sig=="SELL" else "#ff5252" if zar_sig=="BUY" else "#666688"};">{zar_sig}</div>
  <div class="kpi-sub">RSI {zar_rsi:.0f} · MOM {zar_momentum:+.5f}</div>
</div>''', unsafe_allow_html=True)
k4.markdown(f'''<div class="kpi">
  <div class="kpi-label">DXY FUNDAMENTAL</div>
  <div class="kpi-val">{dxy:.2f}</div>
  <div class="kpi-sub" style="color:{"#00e676" if dxy_chg<0 else "#ff5252"};">{dxy_chg:+.2f}% today</div>
  <div class="kpi-sub">MOM {dxy_momentum:+.2f}</div>
</div>''', unsafe_allow_html=True)

losses_pct_class = ["loss-0","loss-25","loss-50","loss-75","loss-100","loss-100"][min(st.session_state.losses, 4)+1 if st.session_state.losses > 0 else 0]
losses_color = "#ff1744" if st.session_state.losses >= 2 else "#FFD700" if st.session_state.losses == 1 else "#00e676"
k5.markdown(f'''<div class="kpi" style="border-top-color:rgba(255,23,68,0.6);">
  <div class="kpi-label">DISCIPLINE</div>
  <div class="kpi-val" style="color:{losses_color};">{st.session_state.losses}/2</div>
  <div class="loss-progress-wrap"><div class="loss-progress-bar {losses_pct_class}"></div></div>
  <div class="kpi-sub" style="color:{losses_color};">{"🔒 KILL-SWITCH" if st.session_state.losses >= 2 else "✅ Discipline OK"}</div>
</div>''', unsafe_allow_html=True)

# ENHANCED CORE LOGIC
setup_bull = ema50>ema200 and price>ema50 and gold_rsi < 70 and gold_macd > 0
setup_bear = ema50<ema200 and price<ema50 and gold_rsi > 30 and gold_macd < 0
fund_bull = dxy_chg < -0.08 and dxy_momentum < 0
fund_bear = dxy_chg > 0.08 and dxy_momentum > 0
session_ok = 10 <= now.hour < 20
agree_buy = setup_bull and fund_bull and session_ok
agree_sell = setup_bear and fund_bear and session_ok

# SA CONFIDENCE - ENHANCED ZAR SELL = GOLD BUY WITH DETAILED BREAKDOWN
base_conf = 50 if (agree_buy or agree_sell) else 0

eur_signal_bonus = 15 if ((eur_sig=="BUY" and agree_buy) or (eur_sig=="SELL" and agree_sell)) else 0
eur_momentum_bonus = 10 if ((eur_momentum > 0 and agree_buy) or (eur_momentum < 0 and agree_sell)) else 0

zar_signal_bonus = 15 if ((zar_sig=="SELL" and agree_buy) or (zar_sig=="BUY" and agree_sell)) else 0
zar_momentum_bonus = 10 if ((zar_momentum < 0 and agree_buy) or (zar_momentum > 0 and agree_sell)) else 0

vol_adjustment = min(gold_volatility / 5.0, 5)
conf = min(int(base_conf + eur_signal_bonus + eur_momentum_bonus + zar_signal_bonus + zar_momentum_bonus + vol_adjustment), 100)

# Enhanced confidence label with new function
conf_label = get_conf_label(conf)
conf_breakdown = get_conf_breakdown(conf, base_conf, eur_signal_bonus, eur_momentum_bonus, zar_signal_bonus, zar_momentum_bonus, vol_adjustment)

# KILL-SWITCH CHECK
if st.session_state.losses >= 2:
    st.markdown(f"""
    <div class="killswitch">
    🚨 KILL-SWITCH ACTIVATED 🚨<br>
    <span style="font-size:14px;font-family:'JetBrains Mono',monospace;font-weight:400;">
    2/2 Consecutive Losses Recorded<br>TRADING DISABLED FOR TODAY<br>
    <em style="font-size:12px;color:rgba(255,255,255,0.7);">"Accept the loss. Reset tomorrow. The stoic endures."</em>
    </span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

left, right = st.columns([1.7,1])
with left:
    tab1, tab2, tab3 = st.tabs(["⚔️ GOLD CORE", "🇪🇺 EURUSD", "🇿🇦 USDZAR"])
    with tab1:
        st.markdown(f'''<div class="glass">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <div class="section-hdr" style="margin:0;">SA SMART LOGIC</div>
            <div>{conf_label}</div>
          </div>
          {conf_breakdown}
        </div>''', unsafe_allow_html=True)
        html="""<div style="height:360px;border-radius:12px;overflow:hidden;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AXAUUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg&hide_side_toolbar=1" style="width: 100%; height: 100%; border: none;"></iframe></div>"""
        st.components.v1.html(html, height=380)
        st.markdown(f'''<div class="glass" style="margin-top:8px;">
          <div class="section-hdr">Gold Metrics</div>
          <div class="metric-grid">
            <div class="metric-item"><div class="metric-lbl">Price</div><div class="metric-val">${price:,.2f}</div></div>
            <div class="metric-item"><div class="metric-lbl">EMA50/200</div><div class="metric-val">{ema50:.0f} / {ema200:.0f}</div></div>
            <div class="metric-item"><div class="metric-lbl">RSI</div><div class="metric-val" style="color:{"#ff9800" if gold_rsi>70 else "#00e676" if gold_rsi<30 else "#d0d0f0"};">{gold_rsi:.1f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Momentum</div><div class="metric-val" style="color:{"#00e676" if gold_momentum>0 else "#ff5252"};">{gold_momentum:+.2f}</div></div>
            <div class="metric-item"><div class="metric-lbl">MACD</div><div class="metric-val" style="color:{"#00e676" if gold_macd>0 else "#ff5252"};">{gold_macd:+.5f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Volatility</div><div class="metric-val">{gold_volatility:.4f}</div></div>
          </div>
        </div>''', unsafe_allow_html=True)
    with tab2:
        html2="""<div style="height:360px;border-radius:12px;overflow:hidden;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AEURUSD&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg&hide_side_toolbar=1" style="width: 100%; height: 100%; border: none;"></iframe></div>"""
        st.components.v1.html(html2, height=380)
        st.markdown(f'''<div class="glass" style="margin-top:8px;">
          <div class="section-hdr">EURUSD Metrics</div>
          <div class="metric-grid">
            <div class="metric-item"><div class="metric-lbl">Price</div><div class="metric-val">{eur_price:.5f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Signal</div><div class="metric-val" style="color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#d0d0f0"};">{eur_sig}</div></div>
            <div class="metric-item"><div class="metric-lbl">EMA20/100</div><div class="metric-val">{eur20:.4f} / {eur100:.4f}</div></div>
            <div class="metric-item"><div class="metric-lbl">RSI</div><div class="metric-val">{eur_rsi:.1f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Momentum</div><div class="metric-val" style="color:{"#00e676" if eur_momentum>0 else "#ff5252"};">{eur_momentum:+.5f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Trend</div><div class="metric-val">{"BULLISH" if eur_sig=="BUY" else "BEARISH" if eur_sig=="SELL" else "NEUTRAL"}</div></div>
          </div>
        </div>''', unsafe_allow_html=True)
    with tab3:
        html3="""<div style="height:360px;border-radius:12px;overflow:hidden;"><iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview&symbol=OANDA%3AUSDZAR&interval=15&theme=dark&style=1&timezone=Africa%2FJohannesburg&hide_side_toolbar=1" style="width: 100%; height: 100%; border: none;"></iframe></div>"""
        st.components.v1.html(html3, height=380)
        st.markdown(f'''<div class="glass" style="margin-top:8px;">
          <div class="section-hdr">USDZAR Metrics</div>
          <div class="metric-grid">
            <div class="metric-item"><div class="metric-lbl">Rate</div><div class="metric-val">R{zar_price:.4f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Signal</div><div class="metric-val" style="color:{"#00e676" if zar_sig=="SELL" else "#ff5252" if zar_sig=="BUY" else "#d0d0f0"};">{zar_sig}</div></div>
            <div class="metric-item"><div class="metric-lbl">EMA20/100</div><div class="metric-val">{zar20:.4f} / {zar100:.4f}</div></div>
            <div class="metric-item"><div class="metric-lbl">RSI</div><div class="metric-val">{zar_rsi:.1f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Momentum</div><div class="metric-val" style="color:{"#00e676" if zar_momentum<0 else "#ff5252"};">{zar_momentum:+.6f}</div></div>
            <div class="metric-item"><div class="metric-lbl">Rand SELL=BUY Gold</div><div class="metric-val" style="color:#FFD700;">{"✅ CONFIRMED" if zar_sig=="SELL" else "❌ WAIT"}</div></div>
          </div>
        </div>''', unsafe_allow_html=True)

    st.write("")
    if len(st.session_state.trades) >= 4:
        trades_str = "<br>".join(st.session_state.trades)
        st.markdown(f'''<div class="locked">
          <div style="font-family:'Orbitron',sans-serif;font-size:18px;font-weight:900;color:#ff5252;margin-bottom:8px;">🔒 SA PORTFOLIO LOCKED — 4/4 TRADES</div>
          <div style="font-size:11px;color:#ff9090;">{trades_str}</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:10px;font-style:italic;">"Know when to stop. Discipline is your edge."</div>
        </div>''', unsafe_allow_html=True)
    elif agree_buy:
        sl, tp = calculate_levels(price, atr, True, rr_v if "rr_v" in locals() else 2.5)
        badge = "HIGH CONVICTION 🇿🇦" if conf >= 75 else "MEDIUM SETUP"
        st.markdown(f'''<div class="buy-signal">
          🟢 ELITE BUY — {badge}<br>
          <span style="font-size:13px;font-family:'JetBrains Mono',monospace;font-weight:600;">
            Entry {price:.2f} · SL {sl:.2f} · TP {tp:.2f}<br>
            Confidence {conf}% · ZAR R{zar_price:.4f}
          </span>
        </div>''', unsafe_allow_html=True)
        if st.button("✅ EXECUTE BUY — SA EDITION"):
            st.session_state.trades.append(f"BUY {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *SA EDITION EXECUTED*\n🟢 BUY XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} USDZAR:{zar_sig} R{zar_price:.4f}\n{len(st.session_state.trades)}/4 TRADES")
            st.rerun()
    elif agree_sell:
        sl, tp = calculate_levels(price, atr, False, rr_v if "rr_v" in locals() else 2.5)
        badge = "HIGH CONVICTION 🇿🇦" if conf >= 75 else "MEDIUM SETUP"
        st.markdown(f'''<div class="sell-signal">
          🔴 ELITE SELL — {badge}<br>
          <span style="font-size:13px;font-family:'JetBrains Mono',monospace;font-weight:600;">
            Entry {price:.2f} · SL {sl:.2f} · TP {tp:.2f}<br>
            Confidence {conf}% · ZAR R{zar_price:.4f}
          </span>
        </div>''', unsafe_allow_html=True)
        if st.button("✅ EXECUTE SELL — SA EDITION"):
            st.session_state.trades.append(f"SELL {now.strftime('%H:%M')} {price:.2f} {conf}%")
            send_alert(f"⚔️ *SA EDITION EXECUTED*\n🔴 SELL XAUUSD {price:.2f}\nSL {sl:.2f} TP {tp:.2f}\nCONF {conf}% EUR:{eur_sig} USDZAR:{zar_sig} R{zar_price:.4f}\n{len(st.session_state.trades)}/4 TRADES")
            st.rerun()
    else:
        st.markdown(f'''<div class="wait-signal">
          <div style="font-family:'Orbitron',sans-serif;font-size:18px;font-weight:900;color:#55557a;margin-bottom:8px;">⚪ STOIC WAIT — SA CHECK</div>
          <div style="font-size:11px;color:#44445a;">
            Gold Setup: {"✅" if (setup_bull or setup_bear) else "❌"} &nbsp;|&nbsp;
            DXY Fund: {"✅" if (fund_bull or fund_bear) else "❌"} &nbsp;|&nbsp;
            EUR: <span style="color:{"#00e676" if eur_sig!="WAIT" else "#555577"};">{eur_sig}</span> &nbsp;|&nbsp;
            ZAR: <span style="color:{"#00e676" if zar_sig=="SELL" else "#555577"};">{zar_sig}</span> (Need SELL for BUY)
          </div>
          <div style="font-size:11px;color:#33334a;margin-top:8px;font-style:italic;">"Patience is not passive. It is concentrated strength." — Marcus Aurelius</div>
        </div>''', unsafe_allow_html=True)

with right:
    # ── RAND CALCULATOR ────────────────────────────────
    st.markdown('<div class="glass"><div class="section-hdr">🇿🇦 Rand Position Calculator</div>', unsafe_allow_html=True)
    bal_usd = st.number_input("Balance $ (Cent)", 10.0, 50000.0, 500.0)
    st.caption(f"≈ R{bal_usd*zar_price:,.2f} at R{zar_price:.2f}/$")
    risk = st.slider("Risk %", 0.5, 2.0, 1.0)
    rr = st.selectbox("Risk:Reward", ["1:2","1:2.5","1:3"], index=1)
    rr_v = float(rr.split(":")[1])
    risk_amt = bal_usd * risk / 100
    lots = max(0.01, min(risk_amt / ((atr * 1.5) * 10), 2.0))
    st.markdown(f'''<div style="background:#0a0a12;border:1px solid rgba(255,215,0,0.15);border-radius:12px;padding:14px 16px;margin-top:10px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;">
        <div><div class="metric-lbl">USD Risk</div><div style="font-size:16px;font-weight:800;color:#FFD700;">${risk_amt:.2f}</div><div style="font-size:10px;color:#555577;">≈ R{risk_amt*zar_price:.2f}</div></div>
        <div><div class="metric-lbl">USD Reward ({rr})</div><div style="font-size:16px;font-weight:800;color:#00e676;">${risk_amt*rr_v:.2f}</div><div style="font-size:10px;color:#555577;">≈ R{risk_amt*rr_v*zar_price:.2f}</div></div>
        <div><div class="metric-lbl">Lot Size</div><div style="font-size:16px;font-weight:800;color:#d0d0f0;">{lots:.2f}</div></div>
        <div><div class="metric-lbl">ATR × 1.5 SL</div><div style="font-size:16px;font-weight:800;color:#d0d0f0;">{atr*1.5:.2f}</div></div>
      </div>
    </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SA VOTE SYSTEM ─────────────────────────────────
    st.markdown('<div class="glass" style="margin-top:12px;"><div class="section-hdr">🗳️ SA Vote System</div>', unsafe_allow_html=True)
    gold_vote = "BUY" if agree_buy else "SELL" if agree_sell else "WAIT"
    for label, sig, hint, weight in [
        ("🥇 GOLD",   gold_vote, "50% — Core signal",           gold_vote != "WAIT"),
        ("🇪🇺 EURUSD", eur_sig,  "25% — Must match Gold",       eur_sig != "WAIT"),
        ("🇿🇦 USDZAR", zar_sig,  "SELL=Strong Rand=Gold BUY",   zar_sig != "WAIT"),
    ]:
        sig_color = "#00e676" if sig in ("BUY","SELL") else "#44445a"
        st.markdown(f'''<div class="vote-row">
          <div><span style="font-size:12px;">{label}</span><br><span style="font-size:10px;color:#44445a;">{hint}</span></div>
          <span style="font-family:'Orbitron',sans-serif;font-size:13px;font-weight:900;color:{sig_color};">{sig}</span>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SIGNAL STRENGTH ────────────────────────────────
    st.markdown('<div class="glass" style="margin-top:12px;"><div class="section-hdr">📡 Signal Strength</div>', unsafe_allow_html=True)
    for lbl, rsi_val in [("Gold RSI", gold_rsi), ("EUR RSI", eur_rsi), ("ZAR RSI", zar_rsi)]:
        rsi_color = "#ff9800" if rsi_val > 70 else "#00e676" if rsi_val < 30 else "#aaaacc"
        rsi_note = "⚡ Overbought" if rsi_val > 70 else "⚠️ Oversold" if rsi_val < 30 else "✅ Neutral"
        rsi_pct = int(rsi_val)
        st.markdown(f'''<div style="margin:6px 0;">
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px;">
            <span style="color:#7777aa;">{lbl}</span>
            <span style="color:{rsi_color};font-weight:700;">{rsi_val:.1f} {rsi_note}</span>
          </div>
          <div class="conf-bar-wrap">
            <div class="conf-bar" style="--w:{rsi_pct}%;width:{rsi_pct}%;background:linear-gradient(90deg,#1a1a30 0%,{rsi_color} 100%);"></div>
          </div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── DISCIPLINE / LOSS TRACKER ──────────────────────
    st.markdown('<div class="glass" style="margin-top:12px;"><div class="section-hdr">⚠️ Stoic Discipline Tracker</div>', unsafe_allow_html=True)
    disc_fill = int(st.session_state.losses / 2 * 100)
    disc_color = "#ff1744" if st.session_state.losses >= 2 else "#ff9800" if st.session_state.losses == 1 else "#00e676"
    st.markdown(f'''<div class="discipline-ring-wrap">
      <div>
        <div class="disc-label">Consecutive Losses</div>
        <div class="disc-count" style="color:{disc_color};">{st.session_state.losses}/2</div>
        <div class="disc-label" style="margin-top:4px;">{"🔒 KILL-SWITCH ARMED" if st.session_state.losses >= 2 else "DISCIPLINE INTACT" if st.session_state.losses == 0 else "⚠️ CAUTION"}</div>
      </div>
      <div style="flex:1;">
        <div class="loss-progress-wrap" style="height:16px;border-radius:10px;">
          <div class="loss-progress-bar" style="background:{disc_color};width:{disc_fill}%;height:16px;border-radius:10px;transition:width 0.6s ease;"></div>
        </div>
        <div style="font-size:10px;color:#44445a;margin-top:5px;font-style:italic;">"Two losses = today is done. Protect the account."</div>
      </div>
    </div>''', unsafe_allow_html=True)
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Log Loss"):
            st.session_state.losses += 1
            send_alert(f"⚠️ Loss recorded: {st.session_state.losses}/2\n{st.session_state.losses}/2 consecutive losses.")
            if st.session_state.losses >= 2:
                send_alert(f"🔒 KILL-SWITCH TRIGGERED!\n2 consecutive losses - Trading disabled for today.")
            st.rerun()
    with col2:
        if st.button("✅ Log Win"):
            st.session_state.losses = 0
            send_alert(f"✅ Win recorded! Loss counter reset to 0.")
            st.rerun()
    if st.button("🔄 Reset Losses"):
        st.session_state.losses = 0
        send_alert(f"🔄 Loss counter manually reset to 0.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── TRADE HISTORY ──────────────────────────────────
    if st.session_state.trade_history:
        st.markdown('<div class="glass" style="margin-top:12px;"><div class="section-hdr">📝 Trade History</div>', unsafe_allow_html=True)
        for trade in reversed(st.session_state.trade_history[-5:]):
            is_win = "WIN" in trade["record"]
            card_class = "trade-win" if is_win else "trade-loss"
            icon = "✅" if is_win else "❌"
            st.markdown(f'''<div class="trade-card {card_class}">
              <span style="color:#6666aa;font-size:10px;">{trade["timestamp"]}</span><br>
              <span style="font-size:11px;">{icon} {trade["record"]}</span>
            </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
