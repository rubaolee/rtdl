# Goal1699 DB to Columnar Payload Native Migration

Date: 2026-05-11

## Verdict

DB family is now zero for lowercase native callable/export ABI names in
`src/native`.

The last real app-shaped native family was migrated from database/table naming
to generic columnar payload, multi-predicate scan, predicate match, and grouped
reduction terminology. Python-facing database semantics remain in Python; the
runtime helpers and ctypes structures keep their compatibility names while the
native binding strings now point at generic engine symbols.

## Renamed Native ABI

| Old native name | New native name |
| --- | --- |
| `rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute` | `rtdl_apple_rt_run_columnar_multi_predicate_scan_numeric_compute` |
| `rtdl_db_conjunctive_scan` | `rtdl_multi_predicate_scan` |
| `rtdl_db_match` | `rtdl_predicate_match` |
| `rtdl_hiprt_prepare_db_table` | `rtdl_hiprt_prepare_columnar_payload` |
| `rtdl_hiprt_destroy_prepared_db_table` | `rtdl_hiprt_destroy_prepared_columnar_payload` |
| `rtdl_hiprt_db_match_prepared` | `rtdl_hiprt_predicate_match_prepared` |
| `rtdl_hiprt_db_match` | `rtdl_hiprt_predicate_match` |
| `rtdl_embree_db_dataset_create` | `rtdl_embree_columnar_payload_create` |
| `rtdl_embree_db_dataset_create_columnar` | `rtdl_embree_columnar_payload_create_from_columns` |
| `rtdl_embree_db_dataset_destroy` | `rtdl_embree_columnar_payload_destroy` |
| `rtdl_embree_db_dataset_conjunctive_scan` | `rtdl_embree_columnar_payload_multi_predicate_scan` |
| `rtdl_embree_db_dataset_grouped_count` | `rtdl_embree_columnar_payload_grouped_reduction_count` |
| `rtdl_embree_db_dataset_grouped_sum` | `rtdl_embree_columnar_payload_grouped_reduction_sum` |
| `rtdl_optix_db_dataset_create` | `rtdl_optix_columnar_payload_create` |
| `rtdl_optix_db_dataset_create_columnar` | `rtdl_optix_columnar_payload_create_from_columns` |
| `rtdl_optix_db_dataset_destroy` | `rtdl_optix_columnar_payload_destroy` |
| `rtdl_optix_db_dataset_conjunctive_scan` | `rtdl_optix_columnar_payload_multi_predicate_scan` |
| `rtdl_optix_db_dataset_conjunctive_scan_count` | `rtdl_optix_columnar_payload_multi_predicate_scan_count` |
| `rtdl_optix_db_dataset_grouped_count` | `rtdl_optix_columnar_payload_grouped_reduction_count` |
| `rtdl_optix_db_dataset_grouped_sum` | `rtdl_optix_columnar_payload_grouped_reduction_sum` |
| `rtdl_optix_db_dataset_compact_summary_batch` | `rtdl_optix_columnar_payload_compact_summary_batch` |
| `rtdl_optix_db_get_last_phase_timings` | `rtdl_optix_columnar_payload_get_last_phase_timings` |
| `rtdl_optix_fill_db_compact_summary_phase` | `rtdl_optix_fill_columnar_compact_summary_phase` |
| `rtdl_optix_db_compact_summary_results_destroy` | `rtdl_optix_columnar_compact_summary_results_destroy` |
| `rtdl_vulkan_db_dataset_create` | `rtdl_vulkan_columnar_payload_create` |
| `rtdl_vulkan_db_dataset_create_columnar` | `rtdl_vulkan_columnar_payload_create_from_columns` |
| `rtdl_vulkan_db_dataset_destroy` | `rtdl_vulkan_columnar_payload_destroy` |
| `rtdl_vulkan_db_dataset_conjunctive_scan` | `rtdl_vulkan_columnar_payload_multi_predicate_scan` |
| `rtdl_vulkan_db_dataset_grouped_count` | `rtdl_vulkan_columnar_payload_grouped_reduction_count` |
| `rtdl_vulkan_db_dataset_grouped_sum` | `rtdl_vulkan_columnar_payload_grouped_reduction_sum` |

## Current Native Scan

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 9 |
| Strict regex occurrences | 14 |
| Known uppercase `RTDL_DB_*` constant false-positive symbols | 9 |
| Known uppercase `RTDL_DB_*` constant false-positive occurrences | 14 |
| Remaining app-shaped callable/export symbols | 0 |

The remaining strict regex hits are uppercase data-kind/operator constants such
as `RTDL_DB_KIND_INT64` and `RTDL_DB_OP_BETWEEN`; they are not lowercase native
callable/export ABI names.

## Compatibility Boundary

The Python API keeps database-oriented names such as `conjunctive_scan`,
`grouped_count`, `grouped_sum`, `PreparedEmbreeDbDataset`,
`PreparedHiprtDbTable`, `PreparedOptixDbDataset`, and
`PreparedVulkanDbDataset`. Those are compatibility names at the Python
orchestration layer, not native engine app customizations.

No pod was used for this local migration. This report is source and Python
binding evidence only; it does not provide hardware execution evidence.

## Release Boundary

The source ABI cleanup for the tracked app-shaped families is complete, but the
blocked wording remains unavailable until the result is independently reviewed
and pod/hardware validation exists:

```text
RTDL native internals are fully app-agnostic.
```
