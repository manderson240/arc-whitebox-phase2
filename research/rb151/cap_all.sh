#!/usr/bin/env bash
# G-RB151: A0 (control) then A2 then A2r TF captures on FIT60+VALID-20 at OMP 2, NW 12
cd ~/cohezion-labs/arc-whitebox/research/rb151
for a in A0 A2 A2r; do ARM=$a NW=${NW:-12} OMP=2 ./cap.sh $(cat tf80.txt); echo "arm $a done $(date -u +%T)"; done
