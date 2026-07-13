# Call For Review: Goal5239 Dragon -> AsianDragon Scaled Same-POD Performance Matrix

Please strictly review Goal5239.

## Files To Review

```text
history/internal_docs/goal5239_dragon_asian_scaled_same_pod_performance_matrix_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_author_dragon_asian_scaled_perf_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_author_dragon_asian_scaled_rt_gpu_rerun_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
```

## Context

Goal5237 established an all-source RTDL route-only HDResult match for
Dragon -> scaled AsianDragon.

Goal5238 established that the required RTDL min-bound translation mirrors the
author PLY loader contract.

Goal5239 measures performance on the same POD and same scaled-public input,
with denominator labels kept separate.

## Claims Under Review

1. Author and RTDL are measured on the same scaled-public all-source input.
2. Correctness remains matched (`author_abs_diff ~= 2.37e-9`).
3. The performance matrix correctly separates:
   - author process wall;
   - author internal `Running.AvgTime`;
   - RTDL full app wall;
   - RTDL route direction time;
   - RTDL phase timings.
4. The diagnostic ratios are correctly labelled and not promoted to paper
   parity/speedup claims.
5. The matrix correctly identifies `nearest_continuation` as the dominant RTDL
   bottleneck.

## Review Questions

1. Does the matrix use the same POD and same input contract for author and RTDL?
2. Are the author and RTDL correctness values still aligned?
3. Are the denominators clearly separated enough to avoid another regime /
   denominator mistake?
4. Is it fair to report the labelled diagnostic ratio
   `RTDL full app wall / author process wall ~= 11.75x slower`?
5. Is it fair to report, with caveats, that RTDL route time divided by author
   internal AvgTime is about `365x` slower?
6. Does the evidence support the conclusion that RTDL's dominant bottleneck is
   `nearest_continuation`, not loading, frontier row production, or max
   reduction?
7. Should the next goal attack the generic nearest continuation bottleneck, or
   move to another paper workload for coverage?

## Expected Answer Shape

```text
Verdict:
  approve_goal5239_same_pod_performance_matrix
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

Reject any summary that says:

```text
RTDL matches author performance.
RTDL reproduces Figure 6.
The 365x ratio is a paper performance ratio.
The 11.75x ratio proves paper parity.
Full X-HD reproduction is complete.
```
