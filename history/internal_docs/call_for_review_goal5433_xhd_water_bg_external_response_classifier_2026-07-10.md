# Call For Review - Goal5433 X-HD Water/BG External Response Classifier

Please strictly review Goal5433.

This goal adds a fail-closed classifier for future WaterBodies->BlockGroups
external responses. It is layered on top of the Goal5329 generic intake
protocol and the Goal5430/5431 request material.

It does **not** receive a real response, acquire artifacts, accept
exact-equivalence, run POD, run author code, run RTDL code, or optimize routes.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
tests/goal5433_water_bg_external_response_classifier_test.py
history/internal_docs/goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5329_external_response_intake_protocol.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
```

## Summary To Attack

Goal5433 supports these response types:

```text
author_hash_manifest
author_input_archive
byte_identical_regeneration_script
acm_supplement_artifact_instructions
exact_equivalence_verdict
explicit_non_availability_statement
other
```

It is Water/BG-specific for the two currently requested paper paths:

```text
USADetailedWaterBodies.wkt
USACensusBlockGroupBoundaries.wkt
```

Important intended behavior:

```text
Both required WKT paths must be present for hash/archive/regeneration positives.
Matching author hashes authorize a same-input gate, not direct exact-paper claim.
Mismatching author hashes keep Level-B and request bytes/regeneration.
Exact-equivalence acceptance must be explicit, scoped to Water/BG, and named.
Accepted exact-equivalence authorizes a bounded accepted-claim matrix, not exact input wording.
Non-availability statements keep Level-B.
Unknown response types fail closed.
```

## Claim Boundary To Attack

Authorized:

```text
classifier_contract_claimed
```

Forbidden:

```text
external_response_received
external_artifacts_acquired
exact_equivalence_accepted
exact_paper_dataset_reproduction_claimed
figure5_reproduction_claimed
full_paper_reproduction_claimed
performance_ratio_claimed
pod_execution_claimed
new_rtdl_route_code_added
explicit_lb_reopened
route_micro_optimization_goal_authorized
```

## Stop-Loss Gate G-1

This goal mentions hashes / byte identity only as response validation criteria.
It must not be app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external response classifier / provenance intake decision gate
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md history/internal_docs/call_for_review_goal5433_xhd_water_bg_external_response_classifier_2026-07-10.md
py -m unittest tests.goal5433_water_bg_external_response_classifier_test tests.goal5432_public_artifact_live_refresh_test tests.goal5431_water_bg_outbox_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5433_xhd_water_bg_external_response_classifier
```

Revise:

```text
revise_goal5433_xhd_water_bg_external_response_classifier
```

Block:

```text
block_goal5433_xhd_water_bg_external_response_classifier
```

## Review Questions

1. Does the classifier correctly build on Goal5329 without replacing the
   generic intake protocol?
2. Does it require both WaterBodies and BlockGroups paths for positive
   hash/archive/regeneration classifications?
3. Does a matching author hash manifest authorize only a same-input gate and
   not direct exact-paper wording?
4. Does a mismatching hash manifest fail closed rather than treating current
   public WKT as exact?
5. Does an exact-equivalence verdict require explicit accepted outcome, Water/BG
   scope, and accepted claim name?
6. Does accepted exact-equivalence still avoid `sufficient_to_claim_exact_input`
   and exact-paper wording?
7. Do non-availability and unknown responses keep Level-B?
8. Does the script avoid POD, author execution, RTDL route execution, and
   route/performance work?
9. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   implementation?
10. Are the tests strong enough to prevent the known failure mode: using a
    response as an informal permission slip to overclaim exact/full paper
    reproduction?

## Expected Answer Shape

Please answer with:

```text
Verdict: <one requested label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```
