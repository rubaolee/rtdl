# Goal4869 - Author+RTDLContractPatch prefix escalation for Block x Water

Date: 2026-07-02

## Purpose

Goal4868 repaired RTDL's directed-segment point-location contract for duplicate
half-edges and validated the repair with:

- synthetic duplicate-half-edge probes,
- focused Block x Water PIP witnesses,
- an explicitly named `Author+RTDLContractPatch` comparator,
- a first-100,000-line exact prefix match.

Goal4869 performs one larger bounded check before any full-stream attempt:
compare the first 250,000 output lines produced by RTDL against the same
`Author+RTDLContractPatch` Block x Water output.

This is deliberately not a full Section 5.7 claim. It is a controlled prefix
escalation to prove the repaired contract survives a larger real-output slice.

## Inputs

RTDL workspace on POD:

`/workspace/rtdl_goal4859_exec`

Author comparator:

`/workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt`

CDB pair:

- left: `/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb`
- right: `/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb`

The author comparator output was generated from the patched author binary whose
only algorithmic change is the same duplicate-half-edge canonicalization
contract used by RTDL.

## Command

```bash
cd /workspace/rtdl_goal4859_exec
export PYTHONPATH=/workspace/rtdl_goal4859_exec/src:/workspace/rtdl_goal4859_exec/history/internal_docs
export LD_LIBRARY_PATH=/workspace/rtdl_goal4859_exec/build:${LD_LIBRARY_PATH:-}
export RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR=/workspace/goal4867_block_water_packed_cache

head -n 250000 \
  /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt \
  > /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head250k.txt

timeout 18m python history/internal_docs/goal4867_block_water_packed_streaming_compare.py \
  --left /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb \
  --right /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb \
  --author-output /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head250k.txt \
  --output-dir /workspace/goal4869_rtdl_vs_author_contract_block_water_prefix250k
```

## Result

Artifact:

`history/internal_docs/goal4869_rtdl_vs_author_contract_block_water_prefix250k_summary.json`

Summary:

- elapsed: `162.69292152673006` seconds
- compared author prefix: first `250,000` output lines
- first reported difference:
  - line: `250001`
  - author: `<eof>`
  - RTDL: `-85.819224 33.635622`
  - context chain: `83334`

Interpretation:

The first 250,000 output lines match exactly. The reported difference is the
expected truncation boundary: the author prefix file intentionally ends after
250,000 lines, while the RTDL stream continues to line 250,001.

This extends the earlier 100,000-line prefix match to 250,000 lines and supports
continuing with bounded window or full-stream comparison under the same
`Author+RTDLContractPatch` contract.

## What this does not authorize

This does not authorize:

- a full Section 5.7 reproduction claim,
- a performance claim,
- a claim against the unpatched AuthorPatch baseline,
- a claim that all eight Section 5.7 pairs reproduce,
- public documentation or tutorial changes.

## Exit label

`completed_author_contract_prefix250k_exact_match__first_diff_is_intentional_eof`
