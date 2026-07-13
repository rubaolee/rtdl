# Goal5337 - X-HD ACM Candidate Bytes / Hash Mapping Gate

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5337 adds an app-owned mapping gate for a future real ACM supplement zip
that contains candidate input/archive bytes and hash material.

It follows Goal5336. Goal5336 classifies artifact-like zip entries; Goal5337
parses simple SHA256 manifest lines and checks whether candidate entries are
covered by matching hashes.

This still does not authorize POD. Candidate bytes plus matching hashes are
not enough to claim exact X-HD paper inputs; the files must still be mapped to
paper workloads and reviewed.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_acm_candidate_bytes_hashes.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5337_acm_candidate_hash_mapping.json
tests/goal5337_xhd_acm_candidate_hash_mapping_test.py
```

## Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\map_xhd_acm_candidate_bytes_hashes.py <zip_path> [--output <mapping_json>]
```

Output schema:

```text
rtdl.paper_reproduction.xhd.acm_candidate_bytes_hash_mapping.v1
```

The script:

```text
1. reuses the Goal5336 zip ingestion/classification logic;
2. reads hash_or_manifest entries from the local zip;
3. parses simple SHA256 lines;
4. compares candidate input/archive sha256 values to manifest entries;
5. emits a conservative mapping status and next review gate.
```

Classification statuses:

```text
all_candidate_hashes_matched__workload_mapping_required
candidate_hash_mismatch_detected
partial_or_missing_candidate_hash_mapping
candidate_bytes_without_parseable_hash_manifest
no_candidate_bytes_to_map
```

Follow-up goal types:

```text
candidate_workload_mapping_review
candidate_hash_mismatch_review
candidate_hash_mapping_gap_review
candidate_identity_review
record_no_candidate_bytes
```

## Validated Behaviors

Tests cover:

```text
candidate bytes plus matching sha256 lines choose candidate_workload_mapping_review;
named candidate hash mismatch chooses candidate_hash_mismatch_review;
candidate bytes without parseable hash manifest choose candidate_identity_review;
invalid zip fails closed;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5337_acm_candidate_hash_mapping.json
py -m unittest tests.goal5337_xhd_acm_candidate_hash_mapping_test
py -m unittest tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test tests.goal5337_xhd_acm_candidate_hash_mapping_test
```

Observed:

```text
json.tool OK
Ran 5 tests OK
Ran 14 tests OK
Ran 66 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5337 adds an app-owned ACM candidate bytes/hash mapping gate. It can verify
simple SHA256 manifest coverage for candidate files, but still requires
workload mapping/review before POD.
```

Forbidden:

```text
claiming the real ACM supplement has been inspected from synthetic tests;
claiming candidate bytes are exact paper inputs from hash matches alone;
claiming exact paper dataset reproduction from this mapping alone;
claiming Figure 5 reproduction from this mapping alone;
claiming full X-HD paper reproduction from this mapping alone;
claiming author-vs-RTDL performance ratio from this mapping alone;
running POD directly from this mapping.
```

## POD Use

Goal5337 did not use POD.

Even if a future real zip produces:

```text
all_candidate_hashes_matched__workload_mapping_required
```

the next step is still:

```text
candidate_workload_mapping_review
```

That later gate must map candidate files to specific paper workloads before any
author/RTDL same-input gate can be justified.

## Exit Label

```text
acm_candidate_hash_mapping_gate_ready__await_real_candidate_zip
```
