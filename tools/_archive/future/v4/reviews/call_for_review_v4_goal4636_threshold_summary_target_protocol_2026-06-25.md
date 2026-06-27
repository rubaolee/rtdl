# Call For Review: V4 Goal4636 Threshold-Summary Target Protocol

Date: 2026-06-25

Requested verdict labels:

- `approve_goal4636_threshold_summary_target_and_pod_gate`
- `approve_with_required_amendments`
- `reject_target_selection_choose_different_operator`
- `blocked_review_unavailable`

## Context

Goal4633 promoted weighted-sum after a bounded POD gate. Goal4634 refreshed the
coverage audit. Goal4635 moved `rt_dbscan` to strong measured operator coverage
with a Numba-scoped generic component-union gate, while preserving external
review debt.

Goal4636 must prove Goal4635 was not a one-off. It must target a second
coverage blocker with a different generic continuation class, without adding an
app-specific kernel or moving CuPy validation ahead of Goal4637.

## Proposed Goal4636 Target

- target coverage row: `hausdorff_xhd`
- generic operator: `fixed_radius_threshold_summary_2d`
- proposed API surface: `v4_fixed_radius_threshold_summary_2d_prepared_runner`
- generic primitive: `FIXED_RADIUS_THRESHOLD_REACHED_COUNT_2D`
- continuation class: `threshold_summary`
- explicit scope: `rtdl_native_prepared_runner`
- current status: predeclared target only, pending POD gate, not measured.

## Files To Review

- `future/v4/v4_goal4636_threshold_summary_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4636_threshold_summary_target.py`
- `tests/v4_goal4636_threshold_summary_target_test.py`
- `src/rtdsl/v4_coverage_audit.py`
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`
- `tests/v3_phoenix_hausdorff_threshold_runner_pod_ab_test.py`
- `tests/v3_phoenix_hausdorff_prepared_execution_runner_wiring_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

## Local Evidence So Far

This is a target-selection review. No measured promotion is claimed yet.

Expected local validation before POD:

- Goal4636 target tests pass;
- Hausdorff runner/wiring tests pass;
- prepared execution session runner tests pass;
- local dry-run, if used, is treated only as command-shape evidence.

## Proposed POD Gate

Command shape:

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

Promotion floors:

- runner vs Embree phase-total `>= 1.20x`;
- runner vs Embree wrapper-wall `>= 1.20x`;
- runner vs legacy phase-total `>= 0.98x`;
- runner vs legacy wrapper-wall `>= 0.98x`;
- all variants match oracle;
- both directed legs execute through the runtime trunk;
- threshold rows are not materialized on host;
- Step-3 residency audit is ready.

## Specific Questions

1. Is `fixed_radius_threshold_summary_2d` a valid generic V4 operator target for
   Goal4636, or is it too tied to the Hausdorff/XHD benchmark row?
2. Is explicit `rtdl_native_prepared_runner` scope acceptable as a measured
   V4 operator-coverage expansion, given that this target is not a Torch/CuPy
   device-array front door?
3. Are the promotion thresholds strong enough to count as material coverage
   expansion rather than trivial parity?
4. Is it correct that this target-selection step does not add a measured catalog
   surface before POD evidence?
5. If approved, may Codex run the POD gate with `--require-rt-hardware` next?

## Required Non-Authorization

This review must not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-Hausdorff speedup;
- all-benchmark speedup;
- measured catalog promotion before POD results;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- Hausdorff-native or other app-specific kernels.
