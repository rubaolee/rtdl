# Goal5330 - X-HD External Response Intake Validator

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5330 adds an executable validator/dispatcher for future X-HD external
response intake JSON.

It turns the Goal5329 response-intake protocol into a local CLI:

```text
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
```

The validator classifies author, ACM-access, or exact-equivalence responses
fail-closed before any POD gate or reproduction claim.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5330_external_response_intake_validator.json
tests/goal5330_xhd_external_response_intake_validator_test.py
```

## Validator Contract

Input schema:

```text
rtdl.paper_reproduction.xhd.external_response_intake.v1
```

Output schema:

```text
rtdl.paper_reproduction.xhd.external_response_intake.validation_result.v1
```

Exit codes:

```text
0 = valid classified response
2 = invalid / fail-closed response
```

Default behavior:

```text
fail_closed
```

The validator never by itself authorizes:

```text
exact paper dataset reproduction;
Figure 5 reproduction;
full X-HD paper reproduction;
author-vs-RTDL performance ratio.
```

## Covered Response Types

```text
author_hash_manifest
author_input_archive
byte_identical_regeneration_script
acm_supplement_artifact_instructions
exact_equivalence_verdict
explicit_non_availability_statement
other
```

## Classification Output

The validator emits:

```text
valid;
errors;
warnings;
response_type;
next_action;
pod_expected;
sufficient_to_claim_exact_input;
requires_review_before_claim;
claim_boundary;
not_allowed.
```

Important invariant:

```text
sufficient_to_claim_exact_input = false
```

Exact claims require a later provenance-ingestion and review goal.

## Validated Behaviors

Tests cover:

```text
template_not_filled fails closed and exits invalid;
author_hash_manifest with available bytes can trigger POD gate but not exact claim;
author_hash_manifest without bytes does not trigger POD;
author_input_archive triggers POD after hash recording/extraction;
ACM listing with no artifact material marks supplement inspected but no POD;
exact-equivalence acceptance can trigger a bounded POD matrix but not full-paper claim;
explicit non-availability statement stays blocked;
CLI writes validation output and returns expected exit code.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5330_external_response_intake_validator.json
py -m unittest tests.goal5330_xhd_external_response_intake_validator_test
py -m unittest tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test
py Paper-reproduction-apps\x-hd-paper\scripts\validate_xhd_external_response_intake.py Paper-reproduction-apps\x-hd-paper\requests\external_response_intake_template.json
```

Observed:

```text
Ran 8 tests OK
Ran 15 tests OK
template command exits 2 and reports valid=false
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5330 adds an executable app-owned validator for future X-HD external
response intake JSON. It classifies responses fail-closed.
```

Forbidden:

```text
claiming a response has arrived;
claiming external artifacts have been acquired;
claiming ACM supplement has been inspected;
claiming exact-equivalence has been accepted;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5330 did not use POD.

POD is triggered only by a future valid positive response classification.
