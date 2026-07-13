# Goal5332 - X-HD External Response Ingest Runner

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5332 adds an app-owned ingest runner for future normalized X-HD external
response JSON.

It wraps the Goal5330 validator and creates an auditable incoming case
directory with:

```text
response.json
validation_result.json
manifest.json
next_action.md
```

This closes the manual gap between "owner receives an external response" and
"the project has a durable, fail-closed intake record."

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5332_external_response_ingest_runner.json
tests/goal5332_xhd_external_response_ingest_runner_test.py
```

## Runner Contract

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\ingest_xhd_external_response.py <response_json> [--incoming-dir <dir>] [--case-id <id>] [--overwrite]
```

Default incoming directory:

```text
Paper-reproduction-apps/x-hd-paper/requests/incoming
```

Exit codes:

```text
0 = valid response ingested
2 = invalid response or ingestion failure
3 = case directory already exists and --overwrite was not supplied
```

The runner always uses the existing Goal5330 validator:

```text
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
```

It does not implement a second classification policy.

## Validated Behaviors

Tests cover:

```text
valid positive archive response creates an auditable case and returns 0;
invalid template response is still recorded and returns 2;
duplicate case id fails closed with return code 3;
summary forbids exact/full/performance claims.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5332_external_response_ingest_runner.json
py -m unittest tests.goal5332_xhd_external_response_ingest_runner_test
py -m unittest tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test tests.goal5332_xhd_external_response_ingest_runner_test
```

Observed:

```text
json.tool OK
Ran 4 tests OK
Ran 16 tests OK
Ran 43 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5332 adds an app-owned intake runner for future normalized X-HD external
response JSON. It creates auditable case directories and reuses the Goal5330
validator.
```

Forbidden:

```text
claiming any real external response has arrived from Goal5332 alone;
claiming external artifacts have been acquired;
claiming ACM supplement has been inspected;
claiming exact-equivalence has been accepted;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5332 did not use POD.

POD remains deferred until a future real response validates as both:

```text
valid = true
pod_expected = true
```

At that point, a separate provenance-ingestion goal should use:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<cmd>"
```

## Exit Label

```text
external_response_ingest_runner_ready__await_real_response
```
