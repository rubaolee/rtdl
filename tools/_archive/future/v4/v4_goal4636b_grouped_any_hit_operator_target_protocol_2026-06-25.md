# V4 Goal4636B Grouped Any-Hit Operator Target Protocol

Date: 2026-06-25

Status: `goal4636_grouped_any_hit_target_predeclared_pending_pod_gate_not_measured`

## Purpose

Goal4636's first candidate, `fixed_radius_threshold_summary_2d`, failed its
predeclared POD gate and was not promoted. Goal4636 therefore continues with a
second predeclared generic target.

Selected target:

- coverage row: `robot_collision`
- generic operator: `ray_triangle_grouped_any_hit_flags_3d`
- proposed API surface: `v4_ray_triangle_grouped_any_hit_flags_3d_prepared_runner`
- generic primitive: `RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D`
- continuation class: `grouped_any_hit_flag_stream`
- execution scope: `rtdl_native_prepared_runner`

This target is selected because `robot_collision` is currently partial coverage:

- generic ray/triangle any-hit flags exist;
- the grouped segment any-hit flag stream is not yet a measured V4 coverage
  surface;
- the target can be measured without CuPy, so it does not preempt Goal4637.

## Why This Is On The V4 Route

Allowed:

- prepared ray/triangle any-hit traversal;
- grouped any-hit flag reduction by query group;
- same-contract Embree vs OptiX timing with CPU probe-reference validation
  separated from no-probe performance timing.

Forbidden:

- a robot-collision-native kernel;
- full robot-planning or continuous-collision claims;
- exact solid-collision claims;
- public whole-app speedup wording;
- catalog promotion before POD evidence.

## Machine-Readable Target

Code:

- `src/rtdsl/v4_goal4636_grouped_any_hit_target.py`

Tests:

- `tests/v4_goal4636_grouped_any_hit_target_test.py`
- `tests/v3_phoenix_robot_collision_no_probe_paired_script_test.py`
- `tests/goal953_robot_native_continuation_metadata_test.py`
- historical `goal2482` / `goal2483` tests exist but are not used as current
  Goal4636B gates because they depend on old report/review files and pre-V4
  source-vocabulary assumptions.

The target validation must prove:

- selected row is `robot_collision`;
- continuation class is `grouped_any_hit_flag_stream`;
- scope is explicitly `rtdl_native_prepared_runner`;
- POD gate is required before measured catalog promotion;
- V4 catalog is not promoted by this target-selection step.

Local pre-POD validation completed:

- `py -m unittest tests.v4_goal4636_grouped_any_hit_target_test tests.v3_phoenix_robot_collision_no_probe_paired_script_test`
  - `Ran 7 tests`
  - `OK`
- `py -m unittest tests.goal953_robot_native_continuation_metadata_test`
  - `Ran 5 tests`
  - `OK`

## Promotion Gate

The focused harness for the Goal4636B POD gate is:

- `scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py`

Required command shape:

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

Required shape:

- dataset: `scaled`;
- pose count: `8192`;
- obstacle count: `2048`;
- link count: `2`;
- timed samples: `5`;
- timed repeats/warmup: `101` / `5`;
- validation repeats/warmup: `5` / `1`;
- RT hardware must be present by environment check.

Required correctness:

- validation status: `pass`;
- timed status: `pass`;
- all timed pairs same contract, shape, signature, and counts;
- validation and timed signatures overlap;
- timed rows use `--no-probe-reference`;
- validation rows keep CPU probe-reference validation.

Required performance:

- mean no-probe tail-total Embree/OptiX speedup: `>= 3.0x`;
- mean traversal Embree/OptiX speedup: `>= 3.0x`;
- mean no-probe wrapper Embree/OptiX speedup: `>= 1.10x`;
- weakest no-probe wrapper Embree/OptiX speedup: `>= 1.00x`.

Important evaluation rule:

- the runner's `timed_status: pass` is a correctness/contract gate only;
- it proves same contract, same shape, same signatures/counts, and
  no-probe timing setup;
- it does not enforce the four performance floors above;
- post-POD promotion review must manually or mechanically check all four
  `aggregate_ratios` floors;
- any floor miss is a gate failure regardless of `timed_status: pass`;
- the traversal floor is valid only if the `traversal` aggregate has
  `count > 0` and a numeric mean.

The wrapper floor is lower than the traversal/tail floors because this runner is
intentionally paired with no-probe timing but still includes Python process and
app lowering costs. The material V4 claim for this target must be about the
generic grouped any-hit flag stream, not full robot-planning wall time.

## Promotion Outcomes

If the gate passes:

- promote `ray_triangle_grouped_any_hit_flags_3d` as measured V4 operator
  coverage under explicit native prepared-runner scope;
- move `robot_collision` from partial to strong measured operator coverage;
- keep whole-app robot planning speedup unauthorized until the formal release
  scorecard/all-app gate.
- state explicitly that the coverage upgrade is for the generic grouped any-hit
  flag-stream continuation only, not robot-collision wall time or robot-planning
  acceleration.
- do not add a catalog surface unless a separate named front-door goal defines
  how `rtdl_native_prepared_runner` scope enters the catalog and exposes a
  generic front-door function.

If the gate fails:

- keep `robot_collision` partial;
- record the failure reason;
- do not add a measured surface;
- continue Goal4636 only by selecting another generic target with a fresh
  predeclared protocol.

## Goal-Level Decision Audit

Decision: choose grouped any-hit flags as Goal4636's second generic coverage
target after threshold-summary failed.

1. Was this decision stupid?
   - No. It moves to a different generic ray/triangle continuation class rather
     than reinterpreting the failed threshold-summary gate.
2. If it were stupid, what action made it stupid?
   - It would be stupid if we framed this as a robot-collision app kernel or
     used the weaker wrapper metric alone. This protocol forbids both and
     requires material tail/traversal gains.
3. Is there another path that avoids being stuck on this thought?
   - Yes. If grouped any-hit flags fail, keep `robot_collision` partial and
     choose AABB/relation prefilter or ranked/top-k under a fresh protocol.
4. Can work start on a different path that truly solves the problem?
   - Yes. The gate is deliberately falsifiable; a failed result forces another
     target rather than post-hoc rewording.

## Non-Authorization

Goal4636B target selection does not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole robot-planning speedup;
- continuous collision support;
- exact solid-collision claims;
- all-benchmark speedup;
- measured catalog promotion;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- robot-collision-native or other app-specific kernels.
