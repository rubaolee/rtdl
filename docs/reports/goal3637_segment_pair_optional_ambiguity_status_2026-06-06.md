# Goal3637 Optional Segment-Pair Ambiguity Status

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3637 adds an opt-in strict-audit route for the candidate generic
`segment_pair_left_id_dense_count` contract. The default hot path from Goal3633 stays unchanged. When the caller passes `include_ambiguity_status=True`, RTDL
returns a third device status pointer for the strict-v0 ambiguity count.

This separates two needs:

- hot route: count accepted segment-pair hits by left id with count plus overflow
  resident on device;
- strict audit route: additionally compute the ambiguity-status counter on
  device, so the full three-column status contract is resident.

The route remains app-agnostic. It does not add RayJoin-specific logic.

## Implementation

Native/ABI:

- `RtdlNativeDeviceGroupedCountI64Columns` now includes
  `ambiguous_count_device_ptr`.
- `rtdl_optix_prepared_segment_pair_left_id_count_device_columns` remains the
  default count/status route.
- `rtdl_optix_prepared_segment_pair_left_id_count_device_columns_with_ambiguity_status`
  is the optional strict-audit entry point.
- The optional entry point launches a generic CUDA post-pass over the resident
  left/right segment arrays to count strict-v0 ambiguous pairs:
  non-finite inputs or absolute denominator `< 1e-7`.

Python/runtime:

- `PreparedOptixSegmentPairIntersection.left_id_count_device_columns(...)` now
  accepts `include_ambiguity_status=False`.
- `OptixNativeDeviceGroupedCountI64Output` exposes
  `ambiguous_count_device_ptr` and `as_cupy_ambiguous_count()`.
- The conformance runner can pass `--include-ambiguity-status` to validate the
  optional route.

## Artifact

Machine artifact:

- `docs/reports/goal3637_segment_pair_ambiguity_status_a5000/summary.json`

Pod source state:

- source commit: `1eeff46c`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)

## Results

All same-contract counts matched, and the optional ambiguity status matched the
Python/analytic reference in every case.

| Case | Pair Count | OptiX Hits | Ambiguous Status | Reference Ambiguous | Ambiguity Valid | Resident Columns | Full Residency |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| adversarial | 49 | 23 | 19 | 19 | yes | 3 | yes |
| crossing_grid_1024 | 1,048,576 | 1,048,576 | 0 | 0 | yes | 3 | yes |
| crossing_grid_2048 | 4,194,304 | 4,194,304 | 0 | 0 | yes | 3 | yes |
| crossing_grid_4096 | 16,777,216 | 16,777,216 | 0 | 0 | yes | 3 | yes |

The residency contract now reports:

- `device_resident_column_count`: `3`
- `all_columns_device_resident`: `true`
- `fallback_required`: `false`

## Diagnostic Timings

These timings are diagnostic only. The optional ambiguity post-pass scans the
pair product and is intentionally not enabled on the default hot route.

| Case | CuPy Dense Kernel Sec | OptiX Optional Wall Sec | OptiX Native Reduction Sec |
| --- | ---: | ---: | ---: |
| adversarial | 0.032834 | 0.348543 | 0.287107 |
| crossing_grid_1024 | 0.000224 | 0.003118 | 0.001626 |
| crossing_grid_2048 | 0.000755 | 0.005641 | 0.003197 |
| crossing_grid_4096 | 0.002925 | 0.011330 | 0.006402 |

The adversarial timing includes first-use setup for the optional ambiguity
kernel inside the measured native window. The large-grid rows are the more
useful steady diagnostic signal, but none of these timings authorize public
speedup wording.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- making the optional strict-audit route the default.

The result is important but narrow: the full segment-pair status contract can
now be made device-resident when requested. The performance route remains the
Goal3633 count-plus-overflow mode unless a caller needs strict ambiguity status.
