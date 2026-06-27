# Claude Review Handoff: Goal4039-4041 Route And Partition Evidence

Date: 2026-06-08

Please perform an independent read-only review of the recent Goal4039-4041 chain
and write your review to:

`docs/reviews/goal4042_claude_review_goal4039_4041_route_and_partition_evidence_2026-06-08.md`

## Context

The project is improving RTDL as a language/runtime for generic RT-core
primitive use plus user-selected partners. The native engine must remain
app-agnostic. Public/release claims remain tightly bounded.

Recent commits:

- `9faa6719` Goal4039 refresh RayJoin mixed route evidence.
- `1edd124b` Goal4040 add device ambiguous partition union.
- `42462c3e` Goal4040 skip empty ambiguous device union.
- `60267376` Goal4041 measure device ambiguous partition union.

## Files To Inspect

- `docs/reports/goal4039_rayjoin_representative_profile_fixed_numba_toolchain_2026-06-08.md`
- `docs/reports/goal4039_rayjoin_representative_profile_fixed_numba_toolchain_pod.json`
- `docs/reports/goal4040_partition_device_ambiguous_union_2026-06-08.md`
- `docs/reports/goal4041_partition_device_ambiguous_union_timing_2026-06-08.md`
- `docs/reports/goal4041_partition_device_ambiguous_union_timing_pod.json`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `scripts/goal4041_partition_device_ambiguous_union_timing.py`
- `tests/goal4039_rayjoin_representative_profile_fixed_numba_toolchain_test.py`
- `tests/goal4040_partition_device_ambiguous_union_test.py`
- `tests/goal4041_partition_device_ambiguous_union_timing_test.py`

## Review Questions

1. Does Goal4039 correctly separate RayJoin subroutes instead of overclaiming a
   single whole-app speedup? In particular, is Numba correctly recommended for
   one-shot PIP while RTDL/OptiX remains recommended for LSI scalar count and
   overlay active count?
2. Does Goal4040 keep the fixed-radius component path generic and
   app-agnostic while adding `partition_point_ordinals` and the
   `cupy_partition_points` ambiguous-union continuation?
3. Does Goal4041 correctly interpret the timing evidence: useful
   device-resident continuation, not a universal speed win and not a default
   promotion?
4. Are claim boundaries intact? The review should explicitly check that release,
   public speedup, broad RT-core, whole-app, hidden-dispatch, automatic partner
   selection, app-specific engine logic, native ABI addition, and true-zero-copy
   claims remain unauthorized.
5. What is the next best engineering target: fused resident component-label
   continuation, prepared/native partition handle, route-decision thresholding,
   or something else?

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal4039_rayjoin_representative_profile_fixed_numba_toolchain_test `
  tests.goal4041_partition_device_ambiguous_union_timing_test `
  tests.goal4040_partition_device_ambiguous_union_test `
  tests.goal4016_partition_convergence_typed_stream_contract_test `
  tests.goal4017_partition_summary_reference_builder_test `
  tests.goal4019_partition_summary_same_contract_validator_test `
  tests.goal4021_partition_convergence_component_reference_test `
  tests.goal4023_partition_summary_status_invariants_test `
  tests.goal4024_partition_summary_edge_case_strengthening_test `
  tests.goal4027_partition_summary_cupy_preview_test `
  tests.goal4029_partition_summary_numba_preview_test `
  tests.goal4035_partition_component_labels_cupy_preview_test
```

Use verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

