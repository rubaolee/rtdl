# Goal5417 — Figure 5 Level-B Same-POD Matrix Plan

## Verdict

```text
completed_figure5_level_b_same_pod_matrix_plan__no_execution_yet
```

Goal5417 defines the next executable Figure-5-like Level-B matrix before any
new POD run.  It does not execute the matrix and does not claim Figure 5
reproduction or any author-vs-RTDL performance ratio.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json
```

Key status:

```text
status = figure5_level_b_same_pod_matrix_plan_ready__no_execution_yet
same_pod_execution_claimed = false
figure5_reproduction_claimed = false
performance_ratio_claimed = false
exact_paper_dataset_reproduction_claimed = false
```

## Included Candidates

### Primary Graphics Candidates

These are the strongest available Figure-5-like Level-B candidates:

| Case | Inputs | Evidence | Planned RTDL Routes |
|---|---|---|---|
| `dragon_happy` | Dragon -> HappyBuddha | author rerun matches paper-branch log; RTDL value matches author | `cell-mbr-fast-scalar`, `cell-mbr-exact-witness_if_operational` |
| `thai_happy_scaled` | ThaiStatuette scaled -> HappyBuddha | author rerun matches paper-branch log; RTDL exact-witness and fast-scalar match | `cell-mbr-exact-witness`, `cell-mbr-fast-scalar` |
| `thai_asian_scaled` | ThaiStatuette scaled -> AsianDragon scaled | author rerun matches paper-branch log; RTDL exact-witness and fast-scalar match | `cell-mbr-exact-witness`, `cell-mbr-fast-scalar` |

Important boundary:

```text
fast-scalar is exact-value-only when per_source_witness_exact=false.
```

### Secondary Bounded Geo Candidates

These are included only as bounded geo sanity rows, not full geo Figure 5:

| Case | Status |
|---|---|
| `county_zcta_bounded` | author/RTDL scalar match within 1e-5; bounded fixture only |
| `water_bg_bounded` | author/RTDL scalar match within 1e-5; bounded fixture only |

## Excluded Candidates

| Case | Reason |
|---|---|
| `dragon_asian_scaled` | author rerun does not match paper-branch author-log value |
| `brats_category` | input provenance/access blocked |
| `full_geo_county_zcta` | full-public County point count differs from paper by +32.2% |

## Planned Denominator Columns

The execution matrix must keep all denominator columns separate:

```text
case_id
category
input_identity_level
point_counts
paper_log_hd_result_if_available
author_rerun_hd_result
rtdl_hd_result
value_abs_diff_author_rtdl
value_abs_diff_author_paper_log
author_running_avg_time_ms
author_reported_time_ms
author_process_wall_sec
rtdl_route_label
rtdl_route_wall_sec
rtdl_process_wall_sec
rtdl_input_load_sec
per_source_witness_exact
cold_or_warm_process
same_pod_gpu
ratio_authorized
```

No ratio is authorized by the plan.  A later review must explicitly accept a
same-denominator ratio before one is reported.

## Execution Plan For Next Goal

Goal5417 itself does not use POD.

Recommended next execution goal:

```text
Goal5418_figure5_level_b_same_pod_matrix_execution
```

Required execution tools:

```text
author graphics runner:
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5298_author_graphics_precheck.py

RTDL hd_exec-compatible runner:
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py

RTDL batch runner:
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

POD access must use:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

Naked SSH is not allowed.

## Claim Boundary

Authorized:

- Figure 5 Level-B same-POD matrix plan;
- candidate inclusion/exclusion list;
- denominator column specification;
- Goal5418 execution recommendation.

Not authorized:

- Figure 5 reproduction;
- full Figure 5 matrix;
- exact paper dataset reproduction;
- author-vs-RTDL ratio;
- full X-HD paper reproduction;
- treating bounded geo fixtures as full geo Figure 5;
- treating fast-scalar early-break routes as exact witness reproduction.

## Validation

Commands:

```text
$env:PYTHONPATH='src'; py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json > $null
$env:PYTHONPATH='src'; py -m unittest tests.goal5417_figure5_level_b_same_pod_matrix_plan_test tests.goal5416_full_reproduction_priority_refresh_test tests.goal5415_stop_or_bounded_trace_gate_decision_test
```

Result:

```text
Ran 15 tests in 0.006s
OK
```

The local Python launcher printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Recommended Next Goal

```text
Goal5418_figure5_level_b_same_pod_matrix_execution
```

Goal5418 should run only after review of this plan or direct user approval.
It should execute the matrix, report all denominator columns side-by-side, and
still avoid ratios unless a same-denominator review authorizes one.
