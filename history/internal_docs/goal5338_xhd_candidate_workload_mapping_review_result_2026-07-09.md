# Goal5338 - X-HD Candidate Workload Mapping Review Gate

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5338 adds an app-owned workload mapping review gate for future real ACM
candidate input files.

It follows Goal5337. Goal5337 can prove that candidate files are covered by
SHA256 manifest entries. Goal5338 validates whether those hashed candidate
files are explicitly mapped to known X-HD paper workload roles before any
same-input POD gate is allowed.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/review_xhd_candidate_workload_mapping.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5338_candidate_workload_mapping_review.json
tests/goal5338_xhd_candidate_workload_mapping_review_test.py
```

## Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\review_xhd_candidate_workload_mapping.py <candidate_mapping_json> <mapping_spec_json> [--target-matrix <target_matrix_json>] [--output <review_json>]
```

Input schemas:

```text
rtdl.paper_reproduction.xhd.acm_candidate_bytes_hash_mapping.v1
rtdl.paper_reproduction.xhd.candidate_workload_mapping_spec.v1
rtdl.paper_reproduction.xhd.paper_target_matrix.v1
```

Output schema:

```text
rtdl.paper_reproduction.xhd.candidate_workload_mapping_review.v1
```

The mapping spec must provide:

```text
external_mapping_review_status: proposed | accepted
workload_id
figure
direction: input1_to_input2
input_type: image | wkt | ply | off
n_dims: 2 | 3
input1.candidate_path
input1.paper_dataset_name
input2.candidate_path
input2.paper_dataset_name
mapping_evidence
```

Dataset names are validated against:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
```

## Classification

Statuses:

```text
accepted_workload_mapping_ready_for_same_input_gate
proposed_workload_mapping_requires_external_acceptance
workload_mapping_invalid_or_incomplete
```

Follow-up goal types:

```text
mapped_candidate_same_input_author_rtdl_gate
external_workload_mapping_acceptance_review
repair_candidate_workload_mapping
```

Even the accepted path only authorizes a later separate same-input POD gate; it
does not itself claim exact paper reproduction.

## Validated Behaviors

Tests cover:

```text
accepted clean mapping becomes same-input gate ready but still not an exact-input claim;
proposed mapping requires external acceptance before POD;
unknown paper dataset fails closed;
dirty candidate hash mapping fails closed;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5338_candidate_workload_mapping_review.json
py -m unittest tests.goal5338_xhd_candidate_workload_mapping_review_test
py -m unittest tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test tests.goal5338_xhd_candidate_workload_mapping_review_test
```

Observed:

```text
json.tool OK
Ran 5 tests OK
Ran 10 tests OK
Ran 71 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5338 adds an app-owned candidate workload mapping review gate. It checks
that hashed candidate files are mapped to known paper workload roles before a
separate same-input POD gate may be opened.
```

Forbidden:

```text
claiming the real ACM supplement has been inspected from synthetic tests;
claiming candidate files are exact paper inputs from workload mapping alone;
claiming exact paper dataset reproduction from this review alone;
claiming Figure 5 reproduction from this review alone;
claiming full X-HD paper reproduction from this review alone;
claiming author-vs-RTDL performance ratio from this review alone;
running POD outside a separate mapped same-input gate.
```

## POD Use

Goal5338 did not use POD.

Only this status:

```text
accepted_workload_mapping_ready_for_same_input_gate
```

can authorize the next separate POD goal:

```text
mapped_candidate_same_input_author_rtdl_gate
```

All other statuses remain local review / repair work.

## Exit Label

```text
candidate_workload_mapping_review_ready__await_real_mapping_spec
```
