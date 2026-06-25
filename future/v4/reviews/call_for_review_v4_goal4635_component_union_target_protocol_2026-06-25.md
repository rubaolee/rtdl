# Call For Review: V4 Goal4635 Component-Union Target Protocol

Date: 2026-06-25

Requested verdict labels:

- `approve_goal4635_component_union_target_and_pod_gate`
- `approve_with_required_amendments`
- `reject_target_selection_choose_different_operator`
- `blocked_review_unavailable`

## Context

Goal4634 completed the post-weighted-sum coverage refresh:

- strong measured: `2`
- partial measured: `5`
- candidate: `0`
- deferred: `3`

Goal4635 must move one remaining coverage blocker using a generic V4 operator,
not an app-specific kernel.

## Proposed Goal4635 Target

- target coverage row: `rt_dbscan`
- generic operator: `fixed_radius_graph_component_union_3d`
- proposed API surface: `v4_fixed_radius_graph_component_union_3d_device_arrays`
- generic primitive: `FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D`
- continuation class: `component_union`
- explicit partner scope: `numba`
- current status: predeclared target only, pending POD gate, not measured.

## Files To Review

- `future/v4/v4_goal4635_component_union_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4635_component_union_target.py`
- `tests/v4_goal4635_component_union_target_test.py`
- `src/rtdsl/v4_coverage_audit.py`
- `scripts/v3_phoenix_component_union_m38_pod_ab.py`
- `tests/v3_phoenix_m39_component_union_harness_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

## Local Evidence So Far

Passed:

- Goal4635 target tests: `Ran 5 tests` / `OK`
- V4 focused gate with Goal4635 included: `Ran 28 tests` / `OK`
- Component-union harness/session tests: `Ran 48 tests` / `OK`
- Broader V4 gate with Goal4635 included: `Ran 79 tests` / `OK`
- local no-hardware dry-run:
  `component_union_m39_harness_ready_not_pod_run`, 3 variants, 0 failed checks.

The target has not been promoted and has not run the serious POD gate yet.

## Specific Questions

1. Is `fixed_radius_graph_component_union_3d` a valid generic V4 operator target
   for Goal4635, or is it too app-specific because it targets `rt_dbscan`?
2. Is explicit `numba` partner scope acceptable for this target, given current
   V4 measured surfaces are mostly Torch CUDA?
3. Are the promotion thresholds strong enough:
   - runner vs Embree hot `>=1.20x`;
   - runner vs Embree wall `>=1.20x`;
   - runner vs legacy wall `>=0.98x`;
   - component labels required;
   - component signature substitution forbidden;
   - runtime trunk end-to-end required;
   - hot-path host materialization forbidden?
4. Is it correct that this target-selection step does not add a measured catalog
   surface before POD evidence?
5. If approved, may Codex run the POD gate with `--require-rt-hardware` next?

## Required Non-Authorization

This review must not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-app RTDBSCAN speedup;
- all-benchmark speedup;
- measured catalog promotion before POD results;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- DBSCAN-native or other app-specific kernels.
