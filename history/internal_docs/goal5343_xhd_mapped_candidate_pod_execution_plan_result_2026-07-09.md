# Goal5343 - X-HD Mapped-Candidate POD Execution Plan Result

Date: 2026-07-09

Status: `implemented_review_pending`

Exit label: `mapped_candidate_pod_execution_plan_ready__await_real_command_ready_packet`

## Purpose

Goal5343 adds an app-owned POD execution-plan builder for future X-HD
mapped-candidate same-input gates.

It consumes a Goal5339 command-ready packet, rewrites local materialized input
paths into a remote POD workspace, rewrites author and RTDL output paths, and
emits wrapper-only upload / remote execute / download / local comparator steps.

It does not run POD preflight, upload files, execute remote commands, download
outputs, or compare outputs.

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_mapped_candidate_pod_execution_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5343_mapped_candidate_pod_execution_plan.json
tests/goal5343_xhd_mapped_candidate_pod_execution_plan_test.py
```

## Plan Contract

Input:

```text
Goal5339 command-ready mapped-candidate same-input packet
remote root directory
remote repo root
remote author hd_exec path
remote Python executable
POD host and port
```

Output schema:

```text
rtdl.paper_reproduction.xhd.mapped_candidate_pod_execution_plan.v1
```

Classification:

```text
mapped_candidate_pod_execution_plan_ready
mapped_candidate_pod_execution_plan_not_ready
```

The ready plan includes:

```text
wrapper_preflight_command
upload_steps using scripts/current_pod_ssh.py upload
wrapper_remote_execute_command using scripts/current_pod_ssh.py exec
download_steps using scripts/current_pod_ssh.py download
local_comparator_command using compare_xhd_mapped_candidate_same_input_outputs.py
```

## Why This Goal Exists

Goal5339 creates command packets with concrete materialized local files.
Goal5342 can produce those packets from a local zip. Goal5343 closes the next
reproducibility gap: it prevents manual remote path rewriting, naked SSH/SCP
drift, and inconsistent remote output naming once a real command-ready packet
exists.

## Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5343_mapped_candidate_pod_execution_plan.json
json.tool OK

py -m unittest tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test
Ran 3 tests OK

py -m unittest tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test
Ran 6 tests OK

py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test
Ran 89 tests OK
```

## Test Coverage

Focused tests cover:

```text
command-ready packet -> wrapper-only POD execution plan
not-ready packet -> fail-closed not-ready plan
status artifact forbids execution/reproduction/performance claims
```

The ready-plan test confirms that generated commands use:

```text
scripts/current_pod_ssh.py
remote author hd_exec path
remote RTDL run_xhd_rtdl_hd_exec.py path
remote staged input paths
download steps for author and RTDL JSON outputs
local Goal5340 comparator command
```

## Claim Boundary

Allowed:

```text
Goal5343 builds a POD execution plan for a future command-ready mapped-candidate
packet. The plan uses scripts/current_pod_ssh.py for all remote operations.
```

Not allowed:

```text
claiming POD preflight ran
claiming files were uploaded
claiming author or RTDL commands were executed
claiming outputs were downloaded or compared
claiming same-input correctness
claiming exact paper dataset reproduction
claiming Figure 5 reproduction
claiming full X-HD paper reproduction
claiming author-vs-RTDL performance ratio
running naked ssh or scp instead of scripts/current_pod_ssh.py
```

## POD Usage

```text
used = false
expected_next = false for the status artifact
```

If a real artifact pipeline produces a command-ready packet, a separate POD
execution goal may use the generated plan. That later goal must record preflight,
uploads, remote commands, downloads, and Goal5340 output comparison as actual
evidence.
