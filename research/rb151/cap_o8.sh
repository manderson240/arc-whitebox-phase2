#!/usr/bin/env bash
# G-RB151: A0 (control, tag a0o8) then A2 (tag a2o8) TF captures on FIT60+VALID-20 at OMP 8, NW 3
cd ~/cohezion-labs/arc-whitebox/research/rb151
for a in A0 A2; do ARM=$a CHAIN=$(echo $a | tr A-Z a-z)o8 NW=${NW:-3} OMP=8 ./cap.sh $(cat tf80.txt); echo "arm $a done $(date -u +%T)"; done
