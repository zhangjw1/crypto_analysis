import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def dt(ts):
    return datetime.fromtimestamp(int(ts) / 1000 if int(ts) > 10_000_000_000 else int(ts), timezone.utc).strftime("%Y-%m-%d")

pap = json.loads((DATA / "coinpaprika.json").read_text(encoding="utf-8"))
print("PAPRIKA")
print(json.dumps({k: pap.get(k) for k in ["name","symbol","rank","beta_value"]}, indent=2)[:500])
print("quotes", json.dumps(pap.get("quotes", {}).get("USD", {}), indent=2)[:2000])

hacks = json.loads((DATA / "llama_hacks.json").read_text(encoding="utf-8"))
print("\nHACKS TYPE", type(hacks), len(hacks) if hasattr(hacks, "__len__") else "")
items = hacks if isinstance(hacks, list) else hacks.get("hacks") or hacks.get("data") or []
hits = []
for item in items:
    text = json.dumps(item).lower()
    if "pendle" in text:
        hits.append(item)
print("pendle hacks", len(hits))
for item in hits[:10]:
    print(json.dumps(item)[:800])

chart = json.loads((DATA / "cg_chart_365.json").read_text(encoding="utf-8"))
prices = chart.get("prices", [])
print("\n365 chart", len(prices), "first", dt(prices[0][0]), prices[0][1], "last", dt(prices[-1][0]), prices[-1][1])
peak = max(prices, key=lambda x: x[1])
low = min(prices, key=lambda x: x[1])
print("365 peak", dt(peak[0]), peak[1], "low", dt(low[0]), low[1])
monthly = {}
for ts, price in prices:
    monthly.setdefault(dt(ts)[:7], []).append(price)
print("monthly last close")
for k, vals in monthly.items():
    print(k, round(vals[-1], 4), "max", round(max(vals), 4))

proto = json.loads((DATA / "llama_protocol.json").read_text(encoding="utf-8"))
print("\nRAISES", json.dumps(proto.get("raises"), indent=2)[:4000])
print("\nHACKS FIELD", json.dumps(proto.get("hacks"), indent=2)[:2000])
print("\nHALLMARKS", json.dumps(proto.get("hallmarks"), indent=2)[:2000])
print("\nTREASURY", proto.get("treasury"))
print("MCAP FIELD", proto.get("mcap"))
