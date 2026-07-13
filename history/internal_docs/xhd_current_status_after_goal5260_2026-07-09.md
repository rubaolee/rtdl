# X-HD Current Status After Goal5260

Date: 2026-07-09

## One-Line Status

RTDL now has a user-facing `hd_exec`-compatible X-HD app entrypoint, and that
entrypoint has all-400 public ModelNet40 exact-witness coverage against author
reruns. Full X-HD paper reproduction is still not complete.

## What Is Now Strong

### 1. User-facing app shape

RTDL runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Author-style key flags:

```text
-input1
-input2
-n_dims
-input_type
-variant rt
-execution cpu|gpu
-json
```

Batch bridge:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

This means the X-HD app is no longer only internal review gates. It has a user
entrypoint and a batch entrypoint.

### 2. ModelNet40 public rerun correctness

Primary evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
```

Result:

```text
selected_case_count = 400
matched_case_count = 400
failed_case_count = 0
all_cases_matched = true
route_label = cell-mbr-exact-witness
```

Error:

```text
max_author_abs_diff    = 6.59728109919655e-08
median_author_abs_diff = 7.368051571643441e-09
tolerance              = 1e-6
```

### 3. Timing denominator safety

The author-shaped JSON contains `Running.AvgTime`, but RTDL now labels it:

```text
Running.TimeSemantics
RTDL.running_avg_time_semantics
```

Meaning:

```text
Running.AvgTime is RTDL route wall time for the selected route label.
It is not author internal Running.AvgTime parity.
```

## What Is Still Not Complete

### 1. Exact paper byte-input identity

The ModelNet40 evidence uses public ModelNet40 OFF files and author-style
normalization. It does not prove the exact byte identity of the paper-run inputs.

### 2. Full paper dataset matrix

The all-400 ModelNet40 route is only one major dataset family. The paper's
broader target matrix and Figures 5-11 are not yet reproduced.

### 3. Author RT-core algorithm equivalence

RTDL uses generic grid/cell-MBR/frontier/nearest-witness routes. It matches
author rerun scalar HDResult under the tested contracts, but it is not a claim
that RTDL has reimplemented the author's fused X-HD RT-core algorithm.

### 4. Performance parity

The current ModelNet40 all-400 exact-witness RTDL route is much slower than the
author internal `Running.AvgTime` denominator. Any performance comparison must
keep denominators separate:

```text
RTDL route wall time
RTDL entrypoint/batch wall time
author process wall time
author internal Running.AvgTime
```

## Current Review Entry Point

```text
history/internal_docs/call_for_review_goals5255_5260_xhd_hd_exec_user_entrypoint_all400_consolidated_2026-07-09.md
```

## Recommended Next Technical Directions

1. **Review and stabilize Goals5255-5260.**
   Treat Goal5260 as the ModelNet40 functional anchor only after strict review.

2. **Return to full-paper blockers.**
   The next major full-reproduction blockers are exact dataset provenance and
   Figure 5-11 mapping.

3. **Attack the author internal AvgTime gap.**
   If performance is prioritized, the next work should target algorithmic gap,
   not app-entrypoint plumbing.

4. **Keep route labels mandatory.**
   No future summary should quote one unqualified "RTDL X-HD performance"
   number.
