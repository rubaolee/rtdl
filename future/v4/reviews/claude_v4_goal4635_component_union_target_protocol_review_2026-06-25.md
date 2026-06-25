# Claude Review: V4 Goal4635 Component-Union Target Protocol

Date: 2026-06-25

Reviewer: Claude

Verdict: `approve_goal4635_component_union_target_and_pod_gate`

## Reviewed Files

- `future/v4/v4_goal4635_component_union_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4635_component_union_target.py`
- `tests/v4_goal4635_component_union_target_test.py`
- `src/rtdsl/v4_coverage_audit.py`
- `scripts/v3_phoenix_component_union_m38_pod_ab.py`
- `tests/v3_phoenix_m39_component_union_harness_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

## Findings

1. `fixed_radius_graph_component_union_3d` is a valid generic operator target.
   `rt_dbscan` is the coverage row being addressed, not app identity inside the
   operator.
2. Explicit Numba partner scope is acceptable for this target. The caveat is
   that this does not extend existing Torch CUDA measured coverage; it would be
   a Numba Tier-2 surface.
3. Promotion thresholds are strong enough:
   - runner vs Embree hot `>= 1.20x`;
   - runner vs Embree wall `>= 1.20x`;
   - runner vs legacy wall `>= 0.98x`;
   - component labels required;
   - signature substitution forbidden;
   - runtime trunk end-to-end required.
4. Target selection does not add a measured catalog surface before POD evidence.
   This is enforced by code and tests.
5. Codex may run the POD gate with `--require-rt-hardware` next.

## Non-Blocking Documentation Gap

Claude noted that the protocol should list
`component_union_phase_accounting_visible` in required residency/metadata,
because the harness already enforces it. Codex applied this amendment to:

- `future/v4/v4_goal4635_component_union_operator_target_protocol_2026-06-25.md`

## Non-Authorization Confirmation

This review does not authorize:

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
