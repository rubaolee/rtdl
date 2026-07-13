# Consolidated Call For Review - X-HD Goals5130-5174 Level-B Author-Directed Route Packet

Date: 2026-07-08

Please strictly review the X-HD paper-app and RTDL system-extraction packet for
Goals5130-5174.

This supersedes the earlier Goals5130-5164 packet as the current review entry
point. The older packet and Goal5165-5174 addenda remain evidence, but this file
is the one-stop review map for the current state.

## Status Under Review

```text
Goals5130-5174: implemented; external review pending
```

Do not treat these goals as externally approved unless this consolidated review
approves them.

Requested status if approved:

```text
xhd_level_b_author_directed_system_route_evidence_complete__pending_exact_dataset_and_fair_performance
```

Meaning:

- Level B same-source representative evidence exists for Stanford graphics
  samples;
- RTDL gained generic grid/cell-MBR/frontier/nearest system APIs;
- the current route is aligned to the author-directed input1-to-input2 contract
  proved by Goal5126;
- the current multiscale route profile exists through full public res4;
- exact paper dataset reproduction is not complete;
- full paper figures are not reproduced;
- author-vs-RTDL speedup/parity ratio is not authorized.

## Prior Reviewed Baseline

The following earlier X-HD work has already been externally reviewed:

```text
Goals5111-5126: bounded same-input completion approved
Goals5127-5128: generic nearest pipeline extraction approved
```

This packet builds on that reviewed baseline but does not reopen it.

Critical prior fact:

```text
Goal5126 proved author HDResult = directed input1 -> input2, not symmetric max.
```

Discriminating fixture:

```text
directed_a_to_b = 0.5
directed_b_to_a = 9.0
symmetric = 9.0
author HDResult = 0.5
```

## Files To Review

### Registers, Manifests, Memory

```text
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/results/README.md
memory/progress.md
memory/todo.md
memory/roadmap.md
```

### Goal Reports

