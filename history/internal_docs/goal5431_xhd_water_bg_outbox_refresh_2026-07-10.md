# Goal5431 - X-HD Water/BG Outbox Refresh

## Verdict

```text
water_bg_outbox_refreshed_from_goal5430__prepared_not_sent
```

Goal5431 refreshes the send-ready WaterBodies->BlockGroups request drafts with
the Goal5430 evidence packet.

It does not send any request, receive any response, acquire any artifact, accept
exact-equivalence, run POD, execute author code, execute RTDL code, or optimize
any route.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
```

## Drafts

Goal5431 writes two request drafts:

```text
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
```

Both are marked:

```text
Status: prepared_not_sent
```

## Author Hash Request Draft

Draft target:

```text
X-HD authors / artifact owner
```

Subject:

```text
X-HD reproduction: WaterBodies/BG paper input hashes or regeneration provenance
```

The draft requests:

```text
USADetailedWaterBodies.wkt bytes or sha256 from the paper-run HDDatasets tree.
USACensusBlockGroupBoundaries.wkt bytes or sha256 from the paper-run HDDatasets tree.
Exact source URLs, snapshot dates, export parameters, and conversion scripts if files cannot be shared.
Paper-log command/config confirming num_points_cell=8.
Preprocessing / simplification / precision / coordinate / ring-vertex extraction policy.
```

It includes the current evidence:

```text
author paper-config HDResult = 0.8964367508888245
RTDL exact-witness HDResult = 0.8964380566690101
abs diff = 1.305780185645311e-06 <= 2e-6
WaterBodies public WKT sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
BlockGroups public WKT sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
WaterBodies point-count delta = 6129
BlockGroups point-count delta = 127
```

## Exact-Equivalence Review Draft

Draft target:

```text
owner or external reviewer
```

Review question:

```text
Can the current deterministic public ArcGIS reconstruction be accepted as
exact-equivalent for a renamed bounded public-reconstruction claim, or must it
remain Level-B same-source evidence?
```

Allowed answers:

```text
exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim
bounded_public_reconstruction_only_keep_level_b
not_accepted_keep_level_b
```

Default without explicit acceptance:

```text
bounded_public_reconstruction_only_keep_level_b
```

The draft explicitly says:

```text
Point counts, MBRs, and HDResult alone are not treated as proof of exact paper input identity.
```

## Claim Boundary

Authorized:

```text
outbox_refreshed = true
```

Not authorized:

```text
request_sent_claimed = false
external_artifacts_acquired = false
exact_equivalence_accepted = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
new_pod_execution_claimed = false
new_rtdl_route_code_added = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

This is a request/outbox goal, not app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: send-ready author artifact request and exact-equivalence review request drafts
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: no app-artifact parity implementation; this only prepares external decision messages.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5431_water_bg_outbox_refresh.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5431_water_bg_outbox_refresh.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
py -m unittest tests.goal5431_water_bg_outbox_refresh_test tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

The known Windows Python prefix warning may appear and is not a failure if
tests pass.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5431_water_bg_outbox_refresh.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
tests/goal5431_water_bg_outbox_refresh_test.py
history/internal_docs/goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
history/internal_docs/call_for_review_goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
```

## Next Recommended Action

```text
owner_or_external_reviewer_can_send_or_review_the_prepared_drafts
```

No POD work is expected until a positive response supplies author files/hashes,
byte-identical regeneration instructions, or exact-equivalence acceptance.
