# Goal5333 - X-HD Provenance Ingestion Action Planner

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5333 adds an app-owned action planner for case directories produced by
Goal5332.

It reads:

```text
requests/incoming/<case-id>/manifest.json
requests/incoming/<case-id>/validation_result.json
```

and emits a fail-closed provenance action plan. The plan explains whether the
case is ready for a separate provenance-ingestion goal, should remain blocked,
or must be repaired before use.

The planner does not run POD, inspect private artifacts, or change any
reproduction claim.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/plan_xhd_provenance_ingestion_from_case.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5333_provenance_ingestion_action_planner.json
tests/goal5333_xhd_provenance_ingestion_action_planner_test.py
```

## Planner Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\plan_xhd_provenance_ingestion_from_case.py <case_dir> [--write] [--overwrite] [--output <path>]
```

When `--write` is supplied, the planner writes into the case directory:

```text
provenance_action_plan.json
provenance_action_plan.md
```

Plan statuses:

```text
ready_for_separate_provenance_ingestion_goal
valid_response_but_no_pod_gate__keep_blocked_or_request_missing_material
invalid_response__keep_blocked
invalid_case_record__repair_before_use
```

The planner requires a separate follow-up goal before any POD work:

```text
requires_new_goal_before_pod = true
```

## Validated Behaviors

Tests cover:

```text
positive archive case maps to author_archive_provenance_ingestion_gate and
  pod_allowed_next=true;
hash-only case stays blocked with pod_allowed_next=false;
invalid template case requests corrected response;
inconsistent manifest/validation_result fails closed;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5333_provenance_ingestion_action_planner.json
py -m unittest tests.goal5333_xhd_provenance_ingestion_action_planner_test
py -m unittest tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test tests.goal5333_xhd_provenance_ingestion_action_planner_test
```

Observed:

```text
json.tool OK
Ran 5 tests OK
Ran 21 tests OK
Ran 48 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5333 adds an app-owned provenance action planner for ingested X-HD external
response cases. It maps validated cases to follow-up goal types and POD
eligibility without running POD.
```

Forbidden:

```text
running POD directly from the planner;
claiming exact paper dataset reproduction from a plan alone;
claiming Figure 5 reproduction from a plan alone;
claiming full X-HD paper reproduction from a plan alone;
claiming author-vs-RTDL performance ratio from a plan alone.
```

## POD Use

Goal5333 did not use POD.

POD remains deferred until:

```text
1. a real response is ingested;
2. the validator reports valid=true and pod_expected=true;
3. the planner reports ready_for_separate_provenance_ingestion_goal;
4. a separate provenance-ingestion goal is opened.
```

At that point, use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<cmd>"
```

## Exit Label

```text
provenance_action_planner_ready__await_real_ingested_case
```
