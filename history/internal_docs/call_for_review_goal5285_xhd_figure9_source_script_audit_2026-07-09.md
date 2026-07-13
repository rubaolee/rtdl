# Call For Review - Goal5285 X-HD Figure 9 Source / Script Audit

Date: 2026-07-09

## Review Scope

Please strictly review Goal5285, which audits the pinned X-HD author source and
scripts for Figure 9 provenance.

This is a source/script provenance goal.  It is not a Figure 9 reproduction
claim, not a new RTDL route, and not a performance ratio.

## Files To Review

```text
history/internal_docs/goal5285_xhd_figure9_source_script_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_source_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json
tests/goal5285_xhd_figure9_source_script_audit_test.py
```

Relevant prior evidence:

```text
history/internal_docs/goal5284_xhd_figure9_auto_tune_semantics_result_2026-07-09.md
history/internal_docs/call_for_review_goal5284_xhd_figure9_auto_tune_semantics_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

## Evidence Summary

Goal5285 reports:

```text
status = figure9_plot_script_expects_missing_run_all_variants__figure9_not_reproduced
author paper head = 8c3846866052e1e8755210021f23fac2cbe8c3d6
figure9_reproduced = false
```

Author plot/source evidence:

```text
plot script = expr/for_the_paper/effective_autoune.py
active tail calls draw_mri_modelnet()
saves auto-tune.pdf
loads logs/run_all/auto_tune
```

The plot script expects four variants:

```text
n_points_cell_false_max_hit_false
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
n_points_cell_true_max_hit_true
```

The current paper-branch `run_all/auto_tune` logs contain only:

```text
n_points_cell_false_max_hit_false = 907
n_points_cell_true_max_hit_true = 907
```

Missing from current `run_all/auto_tune` logs:

```text
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
```

Training-sweep evidence:

```text
gen_train.sh and logs/train contain multi-value parameter sweeps.
But effective_autoune.py reads logs/run_all/auto_tune for the figure.
not_same_as_figure9_run_all = true
```

## Review Questions

1. Does Goal5285 correctly identify the author plot script and its active draw
   call without overstating that it is already a reproduced Figure 9?
2. Does the artifact correctly show that the plot script expects four variants?
3. Does the artifact correctly show that the current paper-branch run_all logs
   contain only two of those variants?
4. Is it correct to keep `figure9_reproduced=false` after this audit?
5. Does Goal5285 correctly separate `logs/train` training sweeps from
   `logs/run_all/auto_tune` plot inputs?
6. Is it correct to forbid summaries such as "training sweep equals Figure 9"?
7. Does the goal avoid RTDL core changes, RTDL route claims, and performance
   ratios?
8. Is the next step correct: recover the missing author-side plot denominator
   before writing more RTDL route code for Figure 9?
9. Can Goal5285 be marked externally reviewed and approved, or are amendments
   required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-9:
Requested verdict label:
```

If approving, please use or adapt:

```text
approve_goal5285_xhd_figure9_source_script_audit__figure9_still_not_reproduced
```
