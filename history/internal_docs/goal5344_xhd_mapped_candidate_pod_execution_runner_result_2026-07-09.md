# Goal5344 - X-HD Mapped-Candidate POD Execution Runner Result

Date: 2026-07-09

Status: `implemented_review_pending`

Exit label: `mapped_candidate_pod_execution_runner_ready__dry_run_only_until_real_plan`

## Purpose

Goal5344 adds an app-owned runner for Goal5343 mapped-candidate POD execution
plans.

The runner defaults to dry-run. It validates the plan and lists the exact
preflight / upload / remote execute / download / local compare stages that
would run. Real POD work requires the explicit `--execute` flag.

This goal does not execute POD, upload files, run author or RTDL commands,
download outputs, or compare outputs in its status artifact.

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_mapped_candidate_pod_execution_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5344_mapped_candidate_pod_execution_runner.json
tests/goal5344_xhd_mapped_candidate_pod_execution_runner_test.py
```

## Runner Contract

Input:

```text
Goal5343 mapped-candidate POD execution plan JSON
```

Default behavior:

```text
dry-run validation only
no preflight
no upload
no remote execute
no download
no local comparison
```

Execution behavior:

```text
requires --execute
runs preflight
runs uploads
runs remote author/RTDL command shell
runs downloads
runs local Goal5340 comparator
```

Output schema:

```text
rtdl.paper_reproduction.xhd.mapped_candidate_pod_execution_run.v1
```

Classifications:

```text
mapped_candidate_pod_execution_dry_run_ready
mapped_candidate_pod_execution_and_comparison_passed
mapped_candidate_pod_execution_finished_comparison_failed_or_missing
mapped_candidate_pod_execution_failed
mapped_candidate_pod_execution_run_not_ready
```

## Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5344_mapped_candidate_pod_execution_runner.json
json.tool OK

py -m unittest tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test
Ran 3 tests OK

py -m unittest tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test
Ran 6 tests OK

py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test
Ran 92 tests OK
```

## Test Coverage

Focused tests cover:

```text
ready plan dry-run lists all seven stages without executing them
not-ready plan fails closed
status artifact forbids POD/reproduction/performance claims
```

The seven dry-run stages are:

```text
preflight
upload input1
upload input2
remote_execute
download author JSON
download RTDL JSON
local_compare
```

## Claim Boundary

Allowed:

```text
Goal5344 adds a dry-run-by-default runner for future Goal5343 POD plans.
The runner can later execute wrapper-only steps with --execute.
```

Not allowed:

```text
claiming POD preflight ran from the status artifact
claiming files were uploaded or downloaded from the status artifact
claiming author or RTDL commands were executed from the status artifact
claiming outputs were compared from the status artifact
claiming same-input correctness
claiming exact paper dataset reproduction
claiming Figure 5 reproduction
claiming full X-HD paper reproduction
claiming author-vs-RTDL performance ratio
```

## POD Usage

```text
used = false
expected_next = false for the status artifact
```

If a future real command-ready plan exists, `--execute` may be used in a
separate POD execution goal. That later goal must record actual stage outputs
and any Goal5340 comparison result.
