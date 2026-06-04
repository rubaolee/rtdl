# Goal3287 Segment Columns 2D Layout And RayJoin Probe

Date: 2026-06-04

## Verdict

Goal3287 adds a reusable generic `SegmentColumns2D` layout primitive and wires
the RayJoin compact LSI left-pack path through it. This is accepted as a
cleaner RTDL preparation contract, but it is **not** a performance win by
itself.

The engineering lesson is sharper than before:

- The RT traversal/count phase is already small.
- Python-side record-to-column and column-to-ctypes packet construction are now
  visible as separate costs.
- The next performance target must move beyond Python object/ctypes packet
  construction toward generic column-to-device or prepared-layout ingestion.

## What Changed

- Added `src/rtdsl/segment_columns.py` with:
  - `SegmentColumns2D`
  - `segment_columns_2d(...)`
  - `segment_columns_with_ids(...)`
- `pack_segments(...)` now accepts `SegmentColumns2D` directly through the
  shared Embree/OptiX packing contract.
- The RayJoin compact LSI packed-left helper now:
  - normalizes left segment records into generic segment columns;
  - remaps caller IDs using `segment_columns_with_ids(...)`;
  - packs the remapped column batch;
  - reports `query_column_prepare_sec` and `query_pack_sec` separately.
- Added primitive discovery metadata:
  `execution.segment_columns_2d`.
- Regenerated `docs/rtdl_primitive_catalog.md`.

No native ABI was added. No RayJoin-specific native logic was added.

## Pod Evidence

Pod: NVIDIA A40, driver 570.211.01

Artifacts:

- `docs/reports/goal3287_segment_columns_lsi_dense_count_pod_2026-06-04.json`
- `docs/reports/goal3287_segment_columns_pack_left_micro_pod_2026-06-04.json`

### Current-Best LSI Dense Count Harness

Input:

- left segments: `br_county_start256_count512.cdb`
- right segments: `br_soil_start256_count512.cdb`
- left segment count: 19,987
- visible LSI count: 269

Result:

| route | status | observed count | CPU reference match | median counted traversal phase |
| --- | --- | ---: | --- | ---: |
| `prepared_optix_left_id_dense_count` | pass | 269 | true | 0.383230 ms |

The harness status is `pass`, and claim-boundary flags remain false for public
speedup, paper reproduction, RTDL-beats-RayJoin, true zero-copy, and whole-app
speedup.

### Packed-Left Micro Timing

For the same 19,987 left segments:

| phase | median |
| --- | ---: |
| `query_column_prepare_sec` | 37.573 ms |
| `query_pack_sec` | 29.741 ms |

This means the new layout is useful for tracing and reuse, but it does not
solve the host-side input-construction bottleneck.

## Interpretation

Goal3287 is a design cleanup and observability improvement:

- Apps can now express "I have reusable 2-D segment columns" without naming a
  benchmark workload.
- The compact LSI path no longer rebuilds intermediate dictionaries for
  left-ID remapping.
- The primitive catalog now exposes segment column preparation as a discoverable
  generic behavior.

But the measured path is still dominated by Python-level host construction:

- record-to-column extraction is tens of milliseconds;
- ctypes packet construction is also tens of milliseconds;
- the actual OptiX dense-count traversal is sub-millisecond.

So this goal confirms the same direction as Goal3285: host-side data layout is
now the blocker. The next useful primitive should ingest reusable columns into
prepared/device layout without a Python loop over every segment.

## Claim Boundary

This goal does not authorize:

- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- true zero-copy claims;
- broad RT-core speedup claims;
- release claims.

It authorizes only this internal engineering conclusion:

> Segment column layout is the right generic abstraction boundary, but the
> current Python/ctypes implementation is not the final high-performance
> realization.

## Next Engineering Target

Build a generic segment-column ingestion path that avoids Python per-segment
packet construction:

- accept `SegmentColumns2D` or equivalent arrays;
- preserve caller IDs and dense remap metadata;
- build the device/prepared segment layout from columns with a lower-level
  bulk path;
- report layout-build, upload, traversal, and reduction phases separately;
- keep the primitive app-agnostic: segment IDs and endpoints only, no RayJoin
  names, no spatial-join policy, no paper-system assumptions.
