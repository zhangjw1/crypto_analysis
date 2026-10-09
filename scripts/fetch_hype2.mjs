import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(ROOT, "data", "hype");
const headers = { "User-Agent": "Mozilla/5.0 research-report", Accept: "application/json" };
const now = Date.now();

const GET = {
  "llama_price_hist2.json": "https://coins.llama.fi/chart/coingecko:hyperliquid?start=1760313600&span=370&period=1d",
  "llama_holders_rev.json": "https://api.llama.fi/summary/fees/hyperliquid?dataType=dailyHoldersRevenue",
  "llama_dydx_fees.json": "https://api.llama.fi/summary/fees/dydx?dataType=dailyFees",
  "llama_dydx_protocol.json": "https://api.llama.fi/protocol/dydx",
  "llama_aster_fees.json": "https://api.llama.fi/summary/fees/aster?dataType=dailyFees",
  "llama_lighter_fees.json": "https://api.llama.fi/summary/fees/lighter?dataType=dailyFees",
  "llama_chain_hl.json": "https://api.llama.fi/v2/historicalChainTvl/Hyperliquid%20L1",
  "llama_stables_hl.json": "https://stablecoins.llama.fi/stablecoincharts/Hyperliquid%20L1",
  "stats_daily_volume.json": "https://stats-data.hyperliquid.xyz/Mainnet/daily_usd_volume",
  "stats_open_interest.json": "https://stats-data.hyperliquid.xyz/Mainnet/open_interest",
  "stats_cum_users.json": "https://stats-data.hyperliquid.xyz/Mainnet/cumulative_new_users",
  "stats_liquidations.json": "https://stats-data.hyperliquid.xyz/Mainnet/daily_notional_liquidated_total",
  "llama_coins_cur.json": "https://coins.llama.fi/prices/current/coingecko:hyperliquid,coingecko:dydx-chain,coingecko:aster-2,coingecko:ethereum,coingecko:bitcoin?searchWidth=4h",
  "binance_hype.json": "https://api.binance.com/api/v3/klines?symbol=HYPEUSDT&interval=1d&limit=1000",
};

const HL = {
  "hl_candles_hype.json": { type: "candleSnapshot", req: { coin: "@107", interval: "1d", startTime: 1732838400000, endTime: now } },
  "hl_candles_hype_w.json": { type: "candleSnapshot", req: { coin: "@107", interval: "1w", startTime: 1732838400000, endTime: now } },
  "hl_af_spot.json": { type: "spotClearinghouseState", user: "0xfefefefefefefefefefefefefefefefefefefefe" },
  "hl_validators.json": { type: "validatorSummaries" },
  "hl_spot_meta.json": { type: "spotMeta" },
  "hl_token_details.json": { type: "tokenDetails", tokenId: "0x0d01dc56dcaaca66ad901c959b4011ec" },
  "hl_perp_dexs.json": { type: "perpDexs" },
};

async function get(name, url, init) {
  for (let i = 0; i < 2; i++) {
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
  ...Object.entries(GET).map(([n, u]) => get(n, u, { headers })),
  ...Object.entries(HL).map(([n, p]) => get(n, "https://api.hyperliquid.xyz/info", { method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify(p) })),
]);
