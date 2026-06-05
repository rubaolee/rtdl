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

## Pod Evidence

Artifact:
`docs/reports/goal3495_overlay_area_device_active_shape_ordinals_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `315a781708023ee1e0bc17e39dbf68fc314c310e`

Command shape:

```text
--active-shapes-only --device-active-shape-ordinals --resident-cupy-inputs --executor-repeats 5
```

Observed public-CDB result:

- Relation rows: 4,543
- Unique active left shapes: 1,261 of 15,700
- Unique active right shapes: 949 of 949
- Component-pair rows: 39,947
- Tile tasks: 54,232
- Planned/processed triangle pairs: 9,653,005
- Exact total area: 26.08321766231046
- Observed total area: 26.08321767208671
- Total absolute error: 9.776250919912854e-09
- Max relation absolute error: 1.0414236140121602e-09
- Positive row count match: true

Timing:

- Relation discovery: 1.6626s
- Device active-shape ordinals: 0.0721s
- Full relation ordinal download for oracle/planning: 0.000062s
- Geometry build: 1.0248s
- Payload build: 7.7470s
- Planning: 0.2986s
- CuPy tile-task input preparation: 0.0958s
- CuPy tile-task executor best repeat: 0.0305s

The important lesson is not that this goal removes the whole bridge cost. At
this public-CDB scale, downloading 4,543 relation ordinals is already tiny.
Goal3495 makes the active-shape discovery contract generic and device-first,
but the remaining large cost is still CPU-owned geometry/payload construction,
especially triangulation and component expansion. The next performance leap
therefore needs device-resident component-pair/tile-task planning or a native
prepared-payload path, not another host-side ordinal-set optimization.

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
