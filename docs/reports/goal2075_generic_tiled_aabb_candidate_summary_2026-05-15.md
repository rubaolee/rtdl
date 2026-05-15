# Goal2075 Generic Tiled AABB Candidate-Summary Primitive

Date: 2026-05-15

Status: `implemented-pending-fresh-pod-timing`

## Purpose

Goal2075 addresses the polygon v2.0 design problem exposed by the final matrix:
`polygon_pair_overlap_area_rows` and `polygon_set_jaccard` should not build an
unbounded candidate-pair table before reducing overlap/Jaccard summaries.

The fix is a generic partner primitive, not a polygon-native customization:

- `aabb_tiled_candidate_pair_payload_2d_partner_columns`
- `aabb_pair_overlap_summary_2d_partner_columns`

The first adapter scans left/right 2D AABB columns in bounded tiles and emits
only overlapping pair indices plus the source AABB columns. The second adapter
reduces that compact pair payload into overlap summary columns.

## What Changed

- Added `aabb_tiled_candidate_pair_payload_2d_partner_columns` to
  `src/rtdsl/partner_adapters.py`.
- Exported it from `src/rtdsl/__init__.py`.
- Rewired `examples/rtdl_control_apps_cupy_rawkernel.py` so the `cupy_extent`
  polygon candidate backend uses the generic tiled AABB adapter rather than
  owning the candidate-pair builder itself.
- Rewired the `cupy_extent` oracle/validation helper to consume the same
  generic tiled AABB adapter, eliminating the old private duplicated candidate
  index builder.

The CLI name `cupy_extent` is retained for compatibility with existing reports
and scripts, but its internal meaning is now the generic tiled AABB
candidate-summary payload.

## Design Boundary

This solves the bounded candidate-summary design gap for axis-aligned extent
summary workloads:

- bounded tile memory instead of one dense all-pairs mask;
- compact positive-pair payload instead of a huge materialized candidate table;
- partner-owned columns, so the continuation can stay on the tensor side;
- native RTDL engine remains app-agnostic and is not given polygon-specific
  reduction logic.

This does not claim arbitrary polygon overlay, full witness-row materialization,
or broad whole-app speedup. The existing Goal2032 pod evidence showed the tiled
approach works and scales through 131,072 copies on an RTX A5000, but that
evidence used a dirty source label. Goal2075 makes the source path clean; a
fresh pod timing run is still required before promoting the final v2.0 matrix
rows.

## Prior Evidence To Retest

Goal2032 development evidence showed:

| Row | Copies | v2/v1.8 ratio |
| --- | ---: | ---: |
| `polygon_pair_overlap_area_rows` | 16,384 | 0.277x |
| `polygon_set_jaccard` | 16,384 | 0.228x |
| `polygon_pair_overlap_area_rows` | 32,768 | 0.397x |
| `polygon_set_jaccard` | 32,768 | 0.278x |
| `polygon_pair_overlap_area_rows` | 65,536 | 0.501x |
| `polygon_set_jaccard` | 65,536 | 0.428x |
| `polygon_pair_overlap_area_rows` | 131,072 | 0.771x |
| `polygon_set_jaccard` | 131,072 | 0.662x |

Goal2075 does not reuse those ratios as release evidence. It makes the source
implementation match the successful design so the next pod run can produce
current-commit evidence.

## Review Follow-Up Closure

The Claude Goal2076 review accepted the design with a boundary and noted one
cleanup risk: the performance path used the new generic adapter while the
oracle/validation path still used a private `_cupy_extent_candidate_indices`
helper. That duplicate helper has been removed, so both timed payload creation
and validation pair extraction now share
`aabb_tiled_candidate_pair_payload_2d_partner_columns`.

The Goal2075 test now also includes a small Torch/CPU functional edge test for
tile-boundary correctness and zero-width touching boxes. This remains a
source-level functional check, not pod timing evidence.

## Claim Boundary

Allowed:

- the generic tiled AABB candidate-summary primitive is implemented;
- the polygon control `cupy_extent` path now uses the generic primitive;
- the design avoids dense all-pairs candidate masks;
- source-tree tests validate the wiring and existing Goal2032 artifacts remain
  documented as prior development evidence.

Not allowed:

- v2.0 release authorization;
- not arbitrary polygon overlay; arbitrary polygon overlay is not solved;
- full segment/polygon witness-row materialization solved;
- broad RT-core or whole-app speedup claims;
- promotion of polygon rows in the final v2.0 matrix without fresh pod timing.

## Next Pod Command Shape

When a pod is available, rerun the polygon control app with current commit label:

```bash
PYTHONPATH=src:. python3 examples/rtdl_control_apps_cupy_rawkernel.py \
  --app all \
  --partner cupy \
  --candidate-backend cupy_extent \
  --copies 16384
```

Then repeat at `32768`, `65536`, and `131072` if memory permits, recording
current `git rev-parse HEAD`, GPU, driver, CUDA, and exact artifacts.
