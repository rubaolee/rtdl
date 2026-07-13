# Call For Review: Goal5343 X-HD Mapped-Candidate POD Execution Plan

Please strictly review Goal5343.

Goal5343 adds an app-owned POD execution-plan builder for a future
mapped-candidate same-input packet. It does not execute the plan.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_mapped_candidate_pod_execution_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5343_mapped_candidate_pod_execution_plan.json
tests/goal5343_xhd_mapped_candidate_pod_execution_plan_test.py
history/internal_docs/goal5343_xhd_mapped_candidate_pod_execution_plan_result_2026-07-09.md
```

## Summary

The plan builder consumes a Goal5339 command-ready packet and emits:

```text
wrapper preflight command
wrapper upload commands
wrapper remote execute command
wrapper download commands
local Goal5340 comparator command
```

All remote operations are expressed through:

```text
scripts/current_pod_ssh.py
```

The goal does not run preflight, upload, execute, download, or compare outputs.

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

## Review Questions

1. Is it correct to add a POD execution-plan builder instead of manually
   translating local packet paths to remote paths later?
2. Does the plan builder require a Goal5339 command-ready packet and fail closed
   otherwise?
3. Does it avoid executing preflight/upload/remote commands/download/comparison?
4. Does it use `scripts/current_pod_ssh.py` for all remote operations?
5. Does it correctly rewrite local input paths into remote staged input paths?
6. Does it correctly rewrite author and RTDL command outputs into remote output
   paths?
7. Does it preserve the separation between plan, execution, output comparison,
   exact-input claims, and performance claims?
8. Is it correct that POD evidence still belongs to a later execution goal?
9. Is Goal5343 ready to close as
   `mapped_candidate_pod_execution_plan_ready__await_real_command_ready_packet`?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5343_mapped_candidate_pod_execution_plan
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5343

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
