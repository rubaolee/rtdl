# Goal5177 Paper Target Log Mapping Result

Date: 2026-07-08

## Verdict

```text
completed_paper_target_log_mapping__implemented_review_pending
```

Goal5177 maps the X-HD paper target matrix from Goal5130 to the author
paper-branch `run_all` log index from Goal5176.

This is figure-target provenance. It is not exact paper dataset reproduction,
figure reproduction, full paper reproduction, or a performance ratio.

## Why This Goal Exists

Goal5176 made the author `paper` branch workload logs machine-readable:

```text
run_all records: 4535
sections:        auto_tune, eb_gpu, hybrid_gpu, rt_gpu
categories:      BraTS2020_ValidationData, ModelNet40, geo, graphics
```

That is still not enough to say any paper figure is reproduced. Goal5177 asks a
more precise question:

```text
Which Figure 5-11 targets have author run_all log evidence, and what is still
missing before a figure-level reproduction claim is allowed?
```

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_paper_targets_to_logs.py
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\map_xhd_paper_targets_to_logs.py \
  --target-matrix Paper-reproduction-apps\x-hd-paper\results\xhd_paper_target_matrix_2026-07-08.json \
  --log-index Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_paper_target_log_mapping_goal5177_2026-07-08.json \
  --max-examples 5
```

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.paper_target_log_mapping.v1
```

## Run-All Coverage Summary

```text
run_all records:   4535
unique pairs:       907

by section:
  auto_tune:        1814
  eb_gpu:            907
  hybrid_gpu:        907
  rt_gpu:            907

by category:
  BraTS2020_ValidationData: 2500
  ModelNet40:               2000
  geo:                        15
  graphics:                   20
```

`ModelNet40` appears in the paper-branch `run_all` logs but was not a named
Goal5130 Table 1 target. The artifact keeps it as paper-branch workload
evidence rather than silently adding it to the paper target matrix.

## Figure Mapping Result

```text
Figure 5:
  status: run_all_timing_logs_cover_required_workload_families__inputs_missing
  records: 2535
  unique pairs: 507
  meaning: strongest paper-log workload coverage, but still missing input
           bytes/hashes and fair author/RTDL denominator alignment.

Figure 6:
  status: partially_covered_by_run_all_timing_logs__phase_counters_missing
  records: 5
  unique pairs: 1
  meaning: Dragon-AsianDragon exists across run_all sections, but pruning
           counters / phase mapping are absent.

Figure 7:
  status: partially_covered_by_run_all_workloads__load_balance_metrics_missing
  records: 25
  unique pairs: 5
  meaning: Lakes-Parks plus graphics workloads exist, but load-balance phase
           metrics are absent.

Figure 8:
  status: not_covered_by_run_all_timing_logs
  records: 0
  meaning: radius-growing strategy is not represented by the extracted run_all
           timing records.

Figure 9:
  status: partially_covered_by_auto_tune_logs__grid_sweep_semantics_missing
  records: 1814
  unique pairs: 907
  meaning: auto_tune records exist, but the full adaptive-grid semantics and
           selected paper grid-size choices are not yet mapped.

Figure 10:
  status: workload_families_present__scale_overlap_labels_missing
  records: 4535
  unique pairs: 907
  meaning: many workload records exist, but scale/overlap subset labels are
           missing.

Figure 11:
  status: not_covered_by_run_all_timing_logs
  records: 0
  meaning: extracted run_all records do not contain GPU memory footprint
           metrics.
```

Coverage status counts:

```text
not_covered_by_run_all_timing_logs:                         2
partially_covered_by_auto_tune_logs__grid_sweep_semantics_missing: 1
partially_covered_by_run_all_timing_logs__phase_counters_missing:  1
partially_covered_by_run_all_workloads__load_balance_metrics_missing: 1
run_all_timing_logs_cover_required_workload_families__inputs_missing: 1
workload_families_present__scale_overlap_labels_missing:    1
```

## Priority Input Subsets

Goal5177 does not choose a paper claim. It identifies the smallest useful
follow-up input targets:

```text
graphics_dragon_happy_buddha:
  purpose: first end-to-end paper-log-to-RTDL route rehearsal, because this is
           close to the existing Level B Stanford route.
  records: 5
  blocker: author/exact converted PLY bytes or same-source reconstruction.

graphics_dragon_asian_dragon:
  purpose: Figure 6 pruning-effectiveness target pair.
  records: 5
  blocker: pruning phase counters plus input bytes/hashes.

geo_county_zipcode:
  purpose: moderate geospatial Figure 5 family target.
  records: 5
  blocker: WKT source snapshot/conversion proof.

geo_lakes_parks:
  purpose: large Figure 7 / Figure 5 geospatial stress target.
  records: 5
  blocker: large WKT input files and load-balance phase metrics.

brats_first_logged_pair:
  purpose: MRI Figure 5 family smoke target.
  records: 5
  blocker: BraTS access/license plus exact validation image list or same-source
           labeling.
```

## Exact Dataset Boundary

The logs provide:

```text
author path names
dataset basenames
HDResult
Running.AvgTime
ReportedTime medians
point counts and MBRs when logged
```

The logs do not provide:

```text
input file bytes
input file hashes
public source snapshot hashes
proof that reconstructed public data are exact paper inputs
```

The artifact explicitly records:

```text
statistics_matching_is_not_exact_identity = true
```

## Manifest Update

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

The manifest now includes the Goal5177 artifact under `evidence.result_artifacts`.

## Validation

Commands:

```text
py -m unittest tests.goal5177_xhd_paper_target_log_mapping_test tests.goal5176_xhd_paper_branch_log_index_test
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_paper_target_log_mapping_goal5177_2026-07-08.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
```

Result:

```text
Ran 2 tests in 0.965s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite this Windows Python noise.

## What This Proves

Goal5177 proves that the paper-branch `run_all` logs can be mapped to the
paper's Figure 5-11 target matrix and that the current evidence can separate:

```text
workload-family log coverage
partial phase coverage
missing input provenance
missing phase counters
missing memory metrics
```

## What This Does Not Prove

Goal5177 does not prove:

```text
full X-HD paper reproduction
exact paper dataset reproduction
any Figure 5-11 result
author-vs-RTDL performance ratio
RTDL reproducing pruning/load-balance/radius/grid/memory figures
input file identity from path/statistics alone
```

## Next Recommended Goal

Use the priority subsets to choose the first acquisition/reconstruction target.

The most practical next target is:

```text
graphics_dragon_happy_buddha
```

Reason: it is small, same-source Stanford graphics, already close to the
existing Level B RTDL route, and still appears in the paper-branch `run_all`
matrix. It can become a disciplined paper-log-to-route rehearsal without
pretending to be Level C exact paper dataset reproduction.
