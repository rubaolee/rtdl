# Goal4871 - Block x Water full-stream comparison result

Date: 2026-07-02

## Verdict

`completed_block_water_full_stream_match_against_author_rtdl_contract_patch`

## Purpose

Goal4871 deliberately ran the full Block x Water Section 5.7 overlay stream
comparison under the repaired duplicate-half-edge contract:

- RTDL current product code with duplicate-half-edge canonicalization.
- `Author+RTDLContractPatch`, an explicitly patched author comparator using the
  same duplicate-half-edge canonicalization contract.

This is the follow-up to the 100k, 250k, and 1M prefix matches.

## Inputs

Left CDB:

`/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb`

Right CDB:

`/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb`

Author comparator output:

`/workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt`

Local artifacts:

- `history/internal_docs/goal4871_rtdl_vs_author_contract_block_water_full_stream_summary.json`
- `history/internal_docs/goal4871_rtdl_vs_author_contract_block_water_full_stream_run.log`

## Command

```bash
cd /workspace/rtdl_goal4859_exec
export PYTHONPATH=/workspace/rtdl_goal4859_exec/src:/workspace/rtdl_goal4859_exec/history/internal_docs
export LD_LIBRARY_PATH=/workspace/rtdl_goal4859_exec/build:${LD_LIBRARY_PATH:-}
export RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR=/workspace/goal4867_block_water_packed_cache

timeout 6h python history/internal_docs/goal4871_block_water_full_stream_compare.py \
  --left /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb \
  --right /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb \
  --author-output /workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt \
  --output-dir /workspace/goal4871_rtdl_vs_author_contract_block_water_full_stream \
  --progress-lines 5000000 \
  --progress-chains 1000000
```

## Result

The full stream matched exactly:

```json
{
  "stream_match": true,
  "first_diff": null,
  "streamed_line_count": 138674679,
  "streamed_chain_count": 46224916,
  "streamed_point_count": 92449763,
  "streamed_face_count": 2581495,
  "elapsed_sec": 1448.1226254478097
}
```

The full author comparator output had:

- `138,674,679` lines
- `46,224,916` output chains
- `92,449,763` output points
- `2,581,495` output faces

RTDL matched all of those exactly against the `Author+RTDLContractPatch`
comparator. No first difference was found.

## Selected RTDL phase data

From the result artifact:

- total: `1447.6409585624933` seconds
- output streaming comparison: `1273.0161385759711` seconds
- point-location prepare: `62.6818917542696` seconds
- LSI row object materialization: `6.294593192636967` seconds
- LSI row sort: `30.312007151544094` seconds

The dominant cost in this validation run is the Python text-stream comparison,
not the native traversal phases.

## What this proves

This proves that, for the Block x Water pair under the explicit
`Author+RTDLContractPatch` duplicate-half-edge contract, RTDL's generated Section
5.7 overlay output is byte-for-byte identical to the comparator stream.

This is a full-stream correctness result for one Section 5.7 pair.

## What this does not prove

This does not prove:

- full eight-pair Section 5.7 reproduction,
- performance superiority,
- equivalence to the old unpatched AuthorPatch baseline,
- public release readiness,
- correctness of every possible polygon-overlay input.

## Next step

The next technical step is to choose one of:

1. run the next Section 5.7 pair under the same explicit contract, if exact
   inputs and an `Author+RTDLContractPatch` comparator output are available;
2. document Block x Water as the completed full-stream pair and close this slice
   as a bounded reproduction result;
3. move performance analysis to a separate goal, only after correctness scope is
   explicitly frozen.
