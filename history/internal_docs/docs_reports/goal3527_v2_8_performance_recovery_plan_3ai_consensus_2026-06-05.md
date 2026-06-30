# Goal3527: v2.8 Performance Recovery Plan 3-AI Consensus

Date: 2026-06-05

Status: accepted with boundary; implementation may start only under the amended
Goal3527 plan.

## Reviewed Plan

- `docs/reports/goal3527_v2_8_performance_recovery_and_promoted_path_plan_2026-06-05.md`
- `tests/goal3527_v2_8_performance_recovery_plan_test.py`

## External Reviews

Claude:

- `docs/reviews/goal3528_claude_review_goal3527_v2_8_performance_recovery_plan_2026-06-05.md`
- verdict: `accept-with-boundary`

Gemini:

- `docs/reviews/goal3529_gemini_review_goal3527_v2_8_performance_recovery_plan_2026-06-05.md`
- verdict: `accept`

## Consensus Decision

Codex, Claude, and Gemini agree that Goal3527 is the correct next engineering
move after the disappointing Goal3524 same-runner table.

Accepted core decisions:

1. Goal3524 remains a same-runner diagnostic table, not the final v2.8
   performance headline.
2. v2.8 needs a separate promoted-path performance table that measures actual
   optimized v2.8 contracts.
3. Barnes-Hut node coverage is P0 because the 0.401x/0.503x regression is real.
4. RayJoin's 1.096x same-runner row must not be used as the optimized-RayJoin
   headline.
5. Weak rows must be repaired, scaled, or honestly classified as parity/noise or
   regression.
6. Partner use must remain explicit: CuPy only where selected, no hidden PyTorch
   in current v2.8 performance rows.
7. No app-specific native-engine shortcuts are allowed.
8. No public/release performance claim is authorized by this plan.

## Claude Boundary Incorporated

Claude raised two critical pre-implementation blockers. Codex amended the
Goal3527 plan and test to close both before writing this consensus:

1. **Sub-millisecond measurement guard.** Workstream A now requires
   `case_repeat` or equivalent repeat count, timing-methodology fields, and a
   `sub_millisecond_measurement_guard` for rows below 1 ms. Such rows need a
   larger scale, repeated steady-state timing, or explicit launch-overhead
   classification before they can be used as speedup evidence.
2. **RayJoin promoted-contract preflight.** Workstream A now requires a preflight
   note before RayJoin promoted-path measurement, listing which contracts are
   already runnable and which require new authoring: count/parity, relation
   columns, shape-pair payload, and overlay-area continuation.

Claude also requested a quantitative Barnes-Hut close rule and a stop condition.
The amended plan now defines:

- `recovered`: v2.8 reaches at least 0.95x of v2.3 in two fresh RTX runs;
- `improved_but_open`: material improvement but still below 0.95x;
- `honest_regression`: after bounded focused investigation, the row remains
  below 0.95x and must be carried visibly rather than hidden.

## Implementation Authorization

Implementation may start only inside these boundaries:

- first perform RayJoin promoted-contract preflight;
- first investigate Barnes-Hut P0 under the same node-coverage contract;
- use scale/repeat controls for sub-millisecond rows;
- keep the same-runner diagnostic and promoted-path table separate;
- keep all claim-boundary flags false until later evidence and review.

This is not a v2.8 release authorization and not public speedup wording.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3527_v2_8_performance_recovery_plan_test tests.goal3524_v2_8_vs_v2_3_same_runner_optix_results_test
```

Result:

```text
Ran 14 tests in 0.026s
OK
```

## Verdict

`accept-with-boundary`

Goal3527 is ready for implementation under the amended plan. The next concrete
engineering step is Barnes-Hut P0 investigation plus RayJoin promoted-contract
preflight, before any promoted-path table is treated as evidence.
