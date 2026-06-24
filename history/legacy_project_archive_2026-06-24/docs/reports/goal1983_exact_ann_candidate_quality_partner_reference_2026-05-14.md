# Goal1983 Exact ANN Candidate Quality Partner Reference

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

`ann_candidate_search` previously had a fast v2 row for fixed-radius candidate
coverage. That is useful as a candidate-filter decision, but it is not the
authored ANN quality question. The richer requirement is: given a user-selected
candidate subset, rerank candidates by exact nearest-neighbor distance and
compare that result to exact full-set nearest-neighbor search.

Goal1983 adds a v2 partner path to the ANN example:

```text
examples/v2_0/apps/ml/rtdl_ann_candidate_app.py --backend partner_exact_quality --partner torch|cupy
```

The implementation uses existing generic point-column partner algebra:

```text
top_k_nearest_points_2d_partner_columns(query_columns, candidate_columns, k=1)
top_k_nearest_points_2d_partner_columns(query_columns, full_search_columns, k=1)
```

The first call computes exact candidate-subset rerank rows. The second computes
the exact full-search reference rows. Python then compares recall and distance
ratio from those partner-owned outputs.

## Boundary

This is not an ANN index inside the native engine. It does not add a native
ANN ABI, training phase, recall/latency optimizer, graph index, IVF index, or
app-shaped engine continuation. Candidate-set construction remains user policy
outside the app-agnostic RTDL engine.

This goal does not authorize v2.0 release, broad whole-app acceleration,
arbitrary partner acceleration, or RT-core acceleration claims.

## Pod Timing

The RTX 2000 Ada pod ran the exact CuPy top-k quality path:

| Copies | Queries | Candidates | Full search | CPU Python quality median s | v2 CuPy exact quality median s | Ratio | Quality match |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 128 | 384 | 384 | 768 | 0.128558 | 0.004728 | 0.03677x | yes |
| 512 | 1536 | 1536 | 3072 | 2.249649 | 0.042325 | 0.01881x | yes |
| 1024 | 3072 | 3072 | 6144 | not run | 0.157958 | n/a | shape/quality recorded |
| 2048 | 6144 | 6144 | 12288 | not run | 0.632197 | n/a | shape/quality recorded |

The exact quality result remains the authored candidate-set behavior:
`recall_at_1 = 0.6666666666666666` and mean distance ratio near `3.6666666667`
for this synthetic candidate-selection policy.

Artifact:

- `docs/reports/goal1983_pod_exact_ann_candidate_quality_cupy_perf.json`

## Design Lesson

This slice shows the distinction we want for v2.0. RTDL can expose generic
point-column output and partner algebra can compute exact top-k quality metrics
without turning the native engine into an ANN engine. A future true ANN layer
would need a generic index-build/search contract, but that should be a separate
partner/runtime feature rather than hidden app customization.
