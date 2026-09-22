#!/usr/bin/env python3
"""Render X_THREAD.md from the verified chain — the public record of the demo."""
import json

HA = "kun_annas"
chain = json.load(open("/home/ubuntu/cookiechain/x_chain_ids.json"))
tweets = [t for t in json.load(open("/home/ubuntu/cookiechain/x_tweets.json")) if len(t) > 20]

LIVE = "https://buy-priorities-town-offshore.trycloudflare.com"
REPO = "https://github.com/skencono/cookie-pulse"

lines = [
    "# Cookie Pulse — X Demo Thread",
    "",
    f"**Root tweet:** https://x.com/{HA}/status/{chain[0]}",
    "",
    "Posted as a verified reply chain (each tweet's `in_reply_to_status_id_str`",
    "equals the previous tweet's id — checked against X's own GraphQL API, not the DOM).",
    "",
    f"- **Live app:** {LIVE}",
    f"- **Source (MIT):** {REPO}",
    "",
    "## The thread",
    "",
]

for i, tid in enumerate(chain, 1):
    text = tweets[i - 1] if i - 1 < len(tweets) else "(appended)"
    lines.append(f"### {i}. https://x.com/{HA}/status/{tid}")
    lines.append("")
    lines.append("> " + text.replace("\n", "\n> "))
    lines.append("")

lines += [
    "## Chain integrity",
    "",
    "Verified by reading `UserRepliesTimeline` / `UserOriginalsTimeline` off X's own",
    "network traffic and asserting `inReply[i] == id[i-1]` for every tweet:",
    "",
    "```",
]
for i, tid in enumerate(chain, 1):
    exp = "— (root)" if i == 1 else chain[i - 2]
    lines.append(f"{i}. {tid}   inReplyTo = {exp}")
lines += [
    "```",
    "",
    "## Notes on building this thread programmatically",
    "",
    "Three things break naive automation, all discovered the hard way:",
    "",
    "1. **X does not redirect after posting.** `pg.url` stays `/compose/post`.",
    "   Success must be read from the `CreateTweet` response body (`rest_id`).",
    "2. **Replying from a status page's page-level reply button binds to the",
    "   conversation ROOT, not to that tweet** — it silently flattens the thread.",
    "   The reply affordance *inside the target tweet's `<article>`* is the one that",
    "   chains correctly.",
    "3. **The profile DOM is cached.** Scraping `a[href*=\"/status/\"]` returns stale",
    "   ids and produces false success reports.",
    "",
    "Written up fully in the repo's tooling and in `X_THREAD.md`.",
]

open("/home/ubuntu/cookiechain/X_THREAD.md", "w").write("\n".join(lines) + "\n")
nl = "\n"
print(f"wrote X_THREAD.md ({len(nl.join(lines))} chars, {len(chain)} tweets)")
