# Call For Review - Goal5294 X-HD Figure 10 Scalability / Overlap Audit

Date: 2026-07-09

Please strictly review Goal5294.

## Review Scope

Goal5294 audits the author-side source/log evidence for X-HD Figure 10
scalability and overlap sensitivity.

This is not a Figure 10 reproduction claim, not an RTDL route result, and not a
performance ratio.  It determines whether the pinned author repository already
contains a usable size/translate `logs/scalability` denominator.

## Files Under Review

```text
history/internal_docs/goal5294_xhd_figure10_scalability_overlap_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure10_scalability_overlap_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json
tests/goal5294_xhd_figure10_scalability_overlap_audit_test.py
```

Supporting evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
.codex_tmp/xhd_author_repo/expr/run_scalability.sh
.codex_tmp/xhd_author_repo/expr/draw_scalability.py
.codex_tmp/xhd_author_repo/expr/logs/scalability
```

## Evidence Summary

Goal5294 reports:

```text
status = figure10_scalability_overlap_audit_ready__figure10_not_reproduced__scalability_logs_missing
figure10_reproduced = false
scalability_numeric_matrix_available = false
run_all_workload_family_records_available = true
run_all_scale_overlap_labels_available = false
author_script_available = true
```

Author script evidence:

```text
expr/run_scalability.sh exists
expr/run_scalability.sh uses all_nodes.wkt, input_type=wkt, n_dims=3
expr/run_scalability.sh runs variants [eb, nn, clover, rt] on gpu
expr/run_scalability.sh defines a size sweep over 6 limit values
expr/run_scalability.sh defines a translate/overlap sweep over 12 translate values
expr/draw_scalability.py exists
expr/draw_scalability.py expects eb/nn/clover/rt gpu logs under scal_vary_size and scal_vary_translate
expr/draw_scalability.py plots Input.Files[0].NumPoints, Input.Translate, and Running.AvgTime
script_draw_contract_aligned = true
```

Checked-in log evidence:

```text
expr/logs/scalability root_exists = false
expr/logs/scalability total_json_count = 0
complete_variant_sweep_matrix_present = false
paper-branch run_all mapping record_count = 4535
paper-branch run_all mapping coverage_status = workload_families_present__scale_overlap_labels_missing
```

Interpretation under review:

```text
The author repository contains Figure 10 scalability / overlap scripts, but the
checked-in scalability numeric matrix is absent.  The paper-branch run_all logs
contain workload-family records, but they do not identify the Figure 10
scale/overlap subsets, overlap diagnostics, or exact input provenance.  Therefore
Figure 10 is not reproduced under current evidence.
```

## Review Questions

1. Does the builder correctly identify the Figure 10 target and prior mapping?
2. Does it correctly parse `run_scalability.sh` as defining size and translate /
   overlap sweeps over `all_nodes.wkt`?
3. Does it correctly parse `draw_scalability.py` as expecting `eb_gpu`,
   `nn_gpu`, `clover_gpu`, and `rt_gpu` logs under both `scal_vary_size` and
   `scal_vary_translate`?
4. Is `script_draw_contract_aligned=true` justified?
5. Is it correct that checked-in `logs/scalability` JSON records are absent?
6. Is it correct that the paper-branch `run_all` mapping has workload-family
   records but lacks Figure 10 scale/overlap labels and diagnostics?
7. Is it correct to conclude that Figure 10 is not reproduced under current
   evidence?
8. Does the result avoid RTDL/author scalability parity, overlap parity,
   performance ratio, exact paper dataset, and full-paper reproduction claims?
9. Is the next-step recommendation correct: regenerate/recover author
   `logs/scalability` first, or explicitly define a separate Level-B diagnostic?
10. Can Goal5294 be marked externally reviewed and approved, or are amendments
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
approve_goal5294_figure10_scalability_overlap_audit__scalability_logs_missing_figure10_not_reproduced
revise_goal5294_figure10_audit_claim_boundary_or_script_mapping
block_goal5294_due_to_incorrect_author_log_or_script_evidence
```
