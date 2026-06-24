# Handoff: Claude Review For Goals3266-3269 RayJoin PIP Chain

Please perform a read-only independent review and write the result to:

`docs/reviews/goal3270_claude_review_goal3266_3269_rayjoin_device_column_chain_2026-06-03.md`

## Context

The current `main` head is `a54488bc`.

This chain follows the RayJoin PIP tuning work:

- Goal3266: crossing-only boundary mode negative probe.
- Goal3267: crossing-scale SoA / compile-time specialization negative probe, then reverted.
- Goal3269: generic closed-shape membership candidate device-column producer.

The current best accepted live PIP count path remains the validated device-filtered closed-shape membership count path from the Goal3264/3266 family. Goal3269 is not claimed as the new fastest app route; it is substrate for the next device-side continuation step.

## Files To Inspect

Core Goal3269 files:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_8_geometry_relation_typed_stream.py`
- `tests/goal3269_closed_shape_membership_candidate_device_columns_test.py`
- `docs/reports/goal3269_closed_shape_membership_candidate_device_columns_2026-06-03.md`
- `docs/reports/goal3269_pod_closed_shape_candidate_device_columns_smoke_2026-06-03.json`

Prior probe context:

- `docs/reports/goal3266_crossing_only_boundary_negative_probe_2026-06-03.md`
- `docs/reports/goal3266_crossing_only_boundary_negative_probe_pod_2026-06-03.json`
- `docs/reports/goal3266_inclusive_boundary_control_z_point_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3267_crossing_scale_soa_negative_probe_2026-06-03.md`
- `docs/reports/goal3267_default_compiletime_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3267_crossing_scale_soa_compiletime_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3267_reverted_control_same_slice_pod_2026-06-03.json`
- `tests/goal3266_crossing_only_boundary_negative_pod_test.py`
- `tests/goal3267_crossing_scale_soa_negative_probe_test.py`

## Review Questions

1. Does Goal3269 keep the native engine app-agnostic, or does it accidentally introduce RayJoin-specific native logic?
2. Is reusing `RtdlNativeDevicePairColumns` for point/shape candidate IDs acceptable, with typed metadata distinguishing `point_id` and `shape_id`?
3. Does the new native path truly write caller point IDs and shape IDs to device-resident columns, rather than wrapping host rows or launch-local indices?
4. Is the owner/release discipline sound enough for this substrate step?
5. Are the claim boundaries honest: no release claim, no true zero-copy claim, no public speedup claim, no RayJoin paper-reproduction claim?
6. Is the next engineering target correctly identified as a generic device-side continuation over the candidate columns?

## Validation To Run If Possible

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3269_closed_shape_membership_candidate_device_columns_test `
  tests.goal3266_crossing_only_boundary_mode_probe_test `
  tests.goal3267_crossing_scale_soa_negative_probe_test
```

Expected: 13 tests pass.

## Required Review Shape

Use one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Lead with findings by severity. State clearly whether Goal3269 is accepted as substrate only, not as a RayJoin performance win.
