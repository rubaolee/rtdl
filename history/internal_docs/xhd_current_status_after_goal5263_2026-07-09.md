# X-HD Current Status After Goal5263

Date: 2026-07-09

## Current User-Facing Entrypoint Coverage

The RTDL X-HD paper app now has a single app-owned `hd_exec`-compatible
entrypoint family covering:

```text
bounded WKT smoke fixtures
public ModelNet40 OFF all-400 author-rerun contract
Stanford Graphics Dragon -> HappyBuddha full-public PLY Level-B representative
```

Primary scripts:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

## ModelNet40 Evidence

```text
artifact = Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
case_count = 400
matched_case_count = 400
failed_case_count = 0
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 cases
```

Performance matrix:

```text
artifact = Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
RTDL route / author process-wall = 1.648034759782505x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

## Stanford Graphics Evidence

```text
pair = Dragon -> HappyBuddha
author_hd_result = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs_diff ~= 2.38e-9
point counts = 437645 / 543652
preprocessing = translate_each_input_to_min_bound
```

Fast HDResult route:

```text
artifact = Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
route_label = cell-mbr-fast-scalar
per_source_witness_exact = false
RTDL route wall ~= 536ms
```

Exact-witness route:

```text
artifact = Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
route_label = cell-mbr-exact-witness
per_source_witness_exact = true
RTDL route wall ~= 621ms
```

## Review Status

Goals5255-5263 are implemented and review pending.

Current consolidated review packet:

```text
history/internal_docs/call_for_review_goals5255_5263_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

## Still Not Complete

The full thread goal is still open. These remain unproved/incomplete:

```text
exact original paper byte-input identity
all non-ModelNet40 paper datasets
Figure 5-11 reproduction
author RT-core algorithm equivalence
author internal Running.AvgTime performance gap
```

## Next Work

The most concrete next choices are:

```text
1. Continue non-ModelNet40 paper dataset/Figure coverage, especially additional
   Stanford Graphics pairs such as Dragon -> AsianDragon if available/feasible.
2. Attack the author RT-core/internal AvgTime gap for the already covered
   representative routes.
3. Continue exact dataset provenance search; exact byte identity remains the
   hardest blocker for full paper completion.
```
