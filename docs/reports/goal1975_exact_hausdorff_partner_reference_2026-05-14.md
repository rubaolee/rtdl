# Goal1975 Exact Hausdorff Partner Reference

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

The v2 fixed-radius family evidence made `hausdorff_distance` look very fast,
but that row was a threshold-decision proxy: it answered whether every point
has a neighbor within a radius. That is useful, but it is not exact directed or
undirected Hausdorff distance.

Goal1975 adds an exact partner reference contract:

```text
directed_hausdorff_2d_partner_columns(source_point_columns,
                                      target_point_columns,
                                      partner="torch"|"cupy")
```

The helper computes pairwise distances in partner tensor space, reduces to the
nearest target per source point, then reduces those nearest distances with max.
This is the exact directed Hausdorff definition.

## Boundary

This is partner algebra, not native engine customization. It does not call
OptiX or claim RT-core acceleration. It upgrades the semantic quality of the v2
Hausdorff example from a threshold proxy to an exact partner-reference path.

The implementation is intentionally generic over point columns and does not
embed the authored app fixture into the native engine.

## Local Validation

Local Windows has neither Torch nor CuPy installed, so local validation checks:

- public helper/export surface;
- static absence of native app customization;
- `partner_exact` CLI and app path wiring;
- CPU/reference oracle path remains unchanged.

## Pod Timing

The RTX 2000 Ada pod ran the exact CuPy partner path with warmups and repeats:

| Copies | Points A | Points B | CPU Python exact median s | v2 CuPy exact median s | Ratio | Correct |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 128 | 512 | 512 | 0.325964 | 0.002686 | 0.00824x | yes |
| 512 | 2048 | 2048 | not run | 0.010296 | n/a | yes |
| 1024 | 4096 | 4096 | not run | 0.026813 | n/a | yes |

The CPU baseline was intentionally limited to the small row so this test would
not become a long O(N^2) Python run. Larger rows prove the exact CuPy partner
path remains functional and fast. This evidence does not authorize a broad whole-app speedup claim.

Artifact:

- `docs/reports/goal1975_pod_exact_hausdorff_partner_cupy_perf.json`
