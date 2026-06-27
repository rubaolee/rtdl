# Goal3872 Prepared-Session Amortization Probe

Date: 2026-06-08

Status: A5000-validated performance triage.

## Purpose

Goal3872 measures a common pattern in the current benchmark packet: several
RTDL apps have tiny hot prepared-query cost but large one-time scene/setup cost.
Those rows look modest in cold file-backed CLI timing, but a learner writing a
real RTDL program should usually prepare once and issue many queries.

This goal does not change the native engine. It provides evidence for the next
major engineering direction: clearer prepared-session residency/front-door
support and benchmark reporting that separates cold setup from hot query work.

## A5000 Evidence

Artifact:

`docs/reports/goal3872_prepared_session_amortization_a5000/summary.json`

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`391b9648`

GPU:

`NVIDIA RTX A5000, 580.126.09`

The artifact reports empty `git_status_short`, `all_pass: true`, and
`all_claim_boundaries_clean: true`.

## Results

The probe used `repeat=50` and `warmup=5` for four scene-heavy prepared rows.

| App | Prepared family | Prepare sec | Hot query/request sec | Prepare/query ratio |
| --- | --- | ---: | ---: | ---: |
| Hausdorff/X-HD | `fixed_radius_threshold_2d` | 0.743487 | 0.010264 | 72.436x |
| LibRTS spatial index | `aabb_index_query_2d` | 0.402613 | 0.029665 | 13.572x |
| RTNN | `fixed_radius_neighbors_3d_ranked_summary` | 1.702647 | 0.000133 | 12757.870x |
| Triangle counting | `ray_triangle_weighted_any_hit_sum_3d` | 0.391839 | 0.000150 | 2605.920x |

Summary:

- row count: `4`;
- all rows pass: `true`;
- all claim boundaries clean: `true`;
- geomean prepare/query ratio: `425.19260550877135x`;
- maximum prepare/query ratio: `12757.870195394278x`.

## Interpretation

The next meaningful performance work should distinguish two concerns:

1. Hot prepared-query execution is already very fast for RTNN and triangle
   counting, and solid for Hausdorff/LibRTS.
2. Cold scene/setup time dominates file-backed CLI rows for RTNN, triangle
   counting, Hausdorff, and LibRTS.

Therefore the next non-minor runtime/design target is prepared-session
residency. In short: this is not another local per-query micro-optimization.
The useful direction is:

- make the user-facing prepared-session path easier and more explicit;
- provide benchmark examples that keep sessions alive across many queries;
- surface prepare/query amortization in reports and docs;
- consider persistent prepared-session caches only with explicit lifetime,
  invalidation, and claim-boundary rules.

This direction is app-agnostic. The prepared families are generic primitives,
and app interpretation stays in Python/examples.

## Boundary

Goal3872 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic
partner selection, AMD performance wording, paper-reproduction wording, or
app-specific native-engine logic.
