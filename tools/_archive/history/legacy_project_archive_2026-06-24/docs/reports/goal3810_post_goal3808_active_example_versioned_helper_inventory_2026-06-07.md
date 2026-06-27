# Goal3810 Post-Goal3808 Active Example Versioned Helper Inventory

Date: 2026-06-07

## Purpose

Goal3806 recorded the active example versioned-helper state before the last two
low-risk app-facing aliases were added. Goal3808 then added current aliases for
Contact Manifold and LibRTS. Goal3810 refreshes the active-example inventory so
future cleanup starts from the current state.

The scan covers active Python example files under `examples/v2_0` and counts
function or class definitions whose names contain version tokens such as
`v2_4`, `v2_5`, `v2_6`, `v2_8`, or `v2_9`. Historical docs and reports are out
of scope.

## Current Inventory

The scan still finds 32 versioned function/class definitions. This is expected:
Goal3808 added aliases and preserved compatibility names rather than removing
old definitions.

| Category | Definition count | Status |
| --- | ---: | --- |
| Legacy compatibility shims now covered by current aliases | 19 | Acceptable; keep for reports, tests, and historical artifacts. |
| RayDB internal implementation/protocol helpers | 11 | Acceptable; changing these would churn stable milestone evidence. |
| RT-Graph prepared-session protocol descriptor | 1 | Acceptable; protocol/history descriptor, not a promoted user route. |
| Named future/topology reference route | 1 | Preserve until the topology-reference lane is superseded. |
| Remaining low-risk app-facing aliases not covered | 0 | Closed for this cleanup round. |

## Compatibility Shims Covered By Current Aliases

| File | Legacy helpers | Current aliases |
| --- | --- | --- |
| `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | `v2_5_plan_payload`, `describe_triangle_counting_v2_6_numba_compact_mask_continuation`, `v2_6_numba_compact_mask_plan_payload`, `run_triangle_counting_v2_6_numba_compact_mask_preview` | `primitive_first_plan_payload`, `describe_triangle_counting_segmented_compact_mask_numba_continuation`, `segmented_compact_mask_numba_plan_payload`, `run_triangle_counting_segmented_compact_mask_numba_preview` |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | `v2_5_plan_payload`, `describe_rayjoin_v2_6_numba_compact_mask_continuation`, `v2_6_numba_compact_mask_plan_payload`, `run_rayjoin_v2_6_numba_compact_mask_preview` | `primitive_first_plan_payload`, `describe_rayjoin_segmented_compact_mask_numba_continuation`, `segmented_compact_mask_numba_plan_payload`, `run_rayjoin_segmented_compact_mask_numba_preview` |
| `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` | `describe_raydb_v2_5_primitive_first_plan`, `describe_raydb_v2_6_numba_neutral_continuation`, `run_raydb_v2_6_numba_neutral_continuation_preview`, `describe_raydb_v2_8_typed_stream_continuation`, `run_raydb_v2_8_typed_stream_continuation_preview` | `describe_raydb_primitive_first_plan`, `describe_raydb_numba_grouped_reduction_continuation`, `run_raydb_numba_grouped_reduction_continuation_preview`, `describe_raydb_grouped_reduction_typed_stream_continuation`, `run_raydb_grouped_reduction_typed_stream_continuation_preview` |
| `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | `describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream`, `run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview` | `describe_barnes_hut_grouped_vector_sum_typed_stream`, `run_barnes_hut_grouped_vector_sum_typed_stream_preview` |
| `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` | `describe_rtnn_v2_8_ranked_summary_typed_stream`, `run_rtnn_v2_8_ranked_summary_typed_stream_preview` | `describe_rtnn_ranked_summary_typed_stream`, `run_rtnn_ranked_summary_typed_stream_preview` |
| `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | `describe_v2_4_bounded_witness_session` | `describe_bounded_witness_session` |
| `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | `v2_5_plan_payload` | `primitive_first_plan_payload` |

## Preserved Internal Or Protocol Names

These names are intentionally not next cleanup targets:

- RayDB internal helpers such as `_run_raydb_v2_5_reference_fallback`,
  `_raydb_v2_5_present_group_outputs`, `_run_raydb_v2_5_triton_front_door`,
  `_v2_4_packed_buffer_descriptor`, `_v2_4_array_buffer_descriptor`,
  `_run_paper_rt_v2_5_primitive_first_result_mode`,
  `_paper_rows_from_v2_5_outputs`, and `_run_raydb_v2_5_triton_or_reference`.
- RayDB protocol helpers such as `describe_paper_rt_v2_4_prepared_session`,
  `describe_raydb_v2_5_partner_continuation`, and
  `run_raydb_v2_5_partner_continuation_preview`.
- Triangle counting's `describe_rt_graph_v2_4_prepared_session`, which is an
  RT-Graph protocol descriptor rather than a current user-facing route.
- RayJoin's `run_rayjoin_v2_9_numba_side_aware_topology_reference`, which marks
  a bounded topology-reference lane and should remain versioned until that lane
  is superseded or promoted through a separate reviewed goal.

## Boundary

- This is an inventory and classification report, not a release gate.
- No source code changed in Goal3810.
- No native engine code changed.
- No public speedup, RT-core speedup, package-install, zero-copy, paper
  reproduction, or release claim is authorized.
- Compatibility names should stay available until a separate reviewed removal
  plan proves they are no longer used by reports, tests, artifacts, or
  historical scripts.

## Validation

- Local Windows alias/inventory slice: 28 tests passed.
- A5000 pod validation on clean `origin/main` at commit `7431931d`: the same
  28-test alias/inventory slice passed.
