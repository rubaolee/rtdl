# Goal2939: RayJoin Row View to Partner Columns Pod Smoke

Date: 2026-06-01
Status: pod smoke passed

## Purpose

Goal2939 validates the Goal2938 generic `OptixRowView` to typed partner-column
bridge on the Spatial RayJoin benchmark route. The goal is to move the
row-bearing continuation boundary from app-shaped Python dictionaries toward
generic typed primitive payload columns.

Artifact:

`docs/reports/goal2939_rayjoin_row_view_partner_columns_pod/goal2939_rayjoin_row_view_partner_columns.json`

## Pod Evidence

- source commit: `fed661d370bd3ee899bc93b8b383ee7a586fbe58`
- source dirty: `[]`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- partner: `cupy`

| Workload | Expected rows | Observed rows | Fields |
| --- | ---: | ---: | --- |
| PIP | `6` | `6` | `point_id`, `shape_id`, `membership` |
| LSI | `1` | `1` | `left_id`, `right_id`, `intersection_point_x`, `intersection_point_y` |
| Overlay seed | `0` | `0` | `left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip` |

Each row used `host_stage_copy_used: true` and
`python_dict_row_materialization_used: false`.

## Result

This does not make the RayJoin row/overlay path fully device-resident. It does
make the next continuation cleaner: rows can cross from generic OptiX row views
into generic CuPy/Torch/Triton-carrier columns without app dictionaries or
RayJoin-specific native engine logic.

That is the right v2.5 stepping stone toward the v3 device-resident row-stream
handoff: users get a consistent typed payload-column path now, while the
remaining performance work is explicit and measurable.

## Boundary

Goal2939 does not authorize v2.5 release, public speedup wording, broad RT-core
wording, whole-app speedup wording, true-zero-copy wording, device-resident
handoff wording, automatic partner-selection wording, package-install wording,
paper-reproduction wording, or app-specific native engine logic.
