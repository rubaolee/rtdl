# Call For Review: V4 Goal4636B Grouped Any-Hit Target Protocol

Date: 2026-06-25

Requested verdict labels:

- `approve_goal4636b_grouped_any_hit_target_and_pod_gate`
- `approve_with_required_amendments`
- `reject_target_selection_choose_different_operator`
- `blocked_review_unavailable`

## Context

Goal4636's first target, `fixed_radius_threshold_summary_2d`, ran a serious
POD gate and failed the predeclared legacy phase-total no-regression floor:

- runner vs Embree phase-total: `1.2759701868849942x`;
- runner vs Embree wrapper-wall: `1.7376484711304498x`;
- runner vs legacy phase-total: `0.9693326333237459x`;
- failed check: `runner_regressed_vs_legacy_phase_total`.

That target was rejected and not promoted.

Goal4636 now needs a second predeclared generic operator target.

## Proposed Goal4636B Target

- target coverage row: `robot_collision`
- generic operator: `ray_triangle_grouped_any_hit_flags_3d`
- proposed API surface: `v4_ray_triangle_grouped_any_hit_flags_3d_prepared_runner`
- generic primitive: `RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D`
- continuation class: `grouped_any_hit_flag_stream`
- explicit scope: `rtdl_native_prepared_runner`
- current status: predeclared target only, pending POD gate, not measured.

## Files To Review

- `future/v4/v4_goal4636b_grouped_any_hit_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4636_grouped_any_hit_target.py`
- `tests/v4_goal4636_grouped_any_hit_target_test.py`
- `src/rtdsl/v4_coverage_audit.py`
- `scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py`
- `examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`
- `src/rtdsl/generic_primitives.py`
- `tests/v3_phoenix_robot_collision_no_probe_paired_script_test.py`
- `tests/goal953_robot_native_continuation_metadata_test.py`

Do not treat historical `goal2482` / `goal2483` report/review-file tests as
current Goal4636B evidence. They are pre-V4 historical tests and currently fail
on missing archived report/review files plus old source-vocabulary assumptions.

## Proposed POD Gate

Command shape:

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py \
  --output-dir future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25 \
  --dataset scaled \
  --pose-count 8192 \
  --obstacle-count 2048 \
  --link-count 2 \
  --sample-count 5 \
  --timed-repeats 101 \
  --timed-warmup 5 \
  --validation-repeats 5 \
  --validation-warmup 1 \
  --heartbeat-sec 30 \
  --timeout-sec 1800
```

Promotion floors:

- validation status: `pass`;
- timed status: `pass`;
- same contract/shape/signature/counts for all timed pairs;
- validation/timed signatures overlap;
- timed rows have probe reference disabled;
- mean no-probe tail-total Embree/OptiX `>= 3.0x`;
- mean traversal Embree/OptiX `>= 3.0x`;
- mean no-probe wrapper Embree/OptiX `>= 1.10x`;
- weakest no-probe wrapper Embree/OptiX `>= 1.00x`.

## Specific Questions

1. Is `ray_triangle_grouped_any_hit_flags_3d` a valid generic V4 operator target
   for `robot_collision`, or is it too app-specific?
2. Are the proposed floors material enough, especially given the wrapper floor
   is lower than the tail/traversal floors?
3. Is it acceptable that this target uses native prepared-runner scope, provided
   any catalog promotion later resolves the same catalog-scope issue raised for
   Goal4636 threshold-summary?
4. Is it correct that this target-selection step does not add a measured catalog
   surface before POD evidence?
5. If approved, may Codex run the POD gate next?

## Required Non-Authorization

This review must not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole robot-planning speedup;
- continuous collision support;
- exact solid-collision claims;
- all-benchmark speedup;
- measured catalog promotion before POD results;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- robot-collision-native or other app-specific kernels.
