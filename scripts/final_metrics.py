import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def dt(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%d")

proto = json.loads((DATA / "llama_protocol.json").read_text(encoding="utf-8"))
fees = json.loads((DATA / "llama_fees.json").read_text(encoding="utf-8"))
rev = json.loads((DATA / "llama_revenue.json").read_text(encoding="utf-8"))
dex = json.loads((DATA / "llama_dexs.json").read_text(encoding="utf-8"))
boros = json.loads((DATA / "llama_boros.json").read_text(encoding="utf-8"))
bf = json.loads((DATA / "llama_boros_fees.json").read_text(encoding="utf-8"))

print("CHAIN CURRENT EXCL STAKING/POOL2")
cur = proto["currentChainTvls"]
for k, v in sorted(cur.items(), key=lambda kv: -kv[1]):
    if not k.endswith("-staking") and not k.endswith("-pool2") and k not in ("staking", "pool2"):
        print(f"{k:20} {v/1e6:10.2f}")
core = sum(v for k, v in cur.items() if not k.endswith("-staking") and not k.endswith("-pool2") and k not in ("staking", "pool2"))
print("core tvl", core)

print("\nCHAIN PEAKS")
for chain, block in proto["chainTvls"].items():
    if chain.endswith("-staking") or chain.endswith("-pool2") or chain in ("staking", "pool2"):
        continue
    series = block.get("tvl") if isinstance(block, dict) else None
    if not series:
        continue
    peak = max(series, key=lambda x: x.get("totalLiquidityUSD", 0))
    print(f"{chain:20} peak {dt(peak['date'])} {peak['totalLiquidityUSD']/1e6:10.1f} last {series[-1]['totalLiquidityUSD']/1e6:8.1f}")

print("\nTVL MILESTONES")
series = proto["tvl"]
for target in [1e8, 1e9, 5e9, 1e10]:
    hit = next((x for x in series if x["totalLiquidityUSD"] >= target), None)
    if hit:
        print(target/1e9, "bn first", dt(hit["date"]), hit["totalLiquidityUSD"])

print("\nYEAR END TVL")
for y in range(2021, 2027):
    vals = [x for x in series if dt(x["date"]).startswith(str(y))]
    if vals:
        print(y, "end", round(vals[-1]["totalLiquidityUSD"]), "avg", round(sum(x["totalLiquidityUSD"] for x in vals)/len(vals)))

print("\nFEES EXTREMES")
chart = fees["totalDataChart"]
peak = max(chart, key=lambda x: x[1])
print("peak day", dt(peak[0]), peak[1])
# top 10 days share
top = sorted(chart, key=lambda x: -x[1])[:15]
print("top days")
for ts, v in top:
    print(dt(ts), round(v))
print("top10 share", sum(v for _, v in top[:10]) / sum(v for _, v in chart))

print("\n2026 YTD through Oct 9")
print("fees", sum(v for ts, v in chart if dt(ts).startswith("2026")))
print("rev", sum(v for ts, v in rev["totalDataChart"] if dt(ts).startswith("2026")))
print("vol", sum(v for ts, v in dex["totalDataChart"] if dt(ts).startswith("2026")))

print("\nBOROS")
print("current", boros["currentChainTvls"])
print("fees totals", {k: bf.get(k) for k in ["total24h","total30d","total1y","totalAllTime"]})
print("boros fee share all time", bf["totalAllTime"] / fees["totalAllTime"])
print("boros fee share 2026", sum(v for ts, v in bf["totalDataChart"] if dt(ts).startswith("2026")) / sum(v for ts, v in chart if dt(ts).startswith("2026")))

print("\nDEX methodology")
print(json.dumps(dex.get("childProtocols"), indent=2)[:2500])
print("chain breakdown", dex.get("chainBreakdown"))

print("\nVALUATION")
mcap = 362252934
fdv = 586934896
ann_fees = fees["total1y"]
ann_rev = rev["total1y"]
print("mcap/fees", mcap/ann_fees, "mcap/rev", mcap/ann_rev)
print("fdv/fees", fdv/ann_fees, "fdv/rev", fdv/ann_rev)
print("30d annualized fees", fees["total30d"]*365/30, "ps", mcap/(fees["total30d"]*365/30))
print("30d annualized rev", rev["total30d"]*365/30, "ps", mcap/(rev["total30d"]*365/30))
print("tvl/mcap", core/mcap)
print("fees/tvl annualized", ann_fees/core)
print("vol/tvl", dex["total1y"]/core)
