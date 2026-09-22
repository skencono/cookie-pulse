# Cookie Pulse — X thread

Posted by [@kun_annas](https://x.com/kun_annas).

**Root tweet:** https://x.com/kun_annas/status/2102267903525683545 _(first attempt —
see note below)_

## Thread content (8 posts, all ≤ 280 chars)

### 1/8
🍪 Built Cookie Pulse — a live on-chain terminal for @TheCookieChain

Every number read from rpc.cookiescan.io. No mock data.

40,000+ accounts indexed on-chain. Sub-second finality. ~$0.000005 fees.

### 2/8
Live: https://buy-priorities-town-offshore.trycloudflare.com
Code: https://github.com/skencono/cookie-pulse 🧵

What's inside?

### 3/8
📡 Slot / epoch / finality — live
⚡ Real TPS + avg fee
🪙 COOK supply from getSupply
🌉 551M COOK locked in the bridge
📈 $GOR price + 24h change
📊 14-day tx & wallet history

All fetched at request time.

### 4/8
Pools aren't from an indexer — they're enumerated on-chain with getProgramAccounts:

• CookieBox DBC
• Cookieswap DAMM
• CookieBox CLMM
• Jupiter v6 · Raydium · Orca
• Cookie Name Service (.cook)
• Squads v4

44,000+ accounts, grouped by program + discriminator.

### 5/8
It's not just read-only 👇

Connect Nightly (plus Phantom / Solflare) and really write to Cookie Chain:

🔸 Tip COOK — SystemProgram.transfer
🔸 Self Transfer — 0.001 COOK test
🔸 Memo Note — text on-chain

### 6/8
Full flow: signing → submitting → confirming → confirmed, with a Cookiescan link.

Error handling is real too.

### 7/8
Not enough COOK? It points you at the faucet instead of dying. Failed txs surface the actual RPC reason.

Paste any address into the Wallet Inspector for COOK balance, tokens and signatures.

### 8/8
Shipping here is fast — one Node process, no build step, no API keys.

🔗 Live: https://buy-priorities-town-offshore.trycloudflare.com
💻 Code: https://github.com/skencono/cookie-pulse
📖 https://docs.cookiechain.wtf

Bridge in: https://hyperlane.cookiescan.io

Need COOK? Follow @CookOvenApps → https://cookoven.xyz/faucet 🍪

---

## Posting notes (hard-won)

X **redirects to `/home` after a successful post**, so the new tweet id is never
in the URL. Two failure modes were hit and fixed:

1. **Reading the profile timeline** returns a cached page — the newly posted tweet
   may not appear for a while, and stale ids get picked up instead.
2. **Reading `article[0]` on the status page** returns the *root* tweet, not the
   reply, so DOM scraping reports every tweet as replying to the first one.

The technique that works:

* `since = time.time()` immediately **before** clicking Post.
* Right after posting, open `https://x.com/<handle>/with_replies` (this stream
  updates immediately) and filter `article` elements by
  `<time datetime>` ≥ `since`.
* The newest surviving id is the tweet just posted.

To prove a chain is real (rather than assuming), query X's internal GraphQL
`TweetResultByRestId` and check each tweet's `in_reply_to_status_id_str` points at
the *previous* tweet, not the root. That call needs three headers beyond
`authorization`:

```
x-csrf-token: <ct0 cookie>
x-twitter-active-user: yes
x-twitter-auth-type: OAuth2Session
```

Without `x-csrf-token` X returns
`This request requires a matching csrf cookie and header.`
