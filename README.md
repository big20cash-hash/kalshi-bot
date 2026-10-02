
# Kalshi Scout — iPhone-friendly first version

This is the first working prototype of the requested Kalshi bot.

## What it does
- Pulls open Kalshi markets through the public REST API.
- Tracks each market's YES price while the server is running.
- Calculates simple 5-minute and 15-minute momentum.
- Produces UP / DOWN / WAIT signals.
- Presents the scanner as a mobile web app that works from an iPhone browser.
- **Does not place real or demo orders.**

Kalshi's API provides public market data and order-book information. The official Demo environment can be used later for mock-money execution.

## Run it
1. Install Python 3.11+.
2. In this folder run:
   `python -m pip install -r requirements.txt`
3. Run:
   `python app.py`
4. On the same Wi-Fi, open `http://YOUR-COMPUTER-IP:8080` on the iPhone.

For a 24/7 iPhone-accessible version, deploy this project to a small cloud host. Do not put Kalshi private API keys in the browser.

## Important
The signal logic is intentionally simple. It is NOT evidence that the strategy is profitable. Backtest/paper-test it before connecting any order execution.
