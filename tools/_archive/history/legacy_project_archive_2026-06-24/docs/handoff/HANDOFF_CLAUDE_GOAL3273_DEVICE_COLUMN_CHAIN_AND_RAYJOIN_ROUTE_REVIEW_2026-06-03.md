# Handoff: Claude Review For Goal3269 / Goal3271 / Goal3272

Date: 2026-06-03

Requested output:

- `docs/reviews/goal3273_claude_review_goal3269_3271_3272_device_column_chain_2026-06-03.md`

## Context

Please perform an independent read-only review of the recent device-column chain:

- Goal3269: generic prepared closed-shape membership candidate device columns.
- Goal3271: generic closed-shape membership point-ID grouped-count device columns.
- Goal3272: experimental RayJoin PIP route that uses the point-ID count columns.

This is v2.8/v3.0-roadmap engineering work, not a release authorization packet.
Do not authorize release, public speedup claims, RayJoin reproduction claims,
RTDL-beats-RayJoin claims, broad RT-core claims, or true-zero-copy claims.

## Files To Inspect

Primary reports and evidence:

- `docs/reports/goal3269_closed_shape_membership_candidate_device_columns_2026-06-03.md`
- `docs/reports/goal3269_pod_closed_shape_candidate_device_columns_smoke_2026-06-03.json`
- `docs/reports/goal3271_closed_shape_membership_point_id_count_device_columns_2026-06-03.md`
- `docs/reports/goal3271_pod_closed_shape_point_id_count_device_columns_smoke_2026-06-03.json`
- `docs/reports/goal3272_rayjoin_point_id_count_route_probe_2026-06-03.md`
- `docs/reports/goal3272_pod/device_filtered_validated_same_slice.json`
- `docs/reports/goal3272_pod/point_id_count_device_columns_same_slice.json`

Implementation:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_8_geometry_relation_typed_stream.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`

Tests:

- `tests/goal3269_closed_shape_membership_candidate_device_columns_test.py`
- `tests/goal3271_closed_shape_membership_point_id_count_device_columns_test.py`
- `tests/goal3272_rayjoin_point_id_count_route_probe_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`

Suggested validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3269_closed_shape_membership_candidate_device_columns_test tests.goal3271_closed_shape_membership_point_id_count_device_columns_test tests.goal3272_rayjoin_point_id_count_route_probe_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

## Review Questions

1. Are the new native ABIs generic and app-agnostic, or did RayJoin/PIP-specific
   logic leak into the engine?
2. Does the Python layer preserve the app boundary correctly: app logic in the
   benchmark app, generic typed device-column contracts in runtime/support code?
3. Does Goal3272 honestly report that point-ID grouped count is correct and
   useful, but not the fastest scalar-count RayJoin PIP route?
4. Are the pod artifacts sufficient for this narrow route/provenance claim?
5. Do all claim boundaries remain blocked: release, public speedup,
   RayJoin-paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, and
   true zero-copy?
6. What should the next engineering target be: keep scalar PIP on
   `device_filtered_validated`, or add a per-point downstream consumer where
   the point-ID count columns are actually needed?

Allowed verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`,
or `reject`.

