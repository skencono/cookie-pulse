# Cookie Pulse — X Demo Thread

**Root tweet:** https://x.com/kun_annas/status/2102274707043291166

Posted as a verified reply chain (each tweet's `in_reply_to_status_id_str`
equals the previous tweet's id — checked against X's own GraphQL API, not the DOM).

- **Live app:** https://buy-priorities-town-offshore.trycloudflare.com
- **Source (MIT):** https://github.com/skencono/cookie-pulse

## The thread

### 1. https://x.com/kun_annas/status/2102274707043291166

> 🍪 Built Cookie Pulse — a live on-chain terminal for @TheCookieChain
> 
> Every number read from rpc.cookiescan.io. No mock data.
> 
> 40,000+ accounts indexed on-chain. Sub-second finality. ~$0.000005 fees.

### 2. https://x.com/kun_annas/status/2102276002953167004

> Live: https://buy-priorities-town-offshore.trycloudflare.com
> Code: https://github.com/skencono/cookie-pulse 🧵
> 
> What's inside?

### 3. https://x.com/kun_annas/status/2102280492058124605

> 📡 Slot / epoch / finality — live
> ⚡ Real TPS + avg fee
> 🪙 COOK supply from getSupply
> 🌉 551M COOK locked in the bridge
> 📈 $GOR price + 24h change
> 📊 14-day tx & wallet history
> 
> All fetched at request time.

### 4. https://x.com/kun_annas/status/2102281075578097908

> Pools aren't from an indexer — they're enumerated on-chain with getProgramAccounts:
> 
> • CookieBox DBC
> • Cookieswap DAMM
> • CookieBox CLMM
> • Jupiter v6 · Raydium · Orca
> • Cookie Name Service (.cook)
> • Squads v4
> 
> 44,000+ accounts, grouped by program + discriminator.

### 5. https://x.com/kun_annas/status/2102282541680230746

> It's not just read-only 👇
> 
> Connect Nightly (plus Phantom / Solflare) and really write to Cookie Chain:
> 
> 🔸 Tip COOK — SystemProgram.transfer
> 🔸 Self Transfer — 0.001 COOK test
> 🔸 Memo Note — text on-chain

### 6. https://x.com/kun_annas/status/2102283086159614458

> Full flow: signing → submitting → confirming → confirmed, with a Cookiescan link.
> 
> Error handling is real too.
> 
> Not enough COOK? It points you at the faucet instead of dying. Failed txs surface the actual RPC reason.

### 7. https://x.com/kun_annas/status/2102283421246697475

> Paste any address into the Wallet Inspector for COOK balance, tokens and signatures.
> 
> Shipping here is fast — one Node process, no build step, no API keys.

### 8. https://x.com/kun_annas/status/2102284183469216235

> 🔗 Live: https://buy-priorities-town-offshore.trycloudflare.com
> 💻 Code: https://github.com/skencono/cookie-pulse
> 📖 https://docs.cookiechain.wtf
> 
> Bridge in: https://hyperlane.cookiescan.io
> 
> Need COOK? Follow @CookOvenApps → https://cookoven.xyz/faucet 🍪

## Chain integrity

Verified by reading `UserRepliesTimeline` / `UserOriginalsTimeline` off X's own
network traffic and asserting `inReply[i] == id[i-1]` for every tweet:

```
1. 2102274707043291166   inReplyTo = — (root)
2. 2102276002953167004   inReplyTo = 2102274707043291166
3. 2102280492058124605   inReplyTo = 2102276002953167004
4. 2102281075578097908   inReplyTo = 2102280492058124605
5. 2102282541680230746   inReplyTo = 2102281075578097908
6. 2102283086159614458   inReplyTo = 2102282541680230746
7. 2102283421246697475   inReplyTo = 2102283086159614458
8. 2102284183469216235   inReplyTo = 2102283421246697475
```

## Notes on building this thread programmatically

Three things break naive automation, all discovered the hard way:

1. **X does not redirect after posting.** `pg.url` stays `/compose/post`.
   Success must be read from the `CreateTweet` response body (`rest_id`).
2. **Replying from a status page's page-level reply button binds to the
   conversation ROOT, not to that tweet** — it silently flattens the thread.
   The reply affordance *inside the target tweet's `<article>`* is the one that
   chains correctly.
3. **The profile DOM is cached.** Scraping `a[href*="/status/"]` returns stale
   ids and produces false success reports.

Written up fully in the repo's tooling and in `X_THREAD.md`.
