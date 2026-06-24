# Goal3631 Segment-Pair Backend Conformance on RTX A5000

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3631 converts the Goal3625-Goal3629 segment-pair contract chain into pod-backed backend evidence. The tested primitive is the candidate generic `segment_pair_left_id_dense_count` route:

- strict v0 segment-pair predicate: non-collinear, endpoint-inclusive intersection with absolute denominator epsilon `1e-7`;
- dense grouped count keyed by left segment id/index;
- RTDL/OptiX prepared right-side segment scene;
- OptiX-produced dense count column exposed as a device-resident `int64` column;
- validation download only for comparing the device output against Python and CuPy references.

This is deliberately app-free. It does not mention RayJoin semantics in the primitive contract and does not use RayJoin data loaders.

## Artifact

Machine artifact:

- `docs/reports/goal3631_segment_pair_backend_conformance_a5000/summary.json`

Pod source state:

- source commit: `4a537484`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)
- raw pod status had unrelated untracked scratch data, disclosed in the JSON artifact.

Note: the artifact was refreshed after Goal3633 so this Goal3631 conformance
packet now also records the strengthened status-column residency evidence. The
primitive contract and tested cases did not change.

## Results

All tested routes produced identical same-contract left-id dense counts.

| Case | Pair Count | Reference Hits | CuPy Hits | OptiX Dense Hits | Match |
| --- | ---: | ---: | ---: | ---: | --- |
| adversarial | 49 | 23 | 23 | 23 | yes |
| crossing_grid_64 | 4,096 | 4,096 | 4,096 | 4,096 | yes |
| crossing_grid_256 | 65,536 | 65,536 | 65,536 | 65,536 | yes |
| crossing_grid_1024 | 1,048,576 | 1,048,576 | 1,048,576 | 1,048,576 | yes |

The adversarial case includes proper crossings, endpoint touches, outside-bound pairs, parallel pairs, collinear overlap, near-parallel excluded pairs, and a degenerate segment. The grid cases are analytic all-crossing cases used to scale the conformance check.

## Diagnostic Timings

These are diagnostics, not public performance claims. The OptiX dense route wall time includes validation wrapping/synchronization/download. The native `reduction_seconds` value is the backend-reported dense count phase.

| Case | CuPy Kernel Sec | CuPy Validation Reduce/Download Sec | OptiX Dense Wall Sec | OptiX Native Reduction Sec |
| --- | ---: | ---: | ---: | ---: |
| adversarial | 0.031514 | 0.024725 | 0.058562 | 0.000054 |
| crossing_grid_64 | 0.000046 | 0.000165 | 0.000434 | 0.000131 |
| crossing_grid_256 | 0.000040 | 0.005916 | 0.000899 | 0.000438 |
| crossing_grid_1024 | 0.000206 | 0.005952 | 0.002885 | 0.001609 |

## Residency Boundary

The OptiX dense-count route returns a device-resident count column and now
retains device-resident status pointers for source/candidate-event count and
overflow:

- `native_symbol`: `rtdl_optix_prepared_segment_pair_left_id_count_device_columns`
- `device_resident`: `true`
- `counts_device_ptr_nonzero`: `true`
- `source_row_count_device_ptr_nonzero`: `true`
- `overflow_device_ptr_nonzero`: `true`
- `overflow`: `false`
- `status_device_columns_valid`: `true`

The broader typed-output residency contract remains bounded. The count and
overflow-status columns are device-resident after the Goal3633 refresh, but the
current contract descriptor still records fallback for the separate
ambiguous-count column. Therefore this packet proves backend conformance plus
partial status-column residency, not complete multi-column residency.

After the Goal3633 refresh, the contract records two resident columns: the dense
count column and the overflow-status column. The ambiguity counter remains the
explicit host-reference fallback, so this is still not complete multi-column
residency.

## Claim Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- making this route the native default.

The validation copy is intentionally marked `validation_download_only`.
