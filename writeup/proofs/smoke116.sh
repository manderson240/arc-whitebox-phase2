cd ~/cohezion-labs/arc-whitebox
for v in v116_t v116_a5 v116_a7 v116_o7 v116_r448; do
  echo "=== $v $(date -u +%T)"
  python3 research/rebuild/remote_check.py submissions/$v --nets 1 2>&1 | tail -2
done
