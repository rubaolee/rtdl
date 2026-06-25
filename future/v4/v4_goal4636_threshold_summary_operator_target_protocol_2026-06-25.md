# V4 Goal4636 Threshold-Summary Operator Target Protocol

Date: 2026-06-25

Status: `goal4636_threshold_summary_target_predeclared_pending_pod_gate_not_measured`

## Purpose

Goal4636 must prove that Goal4635 was not a one-off. It targets a second
coverage blocker with a different generic continuation class, while preserving
the same rule: generic operator/runtime work is allowed; app-identity kernels
are forbidden.

Selected target:

- coverage row: `hausdorff_xhd`
- generic operator: `fixed_radius_threshold_summary_2d`
- proposed API surface: `v4_fixed_radius_threshold_summary_2d_prepared_runner`
- generic primitive: `FIXED_RADIUS_THRESHOLD_REACHED_COUNT_2D`
- continuation class: `threshold_summary`
- execution scope: `rtdl_native_prepared_runner`

This target is selected because `hausdorff_xhd` is currently partial coverage:

- nearest-witness and count-threshold adjacent surfaces exist;
- the directed Hausdorff/XHD threshold workflow is not yet a reviewed V4
  release-scorecard row;
- it can be measured without pulling CuPy validation forward from Goal4637.

## Why This Is On The V4 Route

Allowed:

- a generic fixed-radius threshold-reached scalar summary;
- two directed threshold-summary legs through the productized prepared runner;
- runtime/residency telemetry as first-class evidence;
- same-contract comparison against Embree and legacy app-front-door OptiX.

Forbidden:

- a Hausdorff-native kernel;
- any app-identity semantics inside the engine;
- treating the existing fixed-radius count-threshold surface as sufficient
  without a serious Hausdorff/XHD workflow gate;
- public whole-Hausdorff or broad V4 speedup wording.

## Machine-Readable Target

Code:

- `src/rtdsl/v4_goal4636_threshold_summary_target.py`

Tests:

- `tests/v4_goal4636_threshold_summary_target_test.py`
- `tests/v3_phoenix_hausdorff_threshold_runner_pod_ab_test.py`
- `tests/v3_phoenix_hausdorff_prepared_execution_runner_wiring_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

The target validation must prove:

- selected row is `hausdorff_xhd`;
- continuation class is `threshold_summary`;
- scope is explicitly `rtdl_native_prepared_runner`;
- POD gate is required before measured catalog promotion;
- V4 catalog is not promoted by this target-selection step.

## Local Pre-POD Validation

Completed on 2026-06-25:

- `py -m unittest tests.v4_goal4636_threshold_summary_target_test`
  - `Ran 5 tests`
  - `OK`
- `py -m unittest tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test`
  - `Ran 7 tests`
  - `OK`
- `py -m unittest tests.v3_phoenix_prepared_execution_session_runner_test`
  - rerun with `PYTHONPATH=src:.`
  - `Ran 42 tests`
  - `OK`

Local no-hardware dry-run:

- `py scripts\v3_phoenix_hausdorff_threshold_runner_pod_ab.py --dry-run --output-dir future\v4\evidence\v4_goal4636_threshold_summary_dry_run_no_hw_gate_2026-06-25 --copies 262144 --threshold 0.4 --repeat 5 --warmup 1`
  - variants: `3`
  - points per side: `1048576`
  - failed checks: `[]`

Local non-GPU dry runs are allowed only as command-shape checks. They do not
count as performance evidence.

## External Review Before POD

Claude returned verdict `approve_with_required_amendments` in:

- `future/v4/reviews/claude_v4_goal4636_threshold_summary_target_protocol_review_2026-06-25.raw.md`

Required amendments:

1. Before any post-POD catalog promotion, define how
   `rtdl_native_prepared_runner` is represented in the catalog without
   confusing it with framework partners such as Torch/CuPy/Numba.
2. Before or alongside the POD run, make the runner's `failed_checks` enforce
   the declared `runner_vs_embree >= 1.20x` material floor.

Amendment 2 has been applied before POD:

- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py` now enforces:
  - `runner_below_embree_phase_total_material_floor`;
  - `runner_below_embree_wrapper_wall_material_floor`.
