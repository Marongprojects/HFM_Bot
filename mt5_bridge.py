"""
mt5_bridge.py — MetaTrader 5 HTTP Bridge Server
================================================
Run this on a **Windows** machine that has MetaTrader 5 installed and the
MetaTrader5 Python package installed:

    pip install MetaTrader5 flask

Then start the server:

    python mt5_bridge.py

Expose the server publicly (ngrok recommended for quick setup):

    ngrok http 5000

In your Streamlit secrets (.streamlit/secrets.toml) set:

    MT5_BRIDGE_URL   = "https://xxxx.ngrok.io"
    MT5_BRIDGE_TOKEN = "<your-secret-token>"

In this file set the same token in BRIDGE_TOKEN below (or via env var
MT5_BRIDGE_TOKEN).

API Endpoints
-------------
POST /order
    Body: { "symbol": "XAUUSD", "direction": "BUY", "lots": 0.05,
            "sl": 3250.00, "tp": 3280.00, "magic": 202501 }
    Returns: { "success": true, "ticket": 12345678 }

POST /close
    Body: { "symbol": "XAUUSD" }   (omit symbol to close ALL positions)
    Returns: { "success": true, "closed": 2 }

GET /positions
    Returns: { "positions": [ { "ticket": ..., "symbol": ...,
               "type": "BUY|SELL", "lots": ..., "open_price": ...,
               "sl": ..., "tp": ..., "profit": ... } ] }

GET /account
    Returns: { "balance": ..., "equity": ..., "margin": ...,
               "free_margin": ..., "margin_level": ..., "currency": ... }

GET /health
    Returns: { "status": "ok", "connected": true }
"""

import os
import logging
from functools import wraps
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Configuration — override via environment variables
# ---------------------------------------------------------------------------
BRIDGE_TOKEN = os.environ.get("MT5_BRIDGE_TOKEN", "change-me-to-a-strong-secret")
MT5_LOGIN    = int(os.environ.get("MT5_LOGIN", "0"))      # set your account login
MT5_PASSWORD = os.environ.get("MT5_PASSWORD", "")
MT5_SERVER   = os.environ.get("MT5_SERVER", "")           # e.g. "HFM-Demo"
MT5_PATH     = os.environ.get("MT5_PATH", "")             # optional: path to terminal64.exe
MAGIC_NUMBER = int(os.environ.get("MT5_MAGIC", "20250819"))
HOST         = os.environ.get("BRIDGE_HOST", "0.0.0.0")
PORT         = int(os.environ.get("BRIDGE_PORT", "5000"))

# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

# Import MT5 — will raise ImportError on non-Windows; handle gracefully so
# the module can at least be imported for unit-testing stubs.
try:
    import MetaTrader5 as mt5
    _MT5_AVAILABLE = True
except ImportError:
    mt5 = None  # type: ignore[assignment]
    _MT5_AVAILABLE = False
    log.warning("MetaTrader5 package not found. Running in STUB mode — no real trades.")


# ---------------------------------------------------------------------------
# MT5 connection helpers
# ---------------------------------------------------------------------------

def _ensure_connected() -> bool:
    """Initialize MT5 connection if not already connected."""
    if not _MT5_AVAILABLE:
        return False
    if mt5.terminal_info() is not None:
        return True
    kwargs: dict = {}
    if MT5_PATH:
        kwargs["path"] = MT5_PATH
    if MT5_LOGIN:
        kwargs["login"] = MT5_LOGIN
        kwargs["password"] = MT5_PASSWORD
        kwargs["server"] = MT5_SERVER
    ok = mt5.initialize(**kwargs)
    if not ok:
        log.error("MT5 initialize failed: %s", mt5.last_error())
    return ok


def _order_type(direction: str):
    """Return MT5 order type constant for BUY or SELL."""
    return mt5.ORDER_TYPE_BUY if direction.upper() == "BUY" else mt5.ORDER_TYPE_SELL


# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if auth != "Bearer " + BRIDGE_TOKEN:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
@require_token
def health():
    connected = _ensure_connected() if _MT5_AVAILABLE else False
    return jsonify({"status": "ok", "connected": connected, "mt5_available": _MT5_AVAILABLE})


@app.get("/account")
@require_token
def account():
    if not _ensure_connected():
        return jsonify({"error": "MT5 not connected"}), 503
    info = mt5.account_info()
    if info is None:
        return jsonify({"error": "Failed to fetch account info", "detail": str(mt5.last_error())}), 500
    return jsonify({
        "balance":      info.balance,
        "equity":       info.equity,
        "margin":       info.margin,
        "free_margin":  info.margin_free,
        "margin_level": info.margin_level,
        "currency":     info.currency,
        "leverage":     info.leverage,
        "name":         info.name,
        "server":       info.server,
    })


