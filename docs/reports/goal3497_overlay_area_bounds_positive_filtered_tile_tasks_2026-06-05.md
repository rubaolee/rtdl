# Goal3497 Overlay Area Bounds-Positive Filtered Tile Tasks

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

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

## Pod Evidence

Artifact:
`docs/reports/goal3497_overlay_area_bounds_positive_filtered_tile_tasks_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `644184ad8ffff19e6585d670358497632aab6ca3`

Command shape:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --resident-cupy-inputs --executor-repeats 5
```

Measured result:

- Relation rows: 4,543
- Bounds-positive candidate rows: 2,274
- Prepared left shapes: 1,106 of 15,700
- Prepared right shapes: 949 of 949
- Component-pair rows: 24,389
- Tile tasks: 36,414
- Planned/processed triangle pairs: 7,655,567
- Exact total area: 26.08321766231046
- Observed total area: 26.083217671827335
- Total absolute error: 9.516874399650987e-09
- Max relation absolute error: 1.0414233919675553e-09
- Positive row count match: true

Compared with Goal3495, the filter reduced:

- candidate/planned rows: 4,543 -> 2,274
- prepared left shapes: 1,261 -> 1,106
- component-pair rows: 39,947 -> 24,389
- tile tasks: 54,232 -> 36,414
- triangle pairs: 9,653,005 -> 7,655,567
- payload build: 7.7470s -> 6.8054s
- planning: 0.2986s -> 0.2113s
- CuPy input preparation: 0.0958s -> 0.0785s
- best resident executor repeat: 0.0305s -> 0.0275s

The improvement is real but bounded. It confirms that a generic device-side
candidate filter can reduce downstream exact-area work, while also confirming
that CPU-owned prepared payload construction remains the dominant cost.
Further large wins need device-resident component-pair/tile-task planning or a
native prepared-payload route.

## Boundary

This is still not device-resident tile-task planning. It is a better generic
candidate filter before the current host planner. This goal does not authorize release,
public speedup claims, RT-core speedup claims, true-zero-copy wording, full
overlay completion claims, or app-specific native-engine behavior.
