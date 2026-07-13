# Call For Review: Goal5331 X-HD External Response Validation Matrix

Please strictly review Goal5331.

## Files To Review

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
history/internal_docs/goal5331_xhd_external_response_validation_matrix_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5330_external_response_intake_validator.json
history/internal_docs/call_for_review_goal5330_xhd_external_response_intake_validator_2026-07-09.md
```

## Goal5331 Summary

Goal5331 adds a synthetic validation matrix for the Goal5330 external response
validator.

It verifies these representative response shapes:

```text
hash_manifest_hashes_only
author_input_archive_private
byte_identical_regeneration_script
acm_listing_no_artifact
water_bg_exact_equivalence_accepted
explicit_non_availability_statement
```

The test imports the validator and checks that each example produces the
expected:

```text
valid;
pod_expected;
next_action;
claim_boundary.
```

All examples are synthetic. They are not external responses and do not acquire
artifacts.

## Review Questions

1. Is it correct to add synthetic examples for the external-response intake
   validator?
2. Does the test really execute the Goal5330 validator rather than merely
   checking static JSON fields?
3. Do the six examples cover the main positive, negative, and review paths?
4. Are `pod_expected` values correct and fail-closed?
5. Does the matrix preserve `sufficient_to_claim_exact_input=false` and all
   exact/full/performance claim boundaries?
6. Is it correct that Goal5331 does not use POD?
7. Is the exit label acceptable?
8. Is the result ready to join the broader Goals5318-5331 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5331_external_response_validation_matrix_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5331

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
8. ...
```
