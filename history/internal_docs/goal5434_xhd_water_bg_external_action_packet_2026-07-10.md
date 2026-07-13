# Goal5434 - X-HD Water/BG External Action Packet

## Verdict

```text
water_bg_external_action_packet_ready__prepared_not_sent
```

Goal5434 creates a single owner-facing action packet for the X-HD
WaterBodies->BlockGroups external-action path.  It packages the current
evidence, the two prepared request drafts, the Goal5433 response classifier,
and the fail-closed rules for any future response.

It does not send a request, receive a response, acquire external artifacts,
accept exact-equivalence, run POD, run author code, run RTDL code, or reopen
route optimization.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
```

## Action Packet

```text
Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
```

The packet is explicitly marked:

```text
Status: prepared_not_sent
```

## Inputs

Goal5434 consumes the already prepared Water/BG evidence and governance chain:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5432_public_artifact_live_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
```

## Current Evidence Embedded

```text
case_id = geo_water_bg_full_public_paper_config
paper_pair = USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
author paper-config num_points_cell = 8
author paper-config HDResult = 0.8964367508888245
RTDL exact-witness HDResult = 0.8964380566690101
abs diff = 1.305780185645311e-06 <= 2e-06
per_source_witness_exact = true
```

This is strong Level-B public-reconstruction evidence. It remains not exact
paper input reproduction because there are no author WKT bytes/hashes, no
byte-identical regeneration proof, no inspectable ACM supplement contents, and
no accepted external exact-equivalence verdict.

Current public reconstruction hashes:

```text
USADetailedWaterBodies.wkt =
0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39

USACensusBlockGroupBoundaries.wkt =
8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

## External Action Workflow

The packet points to two prepared-not-sent drafts:

```text
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
```

If a response arrives, the packet instructs the owner to normalize it with:

```text
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
```

Then classify it with:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py --input <response.json> --output <classified.json>
```

The packet forbids improvising a stronger claim from raw response text.

## Positive Classifications

The packet lists the only positive classifier outcomes:

```text
author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim
author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate
byte_identical_regeneration_available__run_regeneration_then_hash_gate
acm_supplement_contains_possible_provenance__map_before_route
exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix
```

Even those outcomes authorize only the next gate. They do not directly
authorize exact paper reproduction wording.

## Fail-Closed Cases

Keep Level-B if:

```text
one of the required WKT paths is missing
hashes do not match current public reconstruction
response type is unknown or underspecified
exact-equivalence verdict is not Water/BG scoped
exact-equivalence verdict lacks an accepted claim name
response says artifacts are unavailable
```

## Claim Boundary

Authorized:

```text
external_action_packet_prepared = true
```

Not authorized:

```text
request_sent_claimed = false
external_response_received = false
external_artifacts_acquired = false
exact_equivalence_accepted = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
pod_execution_claimed = false
new_rtdl_route_code_added = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

Goal5434 mentions hashes and exact-equivalence only as external-action and
response-classification governance. It does not implement app-artifact parity
or reopen `-lb`/row/hash/offload-stream work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external action packet / response classification workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: packaging external action, not app-artifact parity implementation.
```

## Validation

Commands:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5434_external_action_packet.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5434_external_action_packet.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5434_xhd_water_bg_external_action_packet_2026-07-10.md history/internal_docs/call_for_review_goal5434_xhd_water_bg_external_action_packet_2026-07-10.md
py -m unittest tests.goal5434_water_bg_external_action_packet_test tests.goal5433_water_bg_external_response_classifier_test tests.goal5432_public_artifact_live_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

The known Windows Python prefix warning may appear and is not a failure if the
commands exit successfully.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5434_external_action_packet.py
Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
tests/goal5434_water_bg_external_action_packet_test.py
history/internal_docs/goal5434_xhd_water_bg_external_action_packet_2026-07-10.md
history/internal_docs/call_for_review_goal5434_xhd_water_bg_external_action_packet_2026-07-10.md
```

## Next Recommended Action

```text
send_or_review_action_packet_and_await_classified_external_response
```

POD is not expected until a positive classifier outcome supplies artifacts,
hashes, byte-identical regeneration instructions, ACM supplement provenance, or
accepted exact-equivalence that authorizes a separate gate.
