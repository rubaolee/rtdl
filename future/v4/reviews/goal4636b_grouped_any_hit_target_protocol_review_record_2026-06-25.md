# Goal4636B Grouped Any-Hit Target Protocol Review Record

Date: 2026-06-25

Status: `target_protocol_approved_with_required_amendments_pod_may_proceed_not_release`

## Review Inputs

- `future/v4/reviews/call_for_review_v4_goal4636b_grouped_any_hit_target_protocol_2026-06-25.md`
- `future/v4/v4_goal4636b_grouped_any_hit_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4636_grouped_any_hit_target.py`
- `tests/v4_goal4636_grouped_any_hit_target_test.py`
- `scripts/v3_phoenix_robot_collision_flag_stream_no_probe_paired.py`
- `examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`
- `src/rtdsl/generic_primitives.py`

## Claude Review

Raw review:

- `future/v4/reviews/claude_v4_goal4636b_grouped_any_hit_target_protocol_review_2026-06-25.raw.md`

Verdict:

- `approve_with_required_amendments`

Summary:

- `ray_triangle_grouped_any_hit_flags_3d` is generic at the native level.
- The grouped flag-stream continuation is distinct from per-ray any-hit flags.
- The traversal/tail-total `>=3.0x` floors are material.
- The wrapper floors are weaker but acceptable because wrapper includes Python
  process/app lowering overhead; the claim must stay operator-scoped.
- Native prepared-runner scope is acceptable only if future catalog promotion
  resolves scope/front-door representation separately.

Required amendments:

1. State that `timed_status: pass` is a correctness/contract gate only and that
   post-POD promotion review must enforce all four performance floors.
2. Scope any future coverage upgrade to generic grouped any-hit flag-stream
   operator coverage only, not robot-collision wall time or robot planning.
3. State that catalog surface addition under `rtdl_native_prepared_runner`
   requires a separately named generic front-door goal.

Amendment status:

- applied to `src/rtdsl/v4_goal4636_grouped_any_hit_target.py`;
- applied to `tests/v4_goal4636_grouped_any_hit_target_test.py`;
- applied to `future/v4/v4_goal4636b_grouped_any_hit_operator_target_protocol_2026-06-25.md`.

## Antigravity Review

Raw files:

- `future/v4/reviews/antigravity_v4_goal4636b_grouped_any_hit_target_protocol_review_2026-06-25.raw.md`
- `future/v4/reviews/antigravity_v4_goal4636b_grouped_any_hit_target_protocol_review_2026-06-25.stderr.txt`

Result:

- command exited `0`;
- stdout and stderr were empty;
- recorded as review debt, not a substantive review.

## Local Verification

- `py -m unittest tests.v4_goal4636_grouped_any_hit_target_test tests.v3_phoenix_robot_collision_no_probe_paired_script_test`
  - `Ran 7 tests`
  - `OK`
- `py -m unittest tests.goal953_robot_native_continuation_metadata_test`
  - `Ran 5 tests`
  - `OK`

## Decision

The Goal4636B POD gate may proceed.

This is not release authorization and not measured catalog promotion. If the
POD gate passes, the post-POD decision must evaluate all four performance
floors from `aggregate_ratios`, must keep the coverage claim operator-scoped,
and must not add a catalog surface without a separate front-door goal.

## Non-Authorization

This record does not authorize:

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
