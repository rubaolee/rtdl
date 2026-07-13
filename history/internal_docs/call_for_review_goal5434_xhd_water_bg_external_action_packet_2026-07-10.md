# Call For Review - Goal5434 X-HD Water/BG External Action Packet

Please strictly review Goal5434.

This goal creates a single WaterBodies->BlockGroups external action packet. It
combines Goal5430 evidence, Goal5431 prepared request drafts, Goal5432 public
artifact refresh status, and the Goal5433 response classifier into one
owner-facing workflow.

It does **not** send a request, receive a response, acquire artifacts, accept
exact-equivalence, run POD, run author code, run RTDL code, or optimize routes.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5434_external_action_packet.py
Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
tests/goal5434_water_bg_external_action_packet_test.py
history/internal_docs/goal5434_xhd_water_bg_external_action_packet_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5432_public_artifact_live_refresh.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
```

## Summary To Attack

Goal5434 writes:

```text
Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
```

The packet is explicitly `prepared_not_sent` and packages:

```text
current Level-B Water/BG public-reconstruction evidence
current public WKT hashes
Goal5432 public artifact refresh status
the two prepared request drafts
the Goal5433 response classifier command
positive classifier outcomes and fail-closed cases
claim boundary and stop-loss fields
```

The packet says the current evidence is strong Level-B public-reconstruction
evidence, not exact paper input reproduction.

## Claim Boundary To Attack

Authorized:

```text
external_action_packet_prepared
```

Forbidden:

```text
request_sent_claimed
external_response_received
external_artifacts_acquired
exact_equivalence_accepted
exact_paper_dataset_reproduction_claimed
figure5_reproduction_claimed
full_xhd_paper_reproduction_claimed
performance_ratio_claimed
pod_execution_claimed
new_rtdl_route_code_added
explicit_lb_reopened
route_micro_optimization_goal_authorized
```

## Stop-Loss Gate G-1

This goal mentions hashes and exact-equivalence only as external-action /
response-governance terms. It must not be app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external action packet / response classification workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5434_external_action_packet.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5434_external_action_packet.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5434_xhd_water_bg_external_action_packet_2026-07-10.md history/internal_docs/call_for_review_goal5434_xhd_water_bg_external_action_packet_2026-07-10.md
py -m unittest tests.goal5434_water_bg_external_action_packet_test tests.goal5433_water_bg_external_response_classifier_test tests.goal5432_public_artifact_live_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5434_xhd_water_bg_external_action_packet
```

Revise:

```text
revise_goal5434_xhd_water_bg_external_action_packet
```

Block:

```text
block_goal5434_xhd_water_bg_external_action_packet
```

## Review Questions

1. Does the action packet correctly package the current Water/BG evidence
   without upgrading Level-B to exact paper input reproduction?
2. Does it clearly distinguish `prepared_not_sent` from sent requests or
   received responses?
3. Does it point to both prepared drafts and the Goal5433 classifier workflow?
4. Does it correctly carry forward Goal5432's public artifact refresh result
   without claiming ACM supplement inspection or exact-input discovery?
5. Do positive classifier outcomes authorize only the next gate, not direct
   exact/full reproduction wording?
6. Do fail-closed cases keep Level-B when required WKT paths, hashes, scope, or
   accepted claim names are missing?
7. Does the JSON claim boundary keep request/response/artifact/exact/Figure 5/
   full-paper/performance/POD/route claims false?
8. Does the script avoid POD, author execution, RTDL route execution, and route
   optimization code?
9. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   implementation?
10. Are the tests strong enough to prevent the known failure mode: treating an
    owner-facing action packet as if it were already an external response or
    exact-equivalence acceptance?

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
