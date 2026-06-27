# V4 Goal4726 Robot Collision Partial/No-Go Row

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `robot_collision_stays_partial_operator_coverage_after_grouped_any_hit_gate_failed_wrapper_wall`

## Purpose

Goal4726 closes `robot_collision` for the current V4 high-performance path. It
does not claim that RTDL lacks useful collision primitives. It says the current
V4 route cannot be used as app-level high-performance evidence versus V2.14.

Machine-readable row:

- `future/v4/evidence/v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.json`

## Denominator

V2.14 already had the promoted route:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

The route decision records it as a prepared grouped-segment any-hit primitive
with NumPy vectorized query lowering and no required partner continuation.

## Evidence

Existing same-contract grouped any-hit gate:

- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/summary.json`
- `src/rtdsl/v4_goal4636_grouped_any_hit_decision.py`

Gate result:

| Check | Result |
| --- | --- |
| correctness validation | pass |
| timed status | pass |
| same contract/signature | pass |
| tail-total Embree/OptiX mean | 4.1278x |
| traversal Embree/OptiX mean | 30.5147x |
| wrapper-wall Embree/OptiX mean | 0.8567x, below 1.10x floor |
| wrapper-wall Embree/OptiX min | 0.8235x, below 1.00x floor |

## Conclusion

The native traversal win is real, but the wrapper-wall path fails the
predeclared promotion floor. Because V2.14 already had the grouped-segment
any-hit primitive, this cannot become a V4-over-V2.14 app-level speed claim.

Robot collision is therefore closed for the current matrix as:

```text
closed_partial_operator_no_go_for_current_high_performance_path
```

## Reopen Condition

Only reopen this row if a new generic lowering removes the wrapper-wall loss and
freezes a true V2.14-vs-V4 same-primitive denominator before POD.

## Next

Proceed to Goal4727: `contact_manifold` fresh generic bounded-witness protocol
or no-go.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4726_robot_collision_partial_no_go_row_test tests.v4_goal4636_grouped_any_hit_target_test tests.v4_goal4724_remaining_app_route_gap_audit_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The goal avoids the stupid path of claiming traversal-only speed as a V4
   app-level win while the wrapper-wall floor failed.

2. If yes, what action made the decision stupid?
   Not applicable. The stupid action would be rerunning or rebranding the same
   failed promotion path instead of recording the no-go.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Record the partial/no-go row and reopen only if a new generic lowering
   changes the wrapper-wall premise.

4. Can I now try the different path that actually solves the problem?
   Yes. Move to `contact_manifold`, whose existing audit already suggests a
   similar no-go unless a genuinely fresh generic bounded-witness route exists.

## Non-Authorization

Goal4726 authorizes no POD spend, no final V4 tag, no public speed claim, no
robot-collision speedup claim, no whole-app high-performance claim, no broad
V4-over-V2.14 claim, no measured catalog promotion, no app-specific native
kernel, no arbitrary callback support, and no hidden V2/V3 fallback.
