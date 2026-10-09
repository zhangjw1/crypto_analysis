import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const D = join(ROOT, "data", "hype") + "/";
const J = (n) => JSON.parse(readFileSync(D + n, "utf8"));
const day = (ts) => new Date(ts * 1000).toISOString().slice(0, 10);
const M = (v) => (v / 1e6).toFixed(1);

// 官方日 K：月末收盘、高低点
const c = J("hl_candles_hype.json");
console.log("candles", c.length, "first", new Date(c[0].t).toISOString().slice(0, 10), c[0].o, "last", new Date(c.at(-1).t).toISOString().slice(0, 10), c.at(-1).c);
const mc = {};
let hi = c[0], lo = c[0];
for (const k of c) {
  mc[new Date(k.t).toISOString().slice(0, 7)] = +k.c;
  if (+k.h > +hi.h) hi = k;
  if (+k.l < +lo.l) lo = k;
}
console.log("month close:", Object.entries(mc).map(([k, v]) => `${k}:${v.toFixed(2)}`).join(" "));
console.log("ATH", new Date(hi.t).toISOString().slice(0, 10), hi.h, "ATL", new Date(lo.t).toISOString().slice(0, 10), lo.l);
const ph2 = J("llama_price_hist2.json").coins["coingecko:hyperliquid"].prices;
console.log("llama price2 last", day(ph2.at(-1).timestamp), ph2.at(-1).price, "n", ph2.length);
let lh = ph2[0];
for (const r of ph2) if (r.price > lh.price) lh = r;
console.log("llama price2 max", day(lh.timestamp), lh.price);

console.log("\ncur prices:", JSON.stringify(J("llama_coins_cur.json").coins));

// 持币者收入（援助基金回购）
const hr = J("llama_holders_rev.json");
const hy = {};
for (const [ts, v] of hr.totalDataChart) hy[day(ts).slice(0, 4)] = (hy[day(ts).slice(0, 4)] || 0) + v;
console.log("\nholdersRev total30d", M(hr.total30d), "1y", M(hr.total1y), "all", M(hr.totalAllTime), "yearly", JSON.stringify(Object.fromEntries(Object.entries(hy).map(([k, v]) => [k, M(v)]))));

// 援助基金持仓
const af = J("hl_af_spot.json");
console.log("\nAF balances:", JSON.stringify(af.balances.filter((b) => +b.total > 1000).map((b) => [b.coin, b.total])));

// 代币详情
const td = J("hl_token_details.json");
const { genesis, ...rest } = td;
console.log("\ntokenDetails:", JSON.stringify(rest).slice(0, 1500));
if (genesis) console.log("genesis keys:", Object.keys(genesis), "userBalances n", genesis.userBalances?.length, "existing", JSON.stringify(genesis.existingTokenBalances).slice(0, 300));

// 验证者质押
const vs = J("hl_validators.json");
const staked = vs.reduce((a, v) => a + +v.stake, 0) / 1e8;
console.log("\nvalidators", vs.length, "active", vs.filter((v) => v.isActive).length, "total stake(HYPE)", staked.toFixed(0));
console.log("top5:", vs.sort((a, b) => b.stake - a.stake).slice(0, 6).map((v) => `${v.name}:${(v.stake / 1e8 / 1e6).toFixed(1)}M`).join(" "));
console.log("sample:", JSON.stringify(vs[0]).slice(0, 400));

// HIP-3 builder DEX
const pd = J("hl_perp_dexs.json");
console.log("\nperpDexs", pd.length, pd.filter(Boolean).map((d) => `${d.name}(${d.fullName})`).join(", "));

// 链 TVL 与稳定币
const ct = J("llama_chain_hl.json");
console.log("\nHL L1 chain tvl last", day(ct.at(-1).date), (ct.at(-1).tvl / 1e9).toFixed(2), "peak", (Math.max(...ct.map((x) => x.tvl)) / 1e9).toFixed(2));
const st = J("llama_stables_hl.json");
const sl = st.at(-1);
console.log("HL stables last", day(+sl.date), (sl.totalCirculatingUSD.peggedUSD / 1e9).toFixed(2));

// 对手方费用
for (const n of ["llama_dydx_fees.json", "llama_aster_fees.json", "llama_lighter_fees.json"]) {
  const j = J(n);
  const y = {};
  for (const [ts, v] of j.totalDataChart) y[day(ts).slice(0, 4)] = (y[day(ts).slice(0, 4)] || 0) + v;
  console.log(`\n${n} 30d ${M(j.total30d)} 1y ${M(j.total1y)} all ${M(j.totalAllTime)} yearly`, JSON.stringify(Object.fromEntries(Object.entries(y).map(([k, v]) => [k, M(v)]))));
}
const dp = J("llama_dydx_protocol.json");
console.log("dydx mcap", dp.mcap, "tvl now", JSON.stringify(dp.currentChainTvls).slice(0, 200));

// 全市场收入排名（近 30 天）
const ov = J("llama_rev_overview.json");
const top = ov.protocols.filter((p) => p.total30d).sort((a, b) => b.total30d - a.total30d).slice(0, 15);
console.log("\nrev rank 30d:", top.map((p) => `${p.name}:${M(p.total30d)}`).join(" | "));
const top1y = ov.protocols.filter((p) => p.total1y).sort((a, b) => b.total1y - a.total1y).slice(0, 15);
console.log("rev rank 1y:", top1y.map((p) => `${p.name}:${M(p.total1y)}`).join(" | "));
