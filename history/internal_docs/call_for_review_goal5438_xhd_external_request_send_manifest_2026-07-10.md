# Call For Review - Goal5438 X-HD External Request Send Manifest

Please strictly review Goal5438.

This goal builds an auditable outbound send manifest for the current X-HD
external request material.  It records prepared request files, intended
audiences, file hashes, and a receipt template to use if the owner sends a
request.

It does **not** send requests, receive responses, acquire artifacts, accept
exact-equivalence, run POD, run author code, run RTDL code, or upgrade claims.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5438_external_request_send_manifest.py
Paper-reproduction-apps/x-hd-paper/requests/external_request_send_manifest.md
Paper-reproduction-apps/x-hd-paper/requests/external_request_send_receipt_template.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5438_external_request_send_manifest.json
tests/goal5438_external_request_send_manifest_test.py
history/internal_docs/goal5438_xhd_external_request_send_manifest_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/requests/author_input_provenance_request.md
Paper-reproduction-apps/x-hd-paper/requests/acm_supplement_inspection_request.md
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
```

## Summary To Attack

Current output:

```text
status = external_request_send_manifest_ready__prepared_not_sent
ready_external_request_count = 4
request_sent_claimed = false
```

Manifested items:

```text
general_author_input_provenance_request
general_acm_supplement_inspection_request
water_bg_author_hash_request
water_bg_exact_equivalence_review_request
water_bg_external_action_packet
```

Every item has:

```text
status = prepared_not_sent
ready_to_send_or_review = true
sent_claimed = false
sha256 = recorded
```

## Claim Boundary To Attack

Authorized:

```text
request_send_manifest_claimed
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

This goal mentions hashes only to make request drafts auditable. It must not be
app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external request send manifest / receipt workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5438_external_request_send_manifest.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5438_external_request_send_manifest.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5438_external_request_send_manifest.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5438_xhd_external_request_send_manifest_2026-07-10.md history/internal_docs/call_for_review_goal5438_xhd_external_request_send_manifest_2026-07-10.md
py -m unittest tests.goal5438_external_request_send_manifest_test tests.goal5437_external_response_next_gate_plan_test tests.goal5435_external_response_inbox_gate_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5438_xhd_external_request_send_manifest
```

Revise:

```text
revise_goal5438_xhd_external_request_send_manifest
```

Block:

```text
block_goal5438_xhd_external_request_send_manifest
```

## Review Questions

1. Does the manifest include the relevant prepared request/action files?
2. Does it record sha256 hashes for every listed file?
3. Does it keep all listed files at `prepared_not_sent` and avoid claiming
   anything was sent?
4. Does it distinguish sendable external requests from the internal action
   packet?
5. Does the receipt template clearly remain a template, not a receipt?
6. Does the receipt template preserve privacy and require normalized response
   intake?
7. Does the JSON claim boundary keep response/artifact/equivalence/exact/Figure
   5/full-paper/performance/POD/route claims false?
8. Does the script avoid network, POD, author execution, RTDL route execution,
   and route optimization code?
9. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   implementation?
10. Are the tests strong enough to prevent the known failure mode: treating
    prepared drafts as sent requests or external evidence?

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
