# Goal3633 Segment-Pair Status Device Columns

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3633 narrows the remaining residency gap in the candidate generic
`segment_pair_left_id_dense_count` output contract. Goal3631 proved backend
conformance and device residency for the dense left-id count column. This goal
keeps the same app-agnostic primitive and exposes two already-computed status
values as retained device pointers:

- source row / candidate event count;
- overflow status.

No app-specific rule or RayJoin-specific continuation was added.

## Implementation

Native OptiX changes:

- `RtdlNativeDeviceGroupedCountI64Columns` now carries
  `source_row_count_device_ptr` and `overflow_device_ptr`.
- The generic grouped-count route retains device allocations for source row
  count and overflow status inside the output owner.
- The prepared segment-pair dense count route retains device allocations for
  candidate event count and overflow status inside the output owner.

Python runtime changes:

- `OptixNativeDeviceGroupedCountI64Output` exposes
  `source_row_count_device_ptr` and `overflow_device_ptr`.
- The runtime can wrap those status columns with
  `as_cupy_source_row_count()` and `as_cupy_overflow_status()`.
- `to_metadata()` records whether both status pointers are present while still
  marking the small host reads as metadata-only validation.

Runner/test changes:

- The A5000 conformance runner reads the two status columns through CuPy for
  validation.
- The residency contract now receives `overflow_device_ptr` and reports two
  resident columns instead of one.

## Artifact

Machine artifact:

- `docs/reports/goal3633_segment_pair_status_device_columns_a5000/summary.json`

The refreshed Goal3631 artifact mirrors the same pod output:

- `docs/reports/goal3631_segment_pair_backend_conformance_a5000/summary.json`

Pod source state:

- source commit: `4a537484`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)
- raw pod status had unrelated untracked scratch data, disclosed in the JSON artifact.

## Results

All same-contract counts still match Python/CuPy references and the new status
device columns are valid in every case.

| Case | Pair Count | OptiX Hits | Source Status | Overflow Status | Status Valid | Resident Columns | Full Residency |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| adversarial | 49 | 23 | 23 | 0 | yes | 2 | no |
| crossing_grid_64 | 4,096 | 4,096 | 4,096 | 0 | yes | 2 | no |
| crossing_grid_256 | 65,536 | 65,536 | 65,536 | 0 | yes | 2 | no |
| crossing_grid_1024 | 1,048,576 | 1,048,576 | 1,048,576 | 0 | yes | 2 | no |

The `source_row_count_from_device_status` value is the backend-produced
candidate-event count. For these strict-v0 crossing-grid cases it equals the
hit count by construction; for the adversarial case the validated strict output
also matches the expected hit total.

## Boundary

This is an incremental residency hardening step, not a release or speedup claim.
The current contract is still intentionally bounded:

- `all_columns_device_resident`: `false`
- `fallback_required`: `true`
- `ambiguous_count` remains the explicit host-reference fallback
- `true_zero_copy_authorized`: `false`
- `public_speedup_claim_authorized`: `false`
- `release_authorized`: `false`

In short, this is not complete multi-column residency.

The larger design question is whether ambiguity classification should be
computed by the fast traversal route or by a separate generic post-pass. That is
deferred because adding it directly into the RT path could slow the useful count
route and would be a separate primitive-design decision.
