# Call For Review: V4 Goal4644 Post-Release Guardrails

Date: 2026-06-25

Requested reviewer: Antigravity or Claude.

Requested verdict labels:

- `accept_goal4644_post_release_guardrails`
- `accept_with_required_amendments`
- `reject_goal4644_scope_reopened`
- `reject_goal4644_incomplete`

## Review Target

Please critically review Goal4644 as the post-publication guardrail for the
already published V4.0.0 formal high-performance generic RT-core operator
release.

Primary files:

- `src/rtdsl/v4_goal4644_post_release_guardrails.py`
- `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`
- `tests/v4_goal4644_post_release_guardrails_test.py`

Related release files:

- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `future/v4/v4_goal4643_publication_decision_2026-06-25.md`
- `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`
- `README.md`
- `docs/current_v4_status.md`
- `docs/learn/performance_wording.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

## Facts To Check

- Goal4642 authorized the bounded V4.0.0 release label.
- Goal4643 published the release state.
- Goal4644 must not expand scope beyond Goal4642/4643.
- V4.0.0 remains limited to documented measured generic RT-core operator
  surfaces.
- Candidate surfaces remain zero in the release count.
- Deferred/excluded families such as Barnes-Hut and Spatial RayJoin must remain
  out of V4.0 coverage/speedup claims.
- Forbidden claims must remain machine-visible and false:
  - broad V4 speedup;
  - whole-application speedup;
  - all-benchmark speedup;
  - public true-zero-copy;
  - Tier-3 callback support;
  - raw OptiX callback support;
  - CuPy performance;
  - C ABI / embedding / non-Python host;
  - app-specific native kernels.

## Verification Already Run By Codex

```text
py -3 -m unittest tests.v4_goal4644_post_release_guardrails_test \
  tests.v4_goal4643_publication_decision_test \
  tests.v4_frontdoor_test tests.v4_scope_gate_test \
  tests.v4_catalog_regression_gate_test
```

Result: `20 tests OK`.

```text
$mods = Get-ChildItem tests -Filter 'v4*_test.py' | ForEach-Object { 'tests.' + $_.BaseName }
py -3 -m unittest $mods
```

Result: `179 tests OK`.

```text
py -3 scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16
```

Result: `status: passed`, `release_authorized: true`, `measured_surface_count:
8`, `candidate_surface_count: 0`.

```text
py -3 examples/v4/v4_frontdoor_quickstart.py
```

Result: `status: ok`, `formal_release_authorized: true`, measured surfaces `8`,
candidate surfaces `0`, forbidden claim flags false.

## Questions

1. Does Goal4644 correctly preserve the already-authorized V4.0.0 release
   without reopening scope?
2. Does it keep deferred/excluded families out of release claims?
3. Are the forbidden-claim locks sufficient and machine-checkable?
4. Does the review cadence/debt language satisfy the owner's rule without
   weakening the release label?
5. Are amendments required before Goal4644 can be considered complete?

## Non-Authorization

This review request does not authorize new scope, broad speedup wording,
whole-application speedup wording, all-benchmark speedup wording, public
true-zero-copy wording, Tier-3 callback support, raw OptiX callback support,
CuPy performance claims, C ABI, embedding, non-Python host bindings, or
app-specific native kernels.
