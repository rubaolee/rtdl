# X-HD Current Status After Goal5261

Date: 2026-07-09

## Current Best Functional Position

The RTDL X-HD paper app now has an app-owned `hd_exec`-compatible user
entrypoint and a summary-driven batch bridge:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

The entrypoint family has all-400 public ModelNet40 coverage through the
exact-witness route:

```text
400 / 400 matched author rerun HDResult
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 cases
```

Primary all-400 user-entrypoint artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
```

## Current Performance Matrix

Goal5261 generated a denominator-separated all-400 performance matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
```

Headline numbers, with denominators:

```text
RTDL hd_exec route-wall sum = 420.31053318828344 s
RTDL hd_exec batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms

RTDL route / author process-wall = 1.648034759782505x slower
RTDL case wall / author process-wall = 2.356026814371663x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

The 150.39x number is a phase/internal-timing gap warning, not a fair
user-facing process-wall denominator.

## Review Status

Goals5255-5261 are implemented and review pending. Consolidated review packet:

```text
history/internal_docs/call_for_review_goals5255_5261_xhd_hd_exec_user_entrypoint_all400_and_performance_2026-07-09.md
```

## Claim Boundary

Allowed:

```text
The RTDL hd_exec-compatible entrypoint matched author rerun HDResult for all
400 public ModelNet40 pair identities represented in the paper-branch log index.
```

Allowed with denominator label:

```text
RTDL route-wall sum / author process-wall sum = 1.65x slower.
RTDL route-wall sum / author internal Running.AvgTime sum = 150.39x slower.
```

Still not allowed:

```text
full X-HD paper reproduction complete
exact paper byte-input identity proved
all X-HD paper datasets reproduced
Figure 5-11 reproduced
author RT-core algorithm equivalence
author performance parity or speedup
RTDL Running.AvgTime comparable to author internal Running.AvgTime without label
```

## Next Work

1. Send Goals5255-5261 for strict external review.
2. If approved, update public X-HD docs to make the `hd_exec`-compatible runner
   the primary RTDL user entrypoint.
3. Continue exact paper dataset/Figure work separately; current ModelNet40
   evidence is public-data rerun evidence, not byte-identical original paper
   input identity.