@app.get("/positions")
@require_token
def positions():
    if not _ensure_connected():
        return jsonify({"error": "MT5 not connected"}), 503
    symbol = request.args.get("symbol")
    if symbol:
        raw = mt5.positions_get(symbol=symbol)
    else:
        raw = mt5.positions_get()
    if raw is None:
        raw = []
    result = []
    for p in raw:
        result.append({
            "ticket":     p.ticket,
            "symbol":     p.symbol,
            "type":       "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL",
            "lots":       p.volume,
            "open_price": p.price_open,
            "current_price": p.price_current,
            "sl":         p.sl,
            "tp":         p.tp,
            "profit":     p.profit,
            "magic":      p.magic,
            "comment":    p.comment,
            "time":       p.time,
        })
    return jsonify({"positions": result})


@app.post("/order")
@require_token
def place_order():
    """Place a market order on MT5."""
    body = request.get_json(force=True, silent=True) or {}
    symbol    = body.get("symbol", "XAUUSD")
    direction = str(body.get("direction", "BUY")).upper()
    lots      = float(body.get("lots", 0.01))
    sl        = float(body.get("sl", 0.0))
    tp        = float(body.get("tp", 0.0))
    magic     = int(body.get("magic", MAGIC_NUMBER))
    comment   = str(body.get("comment", "MarongStoicBot"))

    if direction not in ("BUY", "SELL"):
        return jsonify({"error": "direction must be BUY or SELL"}), 400
    if lots <= 0:
        return jsonify({"error": "lots must be > 0"}), 400

    if not _ensure_connected():
        return jsonify({"error": "MT5 not connected"}), 503

    # Get current ask/bid price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return jsonify({"error": f"Symbol {symbol} not found or market closed"}), 400

    price = tick.ask if direction == "BUY" else tick.bid
    order_type = _order_type(direction)

    request_payload = {
        "action":        mt5.TRADE_ACTION_DEAL,
        "symbol":        symbol,
        "volume":        lots,
        "type":          order_type,
        "price":         price,
        "sl":            sl,
        "tp":            tp,
        "deviation":     20,
        "magic":         magic,
        "comment":       comment,
        "type_time":     mt5.ORDER_TIME_GTC,
        "type_filling":  mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request_payload)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        retcode = result.retcode if result else -1
        comment_err = result.comment if result else "no result"
        log.error("order_send failed: retcode=%s comment=%s", retcode, comment_err)
        return jsonify({"success": False, "retcode": retcode, "comment": comment_err}), 500

    log.info("Order placed: %s %s %.2f lots @ %.5f ticket=%s", direction, symbol, lots, price, result.order)
    return jsonify({"success": True, "ticket": result.order, "price": price})


@app.post("/close")
@require_token
def close_positions():
    """Close all open positions for a symbol (or all positions if no symbol given)."""
    body = request.get_json(force=True, silent=True) or {}
    symbol = body.get("symbol")

    if not _ensure_connected():
        return jsonify({"error": "MT5 not connected"}), 503

    positions_raw = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
    if positions_raw is None:
        positions_raw = []

    closed = 0
    errors = []
    for pos in positions_raw:
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            errors.append({"ticket": pos.ticket, "error": "no tick"})
            continue

        close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        close_price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask

        req = {
            "action":       mt5.TRADE_ACTION_DEAL,
            "symbol":       pos.symbol,
            "volume":       pos.volume,
            "type":         close_type,
            "position":     pos.ticket,
            "price":        close_price,
            "deviation":    20,
            "magic":        pos.magic,
            "comment":      "MarongStoicBot KillSwitch",
            "type_time":    mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(req)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            closed += 1
            log.info("Closed ticket=%s", pos.ticket)
        else:
            retcode = result.retcode if result else -1
            errors.append({"ticket": pos.ticket, "retcode": retcode})
            log.error("Close failed ticket=%s retcode=%s", pos.ticket, retcode)

    return jsonify({"success": len(errors) == 0, "closed": closed, "errors": errors})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log.info("Starting MT5 Bridge on %s:%s", HOST, PORT)
    if _MT5_AVAILABLE:
        if _ensure_connected():
            log.info("MT5 connected successfully.")
        else:
            log.warning("MT5 connection failed at startup — will retry on first request.")
    else:
        log.warning("MetaTrader5 package not installed. Install it on Windows: pip install MetaTrader5")
    app.run(host=HOST, port=PORT, debug=False)
