# V4 Goal4636B Grouped Any-Hit POD Gate Decision

Status: `goal4636b_grouped_any_hit_pod_gate_failed_no_promotion_not_release`

Decision: `reject_grouped_any_hit_promotion_keep_robot_collision_partial`

## Evidence

- POD evidence: `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/summary.json`
- Target protocol: `future/v4/v4_goal4636b_grouped_any_hit_operator_target_protocol_2026-06-25.md`
- Review record: `future/v4/reviews/goal4636b_grouped_any_hit_target_protocol_review_record_2026-06-25.md`
- Machine decision: `src/rtdsl/v4_goal4636_grouped_any_hit_decision.py`

## Gate Result

The candidate was serious and same-contract, but it did not pass the predeclared
promotion gate.

| Check | Result |
| --- | --- |
| Validation status | `pass` |
| Timed status | `pass` |
| Timed rows exclude probe reference | `true` |
| Validation/timed signature overlap | `true` |
| Same contract/shape/signature counts | `true` |
| Tail-total mean Embree/OptiX | `4.128x` vs floor `3.0x` |
| Traversal mean Embree/OptiX | `30.515x` vs floor `3.0x` |
| Wrapper mean Embree/OptiX | `0.857x` vs floor `1.10x` |
| Wrapper min Embree/OptiX | `0.823x` vs floor `1.00x` |

The tail/traversal path is strong, but wrapper-wall performance failed both
predeclared wrapper floors. Therefore this is not a measured V4 Tier-2
promotion.

## Coverage Effect

- `robot_collision` remains `partial_measured_operator_coverage`.
- `ray_triangle_grouped_any_hit_flags_3d` is not added to the measured public
  V4 catalog.
- No whole-app robot planning, continuous collision, or broad V4 speedup claim is
  authorized.

## Next Action

Continue Goal4636 with another predeclared generic target, or return to grouped
any-hit only through a separate wrapper/front-door hardening goal that explains
the wrapper-wall loss before any rerun.

## Goal-Level Decision Audit

1. Was the decision foolish?

   No. The gate was predeclared, the POD run was serious, and the failed wrapper
   floors are being recorded instead of hidden.

2. If it had been foolish, what action would have made it foolish?

   Promoting the operator because traversal was fast, while ignoring the wrapper
   wall regression, would have repeated the old error of turning local green
   numbers into release progress.

3. Is there another path that avoids being stuck on the wrong idea?

   Yes. Treat grouped any-hit as useful diagnostic evidence, not a promotion,
   and move to the next generic coverage target. If grouped any-hit returns, it
   must be through wrapper/front-door hardening with a fresh protocol.

4. Can we start a different path that better solves the problem?

   Yes. Goal4636 should continue by selecting a target whose promotion can move
   a partial or deferred app row through an operator-level gate, without relying
   on hidden app-specific kernel work.

## Non-Authorization

This decision does not authorize V4 release, release-candidate wording, broad
speedup claims, whole-app speedup claims, public true-zero-copy claims, Tier-3
callback support, raw OptiX callback support, CuPy performance claims, C ABI,
embedding, non-Python host claims, or app-specific native kernels.
