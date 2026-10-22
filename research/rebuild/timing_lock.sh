#!/usr/bin/env bash
# Readers-writer lock for heavy runs.
#   research/rebuild/timing_lock.sh <cmd...>
# TIMING runs (eval_mem / Mini-10 / bisect / bars / ladder) take the lock EXCLUSIVELY and wait for load < 5:
#   2026-10-18: two builders measuring at once voided a Mini-10 session and failed a bar by 1.1 ms on noise.
# COMPUTE-only chunks (MSE evals, cache captures, fits: nothing is timed) take it SHARED and run concurrently.
#   2026-10-19: everything was exclusive, so G-RB130 queued ~2 h behind other chunks with 27/32 threads idle.
# Writer preference: a queued timing run drops .timing.pending; new compute waits until it clears
# (a marker older than 4 h is ignored, so a killed timing waiter cannot block compute forever).
set -u
DIR="$(dirname "$0")"
LOCK="$DIR/.timing.lock"
PENDING="$DIR/.timing.pending"
SHARED_RE="${TIMING_LOCK_SHARED_RE:-rb130/(cap|eval)\.sh|rb131/s131|rb132/}"
FLOOR_KB=$(( (25 + 8) * 1024 * 1024 ))  # :13305 admission floor 25 GB + 8 GB headroom per new compute job
exec 9>"$LOCK"
if [[ "$*" =~ $SHARED_RE ]]; then
  echo "timing_lock: COMPUTE (shared) waiting ($(date -u +%T)): $*" >&2
  while [ -n "$(find "$PENDING" -mmin -240 2>/dev/null)" ] || ! awk -v f="$FLOOR_KB" '/MemAvailable/{exit !($2 > f)}' /proc/meminfo \
        || ! awk '{exit !($1 < 24)}' /proc/loadavg; do sleep 20; done
  flock -s 9
  echo "timing_lock: COMPUTE acquired ($(date -u +%T), load $(cut -d' ' -f1 /proc/loadavg))" >&2
  "$@"
else
  echo "timing_lock: TIMING (exclusive) waiting ($(date -u +%T))" >&2
  touch "$PENDING"
  flock -x 9
  until awk '{exit !($1 < 5)}' /proc/loadavg; do sleep 20; done
  rm -f "$PENDING"
  echo "timing_lock: TIMING acquired ($(date -u +%T), load $(cut -d' ' -f1 /proc/loadavg))" >&2
  "$@"
fi
