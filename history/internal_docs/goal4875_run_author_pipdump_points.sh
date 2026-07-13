#!/usr/bin/env bash
set -euo pipefail

WORK=/workspace/goal4875_section57_au_representative/small_chain21
BIN=/workspace/RayJoin_goal4867_author_dump/build_dump/bin/polyover_exec

if [[ "$#" -eq 0 ]]; then
  set -- 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135
fi

for point_index in "$@"; do
  echo "=== POINT ${point_index} ==="
  RJ_DUMP_PIP_QUERY_MAP_ID=0 RJ_DUMP_PIP_POINT_INDEX="${point_index}" \
    "${BIN}" \
    -poly1 "${WORK}/left_chain21.cdb" \
    -poly2 "${WORK}/right_relevant_chains.cdb" \
    -serialize="${WORK}/serialize_pipdump_${point_index}" \
    -grid_size=15000 \
    -mode=rt \
    -v=1 \
    -fau \
    -xsect_factor 0.1 \
    -enlarge=3.5 \
    -check=false \
    -output "${WORK}/author_pipdump_unused_${point_index}.txt" \
    >"${WORK}/author_pipdump_${point_index}.log" 2>&1 || true
  grep -E 'RJ_DUMP_PIP|RJ_DUMP_PIP_EDGE|Map [01], Xsect|Total chains' \
    "${WORK}/author_pipdump_${point_index}.log" || true
done
