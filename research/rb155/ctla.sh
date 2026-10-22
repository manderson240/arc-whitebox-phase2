#!/usr/bin/env bash
# G-RB155 control stage (a): refit on the EXISTING rebuild/aug_dumpF2_*.npz with NOQLAST 1 and 0.
R=~/cohezion-labs/arc-whitebox/research/rb155
B=~/cohezion-labs/arc-whitebox/research/rebuild
"$R/fitlam.sh" "$B/aug_dumpF2.npz" "$R/lam_ctla_q1.npz" 1 "$R/ctla_q1.log"
"$R/fitlam.sh" "$B/aug_dumpF2.npz" "$R/lam_ctla_q0.npz" 0 "$R/ctla_q0.log"
