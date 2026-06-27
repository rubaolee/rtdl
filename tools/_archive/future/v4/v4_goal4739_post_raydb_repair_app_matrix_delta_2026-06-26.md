# V4 Goal4739 Post-RayDB-Repair App Matrix Delta

Date: 2026-06-26

Status: `delta_matrix_complete_pending_external_review_debt`

Decision:
`raydb_regression_removed__formal_high_performance_v4_still_blocked`

## Purpose

Goal4737 recorded the post-Triangle/Barnes-Hut matrix before RayDB was repaired.
Goal4738 then fixed a real timing-boundary bug in RayDB: the V4 hot path was
charging Python row materialization even though the intended measured contract
was direct device-output execution with row materialization after the hot
window.

Goal4739 records the updated current matrix without rewriting Goal4737 history.

## Source Evidence

- Goal4730 frozen complete 10-app matrix:
  `future/v4/evidence/v4_goal4730_complete_10_app_matrix_2026-06-26.json`
- Goal4733 Triangle high-repeat focused rerun:
  `future/v4/evidence/v4_goal4733_triangle_v3_regression_resolution_2026-06-26.json`
- Goal4734 RTDBSCAN no-go:
  `future/v4/evidence/v4_goal4734_rt_dbscan_generic_continuation_no_go_2026-06-26.json`
- Goal4736 Barnes-Hut complete workflow:
  `future/v4/evidence/v4_goal4736_barnes_hut_complete_workflow_focused_pod_2026-06-26.json`
- Goal4738 RayDB hot-path repair:
  `future/v4/evidence/v4_goal4738_raydb_hotpath_materialization_boundary_repair_2026-06-26.json`

## Current Matrix Delta

| App | Current status | V4/V2.14 hot | V4/V3.0.2 hot | Release reading |
|---|---|---:|---:|---|
| `rt_dbscan` | modest gain/no-go for current grouped-union trunk | 1.086x | 1.083x | bounded modest route, below formal bar |
| `raydb_style` | V3 regression cleared by hot-path boundary repair | 1.103x | 1.105x | modest device-output win, below formal bar |
| `triangle_counting` | focused candidate win | 6.381x | 1.043x | clean app candidate row after high-repeat rerun |
| `librts_spatial_index` | parity | 1.003x | 1.004x | parity, not speed evidence |
| `hausdorff_xhd` | true app candidate win | 201581.860x | 2.546x | strong V4 app candidate row with denominator caveat |
| `rtnn` | measured no-win | 0.999x / 0.994x | 1.005x / 0.993x | no-win at serious scales |
| `robot_collision` | partial/no-go | full-app ratio not certified; OptiX flags subroute 5.053x over Embree control | full-app ratio not certified | V2.14 already had prepared OptiX any-hit flags; no new same-primitive V4 speed row |
| `contact_manifold` | design no-go | blocked: no fresh generic V4 bounded-witness route | blocked: no fresh generic V4 bounded-witness route | reuses existing collect-k/witness plumbing |
| `spatial_rayjoin` | no current V4 app route | 0.963x subprobe | 0.977x subprobe | blocker; relation-topology route missing |
| `barnes_hut` | complete app candidate vs V2, V3 no-regression | 282.468x | 1.003x | complete aggregate workflow candidate, no RT-core force-law wording |

## What Changed Since Goal4737

RayDB is no longer a V3-regression blocker:

- old Goal4737 RayDB V4/V3.0.2 hot: `0.954x`;
- new Goal4738 RayDB V4/V3.0.2 hot: `1.105x`;
- new Goal4738 RayDB V4/V2.14 hot: `1.103x`;
- V4 row materialization is now outside the measured hot path;
- correctness parity remains true.

This is a real repair, but it is not a formal high-performance app win because
the row remains below the material-speed threshold used for candidate rows.

## Current Candidate Count

The current 10 benchmark-app matrix has three app-level candidate rows versus
V2.14 with V3 no-regression:

1. `hausdorff_xhd`
2. `triangle_counting`
3. `barnes_hut`

RayDB is now a clean modest row, not a blocker and not a candidate.

## Why Formal High-Performance V4 Is Still Blocked

Formal high-performance V4 is still blocked because several rows remain parity,
modest, no-win, partial, design no-go, or no-route:

- `rt_dbscan` is below the formal candidate bar;
- `raydb_style` is fixed but still only a modest win;
- `librts_spatial_index` is parity;
- `rtnn` is measured no-win;
- `robot_collision` is partial/no-go;
- `contact_manifold` is design no-go;
- `spatial_rayjoin` still has no current full V4 app route.

The honest current state is:

`three app candidate rows plus one repaired modest row; final high-performance tag still blocked`

## Next Engineering Decision

The next work must not be another matrix narration. The next work must attempt
to move one remaining named app-level blocker with a generic V4 mechanism, or
close it with evidence.

Priority order:

1. `robot_collision`: inspect whether the wrapper-wall failure is another hot-
   path materialization/accounting boundary that can be repaired generically.
2. `spatial_rayjoin`: only proceed if a real relation-topology V4 route can be
   implemented and measured; do not rerun the failed shape-pair subprobe as
   churn.
3. `rtnn` / `librts_spatial_index`: treat as lower priority unless a new
   generic operator lever is identified.

## Claim Boundary

Goal4739 authorizes only this internal statement:

V4 currently has three benchmark-app candidate rows, RayDB is no longer a V3
regression, and the final high-performance release remains blocked pending more
app-level wins or an honest bounded-release decision.

Goal4739 does not authorize:

- final V4 tag;
- public all-benchmark speedup claim;
- geomean headline;
- all-app high-performance wording;
- broad V4-over-V3 wording;
- app-specific native kernels;
- arbitrary callback support;
- raw OptiX callback support;
- true-zero-copy wording.

## Goal-Level Decision Audit

1. Was I being foolish?

No. It would be foolish to keep reporting the stale RayDB regression after
Goal4738 fixed the timing boundary and reran the POD evidence.

2. If yes, what action made the decision foolish?

Not applicable. The foolish action would be to inflate RayDB's `1.105x` modest
repair into a high-performance candidate row.

3. Was there another path?

Yes. I could have skipped the matrix update and jumped to another target. That
would make later release decisions operate on stale facts.

4. Can I now try a different path that actually solves the problem?

Yes. With RayDB removed as a regression blocker, the correct next path is to
attack a remaining named app-level blocker, starting with `robot_collision` if
its wrapper-wall failure is a generic hot-path boundary issue.

## Non-Authorization

Goal4739 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
