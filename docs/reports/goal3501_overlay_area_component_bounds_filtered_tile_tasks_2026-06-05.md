# Goal3501 Overlay Area Component-Bounds Filtered Tile Tasks

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3501 adds a prepared-component bounds filter for the simple-polygon
overlay-area tile-task route:

```text
--component-bounds-filter
```

Prepared component records now carry `(min_x, min_y, max_x, max_y)` bounds.
When the filter is enabled, component pairs whose bounds have non-positive
overlap are skipped before exact triangle-pair tile execution. This is a
generic zero-area rejection rule over prepared component payloads, not a
RayJoin-specific rule.

The filter applies to both routes:

- host component-pair/task planning;
- Goal3498's CuPy device tile-task planner.

## Pod Evidence

Artifact:
`docs/reports/goal3501_overlay_area_component_bounds_filtered_tile_tasks_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `ca5ab36a2cf6f9a17ce195e1e86fe6f94ea66c13`

Command shape:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --component-bounds-filter --device-tile-task-planner --device-planner-repeats 5 --resident-cupy-inputs --executor-repeats 5
```

Measured result:

- Relation rows: 4,543
- Bounds-positive candidate rows: 2,274
- Supported relation rows after component filtering: 2,149
- Component-bounds filtered rows: 122
- Topology/triangulation unsupported rows: 3
- Component-pair rows: 4,524
- Tile tasks: 11,617
- Planned/processed triangle pairs: 4,070,240
- Exact total area: 26.08321766231046
- Observed total area: 26.083217671538257
- Total absolute error: 9.227797193034348e-09
- Max relation absolute error: 1.0414236140121602e-09
- Positive row count match: true

Compared with Goal3498:

- Component-pair rows: 24,389 -> 4,524
- Tile tasks: 36,414 -> 11,617
- Triangle pairs: 7,655,567 -> 4,070,240
- Executor best repeat: 0.0251s -> 0.0146s

The component-bounds filter is a real exact-work reduction. It still does not
address the dominant CPU-owned prepared-payload cost, which remains about
6.89s on this pod run.

## Boundary

This goal does not change polygon topology handling, does not construct
prepared payloads on device, and does not claim full overlay geometry output.
It only reduces unnecessary exact triangle-pair work after CPU-owned prepared
payloads already exist. It does not authorize release, public speedup claims,
RT-core speedup claims, true-zero-copy wording, full overlay completion claims,
or app-specific native-engine behavior.
