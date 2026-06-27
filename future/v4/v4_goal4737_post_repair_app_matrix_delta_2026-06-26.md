# V4 Goal4737 Post-Repair App Matrix Delta

Date: 2026-06-26

Status: `delta_matrix_complete_pending_external_review_debt`

Decision:
`v4_app_matrix_improved_but_formal_high_performance_tag_still_blocked`

## Purpose

Goal4730 was the frozen complete 10-app matrix. Goals4732-4736 then moved
several named blockers. Goal4737 records the current delta without rewriting
Goal4730 history.

Source deltas:

- Goal4732: RayDB route binding repaired; V4/V2.14 no-regression, V4/V3 still
  regression.
- Goal4733: triangle V4/V3 regression cleared by high-repeat focused rerun.
- Goal4734: RTDBSCAN closed as no-go for the second true V4 win.
- Goal4736: Barnes-Hut complete aggregate weighted workflow candidate row
  passed frozen gates.

## Current Matrix Delta

| App | Current status | V4/V2.14 hot | V4/V3.0.2 hot | Release reading |
|---|---|---:|---:|---|
| `rt_dbscan` | modest gain/no-go for second win | 1.086x | 1.083x | bounded modest route, below formal bar |
| `raydb_style` | V2 no-regression repair, V3 regression open | 0.985x | 0.954x | not a speed win; still needs V3 recovery or no-go |
| `triangle_counting` | focused candidate win | 6.381x | 1.043x | clean app candidate row after high-repeat rerun |
| `librts_spatial_index` | parity | 1.003x | 1.004x | parity, not speed evidence |
| `hausdorff_xhd` | true app candidate win | 201581.860x | 2.546x | strong V4 app candidate row |
| `rtnn` | measured no-win | 0.999x / 0.994x | 1.005x / 0.993x | no-win at serious scales |
| `robot_collision` | partial/no-go | full-app ratio not certified; OptiX flags subroute 5.053x over Embree control | full-app ratio not certified | V2.14 already had prepared OptiX any-hit flags; no new same-primitive V4 speed row |
| `contact_manifold` | design no-go | blocked: no fresh generic V4 bounded-witness route | blocked: no fresh generic V4 bounded-witness route | reuses existing collect-k/witness plumbing |
| `spatial_rayjoin` | no current V4 app route | 0.963x subprobe | 0.977x subprobe | blocker; relation-topology route missing |
| `barnes_hut` | complete app candidate vs V2, V3 no-regression | 282.468x | 1.003x | complete aggregate workflow candidate, no RT-core force-law wording |

## What Improved

Goal4730 had only one full-app true V4 candidate win. Goal4737 now has three
app-level candidate rows that pass V2.14 material speed and V3 no-regression:

1. `hausdorff_xhd`
2. `triangle_counting`
3. `barnes_hut`

This is real progress. It is not a wording change.

## Why Formal High-Performance V4 Is Still Blocked

The current matrix still has blockers:

- `raydb_style` is below V3.0.2 (`0.954x`);
- `rt_dbscan` is only modest (`1.086x`) and already no-go for the current
  grouped-union trunk;
- `librts_spatial_index` is parity;
- `rtnn` is measured no-win;
- `robot_collision`, `contact_manifold`, and `spatial_rayjoin` are partial,
  design no-go, or no-route rows.

The honest current state is:

`substantially improved candidate set, still not final formal high-performance V4`

## Next Engineering Decision

The highest-value remaining blockers are:

1. Goal4738: decide whether RayDB's V3 regression can be fixed generically or
   must be closed as no-go.
2. Goal4739: decide whether Spatial RayJoin gets a real relation-topology route
   or remains blocked for V4.
3. Goal4740: only after those, rerun/assemble the next full app matrix and make
   a release decision.

## Claim Boundary

Goal4737 authorizes the internal statement that V4 now has three app-level
candidate rows versus V2.14 with V3 no-regression. It does not authorize:

- final V4 tag;
- public all-benchmark speedup claim;
- geomean headline;
- all-app high-performance wording;
- broad V4-over-V3 wording;
- app-specific native kernels;
- true-zero-copy wording.

## Goal-Level Decision Audit

1. Was I being foolish?
   No. It would be foolish to leave the old Goal4730 matrix as the current
   state after several blockers moved.

2. If yes, what action made the decision foolish?
   The foolish action would be overwriting Goal4730 history or pretending the
   improved delta authorizes final release.

3. Was there another path?
   Yes. Jump straight to tag from the improved rows. That would ignore RayDB,
   RTDBSCAN, LibRTS, RTNN, and no-route/no-go rows.

4. Can I now try a different path that actually solves the problem?
   Yes. Use Goal4737 to select the next real blocker: RayDB V3 regression first.

## Non-Authorization

Goal4737 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
