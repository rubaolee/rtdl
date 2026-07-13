# Goal5336 - X-HD ACM Artifact-Instruction Ingestion Manifest

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5336 adds an app-owned artifact-instruction ingestion manifest builder for
a future real ACM supplement zip.

It is the follow-up to Goal5335. If the zip contains artifact-like entries,
Goal5336 computes per-entry hashes, classifies entries, and selects the next
follow-up gate.

It does not run POD, run author binaries, run RTDL, extract private material
into the public repository, or claim exact paper reproduction.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5336_acm_artifact_instruction_ingestion.json
tests/goal5336_xhd_acm_artifact_instruction_ingestion_test.py
```

## Manifest Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\ingest_xhd_acm_artifact_instructions.py <zip_path> [--output <manifest_json>]
```

Output schema:

```text
rtdl.paper_reproduction.xhd.acm_artifact_instruction_ingestion_manifest.v1
```

For artifact-like entries, the manifest records:

```text
path;
category;
size;
sha256.
```

Classification statuses:

```text
candidate_bytes_and_hash_material_found
candidate_bytes_without_hash_material_found
script_or_instruction_material_found
no_actionable_artifact_material_found
```

Follow-up goal types:

```text
acm_candidate_bytes_hash_mapping_gate
acm_candidate_bytes_identity_review
acm_regeneration_or_instruction_review
record_acm_no_actionable_artifact
```

## Validated Behaviors

Tests cover:

```text
candidate bytes plus hash material choose acm_candidate_bytes_hash_mapping_gate;
script/instruction-only material chooses acm_regeneration_or_instruction_review;
manuscript-only zip chooses record_acm_no_actionable_artifact;
invalid zip fails closed;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5336_acm_artifact_instruction_ingestion.json
py -m unittest tests.goal5336_xhd_acm_artifact_instruction_ingestion_test
py -m unittest tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test tests.goal5336_xhd_acm_artifact_instruction_ingestion_test
```

Observed:

```text
json.tool OK
Ran 5 tests OK
Ran 9 tests OK
Ran 61 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5336 adds an app-owned ACM artifact-instruction ingestion manifest builder
for a future real ACM supplement zip. It computes per-entry hashes for
artifact-like files and selects a follow-up gate without running POD.
```

Forbidden:

```text
claiming the real ACM supplement has been inspected from synthetic tests;
claiming exact paper dataset reproduction from this manifest alone;
claiming Figure 5 reproduction from this manifest alone;
claiming full X-HD paper reproduction from this manifest alone;
claiming author-vs-RTDL performance ratio from this manifest alone;
running POD directly from this manifest.
```

## POD Use

Goal5336 did not use POD.

Even if a future real zip contains candidate bytes and hashes, the immediate
next action is a mapping/review gate:

```text
acm_candidate_bytes_hash_mapping_gate
```

That later gate must map entries to paper workloads, verify hashes, and only
then decide whether a POD author/RTDL same-input gate is justified.

## Exit Label

```text
acm_artifact_instruction_ingestion_ready__await_real_artifact_zip
```
