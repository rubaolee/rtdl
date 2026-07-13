# Goal5314 - X-HD WaterBodies/BG Corrected Comparison Summary Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5314 creates the corrected WaterBodies -> BlockGroups comparison layer
after Goal5313 identified the author-denominator drift.

It does not erase Goal5311 or Goal5312. Instead, it preserves them as historical
evidence and publishes the correct denominator for paper-log comparison:

```text
author hd_exec full-public WKT with n_points_cell=8
```

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
tests/goal5314_xhd_water_bg_corrected_comparison_summary_test.py
```

Source evidence consumed:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_n_points_cell_alignment_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_witness_distance_probe.json
```

## Corrected Denominator

The corrected summary explicitly records:

```text
paper_config_author_denominator =
  author_hd_exec_full_public_wkt_n_points_cell_8

supersedes_default_author_denominator_for_paper_log_comparison = true
default_author_rerun_retained_as_config_sensitivity_evidence = true
```

This is the central correction:

```text
Goal5311 default author rerun:
  n_points_cell = 15
  HDResult = 0.8970130085945129
  does not match paper log

Goal5313 paper-config author rerun:
  n_points_cell = 8
  HDResult = 0.8964367508888245
  matches paper log exactly
```

## RTDL Boundary

Goal5314 keeps the fast scalar route and exact-witness route separate.

Fast scalar:

```text
correctness_gate = false
reason = global-bound early-break; per-source witnesses not exact
```

Exact witness:

```text
correctness_gate = true
per_source_witness_exact = true
RTDL float64 HDResult = 0.8964380566690101
abs diff vs author paper-config = 1.305780185645311e-06
```

The tolerance boundary is explicit:

```text
author_numeric_type = float32
rtdl_reported_distance_type = float64
same_witness_float64_distance = 0.8964380566690101
same_witness_float32_distance = 0.8964367508888245
matches_at_1e_6 = false
matches_at_2e_6 = true
exact_float32_match = true
```

Thus the corrected comparison is:

```text
author paper-config scalar == paper log exactly
RTDL exact-witness float64 differs by ~1.31e-6
RTDL witness rounded to float32 equals author/paper exactly
```

## Validation

Commands:

```text
py -m unittest \
  tests.goal5314_xhd_water_bg_corrected_comparison_summary_test \
  tests.goal5313_xhd_water_bg_n_points_cell_alignment_test

py -m unittest \
  tests.goal5310_xhd_water_bg_full_public_wkt_candidate_test \
  tests.goal5311_xhd_water_bg_full_public_author_ingestion_test \
  tests.goal5312_xhd_water_bg_full_public_rtdl_summary_test \
  tests.goal5313_xhd_water_bg_n_points_cell_alignment_test \
  tests.goal5314_xhd_water_bg_corrected_comparison_summary_test
```

Results:

```text
Ran 6 tests OK
Ran 18 tests OK
```

## Claim Boundary

Allowed summary:

```text
For the full-public WaterBodies/BG candidate, author hd_exec with the paper-log
n_points_cell=8 configuration reproduces the paper-log scalar exactly. RTDL
exact-witness reports the corresponding witness in float64; the same witness
rounded to float32 equals the author/paper value. Use an explicit 2e-6 scalar
tolerance for RTDL float64-vs-author float32 comparison on this candidate.
```

Forbidden summaries:

```text
Exact paper WKT files are recovered.
Figure 5 is fully reproduced.
Performance parity is established.
Author and RTDL use identical numeric precision internally.
The Goal5311 n_points_cell=15 default author rerun is the paper-log denominator.
```

## Next Recommended Goal

Goal5315 should update the X-HD full-public status / README-style summary and
review register so WaterBodies-BG no longer appears as an unresolved author
scalar mismatch.

It must retain:

```text
no exact paper WKT file hash;
no Figure 5 completion;
no performance ratio;
explicit numeric tolerance boundary;
Goal5311 default rerun preserved as config-sensitivity evidence.
```
