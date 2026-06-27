# V4 Goal4669 Full App-Level POD Benchmark

Status: `goal4669_evidence_collected_not_release`
Profile: `serious`

```text
release_authorized: false
broad_v4_speed_claim_authorized: false
formal_high_performance_v4_authorized: false
formal_tag_native_optix_purity: False
formal_release_blocker: v2_14/v3_0_2 OptiX libraries could not be built on this POD because OptiX SDK headers are absent; OptiX-dependent old-version rows use a declared V4 compatibility native library
```

## App Scorecard

| App | V4/V2.14 hot | V4/V3.0.2 hot | V4/V2.14 primary wall | V4/V3.0.2 primary wall | RC OK | Parity |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `rt_dbscan` | 1.086x | 1.083x | 1.074x | 1.071x | True | True |
| `raydb_style` | 0.974x | 1.005x | 0.974x | 1.005x | True | True |
| `triangle_counting` | 4.055x | 0.948x | 4.055x | 0.948x | True | True |
| `librts_spatial_index` | 1.003x | 1.004x | 1.049x | 1.195x | True | True |
| `hausdorff_xhd` | 201581.860x | 2.546x | 114.824x | 1.112x | True | True |

## Hausdorff Boundary

- Hausdorff is included because Goal4667 passed the focused gate.
- The row is not a release by itself; it must remain classified inside the full app scorecard.
- The 1M coordinate-normalized correctness probe is required and recorded separately.

## Route And Provenance Notes

- V2.14 and V3.0.2 source trees are clean tag archives from git.
- V2.14 and V3.0.2 Embree libraries were built in their tag trees.
- V2.14 and V3.0.2 OptiX native libraries could not be built on this POD because OptiX SDK headers are absent.
- OptiX-dependent old-version rows therefore use a declared V4 compatibility native library; this blocks pure tag-native release authorization from Goal4669 alone.

## Raw Rows

| Version | App | RC | Hot sec | Wall sec | Route | Native purity |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `v2_14` | `rt_dbscan` | 0 | 1.679196 | 1.679196 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v2_14` | `rt_dbscan_parity` | 0 | 0.584614 | 0.584614 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v2_14` | `raydb_style` | 0 | 0.005527 | 0.005527 | `paper_rt_optix_prepared_grouped_reduction` | False |
| `v2_14` | `triangle_counting` | 0 | 0.000808 | 0.000808 | `rt_graph_2a1_generic_rt` | False |
| `v2_14` | `librts_spatial_index` | 0 | 0.384338 | 3.873740 | `optix_aabb_index` | False |
| `v2_14` | `hausdorff_xhd` | 0 | 809.965928 | 809.965928 | `embree` | False |
| `v3_0_2` | `rt_dbscan` | 0 | 1.674543 | 1.674543 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v3_0_2` | `rt_dbscan_parity` | 0 | 0.577055 | 0.577055 | `optix_rt_core_grouped_stream_cupy_column_signature_3d` | False |
| `v3_0_2` | `raydb_style` | 0 | 0.005698 | 0.005698 | `paper_rt_optix_prepared_grouped_reduction` | False |
| `v3_0_2` | `triangle_counting` | 0 | 0.000189 | 0.000189 | `rt_graph_2a1_segmented_generic_rt` | False |
| `v3_0_2` | `librts_spatial_index` | 0 | 0.384743 | 4.413821 | `optix_aabb_index` | False |
| `v3_0_2` | `hausdorff_xhd` | 0 | 0.010229 | 7.847416 | `optix_device_max_nearest` | False |
| `v4_current` | `rt_dbscan` | 0 | 1.546039 | 1.563495 | `optix_rt_core_grouped_stream_numba_column_signature_3d` | True |
| `v4_current` | `rt_dbscan_parity` | 0 | 0.972488 | 0.972967 | `optix_rt_core_grouped_stream_numba_column_signature_3d` | True |
| `v4_current` | `raydb_style` | 0 | 0.005672 | 0.005672 | `paper_rt_optix_prepared_grouped_reduction` | True |
| `v4_current` | `triangle_counting` | 0 | 0.000199 | 0.000199 | `rt_graph_2a1_segmented_generic_rt` | True |
| `v4_current` | `librts_spatial_index` | 0 | 0.383245 | 3.693070 | `optix_aabb_index` | True |
| `v4_current` | `hausdorff_xhd` | 0 | 0.004018 | 7.053993 | `optix_device_max_nearest` | True |
| `v4_current` | `hausdorff_xhd_correctness_1m` | 0 | 0.010495 | 32.660662 | `optix_device_max_nearest` | True |

## Non-Authorization

Goal4669 does not authorize public V4 release wording, broad speedup wording,
or a formal high-performance V4 claim. The output is input to the next decision analysis.
