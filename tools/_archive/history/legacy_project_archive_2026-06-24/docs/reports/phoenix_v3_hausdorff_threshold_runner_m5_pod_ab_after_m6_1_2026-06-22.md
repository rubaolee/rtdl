# Phoenix V3 Hausdorff M5 POD A/B After M6.1

Date: 2026-06-22
Status: `focused_no_regression_pass_candidate_not_release_pending_review`

## Verdict

The M6.1 focused Hausdorff M5 canary passed the pre-authorized no-regression
gate:

- runner-vs-legacy phase-total: `1.0317x`
- runner-vs-legacy wrapper wall: `1.0541x`
- runner-vs-legacy query: `1.0841x`
- failed checks: none

This is positive focused runtime-trunk evidence. It is not V3 release
authorization, not all-app rerun authorization, and not public speedup wording.
It should be reviewed before being counted as a Set-A material runner-backed
probe.

## Artifact Paths

Local:

```text
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622_m6_1/
```

Remote:

```text
/root/rtdl_v3_rebuild_20260620/current/docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622_m6_1/
```

Remote backup before sync:

```text
/root/rtdl_v3_rebuild_20260620/phoenix_v3_patch_backups_20260622_m6_1
```

Hardware:

```text
NVIDIA RTX 4000 Ada Generation
driver 550.127.05
```

## Configuration

```text
points per side: 1,048,576
copies: 262,144
threshold: 0.4
repeat: 5
warmup: 1
variants:
  - same_contract_embree
  - legacy_app_front_door_prepared_optix
  - productized_prepared_execution_runner
```

## Remote Gates Before Benchmark

```text
py_compile:
  src/rtdsl/prepared_execution.py
  src/rtdsl/prepared_session_residency.py
  examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py
  scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py
  scripts/v3_phoenix_runner_overhead_microbench.py

tests:
  tests.v3_phoenix_prepared_execution_session_runner_test
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test
  tests.v3_phoenix_runner_overhead_microbench_test

38 tests OK
```

## Results

| Comparison | Query | Phase Total | Wrapper Wall |
| --- | ---: | ---: | ---: |
| Legacy OptiX vs Embree | 1.5118x | 1.1852x | 1.4589x |
| Runner OptiX vs Embree | 1.6389x | 1.2228x | 1.5378x |
| Runner vs Legacy | 1.0841x | 1.0317x | 1.0541x |

Failed checks:

```text
[]
```

Runner route phase disclosure:

```text
input_construction_sec: 3.768221378326416
scene_prepare_sec / runner_native_prepare_sec: 6.128043569624424
runner_outer_prepare_sec: 6.128261797130108
runner_outer_cache_load_sec: 0.0
query_fixed_radius_threshold_reached_count_sec: 6.076059751212597
runner_outer_query_sec: 6.076117627322674
runner_outer_query_total_sec: 27.648195885121822
validation_sec: 0.00017026811838150024
```

The native and outer prepare times are both visible. The aligned phase metric
uses the same native prepare scope as the legacy prepared OptiX route, while
wrapper wall remains the end-to-end guard against hidden runner tax.

## Metadata And Boundary Intake

The productized runner variant reported:

```text
prepared_execution_session_runner.used: true
both_directed_legs_runtime_executed: true
both_directed_legs_runtime_trunk_end_to_end: true
both_directed_legs_no_threshold_rows_materialized_on_host: true
both_directed_legs_internal_device_residency_between_rtdl_phases: true
```

All claim flags remained false:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_external_buffer_claim_authorized: false
all_app_rerun_authorized: false
whole_hausdorff_speedup_claim_authorized: false
```

## Classification

Current classification:

```text
focused_no_regression_pass_candidate_not_release_pending_review
```

This run passes the focused no-regression gate that M6.1 was authorized to
test. It also shows the productized runner-backed OptiX route beating the
same-contract Embree control by `1.2228x` phase-total and `1.5378x`
wrapper-wall on this threshold-summary canary.

Do not promote this automatically to V3 release evidence. Request result review
first. If accepted, it can be counted as a positive focused productized
runner-backed Hausdorff/threshold-summary probe. It still does not authorize an
all-app run by itself.

## Resource Use

Approximate paid POD use for the benchmark command:

```text
wall time: about 2.7 minutes benchmark command
sync/gate/copy overhead: a few minutes
estimated pod cost at $1 / 4 h: well under $0.25
```

## Next Action

Ask fallback reviewer to classify the result:

- `accept_as_positive_focused_runner_backed_hausdorff_probe_not_release`
- `accept_as_no_regression_only_not_material_probe`
- `reject_due_metric_alignment_or_hidden_cost`
- `reject_run_invalid_must_rerun`

Do not run another Hausdorff sample unless review says the run is invalid.

## Goal-Level Decision Audit

Decision: classify the M6.1 POD canary as a focused no-regression pass pending
review, not as release evidence.

1. Was I foolish?

   No for this decision. The run passed the exact focused gates that were
   authorized, but release/all-app/public claims remain blocked.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be using one focused canary to
   claim broad V3 performance.

3. Was there another path that would have avoided getting stuck?

   Yes. If the run had failed phase-total, the correct path would be query-path
   work, not reruns. Since it passed, the correct path is result review.

4. Can I now try a different path that actually solves the problem?

   Yes. Preserve this as one focused productized-runner probe and continue
   building the runtime trunk across additional Set-A families before any
   all-app run.
