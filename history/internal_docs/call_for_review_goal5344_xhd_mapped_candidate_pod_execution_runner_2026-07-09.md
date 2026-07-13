# Call For Review: Goal5344 X-HD Mapped-Candidate POD Execution Runner

Please strictly review Goal5344.

Goal5344 adds a dry-run-by-default runner for a Goal5343 mapped-candidate POD
execution plan. It does not execute POD in this goal.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_mapped_candidate_pod_execution_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5344_mapped_candidate_pod_execution_runner.json
tests/goal5344_xhd_mapped_candidate_pod_execution_runner_test.py
history/internal_docs/goal5344_xhd_mapped_candidate_pod_execution_runner_result_2026-07-09.md
```

## Summary

The runner consumes a Goal5343 plan. By default it dry-runs and emits all stages
without executing them. With explicit `--execute`, it can run:

```text
preflight
uploads
remote author/RTDL command shell
downloads
local Goal5340 comparator
```

The status artifact for Goal5344 is dry-run only and contains no POD execution
evidence.

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

## Review Questions

1. Is dry-run-by-default the correct safety posture?
2. Does the runner require `--execute` before any POD or local comparator work?
3. Does it fail closed when the Goal5343 plan is not ready?
4. Does it preserve the stage order correctly?
5. Does it preserve wrapper-only remote operations through
   `scripts/current_pod_ssh.py`?
6. Does it correctly separate dry-run, real execution, output comparison,
   same-input correctness, exact-input claims, and performance claims?
7. Are the tests sufficient for runner readiness without actual POD execution?
8. Is Goal5344 ready to close as
   `mapped_candidate_pod_execution_runner_ready__dry_run_only_until_real_plan`?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5344_mapped_candidate_pod_execution_runner
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5344

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
8. ...
```
