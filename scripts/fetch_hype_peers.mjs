import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const D = join(ROOT, "data", "hype") + "/";
const IDS = ["hype-hyperliquid", "aave-new", "uni-uniswap", "ena-ethena", "pump-pumpfun", "aster-aster", "dydx-dydx", "ldo-lido-dao", "pendle-pendle", "jup-jupiter", "bnb-binance-coin", "gmx-gmx", "sky-sky"];

const out = {};
await Promise.all(IDS.map(async (id) => {
  try {
    const r = await fetch(`https://api.coinpaprika.com/v1/tickers/${id}`, { signal: AbortSignal.timeout(60000) });
    const j = await r.json();
    out[id] = { price: j.quotes?.USD?.price, mcap: j.quotes?.USD?.market_cap, total: j.total_supply, max: j.max_supply, circ: j.circulating_supply, ath: j.quotes?.USD?.ath_price, err: j.error };
  } catch (e) {
    out[id] = { err: e.message };
  }
}));
writeFileSync(D + "peers_paprika.json", JSON.stringify(out, null, 1));
for (const [k, v] of Object.entries(out)) console.log(k, v.err || "", v.price?.toFixed?.(3), "mcap(B)", (v.mcap / 1e9).toFixed(2), "circ(M)", (v.circ / 1e6).toFixed(0), "total(M)", (v.total / 1e6).toFixed(0), "max(M)", (v.max / 1e6).toFixed(0));

const ov = JSON.parse(readFileSync(D + "llama_rev_overview.json", "utf8"));
const want = ["Hyperliquid", "Aave", "Uniswap", "Ethena", "pump.fun", "Aster", "dYdX", "Lido", "Pendle", "Jupiter", "GMX", "Sky", "Lighter", "edgeX", "Raydium", "PancakeSwap"];
for (const w of want) {
  const ps = ov.protocols.filter((p) => (p.parentProtocol || "").toLowerCase().includes(w.toLowerCase().replace(".", "")) || p.name.toLowerCase().startsWith(w.toLowerCase()));
  const s30 = ps.reduce((a, p) => a + (p.total30d || 0), 0), s1y = ps.reduce((a, p) => a + (p.total1y || 0), 0);
  console.log(`REV ${w}: 30d ${(s30 / 1e6).toFixed(1)}M 1y ${(s1y / 1e6).toFixed(1)}M  [${ps.map((p) => p.name).join(", ")}]`);
}
