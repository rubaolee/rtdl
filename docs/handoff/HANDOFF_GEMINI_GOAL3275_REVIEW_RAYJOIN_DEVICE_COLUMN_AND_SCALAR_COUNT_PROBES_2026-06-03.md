# Handoff: Gemini Review For Goals3269-3274

Date: 2026-06-03

Please perform an independent read-only review of the recent RayJoin-adjacent
generic device-column and scalar-count probes. Write the review to:

- `docs/reviews/goal3275_gemini_review_rayjoin_device_column_and_scalar_count_probes_2026-06-03.md`

## Scope

Review these goals:

- Goal3269: prepared point/closed-shape membership candidate device columns.
- Goal3271: point-ID grouped-count device columns.
- Goal3272: RayJoin PIP route using point-ID count columns; correct but not
  the fastest scalar-count route.
- Goal3274: gated scalar-count pipeline probe; correct, source-clean pod
  measured, but not promoted because the win is not clear and native count-pass
  timing is worse than default control.

## Key Files

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
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`

Suggested validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3269_closed_shape_membership_candidate_device_columns_test tests.goal3271_closed_shape_membership_point_id_count_device_columns_test tests.goal3272_rayjoin_point_id_count_route_probe_test tests.goal3274_closed_shape_scalar_count_pipeline_probe_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

## Review Questions

1. Are the native additions app-agnostic generic closed-shape/device-column
   primitives rather than RayJoin-specific engine logic?
2. Is the Goal3272 conclusion honest: point-ID grouped count is useful for
   downstream per-point consumers, but scalar PIP should keep the faster
   `device_filtered_validated` route?
3. Is the Goal3274 conclusion honest: the gated scalar-count pipeline is not
   promoted because the evidence is neutral/negative?
4. Are pod artifacts source-clean where claimed, count-preserving, and
   claim-boundary-clean?
5. What is the next best generic performance direction?

Allowed verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

