# Codex + Claude Consensus: Phoenix V3 M21 All-App POD Protocol

Status: `authorize_m21_one_all_app_pod_run_not_release`

This records the two-AI consensus after the M21 protocol packet and Claude external review.

## Inputs

```text
Protocol JSON: docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json
Protocol MD: docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
Call for review: docs/reviews/call_for_review_phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
Codex self-review: docs/reviews/codex_phoenix_v3_m21_all_app_pod_protocol_self_review_2026-06-23.md
Claude review: docs/reviews/claude_phoenix_v3_m21_all_app_pod_protocol_review_2026-06-23.md
```

## Claude Verdict

```text
authorize_m21_one_all_app_pod_run
one_all_app_pod_run_authorized: true
max_run_count: 1
expected_resource_window_hours: 5.5-7.0
hard_cap_hours_before_new_review: 8.0
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```

Claude found two non-blocking enforcement gaps:

```text
1. CuPy/Numba import is required by protocol but logged under || true in the runner.
2. GPU/driver identity is logged but not programmatically fail-closed in the runner.
```

Codex accepts the authorization and strengthened both gates before launching the run. This is stricter than the authorized packet and does not expand run scope.

## Codex Position

Codex concurs with the one-run authorization after hardening the two minor gaps:

```text
one_all_app_pod_run_authorized_after_hardening: true
max_run_count: 1
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The run is an evidence run. Even if all fail-closed bars clear, the post-run wording remains:

```text
blocking bars cleared; scorecard baseline advances; release remains not authorized; public V3-over-V2 speedup claims remain unauthorized
```

## Required Before Launch

```text
runner GPU/driver/compute-cap check exits 67 before benchmarks on mismatch
runner CuPy/Numba import check exits 68 before benchmarks on failure
local targeted tests pass
protocol JSON parses
release wording gate passes
remote bash -n passes
no-benchmark POD preflight passes
```

## Goal-Level Decision Audit

1. Was I foolish?

No for this decision.

2. If yes, what actions made the decision foolish?

It would be foolish to treat Claude's "minor non-blocking" notes as reasons to ignore easy hardening before a 5.5-7 hour run.

3. Was there another path?

Yes: run immediately under the authorized packet. That is allowed, but weaker than necessary.

4. Can I now try a different path?

Yes. Apply the two fail-closed hardenings, verify locally and remotely, then spend the single authorized POD run.
