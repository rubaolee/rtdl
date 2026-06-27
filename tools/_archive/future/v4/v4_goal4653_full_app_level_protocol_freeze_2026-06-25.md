# V4 Goal4653 Full App-Level Protocol Freeze

Date: 2026-06-25
Status: protocol frozen locally, pending external/debt record before Goal4654 POD run

## Purpose

Goal4653 freezes the app-level V2.14/V3/V4 benchmark protocol before any new
POD result is seen. It uses Goal4652's route matrix as input and prevents three
failure modes:

- silently falling back to V2/V3 while calling it V4;
- turning partial operator coverage into whole-app V4 performance;
- changing app inclusion or pass/fail bars after seeing results.

This protocol does not authorize a release or a public performance claim.

## Source Files

- `src/rtdsl/v4_app_benchmark_protocol.py`
- `src/rtdsl/v4.py`
- `tests/v4_goal4653_app_level_protocol_test.py`
- Evidence:
  `future/v4/evidence/v4_goal4653_full_app_level_protocol_2026-06-25.json`

## Test Gate

Command:

```text
py -m unittest tests.v4_goal4653_app_level_protocol_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test
```

Result:

```text
30 tests OK
```

## Frozen Shape

| Row type | Count | Role in Goal4654/4655 |
| --- | ---: | --- |
| `full_app_v4_speed_row_candidate` | 4 | Run as V4 app-level speed candidates. |
| `partial_operator_control_not_app_claim` | 4 | Visible controls only; excluded from formal app speed score. |
| `no_v4_route_blocker` | 1 | Visible blocker; no V4 run. |
| `deferred_excluded_with_reason` | 1 | Visible deferred row; no V4 app-identity kernel. |

## Full App V4 Speed Rows

| App | V4 route | Scale | Bar |
| --- | --- | --- | --- |
| `rt_dbscan` | fixed-radius count-threshold + fixed Numba component-union | clustered3d 262144 points plus fixed-radius operator scale | correctness parity; V4/V2.14 >= 1.20x; V4/V3 >= 1.05x; no row < 0.98x |
| `raydb_style` | grouped-i64 + grouped-argmin + any-hit | generated rows >=131072, grouped-i64 widths 1/16/256 | correctness parity; V4/V2.14 >= 1.20x; V4/V3 >= 1.05x; no row < 0.98x |
| `triangle_counting` | any-hit weighted-sum + grouped-i64 | Goal4633 shapes 32768/131072/262144/524288 plus grouped-i64 controls | correctness parity; V4/V2.14 >= 1.20x; V4/V3 >= 1.05x; no row < 0.98x |
| `librts_spatial_index` | generic prepared AABB all-ops count | 1,000,000 boxes, 1,000 queries, operation=all, repeat=240 | correctness parity; V4/V2.14 >= 1.20x; V4/V3 >= 1.05x; outlier label required |

These rows are the only rows that can contribute to a formal high-performance
V4 subset decision in Goal4655.

## Partial Controls

| App | Current V4 coverage | Rule |
| --- | --- | --- |
| `hausdorff_xhd` | point-group nearest-witness + fixed-radius controls | control only; no whole-app speed claim |
| `robot_collision` | any-hit flags control | control only; no whole-app speed claim |
| `contact_manifold` | nearest-witness control | control only; no whole-app speed claim |
| `rtnn` | nearest-witness control | control only; ranked/top-k blocker remains |

These may be used for coverage and regression context, but not as app-level V4
wins.

## Blocker / Deferred Rows

| App | Status | Reason |
| --- | --- | --- |
| `spatial_rayjoin` | `no_v4_route_blocker` | Relation topology/PIP stream is not a current V4 generic Tier-2 surface. |
| `barnes_hut` | `deferred_excluded_with_reason` | Aggregate-tree weighted vector sum is app-identity shaped and excluded from V4.0 generic Tier-2. |

They remain visible in the scorecard. They are not hidden exclusions.

## Protocol Locks

- No naive whole-suite geomean can trigger release.
- No post-hoc app exclusion is allowed.
- Partner migration cannot count as a V4 speed win.
- Algorithmic-complexity outliers must be labeled.
- `spatial_rayjoin` and `barnes_hut` must stay visible.
- Goal4654 must run from this frozen protocol, or record a protocol violation.

## Goal-Level Decision Audit

1. Was I being stupid?
   - The known stupid path would be to run POD first and then explain the app
     set afterward. This goal avoids that by freezing the protocol first.
2. If yes, what action made it stupid?
   - Treating partial V4 operator coverage as full app-level V4 readiness would
     be the bad action. The protocol separates these row types.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: run only the four full-route rows as V4 app-level speed candidates
     while keeping partial, blocker, and deferred rows visible.
4. Can I now try the different path that actually solves the problem?
   - Yes: Goal4654 can run the frozen app-level benchmark without changing the
     app list or bars after seeing results.

## Non-Authorization

Goal4653 does not authorize POD spend by itself, public V4 release, broad V4
speed claims, whole-app speed claims, CuPy blanket claims, arbitrary Numba
callbacks, C ABI, embedding, true-zero-copy, non-Python hosts, or app-specific
native kernels.
