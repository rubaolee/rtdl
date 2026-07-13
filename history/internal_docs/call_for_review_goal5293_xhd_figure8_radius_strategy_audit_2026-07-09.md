# Call For Review - Goal5293 X-HD Figure 8 Radius-Strategy Audit

Date: 2026-07-09

Please strictly review Goal5293.

## Review Scope

Goal5293 audits the author-side source/log evidence for X-HD Figure 8 radius
growing strategies.

This is not a Figure 8 reproduction claim, not an RTDL route result, and not a
performance ratio.  It determines whether the pinned author repository already
contains a usable add/double/adaptive `tune_radius` denominator.

## Files Under Review

```text
history/internal_docs/goal5293_xhd_figure8_radius_strategy_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure8_radius_strategy_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json
tests/goal5293_xhd_figure8_radius_strategy_audit_test.py
```

Supporting evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
.codex_tmp/xhd_author_repo/expr/run_radius_tuning.sh
.codex_tmp/xhd_author_repo/expr/draw_tune_radius.py
.codex_tmp/xhd_author_repo/expr/logs/tune_radius
```

## Evidence Summary

Goal5293 reports:

```text
status = figure8_radius_strategy_audit_ready__figure8_not_reproduced__tune_radius_logs_missing
figure8_reproduced = false
tune_radius_numeric_matrix_available = false
run_all_radius_strategy_evidence_available = false
author_script_available = true
```

Author script evidence:

```text
expr/run_radius_tuning.sh exists
expr/run_radius_tuning.sh lists geo and graphics workloads
expr/run_radius_tuning.sh runs tune_radius values [add, double, adaptive]
expr/draw_tune_radius.py exists
expr/draw_tune_radius.py expects rt_gpu_radius_add/double/adaptive under geo and graphics
script_draw_contract_aligned = true
```

Checked-in log evidence:

```text
expr/logs/tune_radius root_exists = false
expr/logs/tune_radius total_json_count = 0
complete_variant_category_matrix_present = false
paper-branch run_all mapping record_count = 0 for Figure 8
```

Interpretation under review:

```text
The author repository contains Figure 8 radius-strategy scripts, but the
checked-in tune_radius numeric matrix is absent and run_all does not cover
radius-growing strategy records. Therefore Figure 8 is not reproduced under
current evidence.
```

## Review Questions

1. Does the builder correctly identify the Figure 8 target and prior mapping?
2. Does it correctly parse `run_radius_tuning.sh` as defining geo/graphics
   add/double/adaptive radius-strategy runs?
3. Does it correctly parse `draw_tune_radius.py` as expecting
   `rt_gpu_radius_add`, `rt_gpu_radius_double`, and `rt_gpu_radius_adaptive`
   logs for geo and graphics?
4. Is `script_draw_contract_aligned=true` justified?
5. Is it correct that checked-in `logs/tune_radius` JSON records are absent?
6. Is it correct that the paper-branch `run_all` mapping provides no Figure 8
   radius-strategy records?
7. Is it correct to conclude that Figure 8 is not reproduced under current
   evidence?
8. Does the result avoid RTDL/author radius-strategy parity, performance ratio,
   exact paper dataset, and full-paper reproduction claims?
9. Is the next-step recommendation correct: regenerate/recover author
   `tune_radius` first, or explicitly define a separate Level-B diagnostic?
10. Can Goal5293 be marked externally reviewed and approved, or are amendments
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
approve_goal5293_figure8_radius_strategy_audit__tune_radius_logs_missing_figure8_not_reproduced
revise_goal5293_figure8_audit_claim_boundary_or_script_mapping
block_goal5293_due_to_incorrect_author_log_or_script_evidence
```