```text
history/internal_docs/goal5130_xhd_paper_target_matrix_2026-07-08.md
history/internal_docs/goal5131_xhd_dataset_provenance_acquisition_matrix_2026-07-08.md
history/internal_docs/goal5132_xhd_stanford_graphics_same_source_acquisition_2026-07-08.md
history/internal_docs/goal5133_xhd_ply_input_bridge_result_2026-07-08.md
history/internal_docs/goal5134_xhd_stanford_graphics_sample_ply_gate_packet_2026-07-08.md
history/internal_docs/goal5135_xhd_stanford_graphics_sample_ply_author_gate_result_2026-07-08.md
history/internal_docs/goal5136_xhd_stanford_graphics_sample_scaling_result_2026-07-08.md
history/internal_docs/goal5137_xhd_algorithmic_route_gap_analysis_2026-07-08.md
history/internal_docs/goal5138_generic_grid_cell_candidate_api_result_2026-07-08.md
history/internal_docs/goal5139_generic_nearest_state_frontier_result_2026-07-08.md
history/internal_docs/goal5140_generic_cell_mbr_traversal_abi_result_2026-07-08.md
history/internal_docs/goal5141_generic_cell_mbr_backend_feasibility_spike_2026-07-08.md
history/internal_docs/goal5142_backend_assisted_cell_mbr_frontdoor_result_2026-07-08.md
history/internal_docs/goal5143_optix_backend_local_probe_result_2026-07-08.md
history/internal_docs/goal5144_pod_optix_gate_result_2026-07-08.md
history/internal_docs/goal5145_dimension_generic_cell_mbr_frontdoor_result_2026-07-08.md
history/internal_docs/goal5146_native_3d_aabb_point_membership_result_2026-07-08.md
history/internal_docs/goal5147_backend_assisted_3d_cell_mbr_frontdoor_result_2026-07-08.md
history/internal_docs/goal5148_native_3d_cell_mbr_frontier_result_2026-07-08.md
history/internal_docs/goal5149_cell_mbr_frontier_nearest_continuation_result_2026-07-08.md
history/internal_docs/goal5150_xhd_cell_mbr_frontier_route_gate_result_2026-07-08.md
history/internal_docs/goal5151_xhd_sample256_cell_mbr_frontier_route_gate_result_2026-07-08.md
history/internal_docs/goal5152_nearest_cell_mbr_seeded_pruning_result_2026-07-08.md
history/internal_docs/goal5153_vectorized_nearest_cell_mbr_seed_result_2026-07-08.md
history/internal_docs/goal5154_xhd_seeded_performance_matrix_result_2026-07-08.md
history/internal_docs/goal5155_xhd_production_mode_and_route_profile_result_2026-07-08.md
history/internal_docs/goal5156_xhd_route_phase_median_profile_result_2026-07-08.md
history/internal_docs/goal5157_vectorized_frontier_nearest_continuation_result_2026-07-08.md
history/internal_docs/goal5158_vectorized_nearest_cell_mbr_seed_result_2026-07-08.md
history/internal_docs/goal5159_row_table_only_frontier_route_result_2026-07-08.md
history/internal_docs/goal5160_active_frontier_rows_result_2026-07-08.md
history/internal_docs/goal5161_numba_nearest_cell_mbr_seed_result_2026-07-08.md
history/internal_docs/goal5162_xhd_sample2048_post_numba_seed_profile_result_2026-07-08.md
history/internal_docs/goal5163_numba_frontier_nearest_continuation_result_2026-07-08.md
history/internal_docs/goal5164_xhd_post_goal5163_three_sample_matrix_result_2026-07-08.md
history/internal_docs/goal5165_xhd_sample4096_scaling_result_2026-07-08.md
history/internal_docs/goal5166_xhd_res4full_scaling_result_2026-07-08.md
history/internal_docs/goal5167_grid_cell_mbr_reduceat_result_2026-07-08.md
history/internal_docs/goal5168_parallel_nearest_cell_mbr_seed_result_2026-07-08.md
history/internal_docs/goal5169_streaming_frontier_capacity_retry_result_2026-07-08.md
history/internal_docs/goal5170_parallel_grouped_frontier_nearest_continuation_result_2026-07-08.md
history/internal_docs/goal5171_native_unsorted_frontier_row_order_result_2026-07-08.md
history/internal_docs/goal5172_native_inline_nearest_frontier_result_2026-07-08.md
history/internal_docs/goal5173_author_directed_route_mode_result_2026-07-08.md
history/internal_docs/goal5174_author_directed_multiscale_matrix_result_2026-07-08.md
```

### Existing Sub-Packets And Addenda

```text
history/internal_docs/call_for_review_goals5130_5164_xhd_level_b_system_route_packet_2026-07-08.md
history/internal_docs/call_for_review_goal5165_xhd_sample4096_scaling_2026-07-08.md
history/internal_docs/call_for_review_goal5166_xhd_res4full_scaling_2026-07-08.md
history/internal_docs/call_for_review_goal5167_grid_cell_mbr_reduceat_2026-07-08.md
history/internal_docs/call_for_review_goal5168_parallel_nearest_cell_mbr_seed_2026-07-08.md
history/internal_docs/call_for_review_goal5169_streaming_frontier_capacity_retry_2026-07-08.md
history/internal_docs/call_for_review_goal5170_parallel_grouped_frontier_nearest_continuation_2026-07-08.md
history/internal_docs/call_for_review_goal5171_native_unsorted_frontier_row_order_2026-07-08.md
history/internal_docs/call_for_review_goal5172_native_inline_nearest_frontier_2026-07-08.md
history/internal_docs/call_for_review_goal5173_author_directed_route_mode_2026-07-08.md
history/internal_docs/call_for_review_goal5174_author_directed_multiscale_matrix_2026-07-08.md
```

