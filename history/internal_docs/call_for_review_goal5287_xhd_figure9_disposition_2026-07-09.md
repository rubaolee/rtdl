# Call For Review - Goal5287 X-HD Figure 9 Disposition

Date: 2026-07-09

## Review Scope

Please strictly review Goal5287, which consolidates Goals5284-5286 and closes
the current Figure 9 line as author-denominator-missing.

This is a disposition goal.  It is not a Figure 9 reproduction claim, not a new
RTDL route, and not a performance ratio.

## Files To Review

```text
history/internal_docs/goal5287_xhd_figure9_disposition_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_disposition.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5287_figure9_disposition_2026-07-09.json
tests/goal5287_xhd_figure9_disposition_test.py
```

Input evidence:

```text
history/internal_docs/goal5284_xhd_figure9_auto_tune_semantics_result_2026-07-09.md
history/internal_docs/goal5285_xhd_figure9_source_script_audit_result_2026-07-09.md
history/internal_docs/goal5286_xhd_figure9_branch_availability_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
```

## Evidence Summary

Goal5287 reports:

```text
status = figure9_closed_current_line_author_denominator_missing
figure9_reproduced = false
close_current_figure9_line = true
matched = true
```

Reason:

```text
The plot script expects four auto-tune variants.
Current run_all logs provide only two.
The two missing variants are not present on pinned main/hybrid branches.
The checked-in auto-tune.pdf is a rendered artifact, not a reproducible denominator.
Training sweeps are not promoted to Figure 9 without a reviewed mapping.
```

Allowed reopen conditions:

```text
regenerate/recover missing run_all variants
externally map logs/train sweeps to plotted PDF quantities
external review accepts a narrower Figure 9 question with explicit denominator limits
```

## Review Questions

1. Does Goal5287 correctly consolidate Goals5284-5286?
2. Is it correct that Figure 9 remains not reproduced under current evidence?
3. Is closing the current Figure 9 line as author-denominator-missing justified?
4. Does the artifact keep the checked-in PDF as evidence without promoting it
   to a reproducible denominator?
5. Does the artifact correctly keep training sweeps separate from Figure 9 plot
   inputs?
6. Are the reopen conditions sufficient and explicit?
7. Does the goal avoid RTDL core changes, RTDL route claims, and performance
   ratios?
8. Can Goal5287 be marked externally reviewed and approved, or are amendments
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
approve_goal5287_xhd_figure9_disposition__current_line_closed_author_denominator_missing
```
