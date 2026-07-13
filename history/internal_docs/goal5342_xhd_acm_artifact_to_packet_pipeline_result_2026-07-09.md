# Goal5342 - X-HD ACM Artifact-To-Packet Pipeline Result

Date: 2026-07-09

Status: `implemented_review_pending`

Exit label: `acm_artifact_to_packet_pipeline_ready__await_real_zip_and_mapping`

## Purpose

Goal5342 adds an app-owned local orchestrator for the existing X-HD ACM
provenance tools.

Given a concrete local ACM supplement zip and a workload mapping spec, it runs:

```text
inspect_xhd_acm_supplement_zip.py
map_xhd_acm_candidate_bytes_hashes.py
review_xhd_candidate_workload_mapping.py
build_xhd_mapped_candidate_same_input_gate_packet.py
```

It also materializes candidate files from the zip into a staging directory so
the Goal5339 command packet can reference concrete local paths.

It does not execute author `hd_exec`, RTDL, POD, or Goal5340. It does not claim
same-input correctness, exact paper input identity, Figure 5 reproduction, full
paper reproduction, or performance ratio.

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_acm_artifact_to_packet_pipeline.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5342_acm_artifact_to_packet_pipeline.json
tests/goal5342_xhd_acm_artifact_to_packet_pipeline_test.py
```

## Pipeline Contract

Input:

```text
local ACM supplement zip path
candidate workload mapping spec JSON
output root
optional author hd_exec command name/path
optional RTDL route label
```

Output:

```text
artifacts/inspection.json
artifacts/candidate_mapping.json
artifacts/materialization.json
artifacts/workload_review.json
artifacts/mapped_candidate_same_input_gate_packet.json
materialized/<candidate files>
gate-output/<expected author/RTDL output paths>
```

Classifications:

```text
local_artifact_pipeline_packet_ready__await_pod_execution
local_artifact_pipeline_not_pod_ready
```

POD is allowed next only when the packet builder emits:

```text
mapped_candidate_same_input_gate_commands_ready
```

## Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5342_acm_artifact_to_packet_pipeline.json
json.tool OK

py -m unittest tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test
Ran 3 tests OK

py -m unittest tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test
Ran 15 tests OK

py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test
Ran 86 tests OK
```

## Test Coverage

Focused tests cover:

```text
accepted mapping + materialized candidate files -> command-ready packet
proposed mapping -> not POD-ready
status artifact forbids execution/reproduction/performance claims
```

The accepted mapping test uses a synthetic ACM-like zip with two PLY files and
a SHA256 manifest. This verifies the orchestration path without pretending that
the real ACM `ics26-106.zip` was available.

## Claim Boundary

Allowed:

```text
Goal5342 adds a local orchestrator for existing ACM artifact inspection,
candidate hash mapping, workload mapping review, candidate materialization, and
command-packet construction.
```

Not allowed:

```text
claiming the real ACM zip was processed by the status artifact
claiming author or RTDL commands were executed
claiming same-input correctness
claiming exact paper dataset reproduction
claiming Figure 5 reproduction
claiming full X-HD paper reproduction
claiming author-vs-RTDL performance ratio
```

## POD Usage

```text
used = false
expected_next = false for this status artifact
```

If a real local zip and accepted mapping spec produce
`local_artifact_pipeline_packet_ready__await_pod_execution`, then a separate POD
execution goal can run the generated packet using `scripts/current_pod_ssh.py`.

## Next Step

If an authorized ACM zip or author artifact appears:

```text
1. run run_xhd_acm_artifact_to_packet_pipeline.py
2. inspect the pipeline summary
3. if command-ready, open a separate POD execution goal
4. compare outputs with Goal5340
```

Until then, full exact-paper reproduction remains blocked on exact input
provenance.
