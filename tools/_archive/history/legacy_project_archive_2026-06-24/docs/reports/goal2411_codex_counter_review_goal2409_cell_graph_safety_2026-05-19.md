# Goal2411 Codex Counter-Review: RT-DBSCAN Cell-Graph Safety

Date: 2026-05-19

Status: supersedes the unsafe part of the Goal2410 implementation contract

## Finding

While translating the Goal2410 plan into code, Codex found a correctness hole in
the proposed radius-sized cell-graph fast path.

The unsafe assumption was:

```text
when all points are core, a radius-sized grid cell can be treated as one graph
component node
```

That is false in 3-D.

If `cell_size == radius`, two points inside the same cell can be farther apart
than `radius` because the cell diagonal is `sqrt(3) * radius`. For example:

```text
radius = 1.0
p0 = (0.00, 0.00, 0.00)
p1 = (0.99, 0.99, 0.99)
distance(p0, p1) = 1.714...
```

Both points can fall in the same grid cell while not sharing a radius edge. With
larger point sets, two disconnected dense subclusters can also inhabit the same
radius-sized cell, and all points can still be core. A fast path that labels all
points in a cell by the cell component would merge disconnected components.

Claude's Goal2409 review correctly required cross-cell point-pair existence
checks, but it did not call out this same-cell disconnected-component case.

## What Remains Valid

The negative Goal2407 result remains valid: raw OptiX any-hit atomic union
should not be promoted.

The broad Candidate B instinct remains useful: the next continuation primitive
should reduce point-level union pressure by grouping work before union-find.

The app-agnostic boundary remains unchanged:

- no DBSCAN-native ABI;
- no hard-coded cluster expansion inside OptiX;
- generic fixed-radius graph/component vocabulary only.

## Corrected Candidate B'

The safe version is a clique-safe microcell graph:

```text
generic fixed-radius microcell component continuation
```

Use a microcell size that guarantees any two points in the same microcell are
within radius. A conservative choice is:

```text
microcell_size = radius / sqrt(3)
```

Then:

1. Build microcell ids from point coordinates.
2. Treat each occupied microcell as an internally connected clique.
3. Scan neighboring microcells out to:

   ```text
   neighbor_range = ceil(radius / microcell_size)
   ```

   For `radius / sqrt(3)`, this is `2`, so the 3-D neighbor stencil is
   `5 x 5 x 5`.
4. Union two microcells only after finding at least one actual cross-microcell
   point pair with `dist^2 <= radius^2`.
5. Label points by their microcell component.
6. Use this fast path only when all points are core.
7. Fall back to `radius_graph_components_3d_cupy_grid_partner_columns` whenever
   any point is non-core, or whenever the microcell path reports an unsupported
   condition.

This is still generic fixed-radius graph continuation, not a DBSCAN-specific
native primitive.

## Corrected Implementation Target

Goal2409 should not implement a radius-cell component graph.

It should implement either:

```python
radius_graph_components_3d_cupy_microcell_graph_partner_columns(...)
```

or keep the earlier public name while making the metadata explicit:

```python
radius_graph_components_3d_cupy_cell_graph_partner_columns(...)
metadata["cell_graph_granularity"] = "clique_safe_microcell"
```

Codex prefers the clearer public adapter name:

```python
radius_graph_components_3d_cupy_microcell_graph_partner_columns(...)
```

The RT-DBSCAN benchmark mode should likewise be:

```text
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

## Required Tests Before Pod Timing

Static tests must reject the unsafe interpretation:

- the implementation must not say that radius-sized cells are internally
  connected;
- metadata must include `cell_graph_granularity =
  "clique_safe_microcell"`;
- metadata must include `microcell_size_policy`;
- metadata must include `neighbor_cell_range`.

Functional tests should include at least these GPU cases when CuPy is available:

1. Same radius cell, disconnected points:

   ```text
   radius = 1.0
   min_neighbors = 1
   points = [(0, 0, 0), (0.99, 0.99, 0.99)]
   ```

   Expected: two separate positive component labels, not one merged label.

2. Two dense subclusters inside one radius-sized cell but separated by more than
   radius.

   Expected: two components.

3. Mixed-core input.

   Expected: fallback to the existing CuPy grid continuation and signature
   match against the CPU reference.

4. Dense all-core clustered input.

   Expected: microcell fast path activates and signature matches.

## Performance Risk

The corrected microcell stencil is wider than the original radius-cell stencil:

```text
5^3 = 125 neighboring microcell offsets
```

instead of:

```text
3^3 = 27 neighboring radius-cell offsets
```

That may reduce or erase the hoped-for speedup if microcell counts become too
large. This is acceptable: correctness wins first. If the microcell path is
correct but slower, the next fight should pivot to prepared CuPy grid hardening
or a compact edge-stream design.

## Updated Decision

Proceed only with the corrected microcell version of Candidate B.

Do not implement the unsafe radius-cell component graph.

No release claim, broad RT-core speedup claim, RT-DBSCAN paper reproduction
claim, or v2.x closure is authorized by this counter-review.
