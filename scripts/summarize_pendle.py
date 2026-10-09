import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def dt(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%d")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


cg = load("coingecko.json")
md = cg["market_data"]
print("=== COINGECKO ===")
for k in ["current_price", "ath", "ath_date", "atl", "atl_date", "market_cap", "fully_diluted_valuation", "total_volume", "circulating_supply", "total_supply", "max_supply"]:
    print(k, md.get(k))
print("mcap_rank", cg.get("market_cap_rank"))
print("genesis", cg.get("genesis_date"))
print("categories", cg.get("categories"))

fees = load("llama_fees.json")
rev = load("llama_revenue.json")
print("\n=== FEES SUMMARY ===")
for obj, label in [(fees, "fees"), (rev, "revenue")]:
    keys = ["total24h", "total48hto24h", "total7d", "total30d", "total1y", "annualized1y", "totalAllTime"]
    print(label, {k: obj.get(k) for k in keys})


def annual(chart, year):
    vals = [v for ts, v in chart if dt(ts).startswith(str(year))]
    return sum(vals), len(vals)


print("\n=== ANNUAL FEES/REVENUE ===")
for obj, label in [(fees, "fees"), (rev, "revenue")]:
    chart = obj["totalDataChart"]
    for y in range(2023, 2027):
        s, n = annual(chart, y)
        print(label, y, round(s, 2), "days", n)

print("\n=== MONTHLY 2025-2026 FEES ===")
monthly = defaultdict(float)
for ts, v in fees["totalDataChart"]:
    key = dt(ts)[:7]
    if key >= "2024-01":
        monthly[key] += v
for k in sorted(monthly):
    print(k, round(monthly[k], 0))


def tvl_series(obj, key="tvl"):
    block = obj.get(key)
    if isinstance(block, list):
        return block
    if isinstance(block, dict) and isinstance(block.get("tvl"), list):
        return block["tvl"]
    return []


proto = load("llama_protocol.json")
print("\n=== PROTOCOL KEYS ===")
print(sorted(proto.keys()))
print("currentChainTvls", proto.get("currentChainTvls"))
print("tvl list?", type(proto.get("tvl")), len(proto.get("tvl") or []))

series = proto.get("tvl") or []
if series:
    print("tvl first", dt(series[0]["date"]), series[0]["totalLiquidityUSD"])
    print("tvl last", dt(series[-1]["date"]), series[-1]["totalLiquidityUSD"])
    peak = max(series, key=lambda x: x["totalLiquidityUSD"])
    print("tvl peak", dt(peak["date"]), peak["totalLiquidityUSD"])
    for y in range(2021, 2027):
        vals = [x["totalLiquidityUSD"] for x in series if dt(x["date"]).startswith(str(y))]
        if vals:
            print("year", y, "avg", round(sum(vals) / len(vals)), "max", round(max(vals)), "end", round(vals[-1]), "n", len(vals))

print("\n=== CHAIN TVL KEYS ===")
print(sorted(proto.get("chainTvls", {}).keys()))

v2 = load("llama_pendle_v2.json")
print("\n=== V2 ===")
print("keys", sorted(v2.keys())[:40])
print("current", v2.get("currentChainTvls"))
v2s = v2.get("tvl") or []
if v2s:
    peak = max(v2s, key=lambda x: x.get("totalLiquidityUSD", 0))
    print("v2 first", dt(v2s[0]["date"]), v2s[0]["totalLiquidityUSD"])
    print("v2 last", dt(v2s[-1]["date"]), v2s[-1]["totalLiquidityUSD"])
    print("v2 peak", dt(peak["date"]), peak["totalLiquidityUSD"])

boros = load("llama_boros.json")
print("\n=== BOROS PROTOCOL ===")
print("keys", sorted(boros.keys()))
print("current", boros.get("currentChainTvls"))
bs = boros.get("tvl") or []
if bs:
    print("boros tvl first", dt(bs[0]["date"]), bs[0])
    print("boros tvl last", dt(bs[-1]["date"]), bs[-1])
    peak = max(bs, key=lambda x: x.get("totalLiquidityUSD", 0))
    print("boros peak", dt(peak["date"]), peak["totalLiquidityUSD"])

bf = load("llama_boros_fees.json")
print("\n=== BOROS FEES ===")
print({k: bf.get(k) for k in ["total24h", "total7d", "total30d", "total1y", "totalAllTime", "name"]})
if bf.get("totalDataChart"):
    print("boros fees first", dt(bf["totalDataChart"][0][0]), bf["totalDataChart"][0][1])
    print("boros fees last", dt(bf["totalDataChart"][-1][0]), bf["totalDataChart"][-1][1])
    print("boros fees sum", sum(v for _, v in bf["totalDataChart"]))

dex = load("llama_dexs.json")
print("\n=== DEXS ===")
print("keys", [k for k in dex.keys() if k not in ("totalDataChart", "totalDataChartBreakdown")])
print({k: dex.get(k) for k in ["total24h", "total7d", "total30d", "total1y", "totalAllTime", "name"]})
if dex.get("totalDataChart"):
    print("dex first", dt(dex["totalDataChart"][0][0]), dex["totalDataChart"][0][1])
    print("dex last", dt(dex["totalDataChart"][-1][0]), dex["totalDataChart"][-1][1])
    for y in range(2023, 2027):
        s, n = annual(dex["totalDataChart"], y)
        print("volume", y, round(s), "days", n)
