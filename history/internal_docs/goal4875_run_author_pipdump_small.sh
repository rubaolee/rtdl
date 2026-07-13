#!/usr/bin/env bash
set -euo pipefail

WORK=/workspace/goal4875_section57_au_representative/small_chain21
POINT_INDEX="${1:-126}"

RJ_DUMP_PIP_QUERY_MAP_ID=0 RJ_DUMP_PIP_POINT_INDEX="$POINT_INDEX" \
  /workspace/RayJoin_goal4867_author_dump/build_dump/bin/polyover_exec \
  -poly1 "$WORK/left_chain21.cdb" \
  -poly2 "$WORK/right_relevant_chains.cdb" \
  -serialize="$WORK/serialize_pipdump_${POINT_INDEX}" \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false \
  -output "$WORK/author_pipdump_unused_${POINT_INDEX}.txt" \
  >"$WORK/author_pipdump_${POINT_INDEX}.log" 2>&1 || true

grep -E 'RJ_DUMP_PIP|RJ_DUMP_PIP_EDGE|Map [01], Xsect|Total chains' "$WORK/author_pipdump_${POINT_INDEX}.log" || true