### Primary Implementation Files

```text
src/rtdsl/partner_continuations.py
src/rtdsl/optix_runtime.py
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_core.cpp
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_workloads.cpp
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_ply_sample.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
scripts/current_pod_ssh.py
```

### Focused Tests

```text
tests/goal5133_xhd_ply_input_bridge_test.py
tests/goal5134_xhd_ply_sample_gate_packet_test.py
tests/goal5138_generic_grid_cell_candidate_api_test.py
tests/goal5139_generic_nearest_state_frontier_api_test.py
tests/goal5140_generic_cell_mbr_traversal_abi_test.py
tests/goal5142_generic_cell_mbr_backend_assisted_frontdoor_test.py
tests/goal5144_cell_mbr_backend_assisted_gate_runner_test.py
tests/goal5145_dimension_generic_cell_mbr_frontdoor_test.py
tests/goal5146_optix_aabb_index_3d_point_membership_test.py
tests/goal5147_backend_assisted_3d_cell_mbr_frontdoor_test.py
tests/goal5148_native_3d_cell_mbr_frontier_test.py
tests/goal5149_cell_mbr_frontier_nearest_continuation_test.py
tests/goal5150_xhd_cell_mbr_frontier_route_gate_test.py
tests/goal5152_nearest_cell_mbr_seed_pruning_test.py
tests/goal5154_xhd_seeded_performance_matrix_test.py
tests/goal5155_xhd_production_validation_and_route_profile_test.py
tests/goal5156_xhd_route_phase_median_profile_test.py
tests/goal5157_vectorized_frontier_nearest_continuation_test.py
tests/goal5158_vectorized_nearest_cell_mbr_seed_test.py
tests/goal5159_row_table_only_frontier_route_test.py
tests/goal5160_active_frontier_rows_test.py
tests/goal5161_numba_nearest_cell_mbr_seed_test.py
tests/goal5162_xhd_sample2048_post_numba_seed_profile_test.py
tests/goal5163_numba_frontier_nearest_continuation_test.py
tests/goal5164_xhd_post_goal5163_three_sample_matrix_test.py
tests/goal5165_xhd_sample4096_scaling_test.py
tests/goal5166_xhd_res4full_scaling_test.py
tests/goal5167_grid_cell_mbr_reduceat_test.py
tests/goal5168_parallel_nearest_cell_mbr_seed_test.py
tests/goal5169_streaming_frontier_capacity_retry_test.py
tests/goal5170_parallel_grouped_frontier_nearest_continuation_test.py
tests/goal5171_unsorted_native_frontier_rows_test.py
tests/goal5172_native_inline_nearest_frontier_test.py
tests/goal5173_author_directed_route_mode_test.py
```

## Summary Of Goal Arc

### Goals5130-5136: Level-B Dataset And Correctness

Claim under review:

```text
exact paper inputs unavailable in current evidence
Stanford Dragon/HappyBuddha are Level B same-source representative inputs
PLY input is app-owned, not an RTDL core feature
author hd_exec and RTDL directed reference match sample256/1024/2048 HDResult
```

Representative values:

```text
sample256:
  author = 0.11612465232610703
  RTDL   = 0.11612464969699586
  diff   = 2.63e-9
  matched = true

sample1024:
  author = 0.1215052381157875
  RTDL   = 0.1215052343959716
  diff   = 3.72e-9
  matched = true

sample2048:
  author = 0.12136761099100113
  RTDL   = 0.12136761603270661
  diff   = 5.04e-9
  matched = true
```

Important boundary:

```text
These are not exact paper datasets.
Matching public Stanford sample HDResult is Level B representative evidence.
```

### Goals5137-5149: Generic System Route Extraction

Claim under review:

