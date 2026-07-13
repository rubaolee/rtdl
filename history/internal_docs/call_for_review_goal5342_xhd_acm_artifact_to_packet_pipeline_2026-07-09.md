# Call For Review: Goal5342 X-HD ACM Artifact-To-Packet Pipeline

Please strictly review Goal5342.

Goal5342 adds a local orchestrator that turns a concrete ACM supplement zip and
a workload mapping spec into a Goal5339 mapped-candidate same-input command
packet.

This is still a local provenance/readiness goal. It does not execute author or
RTDL commands, does not run POD, and does not claim reproduction or performance.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_acm_artifact_to_packet_pipeline.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5342_acm_artifact_to_packet_pipeline.json
tests/goal5342_xhd_acm_artifact_to_packet_pipeline_test.py
history/internal_docs/goal5342_xhd_acm_artifact_to_packet_pipeline_result_2026-07-09.md
```

## Pipeline

The script orchestrates existing tools:

```text
inspect_xhd_acm_supplement_zip.py
map_xhd_acm_candidate_bytes_hashes.py
review_xhd_candidate_workload_mapping.py
build_xhd_mapped_candidate_same_input_gate_packet.py
```

It materializes candidate files from the zip into a staging directory and emits
the command packet expected by the later POD execution goal.

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

## Review Questions

1. Is it correct to add this local orchestrator instead of manually running the
   Goal5335-Goal5339 scripts once a real zip appears?
2. Does it correctly reuse existing tools rather than introducing a second
   interpretation of the artifact/mapping contracts?
3. Does it correctly materialize candidate files while preserving fail-closed
   behavior for proposed mappings?
4. Does an accepted mapping plus matching materialized files produce a
   command-ready packet in tests?
5. Does a proposed mapping remain not POD-ready?
6. Does the pipeline correctly avoid executing author/RTDL commands?
7. Does the pipeline correctly avoid claiming same-input correctness, exact
   paper input reproduction, Figure 5 reproduction, full paper reproduction, or
   performance ratio?
8. Is it correct that POD begins only in a later execution goal after the
   pipeline emits a command-ready packet?
9. Is Goal5342 ready to close as
   `acm_artifact_to_packet_pipeline_ready__await_real_zip_and_mapping`?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5342_acm_artifact_to_packet_pipeline
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5342

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
9. ...
```
