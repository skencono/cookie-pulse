#!/usr/bin/env node
/**
 * COOKIE PULSE — backend
 * Live on-chain data aggregator for Cookie Chain (SVM).
 * Serves: chain health, pool data, bridge stats, token price, NFT collections,
 *         activity feed, and proxies wallet txs to the Cookie Chain RPC.
 */
const express = require("express");
const {
  Connection, PublicKey, LAMPORTS_PER_SOL, clusterApiUrl, SystemProgram,
  Transaction, sendAndConfirmTransaction, Keypair,
} = require("@solana/web3.js");

const RPC = process.env.RPC || "https://rpc.cookiescan.io";
const SCAN = "https://cookiescan.io";
const conn = new Connection(RPC, "confirmed");

const PROGRAMS = {
  "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Meteora Bonding Curve (fork)",
  "DBCg4ugDEztk6MbqHEJvx5a5YGJTj45Jb5NvtQ48Rvsf": "CookieBox DBC",
  "DAMMjDCEFTDkt7ywazZS8GoaLtjb3HaJo3pLbf64xrPY": "Cookieswap DAMM",
  "EvRMsRW8NcaSRcy5Mgmsdj9Udk9ryGYq6hwkhicCZzSF": "Cookieora DAMMv2",
  "5cYqbWRziT7dNi8Nb5poJr7nSuuocREj9SfBiuUYVVqc": "Cookieswap CPAMM v3",
  "6Y3VJBWWqFvDkSBdT3Pcb3DNaJ7cA1JPHAiLfo7JhyFq": "Cookieswap CPAMM v2",
  "WTzkPUoprVx7PDc1tfKA5sS7k1ynCgU89WtwZhksHX5": "Cookieswap SAMM",
  "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter v6",
  "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM v4",
  "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
  "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token",
  "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "Token-2022",
  "namesLPneVptA9Z5rqUDD9tMTWEJwofgaYwp8cawRkX": ".cook Name Service",
  "SQDS4ep65T869zMMBKyuUq6aD6EgTu8psMjkvj52pCf": "Squads v4",
};

const app = express();
app.use(express.json());
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type");
  res.header("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

const cache = new Map();
const cached = async (key, ttl, fn) => {
  const hit = cache.get(key);
  if (hit && Date.now() - hit.t < ttl) return hit.v;
  const v = await fn();
  cache.set(key, { t: Date.now(), v });
  return v;
};
const j = async (url, ms = 12000) => {
  const c = new AbortController(); const t = setTimeout(() => c.abort(), ms);
  try { const r = await fetch(url, { signal: c.signal,
    headers: { "User-Agent": "cookie-pulse/1.0" } });
    return await r.json(); } catch { return null; } finally { clearTimeout(t); }
};

/* ---------------- chain health ---------------- */
app.get("/api/health", async (_req, res) => {
  try {
    const [slot, height, epoch, version, supply] = await Promise.all([
      conn.getSlot(), conn.getBlockHeight(), conn.getEpochInfo(),
      conn.getVersion(), conn.getSupply(),
    ]);
    const samples = await conn.getRecentPerformanceSamples(4).catch(() => []);
    const tps = samples.length
      ? Math.round(samples.reduce((a, s) => a + s.numTransactions / s.samplePeriodSecs, 0) / samples.length)
      : null;
    res.json({ ok: true, slot, blockHeight: height, epoch: epoch.epoch,
      slotsInEpoch: epoch.slotsInEpoch, absoluteSlot: epoch.absoluteSlot,
      transactionCount: epoch.transactionCount, version,
      supplyCook: Number(supply.value.circulating) / LAMPORTS_PER_SOL,
      tps, finalityMs: 1000, live: true });
  } catch (e) { res.status(500).json({ ok: false, error: String(e.message || e) }); }
});

/* ---------------- aggregate stats ---------------- */
app.get("/api/stats", async (_req, res) => {
  const [brk, bridge, gor, daily] = await Promise.all([
    j(`${SCAN}/api/break/stats`), j(`${SCAN}/api/bridge/stats`),
    j(`${SCAN}/api/gor/price`), j(`${SCAN}/api/analytics/daily`),
  ]);
  res.json({ ok: true, network: brk, bridge, token: gor,
    analytics: daily ? { days: (daily.days || []).slice(-14) } : null });
});

/* ---------------- pools (real on-chain) ---------------- */
const b58 = (buf) => {
  const A = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  let n = 0n; for (const b of buf) n = n * 256n + BigInt(b);
  let s = ""; while (n > 0n) { s = A[Number(n % 58n)] + s; n /= 58n; }
  for (const b of buf) { if (b === 0) s = "1" + s; else break; }
  return s;
};

app.get("/api/pools", async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 60, 300);
  try {
    const out = await cached("pools", 60000, async () => {
      const results = [];
      for (const [pid, label] of Object.entries(PROGRAMS)) {
        try {
          const accts = await conn.getProgramAccounts(new PublicKey(pid),
            { dataSlice: { offset: 0, length: 120 }, filters: undefined });
          if (!accts.length) continue;
          const disc = {};
          for (const a of accts) {
            const d = Buffer.from(a.account.data).subarray(0, 8).toString("base64");
            disc[d] = (disc[d] || 0) + 1;
          }
          results.push({ program: pid, label, accounts: accts.length,
            discriminators: disc, samples: accts.slice(0, 5).map(a => a.pubkey.toBase58()) });
        } catch (e) { /* skip program */ }
      }
      return results.sort((a, b) => b.accounts - a.accounts);
    });
    res.json({ ok: true, programs: out, count: out.length, limit });
  } catch (e) { res.status(500).json({ ok: false, error: String(e.message || e) }); }
});

