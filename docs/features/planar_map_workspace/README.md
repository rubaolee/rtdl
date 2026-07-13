# Planar-Map Workspace

## Purpose

The planar-map workspace is a reusable OptiX workspace for applications that
need both CDB/planar-map line-segment intersection and directed point-location
on the same pair of planar maps.

Use it when your app has this shape:

```text
load and pack two CDB/planar-map inputs once
-> prepare LSI once
-> prepare point-location in both directions once
-> run app-owned continuation or output assembly
```

The workspace is a lifecycle helper around public RTDL primitives. It is not a
RayJoin overlay helper, and it does not expose raw OptiX callbacks.

## Public API

```python
from rtdsl import prepare_planar_map_workspace_2d_optix

with prepare_planar_map_workspace_2d_optix("left_Point.cdb", "right_Point.cdb") as workspace:
    lsi_pairs = workspace.run_lsi_pair_id_rows()
    left_faces = workspace.run_left_points_in_right()
    right_faces = workspace.run_right_points_in_left()
```

The main methods are:

| Method | Result |
| --- | --- |
| `run_lsi_pair_id_rows()` | host row view with `left_id` and `right_id` for accepted planar-map segment intersections |
| `run_lsi_raw()` | full host row view for callers that need full intersection payloads |
| `run_left_points_in_right()` | point-location rows for left-map points against the prepared right-map locator |
| `run_right_points_in_left()` | point-location rows for right-map points against the prepared left-map locator |
| `metadata()` | setup timings, input sizes, and claim boundaries |

## Example

Run the small workspace example from the repository root:

```bash
python examples/current/features/spatial/rtdl_planar_map_workspace_lsi_pip.py
```

The example writes two tiny CDB-like fixtures, prepares one workspace, runs LSI
and point-location as separate primitive calls, and finishes with a small
Python or Numba continuation that summarizes the rows.

## Boundary

This workspace is generic at the RTDL API boundary:

- it does not import the bundled RayJoin compatibility helper;
- it does not implement polygon overlay;
- it does not place application continuation inside RTDL core;
- it does not authorize a broad performance claim.

Application code still owns topology-specific assembly, output formatting, and
paper-reproduction compatibility rules.

## Related Features

- [LSI: Line Segment Intersection](../lsi/README.md)
- [Point-in-Polygon / Point Location](../pip/README.md)
- [Overlay](../overlay/README.md)
