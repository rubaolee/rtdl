# Embree Baseline Contracts

This document is the frozen Step 1 and Step 2 contract for the RTDL Embree baseline.

It records:

- the fixed workload set,
- the allowed precision mode,
- the shared runtime ABI expectations,
- the input and output record contracts,
- the cross-backend comparison policy,
- the named representative datasets for baseline work.

The machine-readable source of truth is:

- `src/rtdsl/baseline_contracts.py`

## Frozen Baseline Workload Set

The Embree baseline workload set is fixed to:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

No other workload is part of baseline completion.

## Baseline Precision Policy

The baseline precision mode is:

- `float_approx`

Interpretation:

- CPU and Embree both operate under the same float-based semantics.
- The baseline does not claim robust or exact computational geometry.
- Cross-backend comparison uses:
  - exact comparison for IDs, flags, and integer counts,
  - epsilon-based comparison for float-valued intersection coordinates.

Current comparison tolerances:

- absolute tolerance: `1e-6`
- relative tolerance: `1e-6`

Additional frozen rules:

- `point_in_polygon` supports only `boundary_mode="inclusive"` in both the CPU and Embree runtimes.
- `segment_polygon_hitcount` and `point_nearest_segment` remain part of the baseline, but their current local execution contract is `native_loop` rather than BVH traversal.

## Shared Runtime ABI

The shared ABI rule is:

- RTDL source kernels define the workload,
- `run_cpu(...)` and `run_embree(...)` accept the same logical input records,
- both backends emit the same logical output rows.

This means the baseline contract is defined at the RTDL logical record layer, not at a backend-specific memory-struct layer.

## Workload Contracts

### `lsi`

Inputs:

- `left`: geometry `segments`, role `probe`
- `right`: geometry `segments`, role `build`

Layout contract:

- layout name: `Segment2D`
- layout fields: `x0, y0, x1, y1, id`

Logical input record fields:

- `id, x0, y0, x1, y1`

Emit fields:

- `left_id`
- `right_id`
- `intersection_point_x`
- `intersection_point_y`

Predicate:

- `segment_intersection`

Comparison mode:

- exact for IDs
- float tolerance for intersection coordinates

Representative datasets:

- `authored_lsi_minimal`
- `tests/fixtures/rayjoin/br_county_subset.cdb`

### `pip`

Inputs:

- `points`: geometry `points`, role `probe`
- `polygons`: geometry `polygons`, role `build`

Layout contract:

- point layout: `Point2D`
- polygon layout: `Polygon2DRef`

Layout fields:

- points: `x, y, id`
- polygons: `vertex_offset, vertex_count, id`

Logical input record fields:

- points: `id, x, y`
- polygons: `id, vertices`

Emit fields:

- `point_id`
- `polygon_id`
- `contains`

Predicate:

- `point_in_polygon`

Comparison mode:

- exact

Representative datasets:

- `authored_pip_minimal`
- `tests/fixtures/rayjoin/br_county_subset.cdb`

### `overlay`

Inputs:

- `left`: geometry `polygons`, role `probe`
- `right`: geometry `polygons`, role `build`

Layout contract:

- both inputs use `Polygon2DRef`
- layout fields: `vertex_offset, vertex_count, id`

Logical input record fields:

- `id, vertices`

Emit fields:

- `left_polygon_id`
- `right_polygon_id`
- `requires_lsi`
- `requires_pip`

Predicate:

- `overlay_compose`

Comparison mode:

- exact

Representative datasets:

- `authored_overlay_minimal`
- `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb`

### `ray_tri_hitcount`

Inputs:

- `rays`: geometry `rays`, role `probe`
- `triangles`: geometry `triangles`, role `build`

Layout contract:

- ray layout: `Ray2D`
- triangle layout: `Triangle2D`

Layout fields:

- rays: `ox, oy, dx, dy, tmax, id`
- triangles: `x0, y0, x1, y1, x2, y2, id`

Logical input record fields:

- rays: `id, ox, oy, dx, dy, tmax`
- triangles: `id, x0, y0, x1, y1, x2, y2`

Emit fields:

- `ray_id`
- `hit_count`

Predicate:

- `ray_triangle_hit_count`

Comparison mode:

- exact

Representative datasets:

- `authored_ray_tri_minimal`
- synthetic generators in `examples/rtdl_ray_tri_hitcount.py`

## Review Rule

Any future implementation review for the Embree baseline should verify:

- kernels match these frozen contracts,
- `run_cpu(...)` and `run_embree(...)` both honor them,
- new tests and benchmark code do not silently redefine them.
