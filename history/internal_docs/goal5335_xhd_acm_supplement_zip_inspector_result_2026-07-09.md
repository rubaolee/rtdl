# Goal5335 - X-HD ACM Supplement Zip Inspector

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5335 adds an app-owned local inspector for a future ACM supplement zip,
especially the unresolved:

```text
ics26-106.zip
```

If an owner or ACM-access reviewer obtains the zip, the inspector can generate
normalized Goal5329 intake JSON for the existing validator / ingest / planner
chain.

This goal does not inspect the real ACM zip and does not claim supplement
contents.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5335_acm_supplement_zip_inspector.json
tests/goal5335_xhd_acm_supplement_zip_inspector_test.py
```

Modified:

```text
Paper-reproduction-apps/x-hd-paper/scripts/plan_xhd_provenance_ingestion_from_case.py
```

The planner now maps:

```text
acm_artifact_instructions_present__ingest_before_pod
```

to:

```text
ready_for_separate_artifact_instruction_ingestion_goal
recommended_goal_type = acm_artifact_instruction_ingestion_gate
pod_allowed_next = false
```

This is deliberate: artifact instructions must be ingested before any POD gate.

## Inspector Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\inspect_xhd_acm_supplement_zip.py <zip_path> \
  --reviewer-name <name> \
  --contact-or-source <source> \
  --received-date <YYYY-MM-DD> \
  [--output <response_json>]
```

Output schema:

```text
rtdl.paper_reproduction.xhd.external_response_intake.v1
```

Response type:

```text
acm_supplement_artifact_instructions
```

The inspector records:

```text
zip filename;
zip sha256;
total file count;
top-level file listing;
all file names;
contains_artifact_material;
dataset_or_hash_entries;
script_or_instruction_entries.
```

Heuristics are intentionally conservative and review-required:

```text
dataset/hash-like entries by dataset suffixes, archive suffixes, hash tokens,
or dataset tokens;
script/instruction-like entries by script suffixes or README/artifact/
reproduce/download tokens.
```

## Validated Behaviors

Tests cover:

```text
camera-ready-only synthetic zip emits no-artifact ACM listing and validator
  keeps blocked;
artifact-bearing synthetic zip emits dataset/hash and script entries;
artifact-bearing synthetic response flows through validator, ingest runner,
  and planner;
planner maps artifact-bearing ACM case to a separate
  acm_artifact_instruction_ingestion_gate with pod_allowed_next=false;
invalid zip fails without output claim;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5335_acm_supplement_zip_inspector.json
py -m unittest tests.goal5335_xhd_acm_supplement_zip_inspector_test
py -m unittest tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5335_xhd_acm_supplement_zip_inspector_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test tests.goal5334_xhd_public_artifact_refresh_test tests.goal5335_xhd_acm_supplement_zip_inspector_test
```

Observed:

```text
json.tool OK
Ran 4 tests OK
Ran 9 tests OK
Ran 56 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5335 adds an app-owned local inspector for a future ACM supplement zip. It
can generate normalized intake JSON for the existing validator/ingest/planner
chain.
```

Forbidden:

```text
claiming the real ACM supplement has been inspected from synthetic tests;
claiming the real ACM supplement contains datasets;
claiming the real ACM supplement contains no useful artifacts;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5335 did not use POD.

Even if a future real ACM zip contains artifact-like entries, the immediate
next action is artifact-instruction ingestion, not direct POD.

POD remains deferred until a later ingestion goal turns artifact instructions
into concrete input bytes, hashes, regeneration commands, or accepted
equivalence criteria.

## Exit Label

```text
acm_supplement_zip_inspector_ready__await_real_zip
```
