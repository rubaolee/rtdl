# Call For Review - Goal5435 X-HD External Response Inbox Gate

Please strictly review Goal5435.

This goal adds an executable inbox gate after the Goal5434 action packet. It
scans `Paper-reproduction-apps/x-hd-paper/requests/incoming` for normalized
external response JSON files and classifies each response with the Goal5433
classifier.

It does **not** send requests, receive private material by itself, contact POD,
run author code, run RTDL code, compare outputs, accept exact-equivalence, or
upgrade claims.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5435_external_response_inbox_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5435_external_response_inbox_gate.json
tests/goal5435_external_response_inbox_gate_test.py
history/internal_docs/goal5435_xhd_external_response_inbox_gate_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/requests/water_bg_external_action_packet.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5434_water_bg_external_action_packet.json
Paper-reproduction-apps/x-hd-paper/scripts/classify_xhd_goal5433_water_bg_external_response.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5433_water_bg_external_response_classifier_contract.json
Paper-reproduction-apps/x-hd-paper/requests/external_response_intake_template.json
```

## Summary To Attack

Current output:

```text
status = external_response_inbox_empty__await_response
response_count = 0
positive_classifier_outcome_count = 0
pod_usage.used = false
pod_usage.expected_next = false
```

The gate handles four states:

```text
external_response_inbox_empty__await_response
external_response_inbox_has_invalid_items__fix_before_gate
external_response_inbox_all_fail_closed__keep_level_b
external_response_inbox_has_positive_classifier_outcome__manual_review_before_gate
```

Even the positive state authorizes only strict review and a separate next gate.
It does not itself authorize exact/full reproduction wording or POD execution.

## Claim Boundary To Attack

Authorized:

```text
inbox_scanned
```

Current:

```text
external_response_received = false
```

Forbidden:

```text
request_sent_claimed
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

This goal mentions hashes / exact-equivalence only as classifier output. It
must not be app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: external response inbox gate / classifier-driven provenance workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5435_external_response_inbox_gate.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5435_external_response_inbox_gate.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5435_external_response_inbox_gate.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5435_xhd_external_response_inbox_gate_2026-07-10.md history/internal_docs/call_for_review_goal5435_xhd_external_response_inbox_gate_2026-07-10.md
py -m unittest tests.goal5435_external_response_inbox_gate_test tests.goal5434_water_bg_external_action_packet_test tests.goal5433_water_bg_external_response_classifier_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5435_xhd_external_response_inbox_gate
```

Revise:

```text
revise_goal5435_xhd_external_response_inbox_gate
```

Block:

```text
block_goal5435_xhd_external_response_inbox_gate
```

## Review Questions

1. Does the inbox gate correctly consume the Goal5434 action-packet state and
   Goal5433 classifier instead of inventing a new response protocol?
2. Does the current empty inbox status avoid claiming a response arrived?
3. Does the positive classifier path still require manual/strict review before
   any separate next gate?
4. Does the positive classifier path avoid claiming exact paper input or full
   paper reproduction directly?
5. Do invalid JSON files fail closed before any gate?
6. Do non-positive classifier outcomes keep Level-B?
7. Does the JSON claim boundary keep request/artifact/equivalence/exact/Figure
   5/full-paper/performance/POD/route claims false?
8. Does the script avoid POD, author execution, RTDL route execution, and route
   optimization code?
9. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   implementation?
10. Are the tests strong enough to prevent the known failure mode: treating a
    positive response classification as if it were already exact/full
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
