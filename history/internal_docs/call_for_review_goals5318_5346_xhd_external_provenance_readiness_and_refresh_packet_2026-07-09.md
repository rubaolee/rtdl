# Call For Review - Goals5318-5346 X-HD External Provenance Readiness And Refresh Packet

Date: 2026-07-09

## Scope

This packet extends the Goals5318-5345 external-provenance/POD-readiness packet
with Goal5346, a current external artifact surface refresh.

It covers:

```text
external artifact request/intake infrastructure;
ACM public metadata and live access probing;
local artifact-to-command-packet tooling;
POD execution plan and dry-run runner readiness;
exact reproduction readiness gate;
current ACM/GitHub/web surface refresh.
```

It does not claim X-HD exact paper reproduction or performance parity.

## Latest Results

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5345_exact_reproduction_readiness.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5346_external_artifact_surface_refresh.json
```

Latest reports:

```text
history/internal_docs/goal5345_xhd_exact_reproduction_readiness_gate_result_2026-07-09.md
history/internal_docs/goal5346_xhd_external_artifact_surface_refresh_result_2026-07-09.md
```

Latest call-for-review files:

```text
history/internal_docs/call_for_review_goal5345_xhd_exact_reproduction_readiness_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5346_xhd_external_artifact_surface_refresh_2026-07-09.md
```

## Current Final Status

Goal5345:

```text
classification = exact_reproduction_not_pod_ready__await_artifact_access
pod_execution_allowed_now = false
```

Goal5346:

```text
exit_label = external_artifact_surface_refresh_no_new_exact_input__acm_still_forbidden
new_exact_input_artifact_found = false
exact_input_blocker_removed = false
```

Current external state:

```text
ACM ics26-106.zip remains visible but forbidden from current environment:
  HEAD 403 / range GET 403 / HTML / no zip magic.

GitHub pwrliang/X-HD remains source/scripts/logs:
  branches main/paper/hybrid present;
  release_count = 0;
  no data directory or exact input artifact found.

Public web search refresh finds ACM metadata, public PDF, and source repo only.
```

## Validation

Latest tests:

```text
py -m unittest tests.goal5345_xhd_exact_reproduction_readiness_test
Ran 4 tests OK

py -m unittest tests.goal5346_xhd_external_artifact_surface_refresh_test
Ran 4 tests OK
```

Full observed external-provenance chain command:

```text
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test tests.goal5341_xhd_acm_live_access_probe_test tests.goal5342_xhd_acm_artifact_to_packet_pipeline_test tests.goal5343_xhd_mapped_candidate_pod_execution_plan_test tests.goal5344_xhd_mapped_candidate_pod_execution_runner_test tests.goal5345_xhd_exact_reproduction_readiness_test tests.goal5346_xhd_external_artifact_surface_refresh_test
Ran 100 tests OK
```

## Review Questions

1. Does the packet correctly preserve the distinction between readiness,
   artifact refresh, execution evidence, and reproduction evidence?
2. Does Goal5345 correctly block POD execution in the current state?
3. Does Goal5346 correctly refresh current external artifact surfaces without
   overclaiming from ACM/PDF/GitHub metadata?
4. Does the current ACM evidence justify only "visible but forbidden", not
   "contents inspected" or "contents absent"?
5. Does the current GitHub evidence justify only "source/scripts/logs, no
   release/data artifact found", not "all possible author artifacts exhausted"?
6. Does the packet keep POD usage disabled until a real artifact, accepted
   mapping, command-ready packet, ready plan, and explicit execution goal exist?
7. Does the packet avoid exact paper dataset, Figure 5, full paper
   reproduction, same-input pass, and performance-ratio claims?
8. Can Goals5318-5346 be accepted as external-provenance/readiness work while
   keeping the active full X-HD reproduction goal open?

## Expected Verdict Labels

Approve:

```text
approve_goals5318_5346_xhd_external_provenance_readiness_and_refresh_packet
```

Revise:

```text
revise_goals5318_5346_claim_boundary_or_pod_readiness
```

Block:

```text
block_goals5318_5346_if_refresh_or_readiness_is_misrepresented_as_reproduction
```

## Requested Answer Shape

Please provide:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to the 8 review questions:
```
