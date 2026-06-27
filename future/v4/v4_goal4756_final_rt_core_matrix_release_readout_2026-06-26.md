# V4 Goal4756 Final RT-Core Matrix Release Readout

Status: `complete_matrix_analyzed__release_not_yet_authorized`

This is the current V4.0 fairness baseline for the 10 promoted benchmark apps.
It uses NVIDIA OptiX/RT-core rows only as the primary denominator. Embree is not
used as a primary denominator.

## Evidence

- Matrix run:
  `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/`
- Matrix summary:
  `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/summary.json`
- Analysis JSON:
  `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json`
- Analysis report:
  `future/v4/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.md`
- Hausdorff exact V3/V4 supplemental route:
  `future/v4/evidence/v4_goal4755_hausdorff_exact_v3_v4_20260626/`

## Completeness

- Apps: `10/10`
- Versions per app: `V2.14`, `V3.0.2`, `V4.0`
- Rows executed: `30/30`
- Return codes: all `0`
- JSON parse: all passed
- `n/a` rows: none
- Primary denominator: NVIDIA RT-core/OptiX rows only

## Hot-Path Matrix

| app | V2.14 hot s | V3 hot s | V4 hot s | V4/V2 hot | V4/V3 hot | class |
|---|---:|---:|---:|---:|---:|---|
| `rt_dbscan` | 1.52489 | 1.51730 | 1.52818 | 0.99785 | 0.99289 | parity/control |
| `raydb_style` | 0.00567069 | 0.00566274 | 0.00509660 | 1.11264 | 1.11108 | parity/control |
| `triangle_counting` | 0.000784576 | 0.000183627 | 0.000179939 | 4.36023 | 1.02050 | material candidate |
| `librts_spatial_index` | 0.385124 | 0.386380 | 0.385432 | 0.99920 | 1.00246 | parity/control |
| `hausdorff_xhd` | 9.99419 | 9.52183 | 9.68538 | 1.03188 | 0.98311 | parity/control |
| `robot_collision` | 0.00234625 | 0.00230105 | 0.00230090 | 1.01971 | 1.00007 | parity/control |
| `contact_manifold` | 0.00618469 | 0.00818093 | 0.00554058 | 1.11625 | 1.47655 | parity/control |
| `rtnn` | 0.000982534 | 0.000976935 | 0.000954494 | 1.02938 | 1.02351 | parity/control |
| `spatial_rayjoin` | 0.0154358 | 0.0155008 | 0.0154353 | 1.00003 | 1.00424 | parity/control |
| `barnes_hut` | 32.1134 | 0.111445 | 0.112229 | 286.142 | 0.99302 | material V3/V4-over-V2 candidate |

Hot-path geomean V4/V2.14: `2.10069x`.

This geomean must not be used as a broad headline. It is dominated by the
Barnes-Hut denominator transition and Triangle. The honest app-level claim is:
V4.0 has a complete 10-app RT-core matrix with no hot-path regressions in this
run, two material hot-path candidate wins over V2.14, and broad parity/control
elsewhere.

## Important Interpretations

`triangle_counting`:
V4 beats V2.14 by `4.36x` and V3 by `1.02x` on the hot replay metric in this
run. This is a valid material hot-path candidate, but public wording must still
name the route and input rather than claiming all triangle-like workloads.

`barnes_hut`:
V4 beats V2.14 by `286x` on the measured hot path, but V4 is only parity with
V3 (`0.993x`). This is not a new V4-only speed invention. It is V4 preserving
the V3/Phoenix device-continuation path and packaging it as part of the V4
superset.

`spatial_rayjoin`:
The earlier all30 matrix used a tiny default overlay row. Goal4756 replaces it
with generated grid64 shape-pair data in the runner itself. On that serious
same-primitive row, V4 is parity with V2.14 and V3 (`1.000x`, `1.004x`).

`hausdorff_xhd`:
The three-version same-primitive threshold row is parity/control, not a V4 speed
win. V2.14 does not expose an RT-core exact nearest-witness route: attempting
`--backend optix --optix-summary-mode rows --require-rt-core` fails in V2.14
because the app enforces RT-core Hausdorff as
`directed_threshold_prepared`. V3 and V4 do expose exact nearest-witness:
current V3 exact hot is `0.006413s`, current V4 exact hot is `0.005547s`, so
V4/V3 exact is `1.156x`. That supplemental route is a V3/V4 exact capability
comparison, not a same-primitive V2/V3/V4 row.

## Release Boundary

This readout does not authorize the final V4.0 tag by itself. Remaining release
work:

- update public docs so V4 is described as a V2/V3 superset plus V4 operator
  surfaces, not as a universal speedup;
- make the 10-app matrix the official benchmark page;
- mark material wins, inherited wins, and parity/control rows separately;
- preserve exact-route Hausdorff as a semantic superset note;
- run final docs/examples/tests validation; and
- send the final packet to Claude and Antigravity review, with any review debt
  explicitly recorded if a reviewer is unavailable.
