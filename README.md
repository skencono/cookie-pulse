# Cookie Pulse 🍪

**A live on-chain terminal for [Cookie Chain](https://www.cookiechain.wtf)** — an SVM
(Solana-compatible) chain with sub-second finality and ~$0.000005 transaction fees.

**Live app:** https://buy-priorities-town-offshore.trycloudflare.com
**Chain RPC:** https://rpc.cookiescan.io
**Explorer:** https://www.cookiescan.io

---

## What it does

Cookie Pulse turns Cookie Chain's RPC into a readable, real-time dashboard and a
working transaction console. **Every number on screen is fetched live from
`rpc.cookiescan.io` — there is no database, no mock data, and no cache.**

| Feature | What it does | How |
|---|---|---|
| **Live chain telemetry** | Slot, block height, epoch, tx count, TPS, finality, supply | `getSlot`, `getEpochInfo`, `getBlockHeight`, `getTransactionCount`, `getSupply` |
| **Wallet Inspector** | COOK balance, SPL holdings, recent signatures for any address | `getBalance`, `getTokenAccountsByOwner`, `getSignaturesForAddress` |
| **Pools & Liquidity** | Enumerates every AMM pool account on-chain | `getProgramAccounts` over 9 AMM programs |
| **Program Registry** | 14 known Cookie Chain programs with live account counts | `getProgramAccounts` |
| **Live Transaction Feed** | Decodes real transactions from recent blocks | `getBlock` + parsed instructions |
| **NFT Collections** | Metaplex collections with supply | Cookie DAS `getAssetsByOwner` |
| **Bridge Stats** | COOK bridged to/from other chains | `api.cookiescan.io/api/bridge/stats` |
| **Daily Network Chart** | 14 days of transactions, active wallets, fees | `api.cookiescan.io/api/analytics/daily` |
| **Send COOK** | Connect a wallet, sign, submit, track confirmation | `@solana/web3.js` |
| **Nightly wallet** | **Required integration — supported** | `window.nightly.solana` → `window.solana` |

## Wallet support

Nightly is a first-class citizen: the app detects `window.nightly.solana`, falls
back to `window.solana`, and exposes the *same* flow for Phantom, Solflare, and
Backpack. Multiple injected providers are resolved by `name` so Nightly wins when
several extensions are installed.

```js
function pick(win) {
  if (win.nightly?.solana) return win.nightly.solana;   // Nightly
  const injected = win.solana;
  if (injected?.providers?.length)
    return injected.providers.find(p => /nightly/i.test(p.name)) || injected.providers[0];
  return injected;
}
```

## Transaction flow

`connect → build → sign → send → confirm`, with the status surfaced at every step:

```
building… → awaiting signature (check your wallet) → submitting… → confirming… → ✅ confirmed
```

Failures are mapped to human hints: user rejection, insufficient COOK (with the
faucet link), blockhash expiry, and RPC errors each get their own message.

## Architecture

```
browser (public/index.html)
   │  @solana/web3.js  ── wallet signing
   ▼
RPC https://rpc.cookiescan.io            ← all chain reads + tx submission
   │
Express (server.js) ── CORS-safe aggregator, static hosting
   │
DAS/REST https://api.cookiescan.io       ← NFTs, bridge, analytics, token price
```

The browser talks to the chain directly for anything that involves a signature.
The Express layer only exists to avoid CORS on the analytics/DAS endpoints and to
serve the static app.

## Run locally

```bash
git clone https://github.com/skencono/cookie-pulse
cd cookie-pulse
npm install

# Node on some VPS hosts aborts (exit 134) when it inherits a polluted environ.
# Use a clean env if that happens — this is what ./start.sh wraps:
env -i PATH=/usr/bin:/bin HOME=$HOME LANG=C.UTF-8 node server.js
```

Open http://localhost:8787.

### Expose publicly

```bash
./cloudflared tunnel --url http://127.0.0.1:8787
```

## API (backend aggregator)

| Endpoint | Returns |
|---|---|
| `GET /api/health` | slot, blockHeight, epoch, txCount, supply, TPS, finality, version |
| `GET /api/stats` | bridge totals, token price, fee stats |
| `GET /api/programs` | the 14-program registry |
| `GET /api/pools` | on-chain AMM pool enumeration |
| `GET /api/activity` | recent decoded transactions |
| `GET /api/nfts` | collections via DAS |
| `GET /api/analytics` | the 14-day daily series |
| `GET /api/wallet/:address` | balance, SPL tokens, signatures |

## Cookie Chain programs used

```
CookieBox DBC      DBCg4ugDEztk6MbqHEJvx5a5YGJTj45Jb5NvtQ48Rvsf
CookieBox DAMM v2  DAMMjDCEFTDkt7ywazZS8GoaLtjb3HaJo3pLbf64xrPY
CookieBox CLMM    CLMMmWqTtyNSomqXP3kETJy2SGKPdr31USsm4GfbLyKs
Jupiter v6         JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4

Cookieswap SAMM    WTzkPUoprVx7PDc1tfKA5sS7k1ynCgU89WtwZhksHX5
Cookieswap CPAMMv2 6Y3VJBWWqFvDkSBdT3Pcb3DNaJ7cA1JPHAiLfo7JhyFq
Cookieswap CPAMMv3 5cYqbWRziT7dNi8Nb5poJr7nSuuocREj9SfBiuUYVVqc
CPAMM              cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG
Cookieswap DAMM    DAMMjDCEFTDkt7ywazZS8GoaLtjb3HaJo3pLbf64xrPY
Cookieora DAMMv2   EvRMsRW8NcaSRcy5Mgmsdj9Udk9ryGYq6hwkhicCZzSF

Solana Name Service namesLPneVptA9Z5rqUDD9tMTWEJwofgaYwp8cawRkX  (.cook)
Squads v4          SQDS4ep65T869zMMBKyuUq6aD6EgTu8psMjkvj52pCf
Raydium AMM v4     675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
Meteora DBC fork   dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN
```

## License

MIT — see [LICENSE](LICENSE).
