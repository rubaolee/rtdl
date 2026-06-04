# Goal3293 Direct CDB Segment Columns

Date: 2026-06-04

Status: local implementation complete; pod timing still required.

## Purpose

Goal3290 and Goal3292 made segment packing faster after Python segment records
already exist. The next bottleneck is earlier: external RayJoin-style CDB chains
were converted into Python segment records, and then the prepared OptiX route
rebuilt those records into generic segment columns before packing.

This goal adds a direct CDB-to-segment-column path so the optimized LSI prepared
routes can start from generic column arrays instead of object/dict records.

## Implementation

- Added `rtdsl.datasets.chains_to_segment_columns(dataset, limit_chains=None)`.
- The converter builds `SegmentColumns2D` arrays directly from consecutive CDB
  chain points, preserving the same caller ids and endpoint geometry as
  `chains_to_segments(...)`.
- Exported `rt.chains_to_segment_columns(...)` from the public Python facade.
- Updated the external CDB LSI loader to accept `segment_column_inputs=True`.
- Updated prepared RayJoin LSI routes to request direct column inputs for
  external CDB datasets.
- Kept the CPU reference route unchanged. CPU reference route still uses ordinary segment records, which protects same-contract validation.

## Boundary

No native ABI changed. The native OptiX/Embree engine still sees generic segment
columns and packed segment buffers; RayJoin-specific meaning, workload names,
and comparison policy remain in Python/example code.

Claim flags:

- release_authorized: false
- public_speedup_claim_authorized: false
- rtdl_beats_rayjoin_claim_authorized: false
- full_rayjoin_reproduction_claim_authorized: false

## Local Validation

The regression test checks that the new CDB columns:

- have the same count as `chains_to_segments(...)`;
- preserve first/last ids and endpoint geometry;
- pack to the same native segment ids as the record path;
- are selected only by the optimized external LSI prepared routes;
- do not introduce app-specific native symbols.

A local Windows sanity probe on a synthetic tiled CDB-shaped fixture with 20,300
segments measured the old full input route (`chains_to_segments(...)` plus
`segments_from_records(...)`) at 66.391 ms median versus
`chains_to_segment_columns(...)` at 18.253 ms median. This is not pod evidence
and does not authorize a public speedup claim; it only confirms that the
loader-side optimization is worth the RTX same-slice retest.

## Pod Boundary

Pod timing is still required. This local change removes a Python-side conversion
layer, but accepted RayJoin same-slice timing still needs the RTX pod harness to
measure whether the end-to-end prepared LSI query path improves over the
Goal3292 packet.
