# Call For Review: Phoenix V3 M38 Component-Union Focused POD Protocol

Date: 2026-06-23

Status: `request_m38_component_union_focused_pod_protocol_review_no_run`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
performance_claim_authorized: false
```

## Review Request

Please critically review M38 as a protocol packet only. It must not authorize a
POD run unless your verdict explicitly says so.

M38 claims only:

1. The focused component-union probe row is serious enough to be meaningful:
   clustered 3D fixed-radius component-union labels at `262144` points,
   warmup `1`, repeat `5`.
2. The productized route must use
   `run_radius_graph_component_union_3d_prepared_session`.
3. Component-signature output cannot substitute for component-union labels.
4. Success/failure bars are predeclared and fail closed.
5. Resource cost is bounded before any POD spend.

M38 does not claim material speedup, release readiness, all-app authorization,
true zero-copy, V4 embedding, automatic partner selection, or broad V3-over-V2
performance.

## Files To Review

- `docs/rebuild/v3/phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.json`
- `docs/rebuild/v3/phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.md`
- `docs/reports/phoenix_v3_m38_component_union_focused_pod_protocol_2026-06-23.md`
- `tests/v3_phoenix_m38_component_union_focused_pod_protocol_test.py`

Important: any command listed in the protocol is a proposed M39 harness command
only. M38 does not claim that `scripts/v3_phoenix_component_union_m38_pod_ab.py`
exists yet, and does not authorize executing it.

## Specific Questions

1. Is the row serious enough, or should the scale/shape change before a POD run
   is even considered?
2. Are the variants truly same-contract for component-union labels?
3. Does the protocol adequately block component-signature shortcuts?
4. Are the success bars correct for a Set-A material candidate?
5. Is the resource estimate reasonable and bounded?
6. Should the next authorized step be M39 local harness only, or one focused
   POD after a harness gate?
7. Are any non-authorization boundaries accidentally weakened?

## Acceptable Verdict Labels

Use exactly one:

- `accept_m38_authorize_m39_runner_harness_no_pod`
- `accept_m38_authorize_one_focused_component_union_pod_after_harness_gate`
- `revise_m38_protocol`
- `reject_m38_protocol`

If you choose revision/reject, list exact required changes.

## Explicit Non-Authorization Block

No matter the verdict, this review must not authorize V3 release, all-app POD
spend, public speedup wording, broad V3-over-V2.x wording, true-zero-copy
wording, automatic partner selection, V4 work, C ABI work, or embedding work.

## Goal-Level Decision Audit

Decision: ask for external review of a focused protocol before spending POD.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to treat M37 structural acceptance as permission to run
   paid POD without a reviewed protocol.

3. Was there another path?

   Yes. Run immediately while the pod is up. That repeats the earlier
   measurement-first problem.

4. Can I now try a different path that actually solves the problem?

   Yes. Freeze the protocol, get review, then either build M39 harness or run
   one focused POD only if explicitly authorized.
