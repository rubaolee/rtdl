# Call For Review - Goals5292-5294 X-HD Figures 7 / 8 / 10 Source-Log Audit Packet

Date: 2026-07-09

Please strictly review the current X-HD author-side source/log audit packet for
Figures 7, 8, and 10.

This packet does **not** claim that any of these figures are reproduced.  It asks
whether the project has correctly identified the current author-side denominator
blockers before spending more RTDL execution work.

## Goals Under Review

```text
Goal5292 - Figure 7 Load-Balance / Heavy-Cell Offload Source-Log Audit
Goal5293 - Figure 8 Radius-Strategy Source-Log Audit
Goal5294 - Figure 10 Scalability / Overlap Source-Log Audit
```

## Files Under Review

### Goal5292

```text
history/internal_docs/goal5292_xhd_figure7_load_balance_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5292_xhd_figure7_load_balance_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure7_load_balance_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
tests/goal5292_xhd_figure7_load_balance_audit_test.py
```

### Goal5293

```text
history/internal_docs/goal5293_xhd_figure8_radius_strategy_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5293_xhd_figure8_radius_strategy_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure8_radius_strategy_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json
tests/goal5293_xhd_figure8_radius_strategy_audit_test.py
```

### Goal5294

```text
history/internal_docs/goal5294_xhd_figure10_scalability_overlap_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5294_xhd_figure10_scalability_overlap_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure10_scalability_overlap_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json
tests/goal5294_xhd_figure10_scalability_overlap_audit_test.py
```

Supporting evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
.codex_tmp/xhd_author_repo/expr/run_lb.sh
.codex_tmp/xhd_author_repo/expr/draw_lb.py
.codex_tmp/xhd_author_repo/expr/run_radius_tuning.sh
.codex_tmp/xhd_author_repo/expr/draw_tune_radius.py
.codex_tmp/xhd_author_repo/expr/run_scalability.sh
.codex_tmp/xhd_author_repo/expr/draw_scalability.py
```

## Packet Summary

### Figure 7

Goal5292 reports:

```text
status = figure7_load_balance_source_audit_ready__figure7_not_reproduced__lb_comparison_logs_missing
figure7_reproduced = false
author_script_available = true
lb_comparison_numeric_matrix_available = false
run_all_iteration_metrics_available = true
run_all_lb0_counterpart_available = false
```

Key evidence:

```text
run_lb.sh exists and lists graphics lb=0/lb=256 runs
draw_lb.py exists and expects geo + graphics lb_comparison logs
expr/logs/lb_comparison total_json_count = 0
run_all rt_gpu has LB=256 profiling-style records
run_all rt_gpu has no LB=0 counterpart
```

Interpretation:

```text
Figure 7 cannot be reproduced from current checked-in logs.  The author-side
lb=0/lb=256 comparison matrix is absent.
```

### Figure 8

Goal5293 reports:

```text
status = figure8_radius_strategy_audit_ready__figure8_not_reproduced__tune_radius_logs_missing
figure8_reproduced = false
author_script_available = true
tune_radius_numeric_matrix_available = false
run_all_radius_strategy_evidence_available = false
```

Key evidence:

```text
run_radius_tuning.sh exists and lists geo/graphics add/double/adaptive runs
draw_tune_radius.py exists and expects rt_gpu_radius_add/double/adaptive logs
expr/logs/tune_radius root_exists = false
expr/logs/tune_radius total_json_count = 0
paper-branch run_all has no Figure 8 radius-strategy records
```

Interpretation:

```text
Figure 8 cannot be reproduced from current checked-in logs.  The author-side
add/double/adaptive tune_radius matrix is absent.
```

### Figure 10

Goal5294 reports:

```text
status = figure10_scalability_overlap_audit_ready__figure10_not_reproduced__scalability_logs_missing
figure10_reproduced = false
author_script_available = true
scalability_numeric_matrix_available = false
run_all_workload_family_records_available = true
run_all_scale_overlap_labels_available = false
```

Key evidence:

```text
run_scalability.sh exists and defines size + translate/overlap sweeps over all_nodes.wkt
draw_scalability.py exists and expects eb/nn/clover/rt gpu logs for scal_vary_size and scal_vary_translate
expr/logs/scalability root_exists = false
expr/logs/scalability total_json_count = 0
paper-branch run_all has 4535 workload-family records
paper-branch run_all lacks Figure 10 scale/overlap labels and diagnostics
```

Interpretation:

```text
Figure 10 cannot be reproduced from current checked-in logs.  The author-side
size/translate scalability matrix is absent, and run_all workload-family records
are not a substitute for Figure 10 scale/overlap evidence.
```

## Shared Claim Boundary

Allowed:

```text
Figures 7/8/10 author source/log audits are implemented.
The relevant author scripts exist.
The checked-in numeric matrices required by the plotting scripts are missing.
Figures 7/8/10 remain not reproduced.
```

Not authorized:

```text
Figure 7 reproduced
Figure 8 reproduced
Figure 10 reproduced
RTDL/author load-balance parity
RTDL/author radius-strategy parity
RTDL/author scalability or overlap parity
author-vs-RTDL performance ratio for these figures
run_all logs treated as substitute Figure 7/8/10 denominators
full X-HD paper reproduction
```

## Review Questions

1. Does Goal5292 correctly identify that the author-side `lb_comparison` matrix
   is absent despite existing scripts and LB=256-like run_all records?
2. Is Goal5292 correct to forbid RTDL Figure 7 comparison work until an
   author-side lb=0/lb=256 matrix exists, or a separately named Level-B
   diagnostic is authorized?
3. Does Goal5293 correctly identify that the author-side `tune_radius` matrix
   is absent despite existing add/double/adaptive scripts?
4. Is Goal5293 correct to forbid RTDL Figure 8 comparison work until an
   author-side add/double/adaptive matrix exists, or a separately named Level-B
   diagnostic is authorized?
5. Does Goal5294 correctly identify that the author-side `logs/scalability`
   matrix is absent despite existing size/translate scripts?
6. Is Goal5294 correct that paper-branch `run_all` workload-family records are
   not a substitute for Figure 10 scale/overlap labels and diagnostics?
7. Is it correct that Figures 7/8/10 all remain not reproduced under current
   evidence?
8. Does the packet avoid performance-ratio, parity, exact-dataset, and
   full-paper-reproduction overclaims?
9. Should the next action be:
   - regenerate/recover the missing author matrices on exact or Level-B inputs;
   - define separately named Level-B diagnostics for selected figures;
   - or pivot to another paper blocker with stronger denominator evidence?
10. Can Goals5292-5294 be marked externally reviewed and approved, or are
    amendments required?

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
recommended_next_action:
```

Possible verdict labels:

```text
approve_goals5292_5294_figures7_8_10_author_matrix_missing_packet
revise_figures7_8_10_packet_claim_boundary_or_script_mapping
block_figures7_8_10_packet_due_to_incorrect_author_log_evidence
```
