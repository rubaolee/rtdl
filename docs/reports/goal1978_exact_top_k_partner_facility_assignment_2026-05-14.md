# Goal1978 Exact Top-K Partner Facility Assignment

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

The v2 all-app table previously treated `facility_knn_assignment` as a fast
fixed-radius threshold row. That row is useful for service-coverage decisions,
but it is not the authored app's richer KNN requirement: ranked nearest depots
and fallback choices per customer.

Goal1978 adds a generic partner continuation:

```text
top_k_nearest_points_2d_partner_columns(query_point_columns,
                                        candidate_point_columns,
                                        k=...)
```

The helper computes exact pairwise squared distances in the selected partner
runtime, sorts by distance with candidate-ID tie-breaking, and emits generic
columns:

- `query_ids`
- `neighbor_ids`
- `distances`
- `neighbor_rank`

The facility app now exposes `--backend partner_exact --partner torch|cupy`.
That path materializes the same public rows as the CPU/Embree KNN path but keeps
the ranked-neighbor computation in partner tensor algebra.

## Boundary

This is not native engine customization. The native engine receives no
facility-specific continuation, no depot-specific ABI, and no app-shaped
primitive. It is also not an RT-core speedup claim: this first exact row is a
partner-reference continuation over generic point columns.

The claim is narrower but more semantically honest than the old threshold row:

- fixed-radius threshold: faster service-coverage decision;
- exact top-k partner row: ranked nearest-depot fallback choices.

## Local Validation

Local Windows validation covers the public surface and CPU path:

- `top_k_nearest_points_2d_partner_columns` is exported from `rtdsl`;
- the adapter implements Torch and CuPy branches with distance-then-ID ranking;
- `examples/rtdl_facility_knn_assignment.py` accepts `--backend partner_exact`;
- the existing CPU reference path still runs.

## Pod Timing

The RTX 2000 Ada pod ran the exact CuPy top-k path with warmups and repeats:

| Copies | Customers | Depots | Rows | CPU Python exact median s | v2 CuPy exact median s | Ratio | Correct shape |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 128 | 512 | 512 | 1536 | 0.101372 | 0.004628 | 0.04565x | yes |
| 512 | 2048 | 2048 | 6144 | not run | 0.031409 | n/a | yes |
| 1024 | 4096 | 4096 | 12288 | not run | 0.114787 | n/a | yes |

The CPU baseline was intentionally limited to the smallest exact row because
the baseline is O(customers x depots) Python. The larger rows prove that the
same exact partner contract scales on the pod and emits the expected K=3 row
shape.

Artifact:

- `docs/reports/goal1978_pod_exact_top_k_facility_cupy_perf.json`

## Release Boundary

This goal improves the v2 semantic story for facility KNN, but it does not
authorize v2.0 release, broad whole-app speedup claims, arbitrary partner
program acceleration claims, or RT-core acceleration claims.
