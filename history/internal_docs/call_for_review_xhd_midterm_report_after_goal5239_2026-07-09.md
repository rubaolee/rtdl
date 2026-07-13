# Call For Review: X-HD Midterm Report After Goal5239

Please strictly review the X-HD midterm report after Goal5239.

This is a midterm checkpoint, not a closeout. The report claims that the
project has achieved a major Level-B single-workload correctness milestone
for Dragon -> scaled AsianDragon, while still being far from full X-HD paper
reproduction and far from author performance.

## Files To Review

Primary report:

```text
history/internal_docs/xhd_midterm_report_after_goal5239_2026-07-09.md
```

Recent result reports:

```text
history/internal_docs/goal5233_graphics_dragon_asian_dragon_subset_route_gate_result_2026-07-09.md
history/internal_docs/goal5234_graphics_dragon_asian_dragon_scaled_author_gate_result_2026-07-09.md
history/internal_docs/goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_result_2026-07-09.md
history/internal_docs/goal5236_graphics_dragon_asian_dragon_scaled_optix_pod_bounded_gate_result_2026-07-09.md
history/internal_docs/goal5237_graphics_dragon_asian_dragon_scaled_all_source_route_only_result_2026-07-09.md
history/internal_docs/goal5238_xhd_author_ply_loader_translation_contract_result_2026-07-09.md
history/internal_docs/goal5239_dragon_asian_scaled_same_pod_performance_matrix_result_2026-07-09.md
```

Existing packet review prompt:

```text
history/internal_docs/call_for_review_goals5233_5238_xhd_dragon_asian_dragon_packet_2026-07-09.md
history/internal_docs/call_for_review_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.md
```

Key evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_raw_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_scaled_1e-3_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset256_optix_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset1024_optix_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_no_translate_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_author_dragon_asian_scaled_perf_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_author_dragon_asian_scaled_rt_gpu_rerun_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.json
```

Relevant tests:

```text
tests/goal5238_xhd_author_ply_loader_translation_contract_test.py
tests/goal5234_xhd_scaled_ply_candidate_test.py
tests/goal5181_xhd_full_public_subset_scaling_gate_test.py
```

## Claims To Review

The midterm report claims:

1. Level A bounded same-input X-HD gates are complete and externally reviewed.
2. X-HD exact paper reproduction is not complete.
3. One large Level-B same-source graphics workload is now correct at the
   all-source scalar-value route level:

   ```text
   Dragon -> scaled AsianDragon
   RTDL route distance = 0.06536787240753439
   author scaled HDResult = 0.06536787003278732
   abs diff = 2.3747470656587666e-09
   matched = true
   ```

4. The passing mode requires:

   ```text
   translate_each_input_to_min_bound = true
   global_bound_early_break = false
   ```

5. The translation is supported by author source evidence from `LoadPLY`:

   ```cpp
   v[i] = (v[i] - vmin[i])
   ```

6. `global_bound_early_break=true` is a no-go for exact all-source reproduction:

   ```text
   matched = false
   per_source_witness_exact = false
   ```

7. Current performance is much slower than author:

   ```text
   RTDL full app wall / author process wall = 11.75434696735015x slower
   RTDL route direction / author internal AvgTime = 365.1670028379467x slower
   RTDL nearest continuation / author internal AvgTime = 336.83875436406305x
   ```

8. The dominant RTDL bottleneck is:

   ```text
   nearest_continuation = 28.124958105385303s
   candidate_distance_evaluations = 6,417,800,660
   ```

9. The next immediate work should attack this as a generic RTDL continuation
   problem, starting with an executor diagnosis and then, if needed, a fused
   generic continuation primitive.

## Questions For The Reviewer

1. Does the midterm report correctly distinguish bounded reproduction, Level-B
   same-source reproduction, exact paper dataset reproduction, and performance
   reproduction?
2. Does the report correctly limit the Dragon -> scaled AsianDragon success to
   **one** large same-source graphics workload, rather than broad Level-B or
   full-paper completion?
3. Does Goal5234 evidence justify the scaled public AsianDragon candidate
   within `1e-6`, while still preserving the boundary that exact paper input
   byte identity is unproved?
4. Does Goal5237 evidence prove an all-source RTDL route-only match against the
   author scaled-public HDResult?
5. Does Goal5238 author-source evidence justify the independent min-bound
   translation as an app-owned author PLY loader contract, not arbitrary RTDL
   normalization?
6. Does the report correctly reject `global_bound_early_break=true` for exact
   all-source reproduction claims?
7. Are the Goal5239 performance ratios labelled with explicit denominators and
   kept as diagnostics rather than paper speedup/parity claims?
8. Is the `nearest_continuation` interpretation correct, or is there another
   larger bottleneck the report underweights?
9. Is the proposed Goal5240 executor diagnosis the right next step, or should
   the team first broaden to another paper workload or continue data-provenance
   search?
10. Does the report keep the RTDL-system boundary clean: generic continuation
    work is allowed, but X-HD-only native primitives are not?
11. Does the report adequately incorporate the previous midterm review lessons:
    exact-value-only caveats, author-rerun vs paper-log distinction, and
    single-workload scope?
12. Are any claims too strong, missing caveats, or using a favorable denominator?

## Expected Answer Shape

```text
Verdict:
  approve_xhd_midterm_after_goal5239
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
```

## Forbidden Summaries

Please reject any summary that says:

```text
Full X-HD paper reproduction is complete.
Exact paper input byte identity is proved.
Figure 6 is reproduced.
RTDL matches author performance.
The result generalizes to all paper workloads.
The Dragon -> AsianDragon result proves broad Level-B completion.
Global-bound early break is exact.
The all-source match works without min-bound translation.
Translation is an RTDL core semantic.
The 365x diagnostic ratio is a paper performance ratio.
```

## Allowed Summary Shape

The strongest allowed summary is:

```text
After Goal5239, X-HD has a major Level-B single-workload milestone:
for Dragon -> scaled AsianDragon, RTDL matches the author rerun HDResult in
all-source route-only exact mode under the documented author PLY loader
min-bound preprocessing contract. This is not exact paper input identity, not
Figure reproduction, and not performance parity. The performance matrix shows
RTDL is still substantially slower, with nearest continuation as the dominant
bottleneck and the next generic RTDL system target.
```
