#!/usr/bin/env bash
set -euo pipefail

WORK=/workspace/goal4875_section57_au_representative/small_chain21
RJ_DUMP_OUTPUT_CHAIN_INDEX=0 RJ_DUMP_OUTPUT_CHAIN_RADIUS=8 \
  /workspace/RayJoin_goal4867_author_dump/build_dump/bin/polyover_exec \
  -poly1 "$WORK/left_chain21.cdb" \
  -poly2 "$WORK/right_relevant_chains.cdb" \
  -serialize="$WORK/serialize_dump" \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false \
  -output "$WORK/author_dump_unused.txt" \
  >"$WORK/author_dump_chain0.log" 2>&1 || true

tail -260 "$WORK/author_dump_chain0.log"
