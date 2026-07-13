# Goal5433 - X-HD Water/BG External Response Classifier

## Verdict

```text
water_bg_external_response_classifier_ready__await_response
```

Goal5433 creates a fail-closed WaterBodies->BlockGroups external-response
classifier on top of the Goal5329 generic intake protocol.

It does not receive any real response, acquire artifacts, accept
exact-equivalence, run POD, run author code, run RTDL code, or optimize routes.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
```

## Script

```text
Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
```

The script can be used in two ways:

```text
# Write the classifier contract artifact.
py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py

# Classify a normalized response saved with the Goal5329 template.
py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py --input <response.json> --output <classified.json>
```

## Required Water/BG Inputs

The classifier is specific to the current strongest exact-equivalence candidate:

```text
USADetailedWaterBodies.wkt
USACensusBlockGroupBoundaries.wkt
```

Current public reconstruction hashes used for comparison:

```text
USADetailedWaterBodies.wkt =
0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39

USACensusBlockGroupBoundaries.wkt =
8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

## Supported Response Types

```text
author_hash_manifest
author_input_archive
byte_identical_regeneration_script
acm_supplement_artifact_instructions
exact_equivalence_verdict
explicit_non_availability_statement
other
```

## Classification Rules

Author hash manifest:

```text
Both required WKT paths must be present.
Hash algorithm must be sha256.
If both author hashes match current public WKT hashes:
  classification = author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim
  sufficient_to_run_pod_gate = true
  sufficient_to_claim_exact_input = false
If hashes do not match:
  classification = author_hashes_do_not_match_current_public_reconstruction__need_author_bytes_or_regeneration
```

Author input archive:

```text
Archive sha256 must be present.
Archive listing must contain both required WKT paths.
Positive classification only authorizes extract/hash/same-input gate, not exact claim.
```

Byte-identical regeneration script:

```text
Expected output hashes must include both required WKT paths.
Positive classification authorizes regeneration/hash gate, not exact claim.
```

ACM supplement artifact instructions:

```text
If listing contains required WKT, hash-like material, or regeneration-like
material, classify as possible provenance and map before route/POD work.
If not, record supplement inspected with no relevant provenance and keep Level-B.
```

Exact-equivalence verdict:

```text
Must explicitly use outcome:
exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim

Must be scoped to WaterBodies/BlockGroups.
Must provide an accepted claim name.

Even then:
  sufficient_to_run_pod_gate = true
  sufficient_to_claim_exact_input = false
```

Non-availability:

```text
classification = external_non_availability_statement__keep_level_b_and_record_blocker
```

Unknown/other:

```text
classification = unsupported_or_other_response__manual_review_keep_level_b
```

## Why This Matters

This prevents the next external response from being used as an informal
permission slip.  In particular:

```text
hash match does not directly mean exact reproduction;
exact-equivalence acceptance does not directly mean exact paper input;
ACM supplement listing does not directly mean usable datasets;
non-availability keeps the blocker visible;
missing one required WKT path fail-closes.
```

## Claim Boundary

Authorized:

```text
classifier_contract_claimed = true
```

Not authorized:

```text
external_response_received = false
external_artifacts_acquired = false
exact_equivalence_accepted = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_paper_reproduction_claimed = false
performance_ratio_claimed = false
pod_execution_claimed = false
new_rtdl_route_code_added = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

This goal mentions hashes and byte identity only as response validation
criteria. It is not app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external response classifier / provenance intake decision gate
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: intake governance, not app-artifact parity implementation.
```

## Validation

Commands:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md history/internal_docs/call_for_review_goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md
py -m unittest tests.goal5433_water_bg_external_response_classifier_test tests.goal5432_public_artifact_live_refresh_test tests.goal5431_water_bg_outbox_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

The known Windows Python prefix warning may appear and is not a failure if the
commands exit successfully.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
tests/goal5433_water_bg_external_response_classifier_test.py
history/internal_docs/goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md
history/internal_docs/call_for_review_goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md
```

## Next Recommended Action

```text
await_external_response_then_classify_before_action
```

No POD work is expected until a real response is classified into a positive
class that requires a same-input gate or accepted bounded matrix.
