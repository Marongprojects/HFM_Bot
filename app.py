from datetime import datetime, timedelta
from dataclasses import replace
import io
import json
import secrets
import zipfile
import logging

import numpy as np
import pandas as pd
import pytz
import streamlit as st
from dotenv import load_dotenv

import bot


logging.basicConfig(
    level=logging.INFO,
    filename=bot.PROJECT_DIR / "bot.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


TIMEFRAME_OPTIONS = {
    "M5": (bot.mt5.TIMEFRAME_M5, "5min"),
    "M15": (bot.mt5.TIMEFRAME_M15, "15min"),
    "H1": (bot.mt5.TIMEFRAME_H1, "1h"),
    "H4": (bot.mt5.TIMEFRAME_H4, "4h"),
}


load_dotenv(bot.ENV_FILE)

for key in [
    "mt5_test_result", "dry_run_result", "positions_result",
    "history_result", "manual_order_result", "filtered_deals_export",
    "live_order_token", "live_order_token_expires", "last_run",
]:
    if key not in st.session_state:
        st.session_state[key] = None

st.set_page_config(
    page_title="MARONG STOIC BOT",
    page_icon=":material/query_stats:",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace !important; }
    .stApp { background: #000; color: #fff; }
    [data-testid="stSidebar"] { background: #000 !important; border-right: 1px solid #FFD700; }
    [data-testid="stSidebar"] * { color: #fff; }
    h1, h2, h3 { color: #FFD700 !important; }
    [data-testid="stMetricValue"] { color: #FFD700; }
    .stoic-header { display: flex; justify-content: space-between; align-items: center; gap: 20px; padding: 18px 22px; margin-bottom: 20px; border-bottom: 2px solid #FFD700; background: repeating-linear-gradient(90deg, #000 0, #000 39px, rgba(255,215,0,.07) 40px, #000 41px); }
    .stoic-brand { color: #FFD700; font-size: clamp(18px, 3vw, 28px); font-weight: 800; letter-spacing: 1px; }
    .stoic-clock { color: #FFD700; font-size: 20px; font-weight: 800; text-align: right; }
    .stoic-caption { color: #777; font-size: 10px; letter-spacing: 1px; text-align: right; }
    .gold-panel { padding: 16px; background: #050505; border: 1px solid #FFD700; border-radius: 14px; box-shadow: 0 0 18px rgba(255,215,0,.12); }
    .signal-wait { padding: 18px; text-align: center; color: #888; background: #0a0a0a; border: 1px dashed #444; border-radius: 14px; }
    .signal-buy { padding: 18px; text-align: center; color: #00e676; background: #001a00; border: 2px solid #00e676; border-radius: 14px; }
    .signal-sell { padding: 18px; text-align: center; color: #ff6b6b; background: #1a0000; border: 2px solid #ff1744; border-radius: 14px; }
    .stButton > button { min-height: 46px; color: #000 !important; background: linear-gradient(90deg, #B8860B, #FFD700, #D4AF37) !important; border: 0 !important; font-weight: 800 !important; }
    [data-testid="stDataFrame"] { border: 1px solid #555; }
    @media (max-width: 720px) {
      .block-container { padding: 1rem .75rem 2rem; }
      .stoic-header { align-items: flex-start; padding: 14px 10px; }
      .stoic-brand { font-size: 17px; }
      .stoic-clock { font-size: 14px; }
      .stoic-caption { font-size: 8px; }
      [data-testid="stMetricValue"] { font-size: 22px; }
      [data-testid="stHorizontalBlock"] { gap: .6rem; }
      .gold-panel { padding: 12px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def mask_secret(value: str) -> str:
    if not value:
        return "Not set"
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"


def infer_point(symbol: str) -> float:
    if symbol.endswith("JPY"):
        return 0.01
    if symbol in {"XAUUSD", "XAGUSD"}:
        return 0.1
    return 0.0001


def frame_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_snapshot_zip(symbol: str) -> tuple[bytes | None, str]:
    files_added = 0
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        positions_result = st.session_state.positions_result
        if positions_result and positions_result.get("loaded") and positions_result.get("payload"):
            positions_df = positions_result["payload"].get("positions")
            orders_df = positions_result["payload"].get("orders")
            if isinstance(positions_df, pd.DataFrame) and not positions_df.empty:
                archive.writestr(f"positions_{symbol}.csv", frame_to_csv_bytes(positions_df))
                files_added += 1
            if isinstance(orders_df, pd.DataFrame) and not orders_df.empty:
                archive.writestr(f"pending_orders_{symbol}.csv", frame_to_csv_bytes(orders_df))
                files_added += 1

        filtered_deals = st.session_state.filtered_deals_export
        if isinstance(filtered_deals, pd.DataFrame) and not filtered_deals.empty:
            archive.writestr(f"trade_history_filtered_{symbol}.csv", frame_to_csv_bytes(filtered_deals))
            files_added += 1

        dry_run_result = st.session_state.dry_run_result
        if dry_run_result:
            archive.writestr("dry_run_result.json", json.dumps(dry_run_result, default=str, indent=2))
            files_added += 1

        manual_order_result = st.session_state.manual_order_result
        if manual_order_result:
            archive.writestr("manual_order_result.json", json.dumps(manual_order_result, default=str, indent=2))
            files_added += 1

    if files_added == 0:
        return None, "No snapshots are loaded yet. Refresh positions/history or run a cycle first."

    return buffer.getvalue(), f"Snapshot bundle ready with {files_added} file(s)."


def token_is_valid() -> bool:
    token = st.session_state.live_order_token
    expires = st.session_state.live_order_token_expires
    if not token or not expires:
        return False
    return datetime.now(pytz.UTC) <= expires


def issue_live_order_token() -> str:
    token = secrets.token_hex(16).upper()
    st.session_state.live_order_token = token
    st.session_state.live_order_token_expires = datetime.now(pytz.UTC) + timedelta(seconds=30)
    return token


def clear_live_order_token() -> None:
    st.session_state.live_order_token = None
    st.session_state.live_order_token_expires = None


@st.cache_data(show_spinner=False)
def build_demo_market_data(symbol: str, bars: int, trend_bias: float, volatility: float, freq: str) -> pd.DataFrame:
    periods = max(80, bars)
    index = pd.date_range(end=pd.Timestamp.now("UTC"), periods=periods, freq=freq)
    base_price = 4407.0 if symbol == "XAUUSD" else 1.08 if symbol.endswith("USD") else 150.0
    trend = np.linspace(0, trend_bias, periods)
    noise = np.random.normal(0, volatility, periods).cumsum()
    close = base_price + trend + noise
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    high = np.maximum(open_, close) + np.abs(np.random.normal(0, volatility / 2, periods))
    low = np.minimum(open_, close) - np.abs(np.random.normal(0, volatility / 2, periods))

    df = pd.DataFrame(
        {
            "time": index,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": np.random.randint(120, 420, periods),
        }
    )
    return bot.add_indicators(df)


def build_demo_request(config: bot.BotConfig, signal: str, price: float) -> dict:
    point = infer_point(config.symbol)
    if signal == "buy":
        sl = price - config.sl_points * point
        tp = price + config.tp_points * point
        order_type = "BUY"
    elif signal == "sell":
        sl = price + config.sl_points * point
        tp = price - config.tp_points * point
        order_type = "SELL"
    else:
        sl = price
        tp = price
        order_type = "HOLD"

    return {
        "symbol": config.symbol,
        "volume": config.lot_size,
        "type": order_type,
        "entry_price": round(price, 5),
        "sl": round(sl, 5),
        "tp": round(tp, 5),
        "dry_run": config.dry_run,
    }


def build_runtime_config(config: bot.BotConfig, symbol: str, lot_size: float, bars: int, dry_run: bool) -> bot.BotConfig:
    return replace(
        config,
        symbol=symbol,
        lot_size=lot_size,
        max_bars=bars,
        dry_run=dry_run,
    )


def fetch_positions_snapshot(config: bot.BotConfig) -> tuple[bool, str, dict | None]:
    try:
        bot.initialize_mt5(config)
        bot.ensure_symbol(config.symbol)

        positions = bot.mt5.positions_get(symbol=config.symbol)
        orders = bot.mt5.orders_get(symbol=config.symbol)

        positions_df = pd.DataFrame(list(positions)) if positions else pd.DataFrame()
        orders_df = pd.DataFrame(list(orders)) if orders else pd.DataFrame()

        if not positions_df.empty and "time" in positions_df.columns:
            positions_df["time"] = pd.to_datetime(positions_df["time"], unit="s", utc=True)
        if not orders_df.empty and "time_setup" in orders_df.columns:
            orders_df["time_setup"] = pd.to_datetime(orders_df["time_setup"], unit="s", utc=True)

        return True, f"Loaded MT5 positions snapshot for {config.symbol}.", {
            "positions": positions_df,
            "orders": orders_df,
        }
    except Exception as exc:
        return False, str(exc), None
    finally:
        bot.shutdown_mt5()


def fetch_trade_history(config: bot.BotConfig, days_back: int) -> tuple[bool, str, pd.DataFrame | None]:
    try:
        bot.initialize_mt5(config)
        end_time = datetime.now(pytz.UTC)
        start_time = end_time - pd.Timedelta(days=days_back)
        deals = bot.mt5.history_deals_get(start_time, end_time, group=f"*{config.symbol}*")
        deals_df = pd.DataFrame(list(deals)) if deals else pd.DataFrame()
        if not deals_df.empty and "time" in deals_df.columns:
            deals_df["time"] = pd.to_datetime(deals_df["time"], unit="s", utc=True)
        return True, f"Loaded deal history for the last {days_back} day(s).", deals_df
    except Exception as exc:
        return False, str(exc), None
    finally:
        bot.shutdown_mt5()


def fetch_real_market_data(config: bot.BotConfig) -> tuple[pd.DataFrame | None, str | None]:
    try:
        bot.initialize_mt5(config)
        bot.ensure_symbol(config.symbol)
        market = bot.fetch_rates(config.symbol, config.timeframe, config.max_bars)
        return bot.add_indicators(market), None
    except Exception as exc:
        return None, str(exc)
    finally:
        bot.shutdown_mt5()


def fetch_live_order_preview(config: bot.BotConfig, side: str) -> tuple[bool, str, dict | None]:
    try:
        bot.initialize_mt5(config)
        bot.ensure_symbol(config.symbol)
        preview = bot.build_order_request(config, side)
        preview["type"] = side.upper()
        return True, "Built live order preview from current MT5 tick data.", preview
    except Exception as exc:
        return False, str(exc), None
    finally:
        bot.shutdown_mt5()


def submit_manual_order(config: bot.BotConfig, side: str) -> tuple[bool, str, dict | None]:
    try:
        bot.initialize_mt5(config)
        bot.ensure_symbol(config.symbol)
        request = bot.build_order_request(config, side)
        result = bot.mt5.order_send(request)
        if result is None:
            raise RuntimeError(f"Order send failed: {bot.mt5.last_error()}")
        if result.retcode != bot.mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Order rejected: {result.retcode} | {result.comment}")
        return True, f"Manual {side} order sent successfully.", result._asdict()
    except Exception as exc:
        return False, str(exc), None
    finally:
        bot.shutdown_mt5()


def run_dry_cycle(config: bot.BotConfig) -> tuple[bool, str, dict | None]:
    try:
        bot.initialize_mt5(config)
        bot.ensure_symbol(config.symbol)
        market = bot.fetch_rates(config.symbol, config.timeframe, config.max_bars)
        market = bot.add_indicators(market)
        signal = bot.generate_signal(market)
        latest = market.iloc[-1]
        order_preview = build_demo_request(config, signal, float(latest["close"]))
        headlines = bot.fetch_news_headlines(config)
        return True, f"Dry-run cycle completed for {config.symbol}.", {
            "signal": signal,
            "close": round(float(latest["close"]), 5),
            "order_preview": order_preview,
            "headlines": headlines,
            "timestamp": datetime.now(pytz.timezone(config.timezone)).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
    except Exception as exc:
        return False, str(exc), None
    finally:
        bot.shutdown_mt5()


def render_dry_cycle_result(result: dict | None) -> None:
    if not result:
        return

    if result["completed"] and result["payload"]:
        payload = result["payload"]
        st.markdown(":blue-badge[Cycle completed]")
        st.write(f"Signal: {payload['signal'].upper()}")
        st.write(f"Last close: {payload['close']:.5f}")
        st.write(f"Time: {payload['timestamp']}")
        st.json(payload["order_preview"], expanded=False)
        if payload["headlines"]:
            st.caption("News snapshot: " + " | ".join(payload["headlines"]))
    else:
        st.caption(result["message"])


@st.fragment(run_every="15s")
def auto_dry_cycle_15s(config: bot.BotConfig, enabled: bool) -> None:
    if not enabled:
        render_dry_cycle_result(st.session_state.dry_run_result)
        return

    completed, message, payload = run_dry_cycle(config)
    st.session_state.dry_run_result = {
        "completed": completed,
        "message": message,
        "payload": payload,
    }
    render_dry_cycle_result(st.session_state.dry_run_result)


@st.fragment(run_every="30s")
def auto_dry_cycle_30s(config: bot.BotConfig, enabled: bool) -> None:
    if not enabled:
        render_dry_cycle_result(st.session_state.dry_run_result)
        return

    completed, message, payload = run_dry_cycle(config)
    st.session_state.dry_run_result = {
        "completed": completed,
        "message": message,
        "payload": payload,
    }
    render_dry_cycle_result(st.session_state.dry_run_result)


@st.fragment(run_every="60s")
def auto_dry_cycle_60s(config: bot.BotConfig, enabled: bool) -> None:
    if not enabled:
        render_dry_cycle_result(st.session_state.dry_run_result)
        return

    completed, message, payload = run_dry_cycle(config)
    st.session_state.dry_run_result = {
        "completed": completed,
        "message": message,
        "payload": payload,
    }
    render_dry_cycle_result(st.session_state.dry_run_result)


def test_mt5_connection(config: bot.BotConfig) -> tuple[bool, str, dict | None]:
    if not config.login or not config.password or not config.server:
        return False, "Fill MT5_LOGIN, MT5_PASSWORD, and MT5_SERVER in .env first.", None

    try:
        bot.initialize_mt5(config)
        account = bot.mt5.account_info()
        if account is None:
            return True, "MT5 initialized, but account information is unavailable.", None

        account_snapshot = {
            "login": account.login,
            "server": account.server,
            "balance": account.balance,
            "equity": account.equity,
            "margin_free": account.margin_free,
            "leverage": account.leverage,
            "currency": account.currency,
            "company": account.company,
            "name": account.name,
        }
        return True, f"Connected to MT5 account {account.login} on {config.server}.", account_snapshot
    except Exception as exc:
        return False, str(exc), None
    finally:
        bot.shutdown_mt5()


config = bot.BotConfig()
demo_timezone = pytz.timezone(config.timezone)
default_timeframe_label = next(
    (label for label, (value, _) in TIMEFRAME_OPTIONS.items() if value == config.timeframe),
    "M15",
)

with st.sidebar:
    st.title("Bot controls")
    with st.form("demo_controls"):
        data_source = st.segmented_control(
            "Chart data source",
            options=["Simulated", "Real MT5"],
            default="Simulated",
            selection_mode="single",
        )
        symbol_options = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
        symbol = st.selectbox("Symbol", symbol_options, index=0)
        timeframe_label = st.segmented_control(
            "Timeframe",
            options=list(TIMEFRAME_OPTIONS.keys()),
            default=default_timeframe_label,
            selection_mode="single",
        )
        lot_size = st.number_input("Lot size", min_value=0.01, value=float(config.lot_size), step=0.01)
        bars = st.slider("Bars", min_value=120, max_value=500, value=int(config.max_bars), step=20)
        trend_bias = st.slider("Trend bias", min_value=-0.08, max_value=0.08, value=0.02, step=0.01)
        volatility = st.slider("Volatility", min_value=0.0005, max_value=0.02, value=0.003, step=0.0005)
        submitted = st.form_submit_button("Refresh demo", type="primary", icon=":material/play_arrow:")

    auto_run_enabled = st.toggle("Auto-run dry cycle", value=False)
    auto_run_interval = st.segmented_control(
        "Auto-run interval",
        options=["15s", "30s", "60s"],
        default="30s",
        selection_mode="single",
    )
    history_days = st.selectbox("History range", [1, 3, 7, 14, 30], index=2)

    if submitted:
        st.toast("Demo market refreshed", icon=":material/autorenew:")
    if auto_run_enabled:
        st.caption(f"Dry cycle loop is active and will refresh every {auto_run_interval}.")

    st.caption(f"Local time: {datetime.now(demo_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    st.caption("The app can use simulated candles or real MT5 candles without placing live orders.")

config.symbol = symbol
config.lot_size = float(lot_size)
config.max_bars = int(bars)
config.timeframe = TIMEFRAME_OPTIONS[timeframe_label][0]

runtime_config = build_runtime_config(config, symbol, float(lot_size), int(bars), True)
demo_freq = TIMEFRAME_OPTIONS[timeframe_label][1]

market_error = None
if data_source == "Real MT5":
    market, market_error = fetch_real_market_data(runtime_config)
    if market is None:
        market = build_demo_market_data(runtime_config.symbol, runtime_config.max_bars, trend_bias, volatility, demo_freq)
else:
    market = build_demo_market_data(runtime_config.symbol, runtime_config.max_bars, trend_bias, volatility, demo_freq)

signal = bot.generate_signal(market)
latest = market.iloc[-1]
order_preview = build_demo_request(runtime_config, signal, float(latest["close"]))
signal_color = {"buy": "green", "sell": "red", "hold": "orange"}[signal]
now = datetime.now(demo_timezone)

st.markdown(
        f"""
        <div class="stoic-header">
            <div class="stoic-brand">MARONG STOIC BOT</div>
            <div>
                <div class="stoic-clock">{now.strftime('%H:%M:%S')}</div>
                <div class="stoic-caption">SOUTH AFRICA STANDARD TIME</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
)
st.title("Live gold analysis", text_alignment="left")
st.markdown(
    ":blue-badge[Demo mode] "
    f":{signal_color}-badge[{signal.upper()} signal] "
    f":gray-badge[{runtime_config.symbol}] "
    f":gray-badge[{timeframe_label}]"
)

if data_source == "Real MT5" and market_error:
    st.warning(
        f"Real MT5 data could not be loaded. Showing simulated data instead. Details: {market_error}",
        icon=":material/warning:",
    )
elif data_source == "Real MT5":
    st.success("Chart is using real MT5 candle data.", icon=":material/query_stats:")

if auto_run_enabled:
    if auto_run_interval == "15s":
        auto_dry_cycle_15s(runtime_config, True)
    elif auto_run_interval == "30s":
        auto_dry_cycle_30s(runtime_config, True)
    else:
        auto_dry_cycle_60s(runtime_config, True)

with st.container(horizontal=True):
    st.metric(
        "Last close",
        f"{latest['close']:.5f}",
        f"{(latest['close'] - market.iloc[-2]['close']):.5f}",
        border=True,
        chart_data=market["close"].tail(24),
        chart_type="line",
    )
    st.metric(
        "Fast EMA",
        f"{latest['ema_fast']:.5f}",
        f"{(latest['ema_fast'] - market.iloc[-2]['ema_fast']):.5f}",
        border=True,
        chart_data=market["ema_fast"].tail(24),
        chart_type="line",
    )
    st.metric(
        "RSI",
        f"{latest['rsi']:.2f}",
        f"{(latest['rsi'] - market.iloc[-2]['rsi']):.2f}",
        border=True,
        chart_data=market["rsi"].tail(24),
        chart_type="line",
    )
    st.metric("Dry run", "On" if config.dry_run else "Off", None, border=True)

col_left, col_right = st.columns((3, 2), vertical_alignment="top")

with col_left:
    with st.container(border=True):
        st.subheader("Price and indicators")
        chart_df = market.set_index("time")[["close", "ema_fast", "ema_slow"]].tail(120)
        st.line_chart(chart_df, height=360)

    with st.container(border=True):
        st.subheader("Recent market rows")
        recent = market.tail(12).copy()
        recent["time"] = recent["time"].dt.tz_convert(runtime_config.timezone).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(
            recent[["time", "open", "high", "low", "close", "ema_fast", "ema_slow", "rsi"]],
            hide_index=True,
            width="stretch",
        )

with col_right:
    with st.container(border=True):
        st.subheader("Credential readiness")
        login_ready = bool(config.login)
        password_ready = bool(config.password)
        server_ready = bool(config.server)
        news_ready = bool(config.news_api_key)
        st.write(f"MT5 login: {'Configured' if login_ready else 'Missing'}")
        st.write(f"MT5 password: {mask_secret(config.password)}")
        st.write(f"MT5 server: {config.server or 'Not set'}")
        st.write(f"News API key: {'Configured' if news_ready else 'Optional / missing'}")
        if login_ready and password_ready and server_ready:
            st.success("Credentials are ready for a real MT5 login.", icon=":material/check_circle:")
        else:
            st.warning("Fill .env before attempting a live MT5 session.", icon=":material/warning:")

        if st.button("Test MT5 connection", type="primary", icon=":material/link:", width="stretch"):
            with st.spinner("Testing MT5 connection..."):
                connected, message, account_snapshot = test_mt5_connection(runtime_config)
            st.session_state.mt5_test_result = {
                "connected": connected,
                "message": message,
                "account": account_snapshot,
            }
            if connected:
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/error:")

        if st.session_state.mt5_test_result and st.session_state.mt5_test_result["connected"]:
            account = st.session_state.mt5_test_result["account"]
            if account:
                st.space("small")
                st.markdown(":green-badge[MT5 session verified]")
                with st.container(horizontal=True):
                    st.metric("Balance", f"{account['balance']:.2f} {account['currency']}", border=True)
                    st.metric("Equity", f"{account['equity']:.2f} {account['currency']}", border=True)
                    st.metric("Free margin", f"{account['margin_free']:.2f} {account['currency']}", border=True)
                    st.metric("Leverage", f"1:{account['leverage']}", border=True)
                st.caption(
                    f"Account: {account['login']} | Server: {account['server']} | Holder: {account['name']} | Company: {account['company']}"
                )

    with st.container(border=True):
        st.subheader("Dry-run bot cycle")
        st.caption("Runs one MT5-backed analysis cycle and previews the order request without sending a trade.")
        if auto_run_enabled:
            st.info(f"Auto-run is active. A new dry cycle will execute every {auto_run_interval}.", icon=":material/update:")
        if st.button("Run one dry cycle", icon=":material/play_circle:", width="stretch"):
            with st.spinner("Running dry cycle..."):
                completed, message, payload = run_dry_cycle(runtime_config)
            st.session_state.dry_run_result = {
                "completed": completed,
                "message": message,
                "payload": payload,
            }
            if completed:
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/error:")

        render_dry_cycle_result(st.session_state.dry_run_result)

    with st.container(border=True):
        st.subheader("Open positions and orders")
        st.caption("Loads the current MT5 positions and pending orders for the selected symbol.")
        if st.button("Refresh positions", icon=":material/account_balance_wallet:", width="stretch"):
            with st.spinner("Loading positions..."):
                loaded, message, payload = fetch_positions_snapshot(runtime_config)
            st.session_state.positions_result = {
                "loaded": loaded,
                "message": message,
                "payload": payload,
            }
            if loaded:
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/error:")

        if st.session_state.positions_result:
            positions_result = st.session_state.positions_result
            st.caption(positions_result["message"])
            if positions_result["loaded"] and positions_result["payload"]:
                positions_df = positions_result["payload"]["positions"]
                orders_df = positions_result["payload"]["orders"]
                st.write(f"Open positions: {len(positions_df)}")
                if positions_df.empty:
                    st.caption("No open positions for this symbol.")
                else:
                    display_positions = positions_df.copy()
                    display_positions["time"] = display_positions["time"].dt.tz_convert(runtime_config.timezone).dt.strftime("%Y-%m-%d %H:%M")
                    st.dataframe(
                        display_positions[["ticket", "type", "volume", "price_open", "price_current", "profit", "time"]],
                        hide_index=True,
                        width="stretch",
                    )
                    st.download_button(
                        "Download positions CSV",
                        data=frame_to_csv_bytes(display_positions),
                        file_name=f"positions_{runtime_config.symbol}.csv",
                        mime="text/csv",
                        icon=":material/download:",
                        width="stretch",
                    )

                st.write(f"Pending orders: {len(orders_df)}")
                if orders_df.empty:
                    st.caption("No pending orders for this symbol.")
                else:
                    display_orders = orders_df.copy()
                    display_orders["time_setup"] = display_orders["time_setup"].dt.tz_convert(runtime_config.timezone).dt.strftime("%Y-%m-%d %H:%M")
                    st.dataframe(
                        display_orders[["ticket", "type", "volume_initial", "price_open", "sl", "tp", "time_setup"]],
                        hide_index=True,
                        width="stretch",
                    )
                    st.download_button(
                        "Download pending orders CSV",
                        data=frame_to_csv_bytes(display_orders),
                        file_name=f"pending_orders_{runtime_config.symbol}.csv",
                        mime="text/csv",
                        icon=":material/download:",
                        width="stretch",
                    )

    with st.container(border=True):
        st.subheader("Trade history")
        st.caption("Shows closed deals from MT5 for the selected symbol over the chosen lookback window.")
        history_side_filter = st.segmented_control(
            "Side filter",
            options=["All", "Buy", "Sell"],
            default="All",
            selection_mode="single",
        )
        history_pnl_filter = st.segmented_control(
            "PnL filter",
            options=["All", "Profit only", "Loss only"],
            default="All",
            selection_mode="single",
        )
        history_ticket_filter = st.text_input("Ticket contains", value="", label_visibility="visible")
        if st.button("Load trade history", icon=":material/history:", width="stretch"):
            with st.spinner("Loading trade history..."):
                loaded, message, deals_df = fetch_trade_history(runtime_config, history_days)
            st.session_state.history_result = {
                "loaded": loaded,
                "message": message,
                "deals": deals_df,
            }
            if loaded:
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/error:")

        if st.session_state.history_result:
            history_result = st.session_state.history_result
            st.caption(history_result["message"])
            if history_result["loaded"] and history_result["deals"] is not None:
                deals_df = history_result["deals"]
                if deals_df.empty:
                    st.caption("No closed deals found for this symbol in the selected time window.")
                else:
                    display_deals = deals_df.copy()
                    if "type" in display_deals.columns:
                        display_deals["side"] = display_deals["type"].map({0: "Buy", 1: "Sell"}).fillna("Other")
                    else:
                        display_deals["side"] = "Other"

                    filtered_deals = display_deals
                    if history_side_filter != "All":
                        filtered_deals = filtered_deals[filtered_deals["side"] == history_side_filter]

                    if history_pnl_filter == "Profit only" and "profit" in filtered_deals.columns:
                        filtered_deals = filtered_deals[filtered_deals["profit"] > 0]
                    elif history_pnl_filter == "Loss only" and "profit" in filtered_deals.columns:
                        filtered_deals = filtered_deals[filtered_deals["profit"] < 0]

                    if history_ticket_filter.strip():
                        ticket_text = history_ticket_filter.strip()
                        filtered_deals = filtered_deals[
                            filtered_deals["ticket"].astype(str).str.contains(ticket_text, case=False, na=False)
                        ]

                    display_deals = filtered_deals.copy()
                    display_deals["time"] = display_deals["time"].dt.tz_convert(runtime_config.timezone).dt.strftime("%Y-%m-%d %H:%M")
                    st.write(f"Filtered deals: {len(display_deals)}")
                    if display_deals.empty:
                        st.session_state.filtered_deals_export = None
                        st.caption("No deals matched the active filters.")
                    else:
                        st.session_state.filtered_deals_export = display_deals
                        st.dataframe(
                            display_deals[["ticket", "order", "side", "entry", "volume", "price", "profit", "time"]],
                            hide_index=True,
                            width="stretch",
                        )
                        st.download_button(
                            "Download filtered deals CSV",
                            data=frame_to_csv_bytes(display_deals),
                            file_name=f"trade_history_{runtime_config.symbol}.csv",
                            mime="text/csv",
                            icon=":material/download:",
                            width="stretch",
                        )

    with st.container(border=True):
        st.subheader("Export snapshots")
        st.caption("Creates one zip with your latest positions, pending orders, filtered deals, and run metadata.")
        zip_bytes, zip_message = build_snapshot_zip(runtime_config.symbol)
        st.caption(zip_message)
        if zip_bytes is not None:
            snapshot_time = datetime.now(demo_timezone).strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "Download snapshots zip",
                data=zip_bytes,
                file_name=f"hfm_snapshots_{runtime_config.symbol}_{snapshot_time}.zip",
                mime="application/zip",
                icon=":material/folder_zip:",
                width="stretch",
            )

    with st.container(border=True):
        st.subheader("Order preview")
        st.json(order_preview, expanded=True)
        st.caption("This mirrors the stop-loss and take-profit math from the bot without sending an order.")

    with st.container(border=True):
        st.subheader("Manual order form")
        st.caption("Build a manual order request with live MT5 prices. Live submission is blocked unless you explicitly arm it and BOT_DRY_RUN=false in .env.")
        if st.button("Generate 30s live token", icon=":material/password:", width="stretch"):
            issued_token = issue_live_order_token()
            st.info(
                f"Live token issued: {issued_token}. It expires in 30 seconds. Submission phrase must be SEND {issued_token}.",
                icon=":material/timer:",
            )

        if token_is_valid():
            expires_in = int((st.session_state.live_order_token_expires - datetime.now(pytz.UTC)).total_seconds())
            st.caption(f"Active token: {st.session_state.live_order_token} (expires in {max(expires_in, 0)}s)")
        else:
            st.caption("No active live token. Generate one before any live submission.")

        with st.form("manual_order_form"):
            manual_side = st.segmented_control(
                "Order side",
                options=["buy", "sell"],
                default="buy",
                selection_mode="single",
            )
            manual_lot = st.number_input("Manual lot size", min_value=0.01, value=float(runtime_config.lot_size), step=0.01)
            manual_sl = st.number_input("Stop-loss points", min_value=1, value=int(runtime_config.sl_points), step=10)
            manual_tp = st.number_input("Take-profit points", min_value=1, value=int(runtime_config.tp_points), step=10)
            arm_live_order = st.checkbox("Arm live order submission")
            confirm_phrase = st.text_input("Type SEND <TOKEN> to allow live submission", value="", label_visibility="visible")
            preview_only = st.form_submit_button("Preview manual order", icon=":material/visibility:")
            send_order = st.form_submit_button("Submit manual order", type="primary", icon=":material/send:")

        manual_config = replace(
            runtime_config,
            lot_size=float(manual_lot),
            sl_points=int(manual_sl),
            tp_points=int(manual_tp),
        )

        if preview_only:
            with st.spinner("Building manual order preview..."):
                loaded, message, preview = fetch_live_order_preview(manual_config, manual_side)
            st.session_state.manual_order_result = {
                "submitted": False,
                "ok": loaded,
                "message": message,
                "payload": preview,
            }
            if loaded:
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/error:")

        if send_order:
            if runtime_config.dry_run:
                st.session_state.manual_order_result = {
                    "submitted": True,
                    "ok": False,
                    "message": "Live submission is blocked because BOT_DRY_RUN is still true in .env.",
                    "payload": None,
                }
                st.error(st.session_state.manual_order_result["message"], icon=":material/error:")
            elif not token_is_valid():
                st.session_state.manual_order_result = {
                    "submitted": True,
                    "ok": False,
                    "message": "Live token missing or expired. Generate a fresh 30-second token first.",
                    "payload": None,
                }
                st.error(st.session_state.manual_order_result["message"], icon=":material/error:")
            elif not arm_live_order:
                st.session_state.manual_order_result = {
                    "submitted": True,
                    "ok": False,
                    "message": "Enable the arm checkbox before any live submission.",
                    "payload": None,
                }
                st.error(st.session_state.manual_order_result["message"], icon=":material/error:")
            elif confirm_phrase != f"SEND {st.session_state.live_order_token}":
                st.session_state.manual_order_result = {
                    "submitted": True,
                    "ok": False,
                    "message": "Live submission requires the exact phrase SEND <TOKEN> using the active token shown above.",
                    "payload": None,
                }
                st.error(st.session_state.manual_order_result["message"], icon=":material/error:")
            else:
                with st.spinner("Submitting live order..."):
                    sent, message, payload = submit_manual_order(manual_config, manual_side)
                clear_live_order_token()
                st.session_state.manual_order_result = {
                    "submitted": True,
                    "ok": sent,
                    "message": message,
                    "payload": payload,
                }
                if sent:
                    st.success(message, icon=":material/check_circle:")
                else:
                    st.error(message, icon=":material/error:")

        if st.session_state.manual_order_result:
            manual_result = st.session_state.manual_order_result
            st.caption(manual_result["message"])
            if manual_result["payload"] is not None:
                st.json(manual_result["payload"], expanded=False)

    with st.container(border=True):
        st.subheader("What happens with your real credentials")
        st.write("1. The bot reads .env when bot.py starts.")
        st.write("2. MetaTrader 5 initializes and attempts mt5.login when login, password, and server are present.")
        st.write("3. Orders are still blocked while BOT_DRY_RUN=true.")
        st.write("4. Real execution only begins after you set BOT_DRY_RUN=false and run bot.py.")
