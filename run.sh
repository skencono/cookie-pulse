#!/usr/bin/env bash
# run.sh — Cookie Chain node runner
# Node on this host aborts (core dumped) when PM2 env vars are inherited.
# Strip them, then exec whatever node command you pass.
unset PM2_USAGE PM2_HOME vizion_running NODE_APP_INSTANCE pm_id \
      exec_interpreter unstable_restarts restart_time treekill \
      prev_restart_delay instance_var pm_cwd
exec "$@"
