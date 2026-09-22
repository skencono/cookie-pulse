# 🍪 Cookie Pulse — Live On-Chain Terminal for Cookie Chain

**A cApp built on [Cookie Chain](https://www.cookiechain.wtf) — a Solana-compatible SVM with sub-second finality and ~$0.000005 transaction fees.**

🔗 **Live app:** https://buy-priorities-town-offshore.trycloudflare.com
📡 **RPC:** `https://rpc.cookiescan.io`

---

## What it does

Cookie Pulse is a **read + write terminal** for Cookie Chain. Every number on the
page is fetched live from `rpc.cookiescan.io` and the public Cookiescan APIs at
request time — there is no mock data, no database, no cache.

### Live chain telemetry (read)
| Panel | Source | What it shows |
|---|---|---|
| Slot / Epoch / Finality | `getSlot`, `getEpochInfo` | current slot, epoch, commitment latency |
| Throughput & Fee | Cookiescan `/api/break/stats` | real network TPS and average fee per tx |
| COOK Supply | `getSupply` | circulating supply |
| Bridge Locked | Cookiescan `/api/bridge/stats` | COOK locked in bridge escrow + transfer count |
| $GOR Price | Cookiescan `/api/gor/price` | live price, 24h change, market cap |
| Daily Activity | Cookiescan `/api/analytics/daily` | 14-day tx / active-wallet / fee history |
| NFT Collections | Metaplex DAS + `/api/collections` | collections minted on Cookie Chain |

### On-chain pool enumeration (read)
Pools are discovered **directly from chain** with `getProgramAccounts` across every
AMM/LB program live on Cookie Chain — no indexer required:

| Program | Label |
|---|---|
| `DBCg4ugDEztk6MbqHEJvx5a5YGJTj45Jb5Nv...` | CookieBox DBC (Meteora bonding curve) |
| `DAMMjDCEFTDkt7ywazZS8GoaLtjb3HaJo3pL...` | Cookieswap DAMM |
| `CLMMmWqTtyNSomqXP3kETJy2SGKPdr31USsm...` | CookieBox CLMM |
| `JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5...` | Jupiter v6 |
| `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24...` | Raydium AMM v4 |
| `namesLPneVptA9Z5rqUDD9tMTWEJwofgaYw...` | Cookie Name Service (`.cook`) |
| `SQDS4ep65T869zMMBKyuUq6aD6EgTu8psMjk...` | Squads v4 |

The dashboard aggregates **40,000+ on-chain accounts** across these programs and
breaks them down by program + data discriminator.

### Wallet connectivity + transactions (write)
- Connects **Nightly** (required by the brief), plus Phantom, Solflare and Backpack.
- Displays the connected wallet address and live COOK balance.
- **Wallet Inspector** — paste any address to read COOK balance, SPL token accounts
  and recent signatures.
- **Write path:**
  - **Tip COOK** — `SystemProgram.transfer` to any address.
  - **Self Transfer** — 0.001 COOK round-trip (safe smoke test for the write path).
  - **Memo Note** — writes a text memo on-chain via the SPL Memo program.
- Full lifecycle feedback: *building → signing → submitting → confirming → confirmed*,
  with a link to the transaction on Cookiescan and human-readable error handling
  (including an explicit "use the faucet" hint when the balance is too low).

---

## Quick start

```bash
git clone <this-repo> && cd cookie-pulse
npm install
npm start          # → http://localhost:8787
```

The server serves both the API and the static frontend. No API keys required —
all endpoints used are public.

### ⚠️ Node + PM2 note
If Node aborts with `core dumped` on start, your shell inherited PM2 environment
variables. Start with a clean environment:

```bash
env -i PATH=/usr/bin:/bin HOME=$HOME LANG=C.UTF-8 node server.js
```

`start.sh` in this repo already does exactly that.

---

## API reference

| Endpoint | Description |
|---|---|
| `GET /api/health` | slot, block height, epoch, tx count, supply, TPS, finality |
| `GET /api/stats` | network stats + bridge reserves + $GOR price + 14-day analytics |
| `GET /api/pools` | on-chain account census across all AMM programs (+ samples) |
| `GET /api/activity` | most recent confirmed transactions |
| `GET /api/wallet/:address` | COOK balance, SPL tokens, recent signatures |
| `GET /api/nfts` | NFT collections on Cookie Chain (DAS) |
| `GET /api/programs` | ecosystem program registry |

---

## Tech

- **Backend:** Node.js + Express + `@solana/web3.js` — talks to Cookie Chain RPC and
  the Cookiescan public APIs.
- **Frontend:** a single dependency-free HTML file using `@solana/web3.js` (IIFE) for
  wallet connection and transaction construction. No framework, no build step.
- **Chain:** Cookie Chain SVM (`solana-core 4.1.2`), chain id equivalent to Solana
  mainnet tooling; SPL Token, Token-2022, Metaplex DAS and Meteora-style AMMs all work.

## Architecture

```
browser  ──HTTP──▶  express server  ──JSON-RPC──▶  rpc.cookiescan.io
   │                     │
   │                     └──REST──▶  cookiescan.io/api/*   (stats, bridge, price, DAS)
   │
   └──wallet adapter──▶ Nightly / Phantom / Solflare  ──signed tx──▶ Cookie Chain
```

The backend exists to normalize RPC results, batch `getProgramAccounts` calls and
add CORS — the frontend never holds a key and every write is signed in the user's
wallet.

## Getting COOK

1. Bridge from Solana at https://hyperlane.cookiescan.io
2. Faucet — follow [@CookOvenApps](https://x.com/CookOvenApps) and claim 5 COOK at
   https://cookoven.xyz/faucet

## License

MIT — see [LICENSE](LICENSE).