/* ---------------- wallet ---------------- */
app.get("/api/wallet/:addr", async (req, res) => {
  try {
    const pk = new PublicKey(req.params.addr);
    const [lamports, tokens, info] = await Promise.all([
      conn.getBalance(pk),
      conn.getParsedTokenAccountsByOwner(pk, { programId: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA") }).catch(() => ({ value: [] })),
      conn.getAccountInfo(pk).catch(() => null),
    ]);
    const sigs = await conn.getSignaturesForAddress(pk, { limit: 25 }).catch(() => []);
    res.json({ ok: true, address: pk.toBase58(), cook: lamports / LAMPORTS_PER_SOL,
      lamports, exists: !!info, tokens: tokens.value.map(t => ({
        mint: t.account.data.parsed.info.mint,
        amount: t.account.data.parsed.info.tokenAmount.uiAmount,
        decimals: t.account.data.parsed.info.tokenAmount.decimals,
      })).filter(t => t.amount > 0),
      signatures: sigs.map(s => ({ signature: s.signature, slot: s.slot,
        blockTime: s.blockTime, err: s.err, memo: s.memo })) });
  } catch (e) { res.status(400).json({ ok: false, error: "Bad address: " + e.message }); }
});

/* ---------------- recent activity ---------------- */
app.get("/api/activity", async (_req, res) => {
  try {
    const slot = await conn.getSlot();
    const block = await conn.getBlock(slot - 2, { maxSupportedTransactionVersion: 0 }).catch(() => null);
    if (!block) return res.json({ ok: true, slot, transactions: [] });
    res.json({ ok: true, slot, blockTime: block.blockTime,
      transactions: (block.transactions || []).slice(0, 30).map(t => ({
        signature: t.transaction.signatures[0],
        fee: t.meta ? t.meta.fee / LAMPORTS_PER_SOL : 0,
        err: t.meta ? !!t.meta.err : null,
        accounts: t.transaction.message.staticAccountKeys
          ? t.transaction.message.staticAccountKeys.length : 0,
      })) });
  } catch (e) { res.json({ ok: true, transactions: [], error: String(e.message) }); }
});

/* ---------------- NFT (DAS) ---------------- */
app.get("/api/nfts", async (_req, res) => {
  const r = await j(`${SCAN}/api/collections`);
  res.json({ ok: true, collections: (r && r.collections) || [] });
});

/* ---------------- programs registry ---------------- */
app.get("/api/programs", (_req, res) =>
  res.json({ ok: true, programs: Object.entries(PROGRAMS).map(([id, label]) => ({ id, label })) }));

/* ---------------- static frontend ---------------- */
const path = require("path");
app.use(express.static(path.join(__dirname, "public")));
app.use((req, res) => {
  if (req.path.startsWith("/api/")) return res.status(404).json({ ok: false, error: "no such endpoint" });
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const PORT = process.env.PORT || 8787;
app.listen(PORT, () => console.log(`🍪 COOKIE PULSE backend on :${PORT} → ${RPC}`));
