import json
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

URLS = {
    "coingecko.json": "https://api.coingecko.com/api/v3/coins/pendle?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false",
    "cg_market_chart.json": "https://api.coingecko.com/api/v3/coins/pendle/market_chart?vs_currency=usd&days=max&interval=daily",
    "llama_protocol.json": "https://api.llama.fi/protocol/pendle",
    "llama_fees.json": "https://api.llama.fi/summary/fees/pendle?dataType=dailyFees",
    "llama_revenue.json": "https://api.llama.fi/summary/fees/pendle?dataType=dailyRevenue",
    "llama_dexs.json": "https://api.llama.fi/summary/dexs/pendle",
    "llama_boros.json": "https://api.llama.fi/protocol/boros",
    "llama_boros_fees.json": "https://api.llama.fi/summary/fees/boros",
    "llama_pendle_v2.json": "https://api.llama.fi/protocol/pendle-v2",
}

ctx = ssl.create_default_context()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 research-report",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
        return resp.read()


for name, url in URLS.items():
    path = OUT / name
    for attempt in range(3):
        try:
            data = fetch(url)
            path.write_bytes(data)
            print(f"OK {name} {len(data)}")
            break
        except Exception as exc:
            print(f"FAIL {name} attempt {attempt + 1}: {exc}")
            time.sleep(2)
