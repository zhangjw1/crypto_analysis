import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
ctx = ssl.create_default_context()
urls = {
    "coinpaprika.json": "https://api.coinpaprika.com/v1/tickers/pendle-pendle",
    "coinpaprika_ohlcv.json": "https://api.coinpaprika.com/v1/coins/pendle-pendle/ohlcv/historical?start=2021-04-01&end=2026-10-10&interval=1d",
    "llama_raises.json": "https://api.llama.fi/raises",
    "llama_hacks.json": "https://api.llama.fi/hacks",
    "cg_chart_365.json": "https://api.coingecko.com/api/v3/coins/pendle/market_chart?vs_currency=usd&days=365",
}
for name, url in urls.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
            data = resp.read()
        (OUT / name).write_bytes(data)
        print("OK", name, len(data))
    except Exception as exc:
        print("FAIL", name, exc)
