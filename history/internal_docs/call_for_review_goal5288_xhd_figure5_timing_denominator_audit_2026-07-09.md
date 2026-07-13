# Call For Review - Goal5288 X-HD Figure 5 Timing Denominator Audit

Date: 2026-07-09

## Review Scope

Please strictly review Goal5288, which audits Figure 5 author timing-log
coverage and denominator alignment.

This is a timing-denominator audit.  It is not a Figure 5 reproduction claim,
not a new RTDL route, and not a performance ratio.

## Files To Review

```text
history/internal_docs/goal5288_xhd_figure5_timing_denominator_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_timing_denominator_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
tests/goal5288_xhd_figure5_timing_denominator_audit_test.py
```

Relevant prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
history/internal_docs/goal5267_xhd_full_paper_coverage_gap_matrix_result_2026-07-09.md
```

## Evidence Summary

Goal5288 reports:

```text
status = figure5_author_timing_denominator_audit_ready__figure5_not_reproduced
record_count = 2535
unique_pair_count = 507
complete_author_pair_count = 507
incomplete_author_pair_count = 0
```

Categories:

```text
BraTS2020_ValidationData = 2500 records / 500 pairs
geo = 15 records / 3 pairs
graphics = 20 records / 4 pairs
```

Each pair has:

```text
auto_tune = 2
eb_gpu = 1
hybrid_gpu = 1
rt_gpu = 1
```

Timing denominator:

```text
author fields = Running.AvgTime, ReportedTime median, repeat_count, GPU name
author GPU = NVIDIA GeForce RTX 3090
same_denominator_author_rtdl_performance = false
```

Current RTDL Figure 5 coverage:

```text
graphics_representative_count = 4
brats_full_workload_gate_present = false
geo_full_workload_gate_present = false
figure5_full_matrix_gate_present = false
ModelNet40 all400 is not a Figure 5 category
```

## Review Questions

1. Does Goal5288 correctly extract the Figure 5 author-log denominator from the
   paper-branch run_all log index?
2. Are the key counts correct: 2535 records, 507 pairs, and all 507 author pairs
   complete with 2 auto_tune + 1 eb_gpu + 1 hybrid_gpu + 1 rt_gpu?
3. Is the category coverage correct: 500 BraTS pairs, 3 geo pairs, 4 graphics
   pairs?
4. Is it correct to keep Figure 5 as not reproduced despite strong author-log
   coverage?
5. Is it correct that author `Running.AvgTime` / `ReportedTime` medians are not
   the same denominator as RTDL route wall or process wall?
6. Is it correct that current RTDL evidence does not cover full Figure 5 because
   BraTS and geo gates are missing?
7. Does the artifact correctly forbid using ModelNet40 all400 as proof of
   Figure 5?
8. Does the goal avoid RTDL core changes, route claims, and performance ratios?
9. Can Goal5288 be marked externally reviewed and approved, or are amendments
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
approve_goal5288_xhd_figure5_timing_denominator_audit__figure5_not_reproduced
```
