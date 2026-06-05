# Goal3495 Overlay Area Device Active Shape Ordinals

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3495 adds a generic CuPy continuation,
`shape_pair_relation_active_shape_ordinals_cupy(...)`, over RTDL/OptiX
shape-pair relation ordinal columns. It computes unique left/right active shape
ordinals plus per-shape relation counts on device, without materializing the
full relation-row ordinal stream during active-shape discovery.

## Why This Exists

Goals3491-3494 made the public-CDB overlay-area continuation much more serious:

- Goal3492 proved full public-CDB scalar exact area over 4,543 relation rows,
  39,947 component-pair rows, 54,232 tile tasks, and 9,653,005 triangle pairs.
- Goal3493 reduced active payload construction by preparing only the 1,261
  active left shapes and 949 active right shapes.
- Goal3494 made the tile-task executor inputs resident in CuPy, with a best
  repeat of about 0.029s for the same 9,653,005 triangle-pair stream.

The remaining bridge is the relation-stream-to-payload path. Before this goal,
the public-CDB runner downloaded all active relation ordinals, then used Python
`set(...)` construction to discover which shapes were active. Goal3495 moves
the unique active-shape discovery step to CuPy over resident generic relation
ordinal columns.

## API Added

`shape_pair_relation_active_shape_ordinals_cupy(relation_columns)` returns a
`ShapePairActiveShapeOrdinalsCupyResult` with:

- `left_unique_ordinals`
- `right_unique_ordinals`
- `left_relation_counts`
- `right_relation_counts`
- metadata with explicit claim boundaries

The operation consumes the same generic relation-column contract used by the
other v2.8 relation continuations:
`shape_pair_relation_flags_with_ordinals_and_geometry_payload`.

## Runner Integration

`scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` now accepts:

```text
--active-shapes-only --device-active-shape-ordinals
```

When both flags are present, the runner computes unique active shape ordinals
on device and only materializes those smaller unique ordinal lists for
CPU-owned Shapely/payload preparation.

## Boundary

This goal does not make tile-task planning device-resident. It does not remove
the exact Shapely oracle path. It does not authorize release, public speedup
claims, RT-core speedup claims, true zero-copy wording, full overlay completion
claims, or app-specific native-engine behavior.

The honest remaining work is still:

- device-resident component-pair and tile-task planning, or an accepted native
  equivalent;
- native-vs-partner acceptance decision for the scalar overlay continuation;
- full overlay geometry output, which is separate from scalar exact area.

