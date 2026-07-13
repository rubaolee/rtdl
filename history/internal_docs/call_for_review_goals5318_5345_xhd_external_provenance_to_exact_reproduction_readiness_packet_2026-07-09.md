# Call For Review - Goals5318-5345 X-HD External Provenance To Exact Reproduction Readiness Packet

Date: 2026-07-09

## Scope

This consolidated packet covers the X-HD exact-input / external-provenance
readiness line from Goal5318 through Goal5345.

The packet is about:

```text
exact paper input acquisition attempts;
ACM supplement / external artifact probing;
candidate artifact inspection and mapping tools;
mapped same-input command packet preparation;
POD execution plan/runner readiness;
final readiness gate for whether real POD execution is currently authorized.
```

It is not a paper reproduction result and not a performance result.

## Latest Files

Latest result:

```text
history/internal_docs/goal5345_xhd_exact_reproduction_readiness_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5345_exact_reproduction_readiness.json
```

Latest call-for-review:

```text
history/internal_docs/call_for_review_goal5345_xhd_exact_reproduction_readiness_gate_2026-07-09.md
```

Prior combined packets:

```text
history/internal_docs/call_for_review_goals5318_5344_xhd_external_provenance_to_pod_runner_readiness_packet_2026-07-09.md
history/internal_docs/call_for_review_goals5318_5343_xhd_external_provenance_to_pod_plan_readiness_packet_2026-07-09.md
history/internal_docs/call_for_review_goals5318_5342_xhd_external_provenance_request_intake_validation_planning_refresh_acm_inspection_artifact_ingestion_hash_workload_mapping_gate_packet_comparator_live_probe_and_pipeline_2026-07-09.md
```

Key scripts added by the tail of the packet:

```text
Paper-reproduction-apps/x-hd-paper/scripts/probe_xhd_acm_supplement_live_access.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_acm_artifact_to_packet_pipeline.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_mapped_candidate_pod_execution_plan.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_mapped_candidate_pod_execution_plan.py
Paper-reproduction-apps/x-hd-paper/scripts/compare_xhd_mapped_candidate_same_input_outputs.py
Paper-reproduction-apps/x-hd-paper/scripts/check_xhd_exact_reproduction_readiness.py
```

## Current Final Status

Goal5345 currently reports:

```text
classification = exact_reproduction_not_pod_ready__await_artifact_access
pod_execution_allowed_now = false
artifact_access_or_zip_ready = false
command_ready_packet_ready = false
pod_execution_plan_ready = false
pod_runner_capability_ready = true
```

Meaning:

```text
The project has strong readiness infrastructure, but it must not run POD yet.
Exact/full X-HD paper reproduction remains unclosed until real artifact access,
accepted mapping, command packet, POD execution, and Goal5340 comparison exist.
```

## Validation Evidence

Latest focused tests:

```text
py -m unittest tests.goal5345_xhd_exact_reproduction_readiness_test
Ran 4 tests OK
```

Latest external-provenance chain tests:

```text
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test tests.goal5345_xhd_exact_reproduction_readiness_test
Ran 96 tests OK
```

## Review Questions

1. Does the Goals5318-5345 packet correctly distinguish external-provenance
   readiness from actual paper reproduction?
2. Does Goal5341 correctly report that ACM supplement access is currently
   visible but forbidden, with no zip contents inspected?
3. Does Goal5342 correctly stop at local artifact-to-command-packet readiness
   and avoid claiming author/RTDL execution?
4. Does Goal5343 correctly produce wrapper-only POD execution plans without
   claiming POD evidence?
5. Does Goal5344 correctly default to dry-run and require `--execute` for real
   POD work?
6. Does Goal5345 correctly block POD execution in the current state because
   artifact access, command-ready packet, and ready plan are missing?
7. Does the packet preserve the rule that all future POD work must use
   `scripts/current_pod_ssh.py`?
8. Do all claim boundaries remain intact: no exact paper input, no Figure 5,
   no full paper reproduction, no same-input output match, and no performance
   ratio yet?
9. Is the next action correctly stated: obtain real ACM/author artifact access
   first, then run Goal5341 -> Goal5342 -> Goal5343 -> Goal5345 -> Goal5344
   `--execute` -> Goal5340 comparison?
10. Can Goals5318-5345 be accepted as a readiness packet while keeping the full
    X-HD paper reproduction objective open?

## Expected Verdict Labels

Approve:

```text
approve_goals5318_5345_xhd_external_provenance_to_readiness_packet
```

Revise:

```text
revise_goals5318_5345_readiness_packet_for_claim_boundary_or_pod_gate
```

Block:

```text
block_goals5318_5345_if_readiness_is_misrepresented_as_reproduction
```

## Requested Answer Shape

Please provide:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to the 10 review questions:
```
