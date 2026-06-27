# V4 Goal4730 Complete 10-App Matrix

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `complete_10_app_matrix_blocks_formal_high_performance_v4_release`

## Purpose

Goal4730 assembles the complete 10 benchmark-app V2.14-vs-V4 matrix. This is
not a new POD run. It combines the five measured full-app rows from Goal4669
with the five closure rows from Goals4725-4729.

Machine-readable matrix:

- `future/v4/evidence/v4_goal4730_complete_10_app_matrix_2026-06-26.json`

## Matrix

| App | Status | Main number / reason |
| --- | --- | --- |
| `rt_dbscan` | measured modest gain | V4/V2.14 hot 1.086x; below formal bar |
| `raydb_style` | measured regression | V4/V2.14 hot 0.974x |
| `triangle_counting` | measured mixed/regression | V4/V2.14 hot 4.055x, but V4/V3.0.2 hot 0.948x |
| `librts_spatial_index` | measured parity | V4/V2.14 hot 1.003x |
| `hausdorff_xhd` | measured true V4 candidate win | V4/V2.14 hot 201581.860x; V4/V3.0.2 hot 2.546x |
| `rtnn` | measured no-win | 262k V4/V2.14 hot 0.999x; 1M 0.994x |
| `robot_collision` | partial/no-go | traversal win exists, wrapper-wall mean 0.857x fails |
| `contact_manifold` | design no-go | target reuses V2.14 collect-k and current witness plumbing |
| `spatial_rayjoin` | no current V4 app route | shape-pair subprobe V4/V2.14 hot 0.963x |
| `barnes_hut` | deferred/subprobe | aggregate-frontier V4/V2.14 win, but no complete app route and V4/V3 0.998x |

## Release-Gate Interpretation

Formal high-performance V4 is not supported by the complete app matrix.

Reasons:

- only one full-app true V4 win candidate is present: `hausdorff_xhd`;
- `raydb_style` regresses below the no-regression floor versus V2.14;
- `triangle_counting` is fast versus V2.14 but regresses versus V3.0.2;
- `rtnn` is measured no-win at serious scales;
- `robot_collision`, `contact_manifold`, `spatial_rayjoin`, and `barnes_hut`
  do not have complete high-performance V4 app rows.

This matrix supports a bounded-operator V4 truth, not a formal high-performance
app-suite release.

## Next

Goal4731 must choose between:

- continue high-performance engineering on generic runtime levers; or
- publish a bounded-operator V4 release with this complete matrix visible.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4730_complete_10_app_matrix_test tests.v4_goal4723_complete_app_protocol_test tests.v4_goal4729_barnes_hut_deferred_subprobe_row_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal avoids hiding no-go rows or using an outlier/geomean headline
   to imply broad high-performance V4.

2. If yes, what action made the decision stupid?
   Not applicable. The stupid action would have been omitting the blocked rows
   from the release-gate interpretation.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Assemble every promoted app exactly once, classify no-go/no-route rows
   explicitly, and fail the formal high-performance gate honestly.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4731 can make an explicit product decision instead of pretending the
   app-level matrix passed.

## Non-Authorization

Goal4730 authorizes no POD spend, no final V4 tag, no public speed claim, no
whole-app high-performance claim, no all-benchmark speedup claim, no geomean
headline, no app-specific native kernel, no arbitrary callback support, and no
hidden V2/V3 fallback.