```text
X-HD pressure yielded generic RTDL APIs:
  grid cell-MBR descriptors
  nearest-state frontier split
  cell-MBR traversal ABI row table
  backend-assisted AABB membership front doors
  native OptiX 3-D AABB point-membership row producer
  native OptiX 3-D cell-MBR nearest-frontier row producer
  generic nearest-witness continuation from frontier rows
```

Native symbols under review:

```text
rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows
rtdl_optix_collect_cell_mbr_nearest_frontier_3d
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
```

Critical system-boundary question:

```text
Are these app-neutral cell/AABB/MBR/frontier primitives, or did X-HD semantics
leak into RTDL core?
```

### Goals5150-5153: Bounded X-HD Route And Seeded Work Reduction

Claim under review:

```text
bounded3D and sample256 route gates match author HDResult
generic nearest-cell-MBR seeding reduces point-distance continuation work
vectorized seed selection improves the route but is not a fair paper performance matrix
```

Sample256 work-reduction evidence:

```text
unseeded continuation: 65536 point-distance evaluations per direction
seeded route: about 1200 total seed+continuation evaluations per direction
```

### Goals5154-5170: Production-Mode Route Performance And Generic Optimizations

Claim under review:

```text
RTDL route performance improved substantially on representative samples,
but no author speedup/parity ratio is authorized.
```

Route evolution:

```text
sample1024:
  Goal5155 production route median             ~= 0.301 s
  Goal5156 median-profile baseline             ~= 0.289 s
  Goal5157 vectorized continuation             ~= 0.170 s
  Goal5158 vectorized seed                     ~= 0.114 s
  Goal5159 row-table-only frontier             ~= 0.108 s
  Goal5160 active-row-only frontier emission   ~= 0.079 s
  Goal5161 Numba nearest-cell-MBR seed         ~= 0.022 s
  Goal5164 three-sample lock point             ~= 0.025 s

sample2048:
  Goal5162 post-Numba-seed profile             ~= 0.059 s
  Goal5163 Numba frontier continuation         ~= 0.025 s
  Goal5164 three-sample lock point             ~= 0.025 s

full public res4:
  Goal5166 initial full-res4 route             ~= 0.059 s
  Goal5167 reduceat grid cell-MBR construction ~= 0.052 s
  Goal5168 parallel seed                       ~= 0.039 s
  Goal5169 frontier capacity retry             ~= 0.036 s
  Goal5170 grouped parallel continuation       ~= 0.034 s
```

Important boundary:

```text
Author Running.AvgTime, author process wall, RTDL route time, and RTDL total
time are different denominators. This packet does not authorize a performance
ratio or parity claim.
```

### Goals5171-5174: Current Author-Directed Route

Goal5171 adds an app-neutral native row-order policy:

```text
sorted control route median  ~= 0.03376 s
native-unsorted route median ~= 0.03309 s
```

Goal5172 adds generic native inline-nearest payload reduction:

```text
same-rebuild no-inline control route median ~= 0.03279 s
inline-nearest route median                 ~= 0.02916 s
continuation candidate evaluations          ~= 1.15M -> 7354
```

Goal5173 adds author-directed route mode based on Goal5126:

```text
symmetric-diagnostic inline route median ~= 0.02916 s
author-directed inline route median      ~= 0.01536 s
directed_b_to_a = null by design
```

Goal5174 records the current multiscale author-directed route:

| Case | Points A | Points B | Matched | Author AvgTime | RTDL Route | RTDL Total | Abs Diff |
|---|---:|---:|---|---:|---:|---:|---:|
| sample256 | 256 | 256 | true | 4.017 ms | 3.07 ms | 5.55 ms | 2.63e-09 |
| sample1024 | 1024 | 1024 | true | 5.001 ms | 5.82 ms | 19.02 ms | 3.72e-09 |
| sample2048 | 2048 | 2048 | true | 4.049 ms | 6.35 ms | 22.94 ms | 5.04e-09 |
| sample4096 | 4096 | 4096 | true | 4.276 ms | 10.63 ms | 36.50 ms | 6.27e-09 |
| res4full | 5205 | 7108 | true | 4.468 ms | 14.92 ms | 53.98 ms | 4.44e-09 |

