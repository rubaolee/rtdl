# Goal5288 - X-HD Figure 5 Timing Denominator Audit

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5288 moves from the now-closed current Figure 9 line to Figure 5, which
Goal5267 identified as having the strongest author paper-log workload coverage.
The goal audits the author timing denominator before any new RTDL performance
claim.

This goal does not run an RTDL route and does not compute an author-vs-RTDL
speedup.

## Inputs

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
```

## Implementation

New app-owned script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_timing_denominator_audit.py
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
```

Focused regression:

```text
tests/goal5288_xhd_figure5_timing_denominator_audit_test.py
```

No RTDL core or native files were changed.

## Author Figure 5 Log Coverage

Goal5288 extracts Figure 5 categories:

```text
BraTS2020_ValidationData
geo
graphics
```

Author log coverage:

```text
record_count = 2535
unique_pair_count = 507
complete_author_pair_count = 507
incomplete_author_pair_count = 0
```

Every author pair has:

```text
auto_tune = 2 records
eb_gpu = 1 record
hybrid_gpu = 1 record
rt_gpu = 1 record
```

Category coverage:

```text
BraTS2020_ValidationData:
  records = 2500
  unique pairs = 500

geo:
  records = 15
  unique pairs = 3

graphics:
  records = 20
  unique pairs = 4
```

Author timing fields available:

```text
Running.AvgTime
Running.ReportedTime median
Running.repeat_count = 5
GPU name = NVIDIA GeForce RTX 3090
```

Section medians over all Figure 5 categories:

```text
auto_tune Running.AvgTime median ~= 10.2461
rt_gpu Running.AvgTime median ~= 10.0544
hybrid_gpu Running.AvgTime median ~= 9.7664
eb_gpu Running.AvgTime median ~= 23.5620
```

These are author-log-internal medians only.

## Current RTDL Coverage

Current strongest RTDL entrypoint evidence from Goal5267 includes:

```text
ModelNet40 all-400 paper-log pair identities
selected graphics representatives
```

For Figure 5 specifically:

```text
graphics_representative_count = 4
brats_full_workload_gate_present = false
geo_full_workload_gate_present = false
figure5_full_matrix_gate_present = false
```

ModelNet40 all-400 is useful system evidence, but it is not a named Figure 5
category and must not be used as proof of Figure 5 reproduction.

## Decision

Goal5288 produces:

```text
status = figure5_author_timing_denominator_audit_ready__figure5_not_reproduced
figure5_reproduced = false
performance_ratio_allowed = false
same_denominator_author_rtdl_performance = false
```

Why Figure 5 is not reproduced:

```text
Author logs cover Figure 5 workload families but do not provide exact input bytes or hashes.
Current RTDL evidence covers ModelNet40 and selected graphics representatives, not BraTS and geospatial Figure 5 full workloads.
Author internal Running.AvgTime / ReportedTime medians are not the same denominator as RTDL route wall or process wall.
No denominator-aligned RTDL/author performance matrix exists for all Figure 5 categories.
```

## Claim Boundary

Allowed:

```text
Figure 5 has complete author run_all timing-log coverage for 507 pairs across
BraTS, geo, and graphics, but RTDL does not yet have a denominator-aligned full
Figure 5 matrix.
```

Not authorized:

```text
Figure 5 reproduced
RTDL/author Figure 5 speedup
author Running.AvgTime equals RTDL route wall
ModelNet40 all400 proves Figure 5
full X-HD paper reproduction
```

## Validation

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_figure5_timing_denominator_audit.py ^
  --log-index Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json ^
  --coverage-gap-matrix Paper-reproduction-apps\x-hd-paper\results\xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json ^
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
```

Result:

```text
status = figure5_author_timing_denominator_audit_ready__figure5_not_reproduced
matched = true
```

Focused validation to run for closeout:

```text
py -m unittest ^
  tests.goal5288_xhd_figure5_timing_denominator_audit_test ^
  tests.goal5267_xhd_full_paper_coverage_gap_matrix_test ^
  tests.goal5177_xhd_paper_target_log_mapping_test
```

## Next Recommended Step

Two realistic Figure 5 paths:

```text
1. Bounded Figure 5 subset:
   Select one or more author-log Figure 5 pairs with available or reconstructable
   inputs, then run author hd_exec and RTDL hd_exec-compatible routes on the
   same POD with explicitly separated author internal AvgTime, author process
   wall, RTDL route wall, and RTDL total wall.

2. Full Figure 5 matrix:
   Acquire or reconstruct BraTS, geo, and graphics inputs with provenance, then
   build a same-hardware denominator-aligned matrix.
```

Do not publish a Figure 5 performance ratio until one of these paths supplies
the missing denominator evidence.
