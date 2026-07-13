# Goal5331 - X-HD External Response Validation Matrix

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5331 adds synthetic external-response examples and an expectation matrix
for the Goal5330 validator.

The goal is to lock response-routing behavior before any real author, ACM, or
external-review response arrives. It does not acquire artifacts, send requests,
or run a POD gate.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/requests/examples/README.md
Paper-reproduction-apps/x-hd-paper/requests/examples/hash_manifest_hashes_only.json
Paper-reproduction-apps/x-hd-paper/requests/examples/author_input_archive_private.json
Paper-reproduction-apps/x-hd-paper/requests/examples/byte_identical_regeneration_script.json
Paper-reproduction-apps/x-hd-paper/requests/examples/acm_listing_no_artifact.json
Paper-reproduction-apps/x-hd-paper/requests/examples/water_bg_exact_equivalence_accepted.json
Paper-reproduction-apps/x-hd-paper/requests/examples/explicit_non_availability_statement.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5331_external_response_validation_matrix.json
tests/goal5331_xhd_external_response_validation_matrix_test.py
```

## Matrix Contract

Result schema:

```text
rtdl.paper_reproduction.xhd.goal5331.external_response_validation_matrix.v1
```

The matrix records six synthetic examples:

```text
hash_manifest_hashes_only
author_input_archive_private
byte_identical_regeneration_script
acm_listing_no_artifact
water_bg_exact_equivalence_accepted
explicit_non_availability_statement
```

For each example it records:

```text
expected_valid;
expected_pod;
expected_next_action.
```

The regression test imports the Goal5330 validator and verifies that each
example is classified exactly as the matrix says.

## Important Boundaries

The examples are deliberately synthetic:

```text
examples_are_real_external_responses = false
```

They do not prove:

```text
an external response was received;
external artifacts were acquired;
ACM supplement was actually inspected;
exact-equivalence was accepted in reality;
exact paper dataset reproduction;
Figure 5 reproduction;
full X-HD paper reproduction;
author-vs-RTDL performance ratio.
```

Even examples that produce `pod_expected=true` only prove that a future real
response of that shape should trigger a POD gate. They do not themselves trigger
POD work.

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5331_external_response_validation_matrix.json
py -m unittest tests.goal5331_xhd_external_response_validation_matrix_test
py -m unittest tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test
py -m unittest tests.goal5326_xhd_external_artifact_request_package_test tests.goal5327_xhd_acm_supplement_public_metadata_followup_test tests.goal5328_xhd_external_request_outbox_test tests.goal5329_xhd_external_response_intake_protocol_test tests.goal5330_xhd_external_response_intake_validator_test tests.goal5331_xhd_external_response_validation_matrix_test
```

Observed:

```text
json.tool OK
Ran 4 tests OK
Ran 12 tests OK
Ran 39 tests OK
```

The Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and is treated as benign because tests passed.

## Claim Boundary

Allowed:

```text
Goal5331 adds synthetic response examples and a validator expectation matrix.
It proves the response validator's routing behavior for representative
response shapes.
```

Forbidden:

```text
claiming any example is a real external response;
claiming external artifacts have been acquired;
claiming ACM supplement has been inspected in reality;
claiming exact-equivalence has been accepted in reality;
claiming exact paper dataset reproduction;
claiming Figure 5 reproduction;
claiming full X-HD paper reproduction;
claiming author-vs-RTDL performance ratio.
```

## POD Use

Goal5331 did not use POD.

POD remains deferred until a future valid positive real response is ingested and
classified by the validator.

## Exit Label

```text
external_response_validation_matrix_ready__await_real_response
```