All Goal5174 cases:

```text
backend = optix
validation_mode = author-only
frontier_inline_nearest = true
frontier_row_order = native
frontier_nearest_executor = numba_parallel
direction_mode = directed-a-to-b
directed_b_to_a = null
matched = true
ratios_authorized = false
```

## Key Result Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_route_optix_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_seeded_optix_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_seeded_vectorized_optix_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_performance_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_continuation_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_vectorized_seed_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_active_frontier_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_numba_seed_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_post_numba_seed_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_numba_continuation_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_2048_post_goal5163_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample4096_post_goal5163_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_post_goal5163_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5167_reduceat_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5168_parallel_seed_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5169_frontier_capacity_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_parallel_frontier_continuation_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5171_native_unsorted_frontier_rows_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_inline_nearest_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5173_author_directed_inline_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5173_author_directed_exact_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json
```

## Local Verification Reported

Most recent local validation after Goal5174:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json > $null
py -m unittest tests.goal5173_author_directed_route_mode_test \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test

Ran 12 tests OK
```

Earlier broader local/POD validations are recorded in the individual goal
reports.

## Claims Not Authorized

Do not approve any of the following unless stronger evidence exists outside
this packet:

- exact X-HD paper dataset reproduction;
- full X-HD paper reproduction;
- Figure 5-11 reproduction;
- author algorithm equivalence;
- denominator-aligned author-vs-RTDL speedup;
- author performance parity;
- treating Level B Stanford samples as exact paper inputs;
- treating author `Running.AvgTime` as directly comparable to RTDL route time;
- claiming the native cell-MBR backend is a complete fused X-HD RT-core clone;
- claiming directed mode computes symmetric Hausdorff.

## Review Questions

1. Are Goals5130-5174 correctly treated as implemented / review pending rather
   than already externally approved?
2. Does the packet preserve the Level B vs exact-paper-dataset boundary?
3. Are the Stanford Dragon/HappyBuddha samples acceptable same-source
   representative evidence under the stated limitations?
4. Is the app-owned PLY bridge correctly separated from RTDL core?
5. Are the author and RTDL correctness gates for the scale ladder sufficient for
   Level B representative correctness, including directed input1-to-input2 and
   min-bound preprocessing?
6. Does Goal5137 honestly identify the algorithmic gap between exact-reference
   Hausdorff and author X-HD RT-core behavior?
7. Are the new grid/cell-MBR/frontier APIs app-neutral enough to count as RTDL
   system improvements rather than X-HD-specific shortcuts?
8. Do the native OptiX symbols remain generic AABB/cell-MBR/frontier row or
   inline-nearest producers rather than X-HD kernels?
9. Is Goal5149's nearest-continuation API sufficiently generic, including its
   non-Hausdorff consumer?
10. Do Goals5150-5153 correctly claim work reduction and correctness, without
    overclaiming fair performance?
11. Does the Goal5154-5174 performance arc use honest regimes and denominators?
12. Is Goal5173's directed-only mode justified by Goal5126, or does it drop
    required symmetric functionality?
13. Is Goal5174 a valid current multiscale route profile under the no-ratio
    policy?
14. Are there any public-surface, manifest, memory, or report overclaims
    introduced by these goals?
15. If approved, what status label should the register use for Goals5130-5174?

## Requested Verdict Shape

Please answer with:

```text
Verdict:
  approve_goals5130_5174_xhd_level_b_author_directed_route_packet
  OR approve_with_required_amendments
  OR revise_before_next_goal
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 15 review questions:
  1. ...
  ...
  15. ...
```

Suggested approval label, if acceptable:

```text
approve_goals5130_5174_xhd_level_b_author_directed_route_packet__no_ratio_no_full_paper_claim
```
