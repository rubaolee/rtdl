# Goal5284 - X-HD Figure 9 Auto-Tune Semantics Matrix

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5284 moves the Figure 9 line forward after the Figure 11 closeout packet.
Goal5177 identified Figure 9 as:

```text
partially_covered_by_auto_tune_logs__grid_sweep_semantics_missing
```

This goal asks what the existing author paper-branch `run_all/auto_tune` logs
actually prove.  It does not run a new RTDL route, does not claim Figure 9
reproduction, and does not claim an author-vs-RTDL performance ratio.

## Implementation

New app-owned script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_auto_tune_matrix.py
```

Input:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

Output:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
```

No RTDL core or native files were changed.

## Main Evidence

The author paper-branch run_all index contains:

```text
auto_tune records = 1814
unique pairs = 907
categories:
  BraTS2020_ValidationData = 1000
  ModelNet40 = 800
  geo = 6
  graphics = 8
```

Every observed pair has exactly the two extracted config labels:

```text
n_points_cell_false_max_hit_false = 907
n_points_cell_true_max_hit_true = 907
complete_pair_count_with_both_observed_configs = 907
incomplete_pair_count = 0
```

The `Running.NumPointsPerCell` value is not a sweep in these records:

```text
all_running_num_points_per_cell_values = [8]
grid_size_sweep_present_in_run_all_auto_tune_logs = false
```

The two configs preserve the same HDResult on every pair:

```text
hd_result_mismatch_pair_count = 0
```

Author internal timing comparison across the paired config labels:

```text
n_points_cell_true_max_hit_true wins by AvgTime on 740 / 907 pairs
n_points_cell_false_max_hit_false wins by AvgTime on 167 / 907 pairs
median true_over_false AvgTime ratio ~= 0.845145287
```

These are author-log-internal comparisons only.  They are not RTDL performance
claims and not Figure 9 reproduction.

## Decision

Goal5284 produces:

```text
status = figure9_auto_tune_mapping_ready__figure9_not_reproduced
figure9_reproduced = false
```

What this proves:

```text
The paper-branch run_all index contains 1814 auto_tune records.
The records cover 907 unique input pairs across BraTS, ModelNet40, geo, and graphics.
Every observed pair has the two extracted config labels.
The two labels can be compared for author-log HDResult and internal timing.
```

What remains missing:

```text
full adaptive-grid parameter sweep semantics
paper Figure 9 selected grid-size choices
author source/script mapping tying these two config labels to the plotted Figure 9 experiment
exact input file bytes or accepted Level-C provenance
RTDL equivalent adaptive-grid route matrix
denominator-aligned author-vs-RTDL performance matrix
```

## Validation

```text
py -m unittest \
  tests.goal5284_xhd_figure9_auto_tune_matrix_test \
  tests.goal5177_xhd_paper_target_log_mapping_test

Ran 3 tests in 0.030s
OK
```

The local Python launcher printed the known noisy line:

```text
Could not find platform independent libraries <prefix>
```

The command exited successfully.

## Claim Boundary

Allowed:

```text
Goal5284 maps the author paper-branch auto_tune logs and shows that the two
observed config labels cover 907 pairs with stable HDResult and author-internal
timing differences.
```

Not authorized:

```text
Figure 9 reproduced
full adaptive-grid sweep reproduced
paper selected grid-size choices recovered
author-vs-RTDL Figure 9 speedup or parity
exact paper dataset reproduction
full X-HD paper reproduction
RTDL route result for Figure 9
```

## Next Recommended Step

If continuing Figure 9:

```text
Inspect author source/scripts for the actual Figure 9 plotting or grid-tuning
driver.  If a separate grid-size sweep artifact exists, extract its grid choices
and target workloads.  If no such artifact exists, keep Figure 9 at author-log
mapping only and move to another figure or dataset blocker.
```

This should be a source/script provenance goal, not another RTDL route or
performance goal.
