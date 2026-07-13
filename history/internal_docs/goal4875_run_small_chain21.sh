#!/usr/bin/env bash
set -euo pipefail

WORK=/workspace/goal4875_section57_au_representative/small_chain21
AUTHOR=/workspace/RayJoin_goal4867_author_dump/release/bin/polyover_exec

"$AUTHOR" \
  -poly1 "$WORK/left_chain21.cdb" \
  -poly2 "$WORK/right_relevant_chains.cdb" \
  -serialize="$WORK/serialize" \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false \
  -output "$WORK/author_small.txt" \
  >"$WORK/author_small.log" 2>&1

cd /workspace/rtdl_goal4859_exec
PYTHONPATH=src RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal4859_exec/build/librtdl_optix.so \
  python3 /workspace/goal4875_public_primitives_au_overlay.py \
  --left "$WORK/left_chain21.cdb" \
  --right "$WORK/right_relevant_chains.cdb" \
  --author-output "$WORK/author_small.txt" \
  --output "$WORK/rtdl_small.txt" \
  --summary "$WORK/rtdl_small_summary.json" \
  >"$WORK/rtdl_small.log" 2>&1

sha256sum "$WORK/author_small.txt" "$WORK/rtdl_small.txt"
wc -l -c "$WORK/author_small.txt" "$WORK/rtdl_small.txt"
grep -E 'Map [01], Xsect|Total chains|Timing results' "$WORK/author_small.log" || true
cat "$WORK/rtdl_small_summary.json"
