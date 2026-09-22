#!/usr/bin/env bash
# Cookie Chain / Node fix: PM2 env vars crash Node + Solana libs
unset NODE_APP_INSTANCE instance_var pm_cwd pm_id PM2_HOME
