#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research
for s in heldout:full:300-340 valid20:valid20 fit12:fit12; do
  tag=${s%%:*}; set=${s#*:}
  rebuild/timing_lock.sh rb140/run_arm.sh rb140/arms_final.json $set rb140/res/final_$tag.jsonl
done
