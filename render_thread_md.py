#!/usr/bin/env python3
"""Render the final X_THREAD.md with the verified chain ids."""
import json, os

chain = json.load(open("/home/ubuntu/cookiechain/x_chain_ids.json"))
tweets = [t for t in json.load(open("/home/ubuntu/cookiechain/x_tweets.json")) if len(t) > 20]
H = "kun_annas"

lines = [
    "# Cookie Pulse — X thread\n",
    f"Posted by [@{H}](https://x.com/{H}).",
    "",
    f"**Live app:** https://buy-priorities-town-offshore.trycloudflare.com  ",
    "**Repo:** https://github.com/skencono/cookie-pulse",
    "",
    "## Thread (verified reply chain)",
    "",
]
for i, t in enumerate(tweets):
    tid = chain[i] if i < len(chain) else None
    link = f"https://x.com/{H}/status/{tid}" if tid else "_(not posted)_"
    lines.append(f"### {i+1}. {link}\n")
    lines.append("```")
    lines.append(t)
    lines.append("```")
    lines.append("")

lines += [
    "## Verification",
    "",
    "Each tweet's `in_reply_to_status_id_str` was read from X's own GraphQL API",
    "(`UserOriginalsTimeline` / `UserRepliesTimeline`) — not from the DOM, which is",
    "cached and unreliable. Run `python3 verify_thread_final.py` to re-check.",
    "",
    f"Root: https://x.com/{H}/status/{chain[0] if chain else '—'}",
    "",
]
open("/home/ubuntu/cookiechain/X_THREAD.md", "w").write("\n".join(lines))
print(f"wrote X_THREAD.md with {len(tweets)} tweets, chain length {len(chain)}")
