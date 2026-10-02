
from flask import Flask, jsonify, render_template, request
import requests, time, threading
from collections import deque

app = Flask(__name__)
BASE = "https://external-api.kalshi.com/trade-api/v2"
history = {}
lock = threading.Lock()

def get_markets(limit=100):
    r = requests.get(f"{BASE}/markets", params={"status":"open","limit":limit}, timeout=10)
    r.raise_for_status()
    return r.json().get("markets", [])

def analyze(market):
    ticker = market.get("ticker")
    price = market.get("yes_bid_dollars") or market.get("last_price_dollars")
    try:
        price = float(price)
    except (TypeError, ValueError):
        return None
    now = time.time()
    with lock:
        q = history.setdefault(ticker, deque(maxlen=180))
        q.append((now, price))
        points = list(q)

    # Compare current price with ~5m and ~15m observations when available.
    def old_price(seconds):
        cutoff = now - seconds
        candidates = [p for t,p in points if t <= cutoff]
        return candidates[-1] if candidates else None

    p5, p15 = old_price(300), old_price(900)
    d5 = (price - p5) if p5 is not None else None
    d15 = (price - p15) if p15 is not None else None

    score = 0
    reasons = []
    if d5 is not None:
        if d5 > 0.015: score += 1; reasons.append("5m momentum up")
        elif d5 < -0.015: score -= 1; reasons.append("5m momentum down")
    if d15 is not None:
        if d15 > 0.02: score += 1; reasons.append("15m momentum up")
        elif d15 < -0.02: score -= 1; reasons.append("15m momentum down")

    if score >= 2: signal = "UP"
    elif score <= -2: signal = "DOWN"
    else: signal = "WAIT"

    return {
        "ticker": ticker,
        "title": market.get("title") or market.get("subtitle") or ticker,
        "yes": price,
        "last": market.get("last_price_dollars"),
        "volume_24h": market.get("volume_24h_fp"),
        "d5": d5,
        "d15": d15,
        "signal": signal,
        "score": score,
        "reasons": reasons,
        "paper_only": True,
    }

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/markets")
def markets():
    try:
        limit = min(int(request.args.get("limit", 50)), 100)
        data = [analyze(m) for m in get_markets(limit)]
        return jsonify([x for x in data if x])
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "mode": "PAPER ONLY"})

if __name__ == "__main__":
    # Bind to all interfaces so it can be opened from another device on the same network.
    app.run(host="0.0.0.0", port=8080, debug=False)
