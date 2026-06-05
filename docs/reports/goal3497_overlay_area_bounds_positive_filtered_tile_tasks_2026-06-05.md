# Goal3497 Overlay Area Bounds-Positive Filtered Tile Tasks

Date: 2026-06-05

## Verdict

`pending-pod-evidence`.

Goal3497 adds an opt-in exact-area execution route for the public-CDB overlay
tile-task runner:

```text
--bounds-positive-filter
```

The route uses the existing generic CuPy continuation
`shape_pair_relation_bounds_overlap_area_cupy(..., group_by=None)` to compute
axis-aligned bounds-overlap area for each resident shape-pair relation row.
Rows with bounds-overlap area equal to zero are provably zero-area polygon
overlap rows, so the runner keeps them in the final row-aligned output as
zeros but skips Shapely geometry preparation, component-pair expansion, and
tile-task planning for those rows.

## Why This Exists

Goal3495 proved that computing unique active shape ordinals on device is
generic and correct, but also showed that full relation ordinal download is
not the bottleneck at public-CDB scale. The expensive work remains CPU-owned
geometry/payload construction and host component/tile planning.

This goal attacks that bottleneck with a generic geometric filter:

- consume the resident relation ordinal + geometry payload contract;
- compute a device-side bounds-overlap area upper-bound;
- execute exact prepared overlay-area tile tasks only for bounds-positive
  candidate rows;
- preserve one output area per original relation row.

## Boundary

This is still not device-resident tile-task planning. It is a better generic
candidate filter before the current host planner. This goal does not authorize release,
public speedup claims, RT-core speedup claims, true-zero-copy wording, full
overlay completion claims, or app-specific native-engine behavior.