- `tests/v3_phoenix_hausdorff_threshold_runner_pod_ab_test.py` now verifies
  that a `1.19x` Embree comparison fails the gate.

Post-amendment tests:

- `py -m unittest tests.v4_goal4636_threshold_summary_target_test`
  - `Ran 5 tests` / `OK`
- `py -m unittest tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test`
  - `Ran 8 tests` / `OK`
- `$env:PYTHONPATH='src;.'; py -m unittest tests.v3_phoenix_prepared_execution_session_runner_test`
  - `Ran 42 tests` / `OK`

Antigravity returned empty stdout/stderr and is recorded as review debt, not as
a substantive review.

## Promotion Gate

The existing focused harness for the Goal4636 POD gate is:

- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`

Required command shape:

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py \
  --output-dir future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25 \
  --copies 262144 \
  --threshold 0.4 \
  --repeat 5 \
  --warmup 1 \
  --heartbeat-sec 30 \
  --timeout-sec 7200 \
  --require-rt-hardware
```

Required shape:

- copies: `262144`;
- points per side: `1048576`;
- threshold: `0.4`;
- repeats: `5`;
- warmup: `1`;
- RT hardware required.

Required correctness:

- Embree, legacy OptiX, and productized runner variants must execute;
- every variant must match the same oracle decision;
- both directed legs must report runtime execution;
- threshold rows must not be materialized on the hot path.

Required performance:

- runner vs Embree phase-total speedup: `>= 1.20x`;
- runner vs Embree wrapper-wall speedup: `>= 1.20x`;
- runner vs legacy phase-total no-regression: `>= 0.98x`;
- runner vs legacy wrapper-wall no-regression: `>= 0.98x`.

Required residency/metadata:

- `runner_metadata.used: true`;
- `both_directed_legs_runtime_executed: true`;
- `both_directed_legs_runtime_trunk_end_to_end: true`;
- `both_directed_legs_no_threshold_rows_materialized_on_host: true`;
- `both_directed_legs_internal_device_residency_between_rtdl_phases: true`;
- Step-3 audit ready for both directed legs.

## Promotion Outcomes

If the gate passes:

- promote `fixed_radius_threshold_summary_2d` as a measured V4 Tier-2 operator
  surface under the explicit native prepared-runner scope;
- move `hausdorff_xhd` coverage from partial to strong measured operator
  coverage;
- keep whole-Hausdorff and broad V4 speedup wording unauthorized until the
  formal release scorecard/all-app gate.

If the gate fails:

- keep `hausdorff_xhd` partial;
- record the failure reason;
- do not add a measured surface;
- continue Goal4636 only by selecting another generic target with a fresh
  predeclared protocol.

## Goal-Level Decision Audit

Decision: choose threshold summary as Goal4636's second generic coverage
expansion target.

1. Was this decision stupid?
   - No. It targets a real partial row with a different generic continuation
     class from Goal4635, and it avoids mixing Goal4636 with CuPy validation.
2. If it were stupid, what action made it stupid?
   - It would be stupid if we treated the existing fixed-radius count-threshold
     API as automatically covering the Hausdorff/XHD workflow, or if we counted
     old V3 row-scoped evidence as V4 release evidence. This protocol forbids
     both.
3. Is there another path that avoids being stuck on this thought?
   - Yes. If this gate fails, keep `hausdorff_xhd` partial and choose a
     different generic target, such as AABB/relation prefilter or ranked/top-k,
     with a new protocol.
4. Can work start on a different path that truly solves the problem?
   - Yes, but not by silently changing the metric after results. A different
     target must be predeclared before it is measured.

## Non-Authorization

Goal4636 target selection does not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-Hausdorff speedup;
- all-benchmark speedup;
- measured catalog promotion;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- Hausdorff-native or other app-specific kernels.
