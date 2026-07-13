# Call For Review - Goal5431 X-HD Water/BG Outbox Refresh

Please strictly review Goal5431.

This goal refreshes WaterBodies->BlockGroups request drafts from Goal5430.  It
does **not** send requests, receive responses, acquire artifacts, accept
exact-equivalence, run POD, run author code, run RTDL code, or optimize routes.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5431_water_bg_outbox_refresh.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
tests/goal5431_water_bg_outbox_refresh_test.py
history/internal_docs/goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
```

Source context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5430_water_bg_exact_equivalence_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5328_external_request_outbox.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5329_external_response_intake_protocol.json
```

## Summary To Attack

Goal5431 writes two drafts:

```text
Paper-reproduction-apps/x-hd-paper/requests/author_water_bg_input_hash_request.md
Paper-reproduction-apps/x-hd-paper/requests/water_bg_exact_equivalence_review_request.md
```

Both must remain:

```text
Status: prepared_not_sent
```

Author request includes:

```text
USADetailedWaterBodies.wkt bytes or sha256
USACensusBlockGroupBoundaries.wkt bytes or sha256
source snapshots/export parameters/conversion scripts if files cannot be shared
paper-log config confirming num_points_cell=8
```

Exact-equivalence review draft asks whether Water/BG can be accepted as
exact-equivalent under a renamed bounded public-reconstruction claim, with
default:

```text
bounded_public_reconstruction_only_keep_level_b
```

## Claim Boundary To Attack

Authorized:

```text
outbox_refreshed
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
new_pod_execution_claimed
new_rtdl_route_code_added
explicit_lb_reopened
route_micro_optimization_goal_authorized
```

## Stop-Loss Gate G-1

This goal mentions hashes / byte identity only as request content.  It must not
be app-artifact parity implementation.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: send-ready author artifact request and exact-equivalence review request drafts
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

## Validation Commands Already Run

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5431_water_bg_outbox_refresh.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5431_water_bg_outbox_refresh.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5431_water_bg_outbox_refresh.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5431_xhd_water_bg_outbox_refresh_2026-07-10.md
py -m unittest tests.goal5431_water_bg_outbox_refresh_test tests.goal5430_water_bg_exact_equivalence_packet_test tests.goal5429_exact_input_or_equivalence_decision_refresh_test tests.goal5329_xhd_external_response_intake_protocol_test
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning is known noise if the command exits successfully.

## Requested Verdict Labels

Approve:

```text
approve_goal5431_xhd_water_bg_outbox_refresh
```

Revise:

```text
revise_goal5431_xhd_water_bg_outbox_refresh
```

Block:

```text
block_goal5431_xhd_water_bg_outbox_refresh
```

## Review Questions

1. Are both drafts genuinely send-ready and updated with Goal5430 evidence?
2. Do both drafts remain clearly marked `prepared_not_sent`?
3. Does the author request ask for the right WKT files/hashes and regeneration
   details?
4. Does the exact-equivalence draft correctly default to Level-B unless
   external acceptance is explicit?
5. Does the exact-equivalence draft explicitly reject point counts, MBRs, and
   HDResult alone as exact-input proof?
6. Does the goal avoid claiming requests were sent, responses arrived, artifacts
   were acquired, or exact-equivalence was accepted?
7. Does the goal avoid Figure 5, full paper, performance-ratio, route, and
   explicit `-lb` claims?
8. Does the Stop-Loss G-1 answer pass, or is this secretly app-artifact parity
   implementation?
9. Is it correct that no POD work is expected from this goal?
10. Is the next action correct: owner/external reviewer can send or review the
    prepared drafts, and POD waits for a positive response?

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
