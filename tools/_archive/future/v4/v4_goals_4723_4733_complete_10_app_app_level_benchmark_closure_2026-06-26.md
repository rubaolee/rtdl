# V4 Goals4723-4733: Complete 10-App App-Level Benchmark Closure

Date: 2026-06-26

Status: `planned_not_executed`

Decision: `block_final_v4_tag_until_complete_10_app_v2_14_vs_v4_matrix`

## Why This Replaces The Previous Next Step

The previous next-step chain let V4 proceed toward final tag after operator and
workflow gate convergence. That is insufficient for the user's stated V4 goal.

The new hard rule:

> V4 cannot be presented as a serious high-performance user release until every
> one of the 10 RTDL benchmark apps has a clear V2.14-vs-V4 app-level row:
> measured win, measured parity, measured regression, or explicit no-route/no-go
> with the missing generic runtime lever named.

This does not mean every app must be faster. It means every app must be
accounted for honestly at app level. Operator-level wins are not allowed to
stand in for missing full-app evidence.

## Goal-Level Decision Audit

1. Was I being stupid?
   Yes.

2. What action made the decision stupid?
   I treated a converged 10-surface operator/workflow release candidate as if it
   could approach final V4 release without first forcing a complete 10-app
   app-level V2.14-vs-V4 matrix. That missed the user's product-level intent.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Move final tag behind a complete app-level closure gate. Rows that lack
   V4 routes must be explicit blockers, not silently omitted.

4. Can I now try the different path that actually solves the problem?
   Yes. The next goals below make complete 10-app app-level evidence the release
   gate and keep implementation focused on generic runtime/operator routes, not
   app-specific kernels.

## Fixed App Set

The app set is frozen to the 10 promoted benchmark apps already recorded by the
V4 route-binding protocol:

1. `rt_dbscan`
2. `raydb_style`
3. `triangle_counting`
4. `librts_spatial_index`
5. `hausdorff_xhd`
6. `robot_collision`
7. `contact_manifold`
8. `rtnn`
9. `spatial_rayjoin`
10. `barnes_hut`

## Current Known Rows Before This Work

Already measured as same-hardware app-level V2.14 vs V4 rows:

| App | V4/V2.14 hot | Current class |
| --- | ---: | --- |
| `rt_dbscan` | `1.086x` | modest gain, below formal high-performance bar |
| `raydb_style` | `0.974x` | regression |
| `triangle_counting` | `4.055x` | fast vs V2.14, but regresses vs V3.0.2; not clean V4 win |
| `librts_spatial_index` | `1.003x` | parity |
| `hausdorff_xhd` | `201581.860x` | true V4 app candidate win |

Rows not yet acceptable as complete app-level V2.14-vs-V4 release evidence:

| App | Current problem |
| --- | --- |
| `robot_collision` | partial any-hit coverage only; V2.14 already has prepared any-hit collision primitive |
| `contact_manifold` | partial nearest-witness coverage only; full contact route missing |
| `rtnn` | candidate route measured at serious scale but parity/slower; needs final app-row disposition |
| `spatial_rayjoin` | no current V4 relation-topology app route |
| `barnes_hut` | aggregate-frontier subprobe exists, but no complete generic Barnes-Hut app route |

## Non-Negotiable Rules

- V2 means exactly V2.14.
- Same RT hardware for all final comparable rows.
- No silent fallback to V2/V3 routes for V4 rows.
- No app-identity kernels: no `dbscan kernel`, no `barnes_hut kernel`, no
  `rayjoin app kernel`.
- Any new work must be a generic runtime/operator lever reusable outside one
  benchmark app.
- Correctness parity is mandatory before timing is credited.
- A missing V4 route is an explicit failure/blocker row, not an omitted row.
- Partner migration does not count as a V4 speed win.
- Operator/subprobe speedups cannot be used as full-app speedups.
- Final tag is blocked until Goal4733.

## Goal4723: Freeze Complete 10-App Protocol

Purpose:

Create the exact 10-app app-level protocol before any more POD spending.

Tasks:

- For each of the 10 apps, freeze:
  - V2.14 command/route;
  - V4 command/route or explicit missing-route blocker;
  - dataset scale;
  - warmup/repeat count;
  - correctness oracle;
  - primary metric: hot and wall where available;
  - no-regression floor;
  - speed bar if the row claims performance.
- Preserve current measured rows, but do not let the existing 5 rows define the
  whole release.
- Define the allowed row classes:
  `measured_win`, `measured_parity`, `measured_regression`,
  `measured_no_win_candidate`, `no_v4_route_blocker`.

Exit gate:

- A machine-readable protocol JSON and readable report exist.
- All 10 apps appear exactly once.
- No app is excluded post hoc.
- No POD run is authorized until this protocol passes local tests.

Estimated time: `2-4 hours`.

## Goal4724: Route-Gap Audit For The Remaining 5 Apps

Purpose:

For the five incomplete apps, identify whether V4 has a real full-app route,
needs a generic runtime/operator implementation, or must record a no-go.

Apps:

- `robot_collision`
- `contact_manifold`
- `rtnn`
- `spatial_rayjoin`
- `barnes_hut`

Exit gate:

- Each app has one of:
  - runnable full V4 route ready for benchmark;
  - generic operator implementation target named;
  - explicit no-route blocker with missing primitive named.
- The audit must state whether V2.14 already had the same primitive.

Estimated time: `3-6 hours`.

## Goal4725: RTNN Final App-Row Disposition

Purpose:

Turn existing RTNN candidate evidence into a formal 10-app matrix row, rerunning
only if the protocol requires it.

