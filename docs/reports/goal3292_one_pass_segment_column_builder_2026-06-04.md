# Goal3292 One-Pass Segment Column Builder

Date: 2026-06-04

## Verdict

Goal3292 reduces the remaining Python-side `SegmentColumns2D` construction
cost by replacing five separate `np.fromiter(...)` passes with one pass over
the input segment records.

This keeps the public `segment_columns_2d(...)` API unchanged and remains
generic: it only reads segment IDs and 2-D endpoints. No RayJoin-specific
logic, native ABI, or claim wording was added.

## What Changed

- `segment_columns_2d(records=...)` now fills five NumPy arrays in one pass:
  `ids`, `x0`, `y0`, `x1`, and `y1`.
- Mapping records and attribute records are both preserved.
- Existing ordering modes still operate after arrays are built.
- Existing callers that pass columns directly are unchanged.

## Pod Evidence

Pod: NVIDIA A40, driver 570.211.01

Artifact:

- `docs/reports/goal3292_one_pass_segment_column_builder_micro_pod_2026-06-04.json`

Dataset:

- left: `br_county_start256_count512.cdb`
- right: `br_soil_start256_count512.cdb`
- left segment count: 19,987

| phase | Goal3290 median | Goal3292 median |
| --- | ---: | ---: |
| `segment_columns_2d(...)` prepare | 32.108 ms | 14.289 ms |
| `SegmentColumns2D` pack to native ABI buffer | 0.415 ms | 0.225 ms |
| prepare + pack total | 33.693 ms | 15.541 ms |

This cuts the reusable segment-column preparation path by more than half on the
bounded RayJoin LSI slice.

## Interpretation

Goal3290 made the ABI pack itself cheap. Goal3292 makes the upstream record to
column conversion substantially cheaper too.

The remaining gap is now more explicit:

- if data is already columnar, RTDL can pack it into the native segment ABI in
  sub-ms time for this slice;
- if data starts as Python objects, the conversion still costs about 14 ms for
  19,987 segments;
- the next larger improvement is to parse/load benchmark datasets directly into
  reusable generic columns or a native prepared segment layout, avoiding Python
  segment objects for hot paths.

## Claim Boundary

The artifact keeps release, public speedup, RTDL-beats-RayJoin, paper
reproduction, true zero-copy, and broad RT-core claims blocked. This is an
internal host-ingestion optimization and evidence packet only.
