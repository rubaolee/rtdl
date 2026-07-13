# X-HD Current Status After Goal5262

Date: 2026-07-09

## Current User-Facing Status

The X-HD paper app README and manifest now expose the RTDL
`hd_exec`-compatible entrypoint family as the current primary user-facing
route:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

Current status string:

```text
xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete
```

## Functional Evidence

Primary all-400 public ModelNet40 user-entrypoint artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
```

Evidence:

```text
route_label = cell-mbr-exact-witness
case_count = 400
matched_case_count = 400
failed_case_count = 0
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 cases
```

## Performance Evidence

Primary all-400 user-entrypoint performance matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
```

Denominator-separated results:

```text
RTDL hd_exec route-wall sum = 420.31053318828344 s
RTDL hd_exec batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms

RTDL route / author process-wall = 1.648034759782505x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

The author internal AvgTime ratio is a phase/algorithm gap warning, not a fair
user-facing process-wall comparison.

## Review Status

Goals5255-5262 are implemented and review pending.

Current consolidated review packet:

```text
history/internal_docs/call_for_review_goals5255_5262_xhd_hd_exec_entrypoint_all400_performance_and_docs_2026-07-09.md
```

## Still Not Complete

The full thread goal is not complete. The following remain open:

```text
exact original paper byte-input identity
all non-ModelNet40 paper datasets
Figure 5-11 reproduction
author RT-core algorithm equivalence
author internal Running.AvgTime performance gap
```

## Next Work

After review, continue toward full paper reproduction by choosing one of the
remaining hard blockers:

```text
1. exact dataset / figure reproduction path;
2. non-ModelNet40 dataset gates;
3. author RT-core/internal AvgTime algorithm gap.
```
