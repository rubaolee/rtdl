# Consolidated Call For Review - X-HD Goals5130-5164 Level-B System Route Packet

Date: 2026-07-08

Please strictly review the X-HD paper-app and RTDL system-extraction packet for
Goals5130-5164.

This packet covers the work after the externally reviewed X-HD bounded
same-input line (Goals5111-5128). It moves from bounded fixtures into
same-source Stanford graphics samples and then extracts/optimizes a generic
cell-MBR/frontier/nearest route. It is intentionally **not** a full X-HD paper
reproduction claim.

## Status Under Review

```text
Goals5130-5164: implemented; external review pending
```

Do not treat these goals as externally approved unless this consolidated review
approves them. This packet asks whether the implemented evidence is sufficient
to classify the current line as:

```text
xhd_level_b_same_source_system_route_evidence_complete__pending_exact_dataset_and_fair_performance
```

Meaning:

- Level B same-source representative evidence exists for Stanford graphics
  samples;
- RTDL has gained generic grid/cell-MBR/frontier/nearest system APIs;
- a current X-HD representative route lock point exists;
- exact paper dataset reproduction is not complete;
- full paper figures are not reproduced;
- author-vs-RTDL speedup/parity ratio is not authorized.

## Prior Reviewed Baseline

The following earlier X-HD packet has already been externally reviewed:

```text
Goals5111-5126: bounded same-input completion approved
Goals5127-5128: generic nearest pipeline extraction approved
```

This packet builds on that reviewed baseline but does not reopen it.

## Files To Review

### Registers And Manifests

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
```

### Existing Sub-Packets

```text
history/internal_docs/call_for_review_goals5130_5131_xhd_target_and_dataset_matrices_2026-07-08.md
history/internal_docs/call_for_review_goals5130_5133_xhd_full_reproduction_feasibility_node_2026-07-08.md
history/internal_docs/call_for_review_goals5130_5134_xhd_level_b_graphics_feasibility_packet_2026-07-08.md
history/internal_docs/call_for_review_goals5130_5135_xhd_level_b_graphics_author_gate_packet_2026-07-08.md
history/internal_docs/call_for_review_goals5130_5136_xhd_level_b_graphics_scaling_packet_2026-07-08.md
```

### Key Implementation Files

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
```

### Result Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_acquisition_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_rtdl_route_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample1024_rtdl_route_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample2048_rtdl_route_summary.json
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

Native symbols under review include:

```text
rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows
rtdl_optix_collect_cell_mbr_nearest_frontier_3d
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

### Goals5154-5164: Production-Mode Route Performance And Profiling

Claim under review:

```text
RTDL route performance improved substantially on representative samples,
but no author speedup/parity ratio is authorized.
```

Route evolution:

```text
sample1024:
  Goal5155 production route median            ~= 0.301 s
  Goal5156 median-profile baseline             ~= 0.289 s
  Goal5157 vectorized continuation             ~= 0.170 s
  Goal5158 vectorized seed                     ~= 0.114 s
  Goal5159 row-table-only frontier             ~= 0.108 s
  Goal5160 active-row-only frontier emission   ~= 0.079 s
  Goal5161 Numba nearest-cell-MBR seed         ~= 0.022 s
  Goal5164 current route lock point            ~= 0.025 s

sample2048:
  Goal5162 post-Numba-seed profile             ~= 0.059 s
  Goal5163 Numba frontier continuation         ~= 0.025 s
  Goal5164 current route lock point            ~= 0.025 s
```

Current lock point from Goal5164:

```text
sample256:
  matched = true
  author Running.AvgTime = 3.991 ms
  RTDL route median = 0.009128741919994354 s
  RTDL total median = 0.011155426502227783 s

sample1024:
  matched = true
  author Running.AvgTime = 4.032 ms
  RTDL route median = 0.025217324495315552 s
  RTDL total median = 0.039307110011577606 s

sample2048:
  matched = true
  author Running.AvgTime = 4.13 ms
  RTDL route median = 0.025157354772090912 s
  RTDL total median = 0.03893127292394638 s

ratios_authorized = false
```

Important boundary:

```text
Author Running.AvgTime, author process wall, RTDL route time, and RTDL total
time are different denominators. This packet does not authorize a performance
ratio or parity claim.
```

## Local Verification Reported

Latest focused local validation from the handoff:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_seeded_sample256_1024_2048_post_goal5163_matrix_pod.json > $null
py -m unittest tests.goal5164_xhd_post_goal5163_three_sample_matrix_test \
  tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5162_xhd_sample2048_post_numba_seed_profile_test \
  tests.goal5161_numba_nearest_cell_mbr_seed_test \
  tests.goal5160_active_frontier_rows_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test

Ran 23 tests OK
```

POD validation reported:

```text
Goal5163 POD focused tests: Ran 14 tests OK (skipped=1)
Goal5162/5163/5164 POD matrix commands: all returned 0 and matched=true
```

## Claims Not Authorized

Do not approve any of the following unless you find stronger evidence outside
this packet:

- exact X-HD paper dataset reproduction;
- full paper reproduction;
- Figure 5-11 reproduction;
- author algorithm equivalence;
- denominator-aligned author-vs-RTDL speedup;
- author performance parity;
- treating Level B Stanford samples as exact paper inputs;
- treating author `Running.AvgTime` as directly comparable to RTDL route time;
- claiming the native cell-MBR backend is a complete fused X-HD RT-core clone.

## Review Questions

1. Are Goals5130-5164 correctly treated as implemented / review pending rather
   than already externally approved?
2. Does the packet preserve the Level B vs exact-paper-dataset boundary?
3. Are the Stanford Dragon/HappyBuddha samples acceptable same-source
   representative evidence under the stated limitations?
4. Is the app-owned PLY bridge correctly separated from RTDL core?
5. Are the author and RTDL correctness gates for sample256/1024/2048 sufficient
   for Level B representative correctness, including the directed input1-to-input2
   contract and min-bound preprocessing?
6. Does Goal5137 honestly identify the algorithmic gap between exact-reference
   Hausdorff and author X-HD RT-core behavior?
7. Are the new grid/cell-MBR/frontier APIs app-neutral enough to count as RTDL
   system improvements rather than X-HD-specific shortcuts?
8. Do the native OptiX symbols introduced in Goals5146 and 5148 remain generic
   AABB/cell-MBR/frontier row producers rather than X-HD kernels?
9. Is Goal5149's nearest-continuation API sufficiently generic, including its
   non-Hausdorff consumer?
10. Do Goals5150-5153 correctly claim work reduction and correctness, without
    overclaiming fair performance?
11. Does the Goal5154-5164 performance arc use honest regimes and denominators?
12. Is the current Goal5164 matrix a valid RTDL route lock point?
13. Should the packet explicitly require another profile before choosing the
    next performance target, rather than attacking a stale bottleneck?
14. Are there any public-surface, manifest, or memory overclaims introduced by
    these goals?
15. If approved, what status label should the register use for Goals5130-5164?

## Requested Verdict Shape

Please answer with:

```text
Verdict:
  approve_goals5130_5164_xhd_level_b_system_route_packet
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
approve_goals5130_5164_xhd_level_b_system_route_packet__no_ratio_no_full_paper_claim
```
