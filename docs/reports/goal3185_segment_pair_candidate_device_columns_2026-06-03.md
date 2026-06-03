# Goal3185: Segment-Pair Candidate Device Columns

Date: 2026-06-03

## Purpose

Goal3183 removed host row materialization for the Spatial RayJoin overlay
active-count subpath. Goal3185 starts the harder resident-output path for the
same generic geometry family: prepared segment-pair traversal can now emit
device-resident candidate ID columns:

- `left_id`
- `right_id`

This is the next primitive-level building block for device-side continuations
over relation candidates.

## Code Changes

- Added generic native ABI:
  `rtdl_optix_prepared_segment_pair_candidate_device_columns`.
- Added release ABI:
  `rtdl_optix_release_segment_pair_candidate_device_columns`.
- Added `RtdlNativeDevicePairColumns` with native-owned CUDA pointers for
  `left_id` and `right_id` columns plus row-count, event-count, overflow,
  capacity, device, owner, and traversal metadata.
- Added an OptiX candidate-column pipeline derived from the existing
  segment-pair conservative candidate any-hit logic.
- Added Python RAII output:
  `OptixNativeDevicePairColumnOutput`.
- Added Python method:
  `PreparedOptixSegmentPairIntersection.candidate_device_columns(...)`.
- Extended v2.8 geometry-relation typed metadata with the generic
  `segment_pair_candidate_2d_device_columns` schema.

## Boundary

This produces device-resident candidate ID columns. It is not exact
intersection witness row materialization; in shorter terms, these are
not exact intersection witness rows.

It does:

- keep native terminology generic,
- reuse the generic segment-pair conservative candidate any-hit logic,
- keep `left_id` and `right_id` columns resident in native-owned CUDA memory,
- return typed stream metadata without forcing a host copy,
- fail closed on overflow.

It does not:

- produce exact `intersection_point_x` / `intersection_point_y` witnesses,
- validate final line-segment intersection predicates,
- provide grouped/reduction continuation over the pair columns yet,
- prove true zero-copy with partner-owned memory,
- prove a public speedup,
- reproduce RayJoin paper results,
- authorize a v2.8 release.

Implementation scope:

- This is a single-launch first slice.
- `left_count * right_count` must fit the uint32 OptiX launch/candidate space.
- chunked append remains future work.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3185_segment_pair_candidate_device_columns_test
```

Initial report status: implementation and local source tests are expected before
pod execution. Pod evidence should be appended only after a clean rebuild and
live OptiX smoke.
