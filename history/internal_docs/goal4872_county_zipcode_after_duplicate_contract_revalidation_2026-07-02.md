# Goal4872 - County x Zipcode revalidation after duplicate-half-edge contract repair

Date: 2026-07-02

## Verdict

`completed_county_zipcode_full_stream_still_matches_after_duplicate_half_edge_contract_repair`

## Purpose

County x Zipcode had already passed a full byte-equality reproduction before
Goal4868 changed RTDL's directed-segment point-location contract for duplicate
half-edges.

Goal4872 reruns County x Zipcode with the current RTDL product code after that
core repair. This is a regression check: prove that the duplicate-half-edge
canonicalization did not break the earlier County x Zipcode Section 5.7 result.

## Inputs

Left CDB:

`/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`

Right CDB:

`/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

Author baseline:

`/workspace/goal4861_author_intended_baseline/author_intended_county_zipcode_overlay.txt`

Local artifacts:

- `history/internal_docs/goal4872_county_zipcode_current_after_duplicate_contract_full_stream_summary.json`
- `history/internal_docs/goal4872_county_zipcode_current_after_duplicate_contract_full_stream_run.log`

## Command

```bash
cd /workspace/rtdl_goal4859_exec
export PYTHONPATH=/workspace/rtdl_goal4859_exec/src:/workspace/rtdl_goal4859_exec/history/internal_docs
export LD_LIBRARY_PATH=/workspace/rtdl_goal4859_exec/build:${LD_LIBRARY_PATH:-}
export RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR=/workspace/goal4872_county_zipcode_packed_cache

timeout 3h python history/internal_docs/goal4871_block_water_full_stream_compare.py \
  --left /workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb \
  --right /workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb \
  --author-output /workspace/goal4861_author_intended_baseline/author_intended_county_zipcode_overlay.txt \
  --output-dir /workspace/goal4872_county_zipcode_current_after_duplicate_contract_full_stream \
  --progress-lines 5000000 \
  --progress-chains 1000000
```

## Result

The full stream still matched exactly:

```json
{
  "stream_match": true,
  "first_diff": null,
  "streamed_line_count": 87758114,
  "streamed_chain_count": 29253961,
  "streamed_point_count": 58504153,
  "streamed_face_count": 115515,
  "elapsed_sec": 593.9219101071358
}
```

The output counts are internally consistent:

`29,253,961 chains + 58,504,153 points = 87,758,114 lines`.

## Interpretation

The duplicate-half-edge canonicalization did not regress County x Zipcode.
Current RTDL still matches the author baseline over the entire output stream.

This means we now have two serious Section 5.7 full-stream correctness results:

| Pair | Comparator | Full-stream status |
|---|---|---|
| County x Zipcode | existing author intended baseline | exact match |
| Block x Water | `Author+RTDLContractPatch` | exact match |

## Performance note

This is a correctness validation run, not a performance benchmark.

Selected phase data:

- total: `593.2380827963352` seconds
- output streaming comparison: `467.61298881471157` seconds
- first-time packed-cache load/write in this run: `188.64966413378716` seconds
- LSI row object materialization: `9.324819460511208` seconds
- LSI row sort: `45.78160282969475` seconds
- point-location prepare: `8.498992122709751` seconds

Because the run includes cache creation and Python text-stream comparison, it
must not be used as a speedup claim.

## What this does not prove

This does not prove:

- all-eight-pair Section 5.7 reproduction,
- performance superiority,
- public release readiness,
- correctness for datasets whose exact CDB inputs and author baselines are not
  available.

## Next step

The next honest step is a Section 5.7 bounded closure packet for the two
validated pairs, or acquisition/restoration of additional exact CDB inputs and
author baselines before attempting more pairs.
