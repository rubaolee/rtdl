# Goal4870 - Author+RTDLContractPatch 1M-line prefix escalation for Block x Water

Date: 2026-07-02

## Purpose

Goal4869 showed that RTDL and the explicitly named
`Author+RTDLContractPatch` comparator match exactly over the first 250,000
output lines of the Block x Water Section 5.7 overlay output.

Goal4870 escalates the same bounded comparison to the first 1,000,000 output
lines. This gives stronger evidence that the repaired duplicate-half-edge
contract remains stable beyond the earliest output region while still avoiding
an uncontrolled full 3.6G / 138,674,679-line comparison.

## Scale facts

The full `Author+RTDLContractPatch` Block x Water output has:

- line count: `138,674,679`
- file size: `3.6G`

That full-stream size is large enough that direct full validation should be a
deliberate step, not an accidental long-running process.

## Inputs

Author full output:

`/workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt`

Author 1M prefix:

`/workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head1m.txt`

CDB pair:

- left: `/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb`
- right: `/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb`

## Command

```bash
cd /workspace/rtdl_goal4859_exec
export PYTHONPATH=/workspace/rtdl_goal4859_exec/src:/workspace/rtdl_goal4859_exec/history/internal_docs
export LD_LIBRARY_PATH=/workspace/rtdl_goal4859_exec/build:${LD_LIBRARY_PATH:-}
export RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR=/workspace/goal4867_block_water_packed_cache

head -n 1000000 \
  /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt \
  > /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head1m.txt

timeout 25m python history/internal_docs/goal4867_block_water_packed_streaming_compare.py \
  --left /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb \
  --right /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb \
  --author-output /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay_head1m.txt \
  --output-dir /workspace/goal4870_rtdl_vs_author_contract_block_water_prefix1m
```

## Result

Artifact:

`history/internal_docs/goal4870_rtdl_vs_author_contract_block_water_prefix1m_summary.json`

Summary:

- elapsed: `174.17043448239565` seconds
- compared author prefix: first `1,000,000` output lines
- first reported difference:
  - line: `1000001`
  - author: `<eof>`
  - RTDL: `-86.985025 33.326329`
  - context chain: `333334`

Interpretation:

The first 1,000,000 output lines match exactly. The reported difference is the
intentional truncation boundary of the 1M-line author prefix.

This is stronger than Goal4868/Goal4869 because it verifies much more output
without encountering a semantic mismatch. It still does not prove full-stream
Section 5.7 reproduction.

## What this does not authorize

This does not authorize:

- full Block x Water byte equality,
- full Section 5.7 reproduction,
- all-eight-pair reproduction,
- performance claims,
- public release documentation.

## Next controlled options

1. Run a complete full-stream comparison under the same
   `Author+RTDLContractPatch` contract, accepting that it reads/writes/streams a
   3.6G, 138,674,679-line output.
2. Add a more efficient internal full-stream hash comparator before full
   validation, if the current Python text comparison proves too slow.
3. Run bounded later-window probes if we need coverage away from the prefix
   before committing to full stream.

## Exit label

`completed_author_contract_prefix1m_exact_match__first_diff_is_intentional_eof`
