# Call For Review - Goal5284 X-HD Figure 9 Auto-Tune Semantics Matrix

Date: 2026-07-09

## Review Scope

Please strictly review Goal5284, which maps the X-HD author paper-branch
`run_all/auto_tune` logs for Figure 9.

This is a source/log semantics goal.  It is not a Figure 9 reproduction claim,
not a new RTDL route, and not a performance ratio.

## Files To Review

```text
history/internal_docs/goal5284_xhd_figure9_auto_tune_semantics_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_auto_tune_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
tests/goal5284_xhd_figure9_auto_tune_matrix_test.py
```

Relevant prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
history/internal_docs/goal5177_paper_target_log_mapping_result_2026-07-08.md
history/internal_docs/goal5267_xhd_full_paper_coverage_gap_matrix_result_2026-07-09.md
```

## Evidence Summary

Goal5284 reports:

```text
status = figure9_auto_tune_mapping_ready__figure9_not_reproduced
auto_tune_record_count = 1814
unique_pair_count = 907
complete_pair_count_with_both_observed_configs = 907
incomplete_pair_count = 0
```

Observed configs:

```text
n_points_cell_false_max_hit_false = 907
n_points_cell_true_max_hit_true = 907
```

Observed `Running.NumPointsPerCell` values:

```text
[8]
```

Important boundary:

```text
grid_size_sweep_present_in_run_all_auto_tune_logs = false
figure9_reproduced = false
```

Paired author-log comparison:

```text
hd_result_mismatch_pair_count = 0
n_points_cell_true_max_hit_true wins by AvgTime on 740 / 907 pairs
n_points_cell_false_max_hit_false wins by AvgTime on 167 / 907 pairs
median true_over_false AvgTime ratio ~= 0.845145287
```

These are author-log-internal observations only.  They do not authorize an
RTDL/author performance comparison.

## Review Questions

1. Does the script correctly restrict itself to author paper-branch
   `run_all/auto_tune` records?
2. Are the key counts correct: 1814 records, 907 unique pairs, and two observed
   config labels with complete pair coverage?
3. Does the artifact correctly show that these records do not contain a
   multi-value grid-size sweep (`NumPointsPerCell=[8]`)?
4. Is it correct to classify the result as `figure9_not_reproduced` despite the
   useful author-log mapping?
5. Does the author-log-internal timing comparison stay within bounds and avoid
   an RTDL performance claim?
6. Does the script avoid modifying RTDL core or adding X-HD-specific system
   behavior?
7. Is the next recommended step correct: inspect author source/scripts for the
   actual Figure 9 plotting or grid-tuning driver before writing any more RTDL
   route code?
8. Can Goal5284 be marked externally reviewed and approved, or are amendments
   required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-8:
Requested verdict label:
```

If approving, please use or adapt:

```text
approve_goal5284_xhd_figure9_auto_tune_mapping__figure9_not_reproduced
```
