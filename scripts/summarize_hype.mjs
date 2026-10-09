import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const D = join(ROOT, "data", "hype") + "/";
const J = (n) => JSON.parse(readFileSync(D + n, "utf8"));
const day = (ts) => new Date(ts * 1000).toISOString().slice(0, 10);

// 费用 / 收入：年度、月度、近 30 天
function series(name) {
  const j = J(name);
  console.log(`\n== ${name} total24h=${j.total24h} total30d=${j.total30d} total1y=${j.total1y} allTime=${j.totalAllTime}`);
  const byY = {}, byM = {};
  for (const [ts, v] of j.totalDataChart) {
    const d = day(ts);
    byY[d.slice(0, 4)] = (byY[d.slice(0, 4)] || 0) + v;
    byM[d.slice(0, 7)] = (byM[d.slice(0, 7)] || 0) + v;
  }
  console.log("yearly(M):", Object.fromEntries(Object.entries(byY).map(([k, v]) => [k, +(v / 1e6).toFixed(1)])));
  console.log("monthly(M):", Object.entries(byM).map(([k, v]) => `${k}:${(v / 1e6).toFixed(1)}`).join(" "));
  const last = j.totalDataChart.slice(-30).reduce((a, [, v]) => a + v, 0);
  console.log("last30 sum(M):", (last / 1e6).toFixed(2), "annualized(M):", ((last * 365) / 30 / 1e6).toFixed(0), "lastDay:", day(j.totalDataChart.at(-1)[0]));
  if (j.totalDataChartBreakdown) console.log("breakdown sample:", JSON.stringify(j.totalDataChartBreakdown.at(-1)).slice(0, 400));
}
series("llama_fees.json");
series("llama_revenue.json");

// TVL
const p = J("llama_protocol.json");
console.log("\n== protocol", p.name, "mcap", p.mcap, "chains", JSON.stringify(p.currentChainTvls));
const tvl = p.tvl || [];
const tvlM = {};
for (const r of tvl) tvlM[day(r.date).slice(0, 7)] = r.totalLiquidityUSD;
console.log("tvl month-end(B):", Object.entries(tvlM).map(([k, v]) => `${k}:${(v / 1e9).toFixed(2)}`).join(" "));
if (tvl.length) {
  const mx = tvl.reduce((a, b) => (b.totalLiquidityUSD > a.totalLiquidityUSD ? b : a));
  console.log("tvl peak:", day(mx.date), (mx.totalLiquidityUSD / 1e9).toFixed(2));
}
console.log("otherProtocols:", p.otherProtocols, "parent:", p.parentProtocol);
console.log("raises:", JSON.stringify(p.raises), "tokenSym:", p.symbol, "gecko:", p.gecko_id);
console.log("hallmarks:", JSON.stringify(p.hallmarks));

// 价格历史（月末）
const ph = J("llama_price_hist.json").coins["coingecko:hyperliquid"].prices;
const pm = {};
for (const r of ph) pm[day(r.timestamp).slice(0, 7)] = r.price;
console.log("\n== price month-end:", Object.entries(pm).map(([k, v]) => `${k}:${v.toFixed(2)}`).join(" "));
const pmax = ph.reduce((a, b) => (b.price > a.price ? b : a)), pmin = ph.reduce((a, b) => (b.price < a.price ? b : a));
console.log("max", day(pmax.timestamp), pmax.price, "min", day(pmin.timestamp), pmin.price, "first", day(ph[0].timestamp), ph[0].price, "last", day(ph.at(-1).timestamp), ph.at(-1).price);

// 永续：OI 与 24h 成交
const [meta, ctx] = J("hl_meta_ctx.json");
let oi = 0, vol = 0;
const rows = meta.universe.map((u, i) => {
  const c = ctx[i];
  const px = +c.markPx, o = +c.openInterest * px, v = +c.dayNtlVlm;
  oi += o; vol += v;
  return { n: u.name, o, v, f: +c.funding };
});
rows.sort((a, b) => b.o - a.o);
console.log("\n== perps markets", meta.universe.length, "OI(B)", (oi / 1e9).toFixed(2), "24hVol(B)", (vol / 1e9).toFixed(2));
console.log("top OI:", rows.slice(0, 12).map((r) => `${r.n}:${(r.o / 1e9).toFixed(2)}B/${(r.v / 1e9).toFixed(2)}B`).join(" "));

// 现货：HYPE
const [smeta, sctx] = J("hl_spot_ctx.json");
const hypeTok = smeta.tokens.find((t) => t.name === "HYPE");
const pair = smeta.universe.find((u) => u.tokens[0] === hypeTok.index && u.tokens[1] === 0);
const hc = sctx[pair.index];
console.log("\n== HYPE spot", JSON.stringify(hc));
let svol = 0;
for (const c of sctx) svol += +c.dayNtlVlm;
console.log("spot 24h vol(M)", (svol / 1e6).toFixed(0), "spot pairs", smeta.universe.length);

// HLP
const h = J("hl_hlp.json");
console.log("\n== HLP", h.name, "apr", h.apr, "followers", h.followers?.length, "leaderCommission", h.leaderCommission);
const pf = h.portfolio || [];
for (const [k, v] of pf) {
  const av = v.accountValueHistory, pnl = v.pnlHistory;
  console.log(k, "acct", av.at(-1)?.[1], "pnl", pnl.at(-1)?.[1], "vlm", v.vlm);
}
