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
.kpi { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 16px; padding: 18px; border: 1px solid #222; border-top: 1px solid rgba(255,215,0,0.3); box-shadow: 0 0 12px rgba(255,2[...]
.kpi:hover { transform: scale(1.02); }
.kpi-val { font-size: 24px; font-weight: 800; color: white; }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }
.gold-text { background: linear-gradient(90deg,#FFD700,#FFA500,#FFD700); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 6s linear[...]
@keyframes shine { 0% { background-position: 0% } 100% { background-position: 200% } }
.buy-signal { background: linear-gradient(135deg, #00c853, #00e676); color: black; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; }
.sell-signal { background: linear-gradient(135deg, #ff1744, #ff5252); color: white; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 22px; }
.wait-signal { background: #16161a; border: 2px dashed #333; border-radius: 16px; padding: 24px; text-align: center; }
.locked { background: linear-gradient(135deg, #2a0a0a, #1a0a0a); border: 1px solid #ff1744; border-radius: 16px; padding: 20px; text-align: center; }
.killswitch { background: linear-gradient(135deg, #8b0000, #ff0000); border: 2px solid #ff1744; border-radius: 16px; padding: 24px; text-align: center; font-weight: 900; font-size: 18px; color: wh[...]
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
.conf-high { background: linear-gradient(90deg,#00c853,#00e676); color:black; padding:8px 14px; border-radius:20px; font-weight:900; }
.conf-mid { background: #333; color:#FFD700; padding:8px 14px; border-radius:20px; font-weight:900; border:1px solid #FFD700; }
.conf-low { background: #222; color:#888; padding:8px 14px; border-radius:20px; }
.conf-verylow { background: #1a0a0a; color:#ff5252; padding:8px 14px; border-radius:20px; border:1px solid #ff5252; }
.status-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:12px; margin:16px 0 8px; }
.status-item { background: linear-gradient(145deg, #1a1a1e, #121214); border-radius: 14px; padding: 14px; border: 1px solid #222; min-height: 92px; }
.status-pill { display:inline-block; margin-top:8px; padding:6px 10px; border-radius:999px; font-size:11px; font-weight:800; letter-spacing:0.5px; }
.stButton>button { background: linear-gradient(90deg,#D4AF37,#FFD700); color: black; font-weight: 900; height: 54px; border-radius: 12px; width: 100%; border: none; }
#MainMenu, footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "trades" not in st.session_state: st.session_state.trades=[]
if "trade_history" not in st.session_state: st.session_state.trade_history = []
if "losses" not in st.session_state: st.session_state.losses = 0
if "last_reset" not in st.session_state: st.session_state.last_reset=datetime.now(SAST).date()
if "balance_usd" not in st.session_state: st.session_state.balance_usd = 5000.0
if "risk_pct" not in st.session_state: st.session_state.risk_pct = 1.0
if "rr_label" not in st.session_state: st.session_state.rr_label = "1:2.5"
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

def format_usd(amount):
    return f"${amount:,.2f}"

# DATA COLLECTION
df_gold, price, atr, ema50, ema200, gold_rsi, gold_macd, gold_momentum, gold_volatility = get_gold()
eur_price, eur_sig, eur20, eur100, eur_rsi, eur_atr, eur_momentum = get_forex("EURUSD=X")
zar_price, zar_sig, zar20, zar100, zar_rsi, zar_atr, zar_momentum = get_forex("USDZAR=X")  # SA PAIR
dxy, dxy_chg, dxy_ema20, dxy_momentum = get_dxy()
now = datetime.now(SAST)
bal_usd = st.session_state.balance_usd
risk = st.session_state.risk_pct
rr_v = float(st.session_state.rr_label.split(":")[1])
risk_amt = bal_usd * risk / 100
equity = bal_usd
available_margin = max(equity - risk_amt, 0.0)
trade_count = len(st.session_state.trades)
buy_count = sum(1 for trade in st.session_state.trades if trade.startswith("BUY"))
sell_count = sum(1 for trade in st.session_state.trades if trade.startswith("SELL"))
margin_ratio = (available_margin / equity) if equity else 0.0

if st.session_state.losses >= 2 or trade_count >= 4 or risk >= 1.8 or margin_ratio < 0.98:
    account_health = "CRITICAL"
    account_health_color = "#ff5252"
    account_health_bg = "rgba(255, 82, 82, 0.18)"
elif st.session_state.losses == 1 or risk >= 1.3 or margin_ratio < 0.99:
    account_health = "WARNING"
    account_health_color = "#FFD54F"
    account_health_bg = "rgba(255, 213, 79, 0.16)"
else:
    account_health = "HEALTHY"
    account_health_color = "#00e676"
    account_health_bg = "rgba(0, 230, 118, 0.16)"

# HEADER SA
st.markdown(f"""
<div class="glass" style="display:flex;justify-content:space-between;align-items:center;">
<div><span class="gold-text" style="font-size:22px;">⚔️ MARONG STOIC BOT</span> <span style="background:#007A4B;color:white;padding:3px 8px;border-radius:4px;margin-left:8px;">🇿🇦 SA EDITION</span></div>
<div style="text-align:right;"><span style="color:#FFD700;font-weight:700;">{now.strftime('%H:%M:%S')}</span> SAST<br><span style="font-size:11px;color:#00e676;">● RAND SMART ACTIVE</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="glass" style="margin-top:16px;">
<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
<div>
<div class="kpi-label">ACCOUNT TOTALS STATUS</div>
<div style="font-size:13px;color:#999;">Live USD overview synced to balance, risk and trade activity</div>
</div>
<div class="status-pill" style="background:{account_health_bg};color:{account_health_color};border:1px solid {account_health_color};">{account_health}</div>
</div>
<div class="status-grid">
<div class="status-item"><div class="kpi-label">Total Account Balance</div><div class="kpi-val">{format_usd(bal_usd)}</div><div style="font-size:12px;color:#888;">Cash balance in USD</div></div>
<div class="status-item"><div class="kpi-label">Risk Amount</div><div class="kpi-val">{format_usd(risk_amt)}</div><div style="font-size:12px;color:#888;">{risk:.1f}% risk per trade</div></div>
<div class="status-item"><div class="kpi-label">Account Equity</div><div class="kpi-val">{format_usd(equity)}</div><div style="font-size:12px;color:#888;">Live equity view in USD</div></div>
<div class="status-item"><div class="kpi-label">Available Margin</div><div class="kpi-val">{format_usd(available_margin)}</div><div style="font-size:12px;color:{account_health_color};">{account_health} • Free after current risk allocation</div></div>
<div class="status-item"><div class="kpi-label">Total Trades Executed</div><div class="kpi-val">{trade_count}</div><div style="font-size:12px;color:#888;">BUY {buy_count} • SELL {sell_count}</div></div>
</div>
</div>
""", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><div class="kpi-label">XAUUSD CORE</div><div class="kpi-val">${price:,.2f}</div><div style="font-size:12px;color:#888;">{ema50:.0f}/{ema200:.0f} | RSI {gold_rsi:.0f}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><div class="kpi-label">EURUSD CONFIRM</div><div class="kpi-val">{eur_price:.5f}</div><div style="font-size:12px;color:{"#00e676" if eur_sig=="BUY" else "#ff5252" if eur_sig=="SELL" else "#999"};">{eur_sig} | RSI {eur_rsi:.0f}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><div class="kpi-label">USDZAR HOME 🇿🇦</div><div class="kpi-val">R{zar_price:.4f}</div><div style="font-size:12px;color:{"#00e676" if zar_sig=="SELL" else "#ff5252" if zar_sig=="BUY" else "#999"};">{zar_sig} | RSI {zar_rsi:.0f}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi"><div class="kpi-label">DXY FUND</div><div class="kpi-val">{dxy:.2f}</div><div style="font-size:12px;color:{"#00e676" if dxy_chg<0 else "#ff5252"}>{dxy_chg:+.2f}% | MOM {dxy_momentum:+.1f}</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi"><div class="kpi-label">LOSSES</div><div class="kpi-val">{st.session_state.losses}/2</div><div style="font-size:12px;color:{"#ff1744" if st.session_state.losses >= 2 else "#00e676"};">{"🔒 KILL-SWITCH" if st.session_state.losses >= 2 else "Status OK"}</div></div>', unsafe_allow_html=True)

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
    bal_usd = st.number_input("Balance $", 100.0, 500000.0, 5000.0, key="balance_usd")
    st.caption(f"{format_usd(bal_usd)} ≈ R{bal_usd*zar_price:,.2f} at R{zar_price:.2f}/$")
    risk = st.slider("Risk %", 0.5, 2.0, 1.0, key="risk_pct")
    rr_options = ["1:2","1:2.5","1:3"]
    rr = st.selectbox("RR", rr_options, index=rr_options.index(st.session_state.rr_label), key="rr_label")
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
