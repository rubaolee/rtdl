# Call For Review - Goal5292 X-HD Figure 7 Load-Balance Audit

Date: 2026-07-09

Please strictly review Goal5292.

## Review Scope

Goal5292 audits the author-side source/log evidence for X-HD Figure 7
load-balance / heavy-cell offload effectiveness.

This is not a Figure 7 reproduction claim, not an RTDL route result, and not a
performance ratio.  It determines whether the pinned author repository already
contains a usable `lb=0` vs `lb=256` Figure 7 denominator.

## Files Under Review

```text
history/internal_docs/goal5292_xhd_figure7_load_balance_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure7_load_balance_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
tests/goal5292_xhd_figure7_load_balance_audit_test.py
```

Supporting evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
.codex_tmp/xhd_author_repo/expr/run_lb.sh
.codex_tmp/xhd_author_repo/expr/draw_lb.py
.codex_tmp/xhd_author_repo/expr/logs/end2end/rt_gpu
.codex_tmp/xhd_author_repo/expr/logs/lb_comparison
```

## Evidence Summary

Goal5292 reports:

```text
status = figure7_load_balance_source_audit_ready__figure7_not_reproduced__lb_comparison_logs_missing
figure7_reproduced = false
lb_comparison_numeric_matrix_available = false
run_all_iteration_metrics_available = true
run_all_lb0_counterpart_available = false
author_script_available = true
```

Author script evidence:

```text
expr/run_lb.sh exists
expr/run_lb.sh lists four graphics pairs
expr/run_lb.sh has lb values [0, 256]
expr/run_lb.sh has profiling/check flags
expr/draw_lb.py exists
expr/draw_lb.py expects both geo and graphics lb_comparison logs
script_draw_contract_mismatch = true
```

Checked-in log evidence:

```text
expr/logs/lb_comparison total_json_count = 0
expr/logs/end2end/rt_gpu record_count = 7
run_all rt_gpu has LB=256 records = true
run_all rt_gpu has LB=0 records = false
run_all rt_gpu has iteration fields = true
```

Interpretation under review:

```text
The author repository contains Figure 7 scripts and LB=256 profiling-style
run_all logs, but the checked-in lb_comparison lb=0/lb=256 matrix required by
draw_lb.py is absent. Therefore Figure 7 is not reproduced under current
evidence.
```

## Review Questions

1. Does the builder correctly identify the Figure 7 target and prior mapping?
2. Does it correctly parse `run_lb.sh` as a graphics-only script with
   `lb=0` and `lb=256` execution intent?
3. Does it correctly parse `draw_lb.py` as expecting both geo and graphics
   `lb_comparison` logs and phase fields?
4. Is the `script_draw_contract_mismatch=true` conclusion justified?
5. Is it correct that checked-in `lb_comparison` JSON logs are absent?
6. Is it correct that checked-in `run_all/rt_gpu` logs provide LB=256
   profiling-style iteration fields but no LB=0 counterpart?
7. Is it correct to conclude that Figure 7 is not reproduced under current
   evidence?
8. Does the result avoid RTDL/author load-balance parity, performance ratio,
   exact paper dataset, and full-paper reproduction claims?
9. Is the next-step recommendation correct: regenerate/recover author
   `lb_comparison` first, or explicitly define a separate Level-B diagnostic?
10. Can Goal5292 be marked externally reviewed and approved, or are amendments
    required?

## Expected Answer Shape

Please answer with:

```text
verdict_label: ...
blocking_findings:
required_amendments:
non_blocking_notes:
answers:
  Q1: ...
  Q2: ...
  ...
  Q10: ...
```

Acceptable verdict examples:

```text
approve_goal5292_figure7_load_balance_audit__lb_comparison_missing_figure7_not_reproduced
revise_goal5292_figure7_audit_claim_boundary_or_script_mapping
block_goal5292_due_to_incorrect_author_log_or_script_evidence
```
