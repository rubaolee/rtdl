# Goal3806 Active Example Versioned Helper Inventory

Date: 2026-06-07

## Purpose

Goals3800, 3802, and 3804 added current aliases for the safest app-facing
legacy helper names. Goal3806 records the remaining state so future cleanup does
not become blind renaming.

The inventory scans active example Python files under `examples/v2_0` for
function or class names containing version tokens such as `v2_5`, `v2_6`, or
`v2_8`. Historical docs and reports are intentionally out of scope.

## Current Inventory

The scan finds 32 versioned function/class names in active examples after
Goals3800/3802/3804.

| Category | Count | Status |
| --- | ---: | --- |
| Legacy compatibility shims now covered by current aliases | 15 | Acceptable; keep old names for reports/tests/artifacts. |
| RayDB internal implementation/protocol helpers | 11 | Acceptable; changing these would churn stable milestone evidence. |
| Remaining candidate aliases not yet migrated | 3 | Low-risk future cleanup, but not urgent for runtime correctness. |
| Named future/topology reference route | 1 | Preserve until the topology-reference lane is superseded. |
| RT-Graph/RayDB prepared-session protocol descriptors | 2 | Preserve as protocol/history descriptors unless a new generic facade is added. |

## Legacy Shims Already Covered By Current Aliases

| File | Legacy helpers | Current aliases |
| --- | --- | --- |
| `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | `v2_5_plan_payload`, `describe_triangle_counting_v2_6_numba_compact_mask_continuation`, `v2_6_numba_compact_mask_plan_payload`, `run_triangle_counting_v2_6_numba_compact_mask_preview` | `primitive_first_plan_payload`, `describe_triangle_counting_segmented_compact_mask_numba_continuation`, `segmented_compact_mask_numba_plan_payload`, `run_triangle_counting_segmented_compact_mask_numba_preview` |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | `v2_5_plan_payload`, `describe_rayjoin_v2_6_numba_compact_mask_continuation`, `v2_6_numba_compact_mask_plan_payload`, `run_rayjoin_v2_6_numba_compact_mask_preview` | `primitive_first_plan_payload`, `describe_rayjoin_segmented_compact_mask_numba_continuation`, `segmented_compact_mask_numba_plan_payload`, `run_rayjoin_segmented_compact_mask_numba_preview` |
| `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` | `describe_raydb_v2_5_primitive_first_plan`, `describe_raydb_v2_6_numba_neutral_continuation`, `run_raydb_v2_6_numba_neutral_continuation_preview`, `describe_raydb_v2_8_typed_stream_continuation`, `run_raydb_v2_8_typed_stream_continuation_preview` | `describe_raydb_primitive_first_plan`, `describe_raydb_numba_grouped_reduction_continuation`, `run_raydb_numba_grouped_reduction_continuation_preview`, `describe_raydb_grouped_reduction_typed_stream_continuation`, `run_raydb_grouped_reduction_typed_stream_continuation_preview` |
| `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | `describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream`, `run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview` | `describe_barnes_hut_grouped_vector_sum_typed_stream`, `run_barnes_hut_grouped_vector_sum_typed_stream_preview` |
| `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` | `describe_rtnn_v2_8_ranked_summary_typed_stream`, `run_rtnn_v2_8_ranked_summary_typed_stream_preview` | `describe_rtnn_ranked_summary_typed_stream`, `run_rtnn_ranked_summary_typed_stream_preview` |

## Preserved Internal Or Protocol Names

These names are not recommended as next cleanup targets because they are
internal implementation details, protocol descriptors, or historical evidence
keys:

- RayDB internal helpers such as `_run_raydb_v2_5_reference_fallback`,
  `_raydb_v2_5_present_group_outputs`, `_run_raydb_v2_5_triton_front_door`,
  `_v2_4_packed_buffer_descriptor`, `_v2_4_array_buffer_descriptor`,
  `_run_paper_rt_v2_5_primitive_first_result_mode`,
  `_paper_rows_from_v2_5_outputs`, and `_run_raydb_v2_5_triton_or_reference`.
- RayDB descriptive protocol helpers such as
  `describe_paper_rt_v2_4_prepared_session`,
  `describe_raydb_v2_5_partner_continuation`, and
  `run_raydb_v2_5_partner_continuation_preview`.
- Triangle counting's `describe_rt_graph_v2_4_prepared_session`, which is an
  RT-Graph protocol descriptor, not a current user-facing route.

## Remaining Candidate Aliases

These are the only remaining low-risk app-facing candidates after this cleanup
round:

| File | Candidate | Suggested current alias |
| --- | --- | --- |
| `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | `describe_v2_4_bounded_witness_session` | `describe_bounded_witness_session` |
| `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | `v2_5_plan_payload` | `primitive_first_plan_payload` |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | `run_rayjoin_v2_9_numba_side_aware_topology_reference` | Keep for now; this names a bounded topology-reference lane, not a promoted public route. |

## Boundary

- This is an inventory and classification report, not a release gate.
- No native engine code changed.
- No public speedup, RT-core speedup, package-install, zero-copy, paper
  reproduction, or release claim is authorized.
- Future cleanup should add aliases before renaming or removing old names.
