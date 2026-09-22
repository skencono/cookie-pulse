#!/usr/bin/env python3
"""Verified thread splitter: split x_thread.txt into <=280-char tweets on blank lines."""
import json, re, sys

MAX = 280
raw = open("/home/ubuntu/cookiechain/x_thread.txt").read().strip()
blocks = [b.strip() for b in re.split(r"\n\s*\n", raw) if b.strip()]

# greedy-pack blocks into tweets without exceeding MAX
tweets, cur = [], ""
for b in blocks:
    cand = (cur + "\n\n" + b).strip() if cur else b
    if len(cand) <= MAX:
        cur = cand
    else:
        if cur:
            tweets.append(cur)
        cur = b
if cur:
    tweets.append(cur)

bad = [(i, len(t)) for i, t in enumerate(tweets, 1) if len(t) > MAX]
print(json.dumps({"count": len(tweets), "over": bad}, indent=1))
for i, t in enumerate(tweets, 1):
    print(f"--- tweet {i} ({len(t)} chars) ---")
    print(t)
print()
json.dump(tweets, open("/home/ubuntu/cookiechain/x_tweets.json", "w"), ensure_ascii=False, indent=1)
