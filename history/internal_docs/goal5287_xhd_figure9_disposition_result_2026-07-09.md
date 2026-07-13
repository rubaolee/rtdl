# Goal5287 - X-HD Figure 9 Disposition

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5287 consolidates Goal5284, Goal5285, and Goal5286 into a Figure 9
disposition.  It decides whether the current evidence is enough to call Figure
9 reproduced.

This goal does not run an RTDL route and does not compute any RTDL/author
performance ratio.

## Inputs

```text
Goal5284 auto-tune matrix:
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json

Goal5285 source/script audit:
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json

Goal5286 branch availability audit:
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
```

## Implementation

New app-owned disposition script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_disposition.py
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5287_figure9_disposition_2026-07-09.json
```

Focused regression:

```text
tests/goal5287_xhd_figure9_disposition_test.py
```

No RTDL core or native files were changed.

## Main Evidence

Consolidated evidence:

```text
auto_tune_records = 1814
auto_tune_unique_pairs = 907
plot script = expr/for_the_paper/effective_autoune.py
plot script saves auto-tune.pdf = true
```

The plot script expects:

```text
n_points_cell_false_max_hit_false
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
n_points_cell_true_max_hit_true
```

Current `run_all/auto_tune` logs provide only:

```text
n_points_cell_false_max_hit_false
n_points_cell_true_max_hit_true
```

Missing:

```text
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
```

Branch availability:

```text
main_run_all_records = 0
hybrid_run_all_records = 0
missing variants not found on pinned main/hybrid branches
```

Other evidence:

```text
checked-in auto-tune.pdf exists on paper branch
training sweeps exist under logs/train
training_sweeps_same_denominator_as_plot = false
```

## Decision

Goal5287 produces:

```text
status = figure9_closed_current_line_author_denominator_missing
figure9_reproduced = false
close_current_figure9_line = true
```

Why closed:

```text
The Figure-9-like plot script expects four auto-tune variants.
Current run_all/auto_tune logs provide only two of those variants.
The missing variants are not present on pinned main or hybrid branches.
The checked-in auto-tune.pdf is a rendered artifact, not a reproducible denominator.
Training sweeps are separate logs and are not promoted to Figure 9 without an externally reviewed mapping.
```

Allowed reopen conditions:

```text
Regenerate or recover the two missing run_all auto_tune variants for the plotted workloads.
Produce an externally reviewed mapping from logs/train sweeps to the checked-in auto-tune.pdf quantities.
Obtain external review accepting a narrower Figure 9 question with explicit denominator limits.
```

## Claim Boundary

Allowed:

```text
Current Figure 9 line is closed as author-denominator-missing under Goals5284-5286 evidence.
Figure 9 can be reopened only by satisfying one of the explicit reopen conditions.
```

Not authorized:

```text
Figure 9 reproduced
all auto-tune variants recovered
checked-in PDF equals reproducible Figure 9
training sweep equals Figure 9
RTDL Figure 9 speedup or parity
full X-HD paper reproduction
```

## Validation

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_figure9_disposition.py ^
  --auto-tune-matrix Paper-reproduction-apps\x-hd-paper\results\xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json ^
  --source-audit Paper-reproduction-apps\x-hd-paper\results\xhd_goal5285_figure9_source_script_audit_2026-07-09.json ^
  --branch-audit Paper-reproduction-apps\x-hd-paper\results\xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json ^
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5287_figure9_disposition_2026-07-09.json
```

Result:

```text
status = figure9_closed_current_line_author_denominator_missing
matched = true
```

Focused validation to run for closeout:

```text
py -m unittest ^
  tests.goal5287_xhd_figure9_disposition_test ^
  tests.goal5286_xhd_figure9_branch_availability_audit_test ^
  tests.goal5285_xhd_figure9_source_script_audit_test ^
  tests.goal5284_xhd_figure9_auto_tune_matrix_test
```

## Next Recommended Step

Do not keep reshaping Figure 9 evidence.  The next full-paper move should be
one of:

```text
1. Explicitly authorize a Figure 9 regeneration goal for the missing variants,
   using author scripts and available inputs; or
2. Move to another full-paper blocker with a complete author-side denominator,
   such as Figure 5 timing matrix, Figure 7 load balance, Figure 8 breakdown,
   Figure 10 scale/overlap labels, or exact input provenance.
```
