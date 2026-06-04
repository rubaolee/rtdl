# Handoff: Claude Review For Goal3269-3276 RayJoin Probe Chain

Date: 2026-06-03

Requested output:

- `docs/reviews/goal3277_claude_review_rayjoin_probe_chain_and_scale_repair_2026-06-03.md`

## Context

Please perform an independent read-only review of the recent RayJoin-oriented,
app-agnostic primitive/probe chain:

- Goal3269: generic prepared closed-shape membership candidate device columns.
- Goal3271: generic closed-shape membership point-ID grouped-count device columns.
- Goal3272: experimental RayJoin PIP route using point-ID count columns.
- Goal3274: gated scalar-count OptiX pipeline probe.
- Goal3276: RayJoin scale-runner input-parity repair plus corrected 128/256/384/512 public-CDB scale diagnostic.

This is v2.8/v3.0-roadmap engineering evidence, not a release authorization
packet. Do not authorize release, public speedup claims, RayJoin paper
reproduction claims, RTDL-beats-RayJoin claims, broad RT-core claims, or true
zero-copy claims.

## Files To Inspect

Reports and pod evidence:

- `docs/reports/goal3269_closed_shape_membership_candidate_device_columns_2026-06-03.md`
- `docs/reports/goal3269_pod_closed_shape_candidate_device_columns_smoke_2026-06-03.json`
- `docs/reports/goal3271_closed_shape_membership_point_id_count_device_columns_2026-06-03.md`
- `docs/reports/goal3271_pod_closed_shape_point_id_count_device_columns_smoke_2026-06-03.json`
- `docs/reports/goal3272_rayjoin_point_id_count_route_probe_2026-06-03.md`
- `docs/reports/goal3272_pod/device_filtered_validated_same_slice.json`
- `docs/reports/goal3272_pod/point_id_count_device_columns_same_slice.json`
- `docs/reports/goal3274_closed_shape_scalar_count_pipeline_probe_2026-06-03.md`
- `docs/reports/goal3274_pod/goal3274_default_control_same_slice.json`
- `docs/reports/goal3274_pod/goal3274_scalar_count_pipeline_same_slice.json`
- `docs/reports/goal3276_rayjoin_scale_runner_input_parity_repair_2026-06-03.md`
- `docs/reports/goal3276_scale_pod/slice_128.json`
- `docs/reports/goal3276_scale_pod/slice_256.json`
- `docs/reports/goal3276_scale_pod/slice_384.json`
- `docs/reports/goal3276_scale_pod/slice_512.json`

Implementation and tests:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_8_geometry_relation_typed_stream.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal3269_closed_shape_membership_candidate_device_columns_test.py`
- `tests/goal3271_closed_shape_membership_point_id_count_device_columns_test.py`
- `tests/goal3272_rayjoin_point_id_count_route_probe_test.py`
- `tests/goal3274_closed_shape_scalar_count_pipeline_probe_test.py`
- `tests/goal3276_rayjoin_scale_runner_input_parity_repair_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`

Suggested validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3269_closed_shape_membership_candidate_device_columns_test tests.goal3271_closed_shape_membership_point_id_count_device_columns_test tests.goal3272_rayjoin_point_id_count_route_probe_test tests.goal3274_closed_shape_scalar_count_pipeline_probe_test tests.goal3276_rayjoin_scale_runner_input_parity_repair_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

## Review Questions

1. Are the new native ABIs generic and app-agnostic, or did RayJoin/PIP-specific
   logic leak into the engine?
2. Does the Python layer preserve the app boundary correctly: app logic in the
   benchmark app, generic typed device-column contracts in runtime/support code?
3. Does Goal3272 honestly report that point-ID grouped count is correct and
   useful for downstream per-point consumers, but not the fastest scalar-count
   RayJoin PIP route?
4. Does Goal3274 honestly keep the scalar-count pipeline gated because evidence
   is neutral/negative, rather than promoting it?
5. Does Goal3276 genuinely repair RayJoin-vs-RTDL input parity for scale probes,
   and do the corrected artifacts support only an internal diagnostic claim?
6. Does the scale diagnostic support the conclusion that the next engineering
   target should be generic grouping/locality, not another scalar-count pipeline
   tweak?
7. Do all claim boundaries remain blocked: release, public speedup,
   RayJoin-paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, and
   true zero-copy?

Allowed verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
