# V4 Goal4654 Full App-Level POD Benchmark

Status: `goal4654_evidence_collected_not_release`
Profile: `serious`

```text
release_authorized: false
broad_v4_speed_claim_authorized: false
formal_tag_native_optix_purity: False
formal_release_blocker: v2_14/v3_0_2 OptiX libraries could not be built on this POD because OptiX SDK headers are absent; OptiX-dependent old-version rows use a declared V4 compatibility native library
```

## App Scorecard

| App | V4/V2.14 hot | V4/V3.0.2 hot | V3.0.2/V2.14 hot | RC OK | Parity |
| --- | ---: | ---: | ---: | --- | --- |
| `rt_dbscan` | 1.070x | 1.084x | 0.987x | True | True |
| `raydb_style` | 0.994x | 1.000x | 0.995x | True | True |
| `triangle_counting` | 15.548x | 1.117x | 13.924x | True | True |
| `librts_spatial_index` | 0.999x | 1.001x | 0.997x | True | True |

## Route And Provenance Notes

- V2.14 and V3.0.2 source trees are clean tag archives from git.
- V2.14 and V3.0.2 Embree libraries were built in their tag trees.
- V2.14 and V3.0.2 OptiX native libraries could not be built on this POD because OptiX SDK headers are absent.
- OptiX-dependent old-version rows therefore use a declared V4 compatibility native library; this blocks pure tag-native release authorization from Goal4654 alone.
- This benchmark is still useful for app front-door/runtime route comparison, but Goal4655 must keep the provenance caveat visible.

## Raw Rows

| Version | App | RC | Hot sec | Wall sec | Route | Native purity |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `v2_14` | `rt_dbscan` | 0 | 1.670616 | 1.670616 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v2_14` | `rt_dbscan_parity` | 0 | 0.590960 | 0.590960 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v2_14` | `raydb_style` | 0 | 0.005617 | 0.005617 | `paper_rt_optix_prepared_grouped_reduction` | False |
| `v2_14` | `triangle_counting` | 0 | 0.002916 | 0.002916 | `rt_graph_2a1_generic_rt` | False |
| `v2_14` | `librts_spatial_index` | 0 | 0.384257 | 4.173169 | `optix_aabb_index` | False |
| `v3_0_2` | `rt_dbscan` | 0 | 1.691960 | 1.691960 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v3_0_2` | `rt_dbscan_parity` | 0 | 0.625209 | 0.625209 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v3_0_2` | `raydb_style` | 0 | 0.005646 | 0.005646 | `paper_rt_optix_prepared_grouped_reduction` | False |
| `v3_0_2` | `triangle_counting` | 0 | 0.000209 | 0.000209 | `rt_graph_2a1_segmented_generic_rt` | False |
| `v3_0_2` | `librts_spatial_index` | 0 | 0.385239 | 3.664391 | `optix_aabb_index` | False |
| `v4_current` | `rt_dbscan` | 0 | 1.561345 | 1.582428 | `optix_rt_core_grouped_stream_numba_column_signature_3d` | True |
| `v4_current` | `rt_dbscan_parity` | 0 | 0.997810 | 0.998235 | `optix_rt_core_grouped_stream_numba_column_signature_3d` | True |
| `v4_current` | `raydb_style` | 0 | 0.005649 | 0.005649 | `paper_rt_optix_prepared_grouped_reduction` | True |
| `v4_current` | `triangle_counting` | 0 | 0.000188 | 0.000188 | `rt_graph_2a1_segmented_generic_rt` | True |
| `v4_current` | `librts_spatial_index` | 0 | 0.384818 | 3.748808 | `optix_aabb_index` | True |

## Non-Authorization

Goal4654 does not authorize public V4 release wording, whole-app speedup wording,
or a formal high-performance V4 claim. Goal4655 must analyze these rows with
the partner-migration and native-provenance locks intact.
