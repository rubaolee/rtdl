# Goal1975 Exact Hausdorff Partner Reference

Date: 2026-05-14

Status: implementation slice; pod timing pending

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

Pod CuPy timing is the next step.