Known evidence:

- 262,144 points: V4/V2.14 hot about `0.999x`.
- 1,048,576 points: V4/V2.14 hot about `0.994x`.

Exit gate:

- RTNN is recorded as measured parity/regression or rerun under Goal4723.
- The row cannot be counted as V4 high-performance evidence unless a new
  generic runtime lever is implemented and passes the frozen bar.

Estimated time: `1-3 hours` if evidence is accepted, `4-8 hours` if rerun.

## Goal4726: Robot Collision Full-App Row Or No-Go

Purpose:

Produce a complete app-level V2.14-vs-V4 row for robot collision.

Required discipline:

- V2.14 already has prepared OptiX any-hit collision primitives, so a V4 row
  must be same-primitive improvement or a truly new generic runtime lever.
- Partial any-hit flag coverage is not a full app result.

Exit gate:

- Complete measured app row with correctness parity, or explicit no-go stating
  the missing generic route.

Estimated time: `6-12 hours`.

## Goal4727: Contact Manifold Full-App Row Or Generic Collect/Witness Target

Purpose:

Produce a complete app-level V2.14-vs-V4 row for contact manifold, or freeze the
missing generic primitive.

Required discipline:

- V2.14 already has bounded contact-witness collection primitives.
- V4 must not claim a win for merely rewrapping nearest-witness coverage.

Exit gate:

- Complete measured app row with correctness parity, or explicit no-go naming
  the missing generic contact/witness operator.

Estimated time: `8-16 hours`.

## Goal4728: Spatial RayJoin Relation-Topology Route Or No-Go

Purpose:

Close the largest route gap: current V4 has no full relation-topology route for
Spatial RayJoin.

Required discipline:

- Do not silently fall back to old V2/V3 mixed routes.
- If implemented, the route must be a generic relation/topology operator, not a
  Spatial-RayJoin-specific native kernel.

Exit gate:

- Runnable V4 route plus app-level benchmark, or explicit no-route blocker with
  the missing relation-topology primitive named.

Estimated time: `12-24 hours` for a minimal generic route attempt, less if
audited no-go.

## Goal4729: Barnes-Hut Generic Aggregate Route Or No-Go

Purpose:

Close the Barnes-Hut gap without using the aggregate-frontier subprobe as a fake
full-app result.

Required discipline:

- Existing aggregate-frontier device-column evidence is only a subprobe.
- A valid V4 Barnes-Hut result must route a complete generic aggregate-tree /
  weighted-vector workflow, not an app-identity Barnes-Hut kernel.

Exit gate:

- Complete measured app row with correctness parity, or explicit no-go naming
  the missing generic aggregate-tree weighted-vector primitive.

Estimated time: `12-24 hours` for a minimal generic route attempt, less if
audited no-go.

## Goal4730: Full 10-App Same-Hardware POD Run

Purpose:

Run the complete Goal4723 protocol on the same RT hardware.

Exit gate:

- All runnable rows execute.
- No-route/no-go rows are included in the final matrix rather than omitted.
- Raw JSON, summary JSON, and markdown report exist.
- Every timed row has correctness parity or an explicit skipped-oracle reason.

Estimated time: `6-12 hours` POD time, depending on route availability and
reruns.

## Goal4731: 10-App Analysis And User-Facing Classification

Purpose:

Produce the table a user actually needs.

For each app:

- V4/V2.14 hot ratio;
- V4/V2.14 wall ratio if available;
- correctness status;
- row class;
- reason;
- whether it can support a V4 performance claim.

Exit gate:

- The final table has all 10 apps.
- The analysis explicitly says whether V4 is:
  - broad app-level high-performance release;
  - partial app-level release;
  - operator/workflow release only;
  - not release-ready.

Estimated time: `2-4 hours`.

## Goal4732: Public Docs Rewrite From 10-App Truth

Purpose:

Rewrite current public docs so users see the complete 10-app reality first, not
just operator-surface scorecards.

Required docs:

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/performance_wording.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `examples/README.md`
- `tutorials/current/README.md`

Exit gate:

- Docs expose the 10-app matrix.
- No doc implies missing app rows are measured.
- No doc uses operator/subprobe rows as full-app evidence.

Estimated time: `3-6 hours`.

## Goal4733: External Review And Final Release Decision

Purpose:

Ask external reviewers to decide whether V4 can be released, and under what
label.

Exit gate:

- Goal4730/4731/4732 evidence is reviewed.
- Reviewers explicitly answer:
  - Are all 10 app rows accounted for?
  - Is the V4 performance claim honest?
  - Is final tag authorized, blocked, or allowed only as an operator/workflow
    release?
- Final tag only happens after this gate.

Estimated time: `2-6 hours`, dependent on reviewer availability.

## Three-Day Execution Budget

Best case:

- Day 1: Goals4723-4726.
- Day 2: Goals4727-4729.
- Day 3: Goals4730-4733.

If Spatial RayJoin or Barnes-Hut requires real new generic operator work beyond
minimal route closure, the honest outcome may be:

- release as operator/workflow V4 with complete 10-app blocker matrix; or
- delay final V4 high-performance release.

The unacceptable outcome is publishing V4 while leaving the five incomplete app
rows vague.

## Non-Authorization

This goal list does not authorize final V4 tag, broad V4 speedup wording,
whole-application speedups, all-benchmark speedups, arbitrary callback support,
raw OptiX callbacks, C ABI, embedding, non-Python host bindings, app-specific
native kernels, or using operator/subprobe results as full app results.
