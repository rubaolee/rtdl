# V4 Goal4742 Current Release Framing After Blocker Closure

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision:
`bounded_high_performance_python_edsl_release_candidate__not_all_benchmark_apps_faster`

## Purpose

Goal4742 assembles the current V4 truth after Goals4733-4741:

- Triangle V4/V3 regression cleared.
- Barnes-Hut complete workflow candidate measured.
- RayDB timing-boundary regression repaired.
- Robot Collision boundary corrected but kept out of V4 speed credit.
- Spatial RayJoin not reopened without a new relation-topology route.
- Custom predicate early-exit measured and productized as a real V4 eDSL
  operator-pushdown workflow.

This goal does not tag a release. It freezes the honest current release
framing that external reviewers must check.

## Current V4 Position

V4 is currently best described as:

`a bounded high-performance Python eDSL/runtime release candidate for measured generic RT-core operator pushdown`

It is not honestly describable as:

`all 10 historical benchmark apps are faster than V2.14`

Both statements matter. The first is real progress; the second is false.

## 10-App Benchmark Matrix

| App | V4/V2.14 hot | V4/V3.0.2 hot | Current reading |
|---|---:|---:|---|
| `hausdorff_xhd` | 201581.860x denominator outlier | 2.546x | candidate row; V2.14 denominator is Embree directed-summary, so do not headline raw V2 ratio |
| `triangle_counting` | 6.381x | 1.043x | app-level candidate win after high-repeat rerun |
| `barnes_hut` | 282.468x | 1.003x | app-level candidate vs V2, V3 no-regression; no RT-core force-law claim |
| `raydb_style` | 1.103x | 1.105x | repaired modest device-output win, below formal candidate bar |
| `rt_dbscan` | 1.086x | 1.083x | modest/no-go for current grouped-union trunk |
| `librts_spatial_index` | 1.003x | 1.004x | parity |
| `rtnn` | 0.999x / 0.994x | 1.005x / 0.993x | measured no-win at serious scales |
| `robot_collision` | full-app V4/V2.14 not certified; OptiX flags subroute 5.053x over Embree control | full-app V4/V3.0.2 not certified | V2.14 already had prepared OptiX any-hit flags; no new same-primitive V4 speed row |
| `contact_manifold` | blocked: no fresh generic V4 bounded-witness route | blocked: no fresh generic V4 bounded-witness route | V2.14 already had bounded OptiX collect-k; current target would rebrand existing work |
| `spatial_rayjoin` | 0.963x subprobe | 0.977x subprobe | no current full V4 route; subprobe failed bars |

Candidate benchmark-app rows versus V2.14 with V3 no-regression:

1. `hausdorff_xhd`
2. `triangle_counting`
3. `barnes_hut`

Hausdorff caveat: the raw V4/V2.14 hot ratio compares V4's OptiX/CuPy route with
a V2.14 Embree directed-summary denominator at 262,144 points/side. The
same-family V4/V3.0.2 hot comparison is `2.546x`; the 1,048,576 points/side
coordinate-normalized row is correctness-boundary evidence, not a speed
headline.
No app row should be reported as `n/a`. If a full-app ratio is missing, the
matrix must show the exact blocker: no complete V4 route, preexisting V2.14
OptiX primitive, or RT-core-only denominator rerun required.

Clean but not candidate:

- `raydb_style`
- `rt_dbscan`
- `librts_spatial_index`

Closed/no-go/no-route:

- `rtnn`
- `robot_collision`
- `contact_manifold`
- `spatial_rayjoin`

## V4 eDSL/Operator-Pushdown Value Row

The strongest V4-specific value row is not one of the legacy 10 app rows. It is
the new constrained callback/operator-pushdown workflow:

`ray_triangle_custom_predicate_early_exit_multi_hit`

Measured surface:

`v4_ray_triangle_custom_predicate_early_exit_3d_numba`

Serious-scale POD result:

- V4/V2.14 materialized-device fallback geomean: `4.633x`
- V4/V3.0.2 materialized-device fallback geomean: `4.633x`
- minimum primary row: `2.055x`
- correctness: pass

This is real V4 value because the old versions did not have any-hit predicate
early termination for constrained user predicates. The fallback traces the same
geometry but must materialize all hit layers before filtering.

## Why This Can Still Be A Valuable V4

V4 is valuable if presented as an eDSL/runtime with measured generic operator
pushdown:

- It exposes measured generic V4 operator surfaces.
- It supports a constrained custom predicate early-exit workflow that changes
  traversal/materialization cost.
- It has three app-level candidate rows.
- It repairs several historical false boundaries and no longer hides blockers.

V4 is not valuable if marketed as a blanket replacement where every old
benchmark app is faster. That claim is unsupported.

## Release Framing

Allowed internal release-candidate wording:

`V4 is a Python eDSL/runtime release candidate for measured RT-core operator pushdown. It includes 10 measured operator/workflow surfaces, a constrained Numba custom-predicate early-exit surface with 4.633x serious-scale geomean versus materialized-device fallback, and three historical benchmark-app candidate wins. It does not claim that all historical benchmark apps are faster than V2.14.`

Blocked wording:

- `all benchmark apps are faster`
- `V4 universally beats V2.14`
- `formal high-performance across the full 10-app suite`
- `arbitrary Python callbacks`
- `raw OptiX callbacks`
- `true zero-copy`
- `non-Python embedding/C ABI`
- `app-specific native kernels`

## Next Required Work

Goal4743:

Update public V4 docs, tutorials, examples, and status pages to match this
bounded framing exactly.

Goal4744:

Run clean local gates and a selected GPU catalog/POD gate for the current V4
front door.

Goal4745:

Send the release-candidate packet to Claude and Antigravity. The packet must
include this file, Goal4739, Goal4740, Goal4741, and the custom predicate
Goal4715-4718 chain.

Goal4746:

Final release/tag decision. The only acceptable outcomes are:

- approve a bounded V4 eDSL/operator-pushdown release; or
- reject release and require more app-level wins.

## Claim Boundary

Goal4742 authorizes no final V4 tag. It authorizes only the internal framing
above for external review.

## Goal-Level Decision Audit

1. Was I being foolish?

No. The foolish action would be to hide the no-go rows and pretend the three
candidate apps plus custom predicate workflow mean the whole 10-app suite is
faster.

2. If yes, what action made the decision foolish?

Not applicable.

3. Was there another path?

Yes. Keep chasing known no-go rows with more POD runs. That would be avoidance,
not progress, unless a new route is designed first.

4. Can I now try a different path that actually solves the problem?

Yes. Move to release hardening under honest wording: docs, tests, external
review, and a final bounded-release decision.

## Non-Authorization

Goal4742 authorizes no final V4 tag, no all-benchmark speedup claim, no broad
V4-over-V2.14 claim, no arbitrary callback claim, no raw OptiX callback claim,
no true-zero-copy claim, no non-Python embedding/C ABI claim, and no
app-specific native kernel.
