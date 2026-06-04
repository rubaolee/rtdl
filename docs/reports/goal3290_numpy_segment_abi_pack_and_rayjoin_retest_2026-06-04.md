# Goal3290 NumPy Segment ABI Pack And RayJoin Retest

Date: 2026-06-04

## Verdict

Goal3290 replaces the slow Python `_RtdlSegment(...)` per-row construction in
the generic 2-D segment packer with a NumPy-owned structured buffer whose memory
layout matches the existing native `RtdlSegment` ABI.

This is accepted as a useful host-ingestion optimization:

- No native ABI changed.
- No app-specific native engine path was added.
- The packed buffer stays alive through `PackedSegments.owner`.
- Segment IDs still remain wide until the final uint32 ABI boundary, where
  Goal3288 fail-closed validation applies.

It is **not** enough to claim RTDL beats RayJoin. The measured RTDL traversal
phase is already sub-ms; the remaining gap is dominated by Python-side input
construction and upstream record/column preparation.

## What Changed

- `PackedSegments` now has an optional `owner` field so non-ctypes buffers can
  safely back the native pointer.
- `pack_segments(...)` can now return a pointer into a NumPy structured array
  with fields and offsets matching `_RtdlSegment`:
  - `id` at offset 0
  - `x0` at offset 8
  - `y0` at offset 16
  - `x1` at offset 24
  - `y1` at offset 32
  - item size 40 bytes
- `SegmentColumns2D` inputs use vectorized field assignment into that ABI buffer.
- Natural record inputs use a one-pass structured-buffer fill. An earlier
  five-pass `fromiter` attempt was rejected because it made the repeated
  RayJoin LSI pack path slower.
- The existing `pack_segments(...)` API and native ABI remain compatible.

## Pod Evidence

Pod: NVIDIA A40, driver 570.211.01

Artifacts:

- `docs/reports/goal3290_numpy_segment_abi_pack_final_micro_pod_2026-06-04.json`
- `docs/reports/goal3290_rayjoin_same_slice_final_numpy_pack_pod_2026-06-04.json`

### Segment Pack Micro

Dataset:

- left: `br_county_start256_count512.cdb`
- right: `br_soil_start256_count512.cdb`
- left segment count: 19,987

| path | median |
| --- | ---: |
| ordinary record `pack_segments(records=...)` | 16.220 ms |
| `segment_columns_2d(...)` prepare | 32.108 ms |
| `SegmentColumns2D` pack to native ABI buffer | 0.415 ms |
| `SegmentColumns2D` prepare + pack total | 33.693 ms |

This separates two different facts:

- The new ABI-buffer pack itself is fast.
- Building columns from Python records is still expensive and is the next
  ingestion bottleneck.

### Same-Slice RayJoin Comparison Retest

Same bounded public CDB slice as Goal3244/Goal3285:

| workload | visible count status | RTDL prepared query median | RayJoin reported query median | RTDL/RayJoin query ratio | RTDL query pack median |
| --- | --- | ---: | ---: | ---: | ---: |
| `lsi` | matching visible count, 269 | 0.392 ms | 0.237 ms | 1.658x | 16.274 ms |
| `pip` | RayJoin positive count not visible | 0.509 ms | 0.193 ms | 2.636x | 0.460 ms |

For LSI, the native phase samples remain sub-ms and count parity holds. The
measured host packing cost dropped from the earlier natural-path baseline, but
it is still much larger than the RT traversal/count phase.

## Interpretation

Goal3290 confirms the current performance map:

1. The generic OptiX RT traversal/count kernel is not the main bottleneck on
   this slice.
2. Python record ingestion and record-to-column construction remain too costly.
3. The reusable `SegmentColumns2D` path is architecturally right, but users only
   see its benefit when data already exists as columns or when the app can reuse
   prepared packed inputs.
4. The next serious target is a first-class generic segment-column ingestion
   path that starts from columnar data earlier, ideally at dataset-load time or
   native bulk-ingest time, instead of repeatedly converting Python segment
   objects.

## Claim Boundary

The artifacts keep these claims blocked:

- no release authorization;
- no public speedup claim;
- no RTDL-beats-RayJoin claim;
- no RayJoin paper reproduction claim;
- no true zero-copy claim;
- no broad RT-core speedup claim.

## Next Engineering Target

The next useful work is not another ordering probe. It is a generic bulk
segment-column ingestion/prepared-layout path:

- accept 2-D segment columns as first-class data earlier in the app pipeline;
- avoid repeated Python object-to-record conversion;
- preserve caller IDs and uint32 ABI fail-closed validation;
- report column construction, native packing/upload, traversal, and reduction
  as separate phases;
- keep all native names generic, with no RayJoin vocabulary.
