# Goal1313: v1.5 Native Jaccard Device-Level Plan

Date: 2026-05-05

## Decision

Do not promote `polygon_set_jaccard` by adding another app-specific shortcut. The remaining v1.5 work should introduce a generic native bounded-collection plus guarded reduction ABI that Jaccard can use, while keeping the app diagnostic until that ABI is implemented and pod-validated.

## Current State

Completed:

- `COLLECT_K_BOUNDED` contract is defined and fail-closed.
- Python/generic collection wrapper fails before score reduction on overflow.
- Embree and OptiX native-assisted Jaccard produce exact summary parity on the pod.
- OptiX-slower reason is recorded: multi-pass candidate discovery plus host/native exact continuation dominates; this is not a monolithic GPU Jaccard kernel.

Still open:

- Native device-level fail-closed bounded collection.
- Native score reduction after complete candidate coverage.

## Required Native Collection ABI

The native collection ABI should be app-name-free. The final exported names
should be backend-keyed wrappers under the same contract:

```c
int rtdl_optix_collect_polygon_pair_candidates_bounded(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlPolygonPairCandidate* candidates_out,
    size_t candidate_capacity,
    size_t* emitted_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size);

int rtdl_embree_collect_polygon_pair_candidates_bounded(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlPolygonPairCandidate* candidates_out,
    size_t candidate_capacity,
    size_t* emitted_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size);
```

Required behavior:

- Candidate output is stable by `(left_polygon_id, right_polygon_id)` after normalization.
- Overflow is fail-closed: `overflowed_out=1`, no downstream score/reduction may run.
- Candidate rows may be a complete positive-candidate set or conservative complete superset, but must not silently truncate.
- The ABI names are backend-keyed because collection is traversal-backend-specific.
- Both wrappers must publish the same metadata contract: capacity, emitted count,
  overflow flag, and stable normalized candidate ordering.
- The ABI name is polygon-pair candidate collection, not Jaccard.

## Required Native Reduction ABI

The reduction step should also be app-name-free and backend-neutral:

```c
int rtdl_native_reduce_polygon_pair_exact_area_summary(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    const RtdlPolygonPairCandidate* candidates,
    size_t candidate_count,
    RtdlPolygonPairAreaSummary* summary_out,
    char* error_out,
    size_t error_size);
```

`polygon_set_jaccard` can compute its final ratio from this generic exact-area summary plus left/right set area. The reduction may initially be CPU-native, but it must be reached only after complete bounded collection. A later v2.0 implementation can move the reduction deeper onto the device.

Naming decision: collection is backend-keyed (`rtdl_optix_*`,
`rtdl_embree_*`) because candidate discovery depends on traversal backend
implementation. Reduction is backend-neutral (`rtdl_native_*`) because the
initial exact-area summary contract is shared after candidate IDs are collected.

## Promotion Gate

Jaccard may leave `diagnostic_blocked` only after:

| Gate | Requirement |
|---|---|
| Native bounded collection | Embree and OptiX expose fail-closed bounded candidate collection or equivalent backend-specific native wrappers |
| Overflow test | Capacity below emitted count fails before exact score reduction |
| No-overflow test | Capacity above emitted count produces exact summary parity |
| Same-contract evidence | Embree and OptiX use the same collection/reduction contract |
| Performance explanation | Existing Goal1312 slower diagnostic remains attached unless new evidence supersedes it |
| Public wording | Still blocked unless a separate 3-AI public wording review authorizes exact bounded wording |

## Non-Goals

- No Vulkan, HIPRT, or Apple RT work before v2.1.
- No broad GIS acceleration claim.
- No whole-app Jaccard speedup claim.
- No app-specific `rtdl_optix_run_polygon_set_jaccard_fast` path.
- No silent bounded collection truncation.

## Recommended Next Slice

Implement the native bounded candidate collector first for OptiX, because NVIDIA RT performance remains the top priority. In the same slice, add or stub the symmetric Embree bounded wrapper contract so same-contract evidence is not deferred. The Embree wrapper may initially call the existing native candidate path, but it must publish the same fail-closed metadata as OptiX before Jaccard can be considered for promotion.

After that, implement the guarded generic reduction wrapper and rerun the pod diagnostics.

## 3-AI Review Corrections

Claude and Gemini reviewed this plan. Gemini accepted it as written. Claude
accepted with three required fixes:

- Guard the Python/generic wrapper against empty score rows for non-empty
  candidate sets. This is fixed in `run_generic_polygon_set_jaccard_summary`.
- Resolve the Embree wrapper decision before the OptiX native slice. This plan
  now requires a symmetric Embree bounded wrapper contract in the same slice.
- Align ABI naming. This plan now documents backend-keyed collection wrappers
  and a backend-neutral reduction wrapper.
