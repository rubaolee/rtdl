# V4 Goal4728 Spatial RayJoin No-Route Blocker Row

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `spatial_rayjoin_closed_as_no_current_v4_app_route_shape_pair_subprobe_no_speed_credit`

## Purpose

Goal4728 closes `spatial_rayjoin` for the current V4 high-performance path as a
visible blocker. The repo has many RayJoin/shape-pair primitives from earlier
versions, but that is not the same thing as a complete current V4 app-level
route.

Machine-readable row:

- `future/v4/evidence/v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.json`

## Evidence

Focused shape-pair subprobe:

- `future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/summary.json`
- `future/v4/v4_goal4681_shape_pair_relation_pod_benchmark_2026-06-25.md`

Result:

| Metric | Result |
| --- | ---: |
| correctness companion | pass |
| serious active-count parity | pass |
| hot-path row-stream materialization | false |
| V4/V2.14 same-primitive hot | 0.9632x |
| V4/V2.14 same-primitive wall | 0.6049x |
| V4/V3.0.2 hot | 0.9770x |

The subprobe is correct, but it failed speed-credit bars. It is also not a full
`spatial_rayjoin` app route.

## Conclusion

`spatial_rayjoin` remains:

```text
closed_no_current_v4_app_route_blocker
```

This row contributes to the complete 10-app matrix as a visible blocker, not as
V4 high-performance evidence.

## Reopen Condition

Only reopen this row if a complete app-level V4 relation-topology route is
bound with frozen V2.14 denominator, correctness parity, and material-speed bars
before POD.

## Next

Proceed to Goal4729: `barnes_hut` generic aggregate weighted workflow or no-go.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4728_spatial_rayjoin_no_route_blocker_row_test tests.v4_goal4681_shape_pair_result_test tests.v4_goal4724_remaining_app_route_gap_audit_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal avoids treating old RayJoin symbols or a failed shape-pair
   subprobe as a complete current V4 app route.

2. If yes, what action made the decision stupid?
   Not applicable. The stupid action would be hiding a V2/V3 fallback under V4
   wording.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Record the no-route blocker and reopen only if a full relation-topology
   V4 app route is actually bound before POD.

4. Can I now try the different path that actually solves the problem?
   Yes. Move to `barnes_hut`, where the question is whether aggregate assets can
   become a generic weighted workflow without app-identity kernel leakage.

## Non-Authorization

Goal4728 authorizes no POD spend, no final V4 tag, no public speed claim, no
spatial-RayJoin speedup claim, no RayJoin paper reproduction claim, no whole-app
high-performance claim, no broad V4-over-V2.14 claim, no app-specific native
kernel, and no hidden V2/V3 fallback.
