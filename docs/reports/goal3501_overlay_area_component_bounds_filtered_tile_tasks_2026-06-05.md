# Goal3501 Overlay Area Component-Bounds Filtered Tile Tasks

Date: 2026-06-05

## Verdict

`pending-pod-evidence`.

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

## Boundary

This goal does not change polygon topology handling, does not construct
prepared payloads on device, and does not claim full overlay geometry output.
It only reduces unnecessary exact triangle-pair work after CPU-owned prepared
payloads already exist. It does not authorize release, public speedup claims,
RT-core speedup claims, true-zero-copy wording, full overlay completion claims,
or app-specific native-engine behavior.

