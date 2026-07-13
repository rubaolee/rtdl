# Call For Review - Goals5284-5287 X-HD Figure 9 Packet

Date: 2026-07-09

## Review Scope

Please strictly review the X-HD Figure 9 packet covering Goals5284-5287.

This packet does **not** claim Figure 9 reproduction.  It asks whether the
current Figure 9 line is correctly closed as author-denominator-missing under
the evidence now available.

## Files To Review

Goal5284:

```text
history/internal_docs/goal5284_xhd_figure9_auto_tune_semantics_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_auto_tune_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
tests/goal5284_xhd_figure9_auto_tune_matrix_test.py
```

Goal5285:

```text
history/internal_docs/goal5285_xhd_figure9_source_script_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_source_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json
tests/goal5285_xhd_figure9_source_script_audit_test.py
```

Goal5286:

```text
history/internal_docs/goal5286_xhd_figure9_branch_availability_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_branch_availability_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
tests/goal5286_xhd_figure9_branch_availability_audit_test.py
```

Goal5287:

```text
history/internal_docs/goal5287_xhd_figure9_disposition_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_disposition.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5287_figure9_disposition_2026-07-09.json
tests/goal5287_xhd_figure9_disposition_test.py
```

Relevant prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
history/internal_docs/goal5177_paper_target_log_mapping_result_2026-07-08.md
history/internal_docs/goal5267_xhd_full_paper_coverage_gap_matrix_result_2026-07-09.md
```

## Evidence Summary

Goal5284 maps current paper-branch `run_all/auto_tune` logs:

```text
auto_tune records = 1814
unique pairs = 907
observed configs:
  n_points_cell_false_max_hit_false = 907
  n_points_cell_true_max_hit_true = 907
Running.NumPointsPerCell = [8]
figure9_reproduced = false
```

Goal5285 maps author source/scripts:

```text
plot script = expr/for_the_paper/effective_autoune.py
active draw call = draw_mri_modelnet()
saves auto-tune.pdf
loads logs/run_all/auto_tune
expected variants:
  n_points_cell_false_max_hit_false
  n_points_cell_true_max_hit_false
  n_points_cell_false_max_hit_true
  n_points_cell_true_max_hit_true
missing from current run_all logs:
  n_points_cell_true_max_hit_false
  n_points_cell_false_max_hit_true
```

Goal5285 also finds training sweeps:

```text
gen_train.sh / logs/train contains multi-value sweeps
but effective_autoune.py reads logs/run_all/auto_tune
training sweeps are not the same denominator as the plot input
```

Goal5286 checks pinned branches:

```text
paper:
  same two configs only; checked-in auto-tune.pdf exists
main:
  no run_all auto_tune logs or Figure-9-like files
hybrid:
  no run_all auto_tune logs or Figure-9-like files
```

Goal5287 disposition:

```text
status = figure9_closed_current_line_author_denominator_missing
figure9_reproduced = false
close_current_figure9_line = true
matched = true
```

Allowed reopen conditions:

```text
regenerate/recover the two missing run_all variants
externally map logs/train sweeps to checked-in auto-tune.pdf quantities
external review accepts a narrower Figure 9 question with explicit denominator limits
```

## Review Questions

1. Are Goal5284's current auto-tune log counts and two-config coverage correct?
2. Is Goal5284 correct to classify the logs as useful author-log mapping but not
   Figure 9 reproduction?
3. Does Goal5285 correctly identify the plot script, active draw call, expected
   four variants, and missing variants?
4. Is Goal5285 correct not to promote `logs/train` sweeps into Figure 9?
5. Does Goal5286 correctly show that the missing variants are not present on
   pinned `main` or `hybrid`?
6. Is it correct to treat checked-in `auto-tune.pdf` as evidence but not a
   reproducible RTDL/author denominator?
7. Is Goal5287's `figure9_closed_current_line_author_denominator_missing`
   disposition justified?
8. Are the reopen conditions sufficient and explicit?
9. Does the packet avoid RTDL core changes, RTDL route claims, Figure 9 speedup
   claims, and full-paper reproduction claims?
10. Can Goals5284-5287 be marked externally reviewed and approved, or are
    amendments required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-10:
Requested verdict label:
```

If approving, please use or adapt:

```text
approve_goals5284_5287_xhd_figure9_packet__current_line_closed_author_denominator_missing
```
