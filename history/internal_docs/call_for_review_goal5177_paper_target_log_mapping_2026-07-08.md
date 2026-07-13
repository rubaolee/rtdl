# Call For Review: Goal5177 Paper Target Log Mapping

Date: 2026-07-08

Please strictly review Goal5177.

## Files Under Review

Result report:

```text
history/internal_docs/goal5177_paper_target_log_mapping_result_2026-07-08.md
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_paper_targets_to_logs.py
tests/goal5177_xhd_paper_target_log_mapping_test.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Allowed claim:

```text
Goal5177 maps the Goal5130 X-HD paper figure targets to the Goal5176
paper-branch run_all log index. It identifies which Figure 5-11 targets have
run_all workload/timing evidence, which are only partially covered, which are
not covered by run_all timing logs, and which priority input subsets should be
considered next. This is figure-target provenance only.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
paper figure reproduction
author-performance parity
author-vs-RTDL performance ratio
path/statistics proving exact input identity
Figure 5-11 results reproduced
```

## Critical Context

Goal5176 parsed the author `paper` branch logs and retained all 4535 `run_all`
records. Those records contain author paths, HDResult, Running.AvgTime,
ReportedTime medians, point counts, MBRs, and GPU names.

They do not contain input file bytes, input file hashes, public source snapshot
hashes, or proof that reconstructed public inputs are byte-identical to the
paper inputs.

Goal5177 must therefore be judged as a provenance/mapping goal, not a
reproduction or performance goal.

## Evidence Summary

Generated artifact:

```text
xhd_paper_target_log_mapping_goal5177_2026-07-08.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.paper_target_log_mapping.v1
status = xhd_paper_target_log_mapping_ready__no_figure_reproduction_claim
run_all_summary.record_count = 4535
run_all_summary.unique_pair_count = 907
claim_boundary.full_paper_reproduction_claimed = false
claim_boundary.exact_paper_dataset_reproduction_claimed = false
claim_boundary.figure_reproduction_claimed = false
claim_boundary.performance_ratio_claimed = false
claim_boundary.paper_input_bytes_available = false
exact_dataset_rule.statistics_matching_is_not_exact_identity = true
```

Figure coverage:

```text
Figure 5:
  run_all_timing_logs_cover_required_workload_families__inputs_missing
  records = 2535

Figure 6:
  partially_covered_by_run_all_timing_logs__phase_counters_missing
  records = 5

Figure 7:
  partially_covered_by_run_all_workloads__load_balance_metrics_missing
  records = 25

Figure 8:
  not_covered_by_run_all_timing_logs
  records = 0

Figure 9:
  partially_covered_by_auto_tune_logs__grid_sweep_semantics_missing
  records = 1814

Figure 10:
  workload_families_present__scale_overlap_labels_missing
  records = 4535

Figure 11:
  not_covered_by_run_all_timing_logs
  records = 0
```

Priority subsets:

```text
graphics_dragon_happy_buddha
graphics_dragon_asian_dragon
geo_county_zipcode
geo_lakes_parks
brats_first_logged_pair
```

Validation:

```text
py -m unittest tests.goal5177_xhd_paper_target_log_mapping_test tests.goal5176_xhd_paper_branch_log_index_test

Ran 2 tests in 0.965s
OK
```

## Review Questions

1. Does Goal5177 correctly treat `run_all` logs as figure-target provenance
   rather than figure reproduction?
2. Are the Figure 5-11 coverage statuses supported by the artifact and the
   Goal5176 run_all index?
3. Is Figure 5 correctly described as strongest workload-family coverage but
   still blocked by missing input bytes/hashes and denominator alignment?
4. Are Figures 6/7/9/10 correctly classified as partial coverage rather than
   reproduced figures?
5. Are Figures 8 and 11 correctly classified as not covered by run_all timing
   logs?
6. Does the artifact preserve the exact-dataset boundary, especially
   `statistics_matching_is_not_exact_identity = true`?
7. Are the priority subsets useful and honestly bounded, or do they accidentally
   overclaim exact paper dataset availability?
8. Is the focused unit test sufficient for mapping logic and claim-boundary
   flags?
9. Does the manifest/register update keep Goal5177 as implemented / review
   pending, not externally approved?
10. Should Goal5177 close as
    `completed_paper_target_log_mapping__implemented_review_pending`, or are
    amendments required?

## Expected Answer Shape

```text
Verdict:
  approve_goal5177_paper_target_log_mapping
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  ...
```
