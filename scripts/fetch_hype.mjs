import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(ROOT, "data", "hype");
mkdirSync(OUT, { recursive: true });

const URLS = {
  "coingecko.json": "https://api.coingecko.com/api/v3/coins/hyperliquid?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false",
  "cg_market_chart.json": "https://api.coingecko.com/api/v3/coins/hyperliquid/market_chart?vs_currency=usd&days=365&interval=daily",
  "llama_protocol.json": "https://api.llama.fi/protocol/hyperliquid",
  "llama_fees.json": "https://api.llama.fi/summary/fees/hyperliquid?dataType=dailyFees",
  "llama_revenue.json": "https://api.llama.fi/summary/fees/hyperliquid?dataType=dailyRevenue",
  "llama_perps.json": "https://api.llama.fi/summary/derivatives/hyperliquid",
  "llama_perps_overview.json": "https://api.llama.fi/overview/derivatives?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true",
  "llama_rev_overview.json": "https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyRevenue",
  "llama_dydx.json": "https://api.llama.fi/summary/derivatives/dydx",
  "llama_emissions.json": "https://api.llama.fi/emission/hyperliquid",
  "llama_price_hist.json": "https://coins.llama.fi/chart/coingecko:hyperliquid?start=1732838400&span=320&period=1d",
};

const HL = {
  "hl_meta_ctx.json": { type: "metaAndAssetCtxs" },
  "hl_spot_ctx.json": { type: "spotMetaAndAssetCtxs" },
  "hl_hlp.json": { type: "vaultDetails", vaultAddress: "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303" },
};

const headers = { "User-Agent": "Mozilla/5.0 research-report", Accept: "application/json" };

async function get(name, url, init) {
  for (let i = 0; i < 3; i++) {
    try {
      const r = await fetch(url, { ...init, signal: AbortSignal.timeout(120000) });
      const t = await r.text();
      writeFileSync(join(OUT, name), t);
      console.log(`OK ${name} ${r.status} ${t.length}`);
      return;
    } catch (e) {
      console.log(`FAIL ${name} attempt ${i + 1}: ${e.message}`);
    }
  }
}

await Promise.all([
  ...Object.entries(URLS).map(([n, u]) => get(n, u, { headers })),
  ...Object.entries(HL).map(([n, p]) => get(n, "https://api.hyperliquid.xyz/info", { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify(p) })),
]);
