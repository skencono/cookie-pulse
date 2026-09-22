#!/usr/bin/env bash
# Cookie Pulse runner: Node on this host aborts when run with the inherited
# Hermes/PM2 environment, so start it with a clean one.
cd /home/ubuntu/cookiechain || exit 1
exec env -i \
  PATH=/usr/bin:/bin:/usr/local/bin \
  HOME=/home/ubuntu \
  LANG=C.UTF-8 \
  PORT="${PORT:-8787}" \
  RPC="${RPC:-https://rpc.cookiescan.io}" \
  node server.js
