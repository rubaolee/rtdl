# Goal1697 Polygon-To-Shape Native Migration

Date: 2026-05-11

Status: eighth local source migration from app-shaped native terminology to
generic primitive terminology; completes the `generic_geometry_anyhit` and
polygon/shape-pair portion of the Goal1672 release-surface cleanup.

## Verdict

Polygon family is now zero in the strict real native app-shaped symbol scan.

Goal1697 migrated the twenty-nine polygon-shaped native ABI names across Apple
RT, Embree, HIPRT, OptiX, Oracle, and Vulkan to generic shape terminology:

| Old native name | New native name |
| --- | --- |
| `rtdl_apple_rt_run_point_polygon_candidates_2d` | `rtdl_apple_rt_run_point_shape_candidates_2d` |
| `rtdl_apple_rt_run_segment_polygon_candidates_2d` | `rtdl_apple_rt_run_segment_shape_candidates_2d` |
| `rtdl_embree_run_segment_polygon_hitcount` | `rtdl_embree_run_segment_shape_hitcount` |
| `rtdl_embree_run_segment_polygon_anyhit_rows` | `rtdl_embree_run_segment_shape_anyhit_rows` |
| `rtdl_embree_collect_polygon_pair_candidates_bounded` | `rtdl_embree_collect_shape_pair_candidates_bounded` |
| `rtdl_hiprt_run_segment_polygon_hitcount` | `rtdl_hiprt_run_segment_shape_hitcount` |
| `rtdl_hiprt_run_segment_polygon_anyhit_rows` | `rtdl_hiprt_run_segment_shape_anyhit_rows` |
| `rtdl_hiprt_segment_polygon_2d` | `rtdl_hiprt_segment_shape_2d` |
| `rtdl_optix_run_segment_polygon_hitcount` | `rtdl_optix_run_segment_shape_hitcount` |
| `rtdl_optix_prepare_segment_polygon_hitcount_2d` | `rtdl_optix_prepare_segment_shape_hitcount_2d` |
| `rtdl_optix_run_prepared_segment_polygon_hitcount_2d` | `rtdl_optix_run_prepared_segment_shape_hitcount_2d` |
| `rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d` | `rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d` |
| `rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d` | `rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d` |
| `rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d` | `rtdl_optix_destroy_prepared_segment_shape_hitcount_2d` |
| `rtdl_optix_run_segment_polygon_anyhit_rows` | `rtdl_optix_run_segment_shape_anyhit_rows` |
| `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded` | `rtdl_optix_run_segment_shape_anyhit_rows_native_bounded` |
| `rtdl_optix_prepare_segment_polygon_anyhit_rows_2d` | `rtdl_optix_prepare_segment_shape_anyhit_rows_2d` |
| `rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d` | `rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d` |
| `rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d` | `rtdl_optix_destroy_prepared_segment_shape_anyhit_rows_2d` |
| `rtdl_optix_collect_polygon_pair_candidates_bounded` | `rtdl_optix_collect_shape_pair_candidates_bounded` |
| `rtdl_oracle_run_segment_polygon_hitcount` | `rtdl_oracle_run_segment_shape_hitcount` |
| `rtdl_oracle_run_segment_polygon_anyhit_rows` | `rtdl_oracle_run_segment_shape_anyhit_rows` |
| `rtdl_oracle_run_polygon_pair_overlap_area_rows` | `rtdl_oracle_run_shape_pair_overlap_area_rows` |
| `rtdl_oracle_run_polygon_set_jaccard` | `rtdl_oracle_run_shape_set_overlap_ratio` |
| `rtdl_oracle_refine_polygon_pair_overlap_area_rows_for_pairs` | `rtdl_oracle_refine_shape_pair_overlap_area_rows_for_pairs` |
| `rtdl_oracle_refine_polygon_set_jaccard_for_pairs` | `rtdl_oracle_refine_shape_set_overlap_ratio_for_pairs` |
| `rtdl_native_reduce_polygon_pair_exact_area_summary` | `rtdl_native_reduce_shape_pair_exact_area_summary` |
| `rtdl_vulkan_run_segment_polygon_hitcount` | `rtdl_vulkan_run_segment_shape_hitcount` |
| `rtdl_vulkan_run_segment_polygon_anyhit_rows` | `rtdl_vulkan_run_segment_shape_anyhit_rows` |

This is a local source migration only. It does not claim new performance
evidence, because no pod was used and no native hardware validation was run for
this local slice.

## Compatibility Boundary

Python-facing polygon semantics remain in Python:

- `segment_polygon_hitcount`, `segment_polygon_anyhit_rows`,
  `polygon_pair_overlap_area_rows`, and `polygon_set_jaccard` remain DSL
  predicate names;
- public Python helpers and compatibility wrappers retain polygon/GIS naming;
- ctypes row structs such as `RtdlPolygonRef`, `RtdlSegmentPolygonHitCountRow`,
  and `RtdlPolygonPairCandidate` remain data-shape names;
- only the native ABI strings and binding targets changed to shape names.

The native ABI now describes generic shape candidate and shape-pair operations,
while polygon/GIS meaning stays at the Python expression layer.

`_segment_shape_`, `_point_shape_`, `_shape_pair_`,
`_shape_set_overlap_ratio`, and `_reduce_shape_pair_exact_area_summary` are
present in `_GENERIC_NATIVE_SYMBOL_FRAGMENTS`. The old `_segment_polygon_`,
`_point_polygon_`, `_polygon_pair_`, and `_polygon_set_jaccard` fragments remain
app-shaped guards against reintroducing polygon-named native ABI.

## Counts Delta

Before Goal1697 (post-Goal1695):

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 68 |
| Strict regex occurrences | 131 |
| Remaining app-shaped callable/export symbols | 59 |
| `polygon` family unique symbols | 29 |

After Goal1697:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 39 |
| Strict regex occurrences | 73 |
| Known uppercase `RTDL_DB_*` constant false-positive symbols | 9 |
| Known uppercase `RTDL_DB_*` constant false-positive occurrences | 14 |
| Remaining app-shaped callable/export symbols | 30 |
| `polygon` family unique symbols | 0 |

Remaining real app-shaped native callable/export families:

| Family term | Unique symbols |
| --- | ---: |
| `db` | 30 |

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src'
py -3 -m unittest tests.goal1697_polygon_to_shape_native_migration_test
```

No pod validation was run. Native rebuild and runtime validation on Apple RT,
Embree, HIPRT, OptiX, Oracle, and Vulkan remain future evidence, not a claim
made by this report.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1697:

```text
RTDL has migrated the polygon-shaped native callable/export family to generic
shape and shape-pair native terminology. The remaining `db` native family still
blocks the full app-agnostic native-engine release claim.
```
