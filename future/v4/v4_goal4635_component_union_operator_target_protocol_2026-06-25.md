# V4 Goal4635 Component-Union Operator Target Protocol

Date: 2026-06-25

Status: `goal4635_component_union_target_predeclared_pending_pod_gate_not_measured`

## Purpose

Goal4635 expands measured V4 operator coverage by targeting one remaining
coverage blocker with a generic operator, not an app-specific kernel.

Selected target:

- coverage row: `rt_dbscan`
- generic operator: `fixed_radius_graph_component_union_3d`
- proposed API surface: `v4_fixed_radius_graph_component_union_3d_device_arrays`
- generic primitive: `FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D`
- continuation class: `component_union`
- partner scope for this target: `numba`

This target is selected because `rt_dbscan` is currently partial coverage:

- fixed-radius count-threshold is measured;
- component-union / component-label continuation is not yet a V4 measured
  operator surface.

## Why This Is On The V4 Route

Allowed:

- a generic fixed-radius graph component-label continuation;
- RT-core fixed-radius traversal feeding a generic component-union continuation;
- Numba as an explicit Python GPU ecosystem partner for this target.

Forbidden:

- a DBSCAN-native kernel;
- DBSCAN app-identity semantics inside the engine;
- component-size signature substitution when the gate requires component labels;
- public whole-app DBSCAN speedup wording.

## Machine-Readable Target

Code:

- `src/rtdsl/v4_goal4635_component_union_target.py`

Tests:

- `tests/v4_goal4635_component_union_target_test.py`
- `tests/v3_phoenix_m39_component_union_harness_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

The target validation must prove:

- selected row is `rt_dbscan`;
- continuation class is `component_union`;
- partner scope is explicitly `numba`;
- POD gate is required before measured catalog promotion;
- V4 catalog is not promoted by this target-selection step.

## Local Pre-POD Validation

Completed on 2026-06-25:

- `py -m unittest tests.v4_goal4635_component_union_target_test`
  - `Ran 5 tests`
  - `OK`
- `py -m unittest tests.v4_goal4627_coverage_audit_test tests.v4_goal4632_release_decision_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_goal4635_component_union_target_test`
  - `Ran 28 tests`
  - `OK`
- `py -m unittest tests.v3_phoenix_m39_component_union_harness_test tests.v3_phoenix_prepared_execution_session_runner_test`
  - `Ran 48 tests`
  - `OK`
- Local dry-run without RT hardware requirement:
  `py scripts/v3_phoenix_component_union_m38_pod_ab.py --dry-run --output-dir future/v4/evidence/v4_goal4635_component_union_dry_run_no_hw_gate_2026-06-25`
  - status: `component_union_m39_harness_ready_not_pod_run`
  - variants: `3`
  - failed checks: `0`

Also checked:

- Local dry-run with `--require-rt-hardware` failed closed on the non-POD host
  before producing performance interpretation. This is expected; the real POD
  gate must run with `--require-rt-hardware`.

## Promotion Gate

The existing harness to adapt for the Goal4635 POD gate is:

- `scripts/v3_phoenix_component_union_m38_pod_ab.py`

Required shape:

- dataset: `clustered3d`;
- point count floor: `262144`;
- repeats: `5`;
- warmup: `1`;
- RT hardware required.

Required correctness:

- Embree, legacy OptiX grouped-stream, and productized runner outputs must have
  matching canonical component signatures;
- runner must emit component labels, not substitute component-size signatures;
- component-union phase accounting must be visible.

Required performance:

- runner vs Embree hot speedup: `>= 1.20x`;
- runner vs Embree wall speedup: `>= 1.20x`;
- runner vs legacy wall no-regression: `>= 0.98x`.

Required residency/metadata:

- `runtime_trunk_executes_end_to_end: true`;
- `component_union_phase_accounting_visible: true`;
- `component_label_columns_present: true`;
- `component_signature_pass_executed: false`;
- `hot_path_host_materialization: false`.

## Promotion Outcomes

If the gate passes:

- promote `v4_fixed_radius_graph_component_union_3d_device_arrays` as a
  measured Numba V4 Tier-2 operator surface;
- move `rt_dbscan` coverage from partial to strong measured operator coverage;
- keep whole-app DBSCAN speedup unauthorized until the formal release
  scorecard/all-app gate.

If the gate fails:

- keep `rt_dbscan` partial;
- record the failure reason;
- do not add a measured surface;
- select another Goal4635/4636 target only after recording why this one failed.

## Goal-Level Decision Audit

Decision: choose component union as Goal4635's first generic coverage expansion
target.

1. Was this decision stupid?
   - No. It attacks a real coverage blocker (`rt_dbscan`) with a generic
     continuation already present in the runtime assets.
2. If it were stupid, what action made it stupid?
   - It would be stupid if we counted old V3 row-scoped evidence as a V4
     measured surface without a V4 predeclared gate, or if we hid the Numba
     partner scope. This protocol forbids both.
3. Is there another path that avoids being stuck on this thought?
   - Yes: if component union fails, keep `rt_dbscan` partial and select the
     next generic target such as ranked/top-k or AABB/relation prefilter with a
     fresh protocol.
4. Can work start on a different path that truly solves the problem?
   - Yes, but only after this gate fails or is rejected. Running multiple
     operator promotions at once would recreate process churn and confuse the
     release scorecard.

## Non-Authorization

Goal4635 target selection does not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-app DBSCAN speedup;
- all-benchmark speedup;
- measured catalog promotion;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- DBSCAN-native or other app-specific kernels.
