# Codex Consensus: Phoenix V3 RTDBSCAN M3.1 Pod A/B Negative Classification

Date: 2026-06-22
Status: `2ai_consensus_approve_blocked_not_release`

External review:

```text
review: docs/reviews/claude_phoenix_v3_rtdbscan_m3_1_pod_ab_negative_classification_review_2026-06-22.md
verdict: approve_blocked_not_release
```

Codex accepts the Claude verdict.

## Consensus Result

```text
m3_1_classification_correct: true
evidence_valid: true
route_uses_productized_runner: true
signature_contract_preserved: true
material_set_a_candidate: false
second_set_a_material_probe_obtained: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
next_action: bounded_generic_runner_overhead_and_fingerprint_correctness_fix
```

## Accepted Findings

1. The RTDBSCAN M3.1 result cannot count as the second material Set-A
   runner-backed probe. The decision-relevant comparison is runner-backed OptiX
   versus the incumbent legacy OptiX grouped-stream route, where the runner is
   `0.5038x` geomean.
2. The `1.4917x` runner-vs-Embree ratio is diagnostic only. It confirms the RT
   backend still works, but it is not Set-A success evidence.
3. The timing data supports the overhead diagnosis: native grouped work is
   close to the legacy path, while Python-side runner overhead dominates the
   loss.
4. The next responsible step is a bounded generic runner fix, not an
   RTDBSCAN-specific native shortcut.
5. Claude identified a correctness risk in `_stable_input_fingerprint`: large
   sequences currently use a truncated `repr(tuple(value))[:2048]`, which is
   both O(N) in the hot path and collision-prone for cache keys. The overhead
   fix must address correctness, not merely speed.

## Required Boundary

No V3 release, public speedup wording, broad V3-over-V2 wording,
true-zero-copy wording, automatic backend/partner selection, or all-app rerun
is authorized by this M3.1 packet.

## Goal-Level Decision Audit

Decision: accept Claude's M3.1 negative-classification review and set the next
engineering step to a bounded generic runner overhead and fingerprint
correctness fix.

1. Was I foolish?
   No for this decision.
2. What actions would have made this foolish?
   It would be foolish to ignore the `0.5038x` incumbent comparison or to treat
   a collision-prone cache key as acceptable because the current sample did not
   collide.
3. Was there another path?
   Yes. I could switch immediately to another Set-A route, but the same
   large-input fingerprint pattern can affect other runner-backed routes.
4. Can I now try a different path that truly solves the problem?
   Yes. Fix the generic runner key/fingerprint overhead and correctness issue,
   then rerun the focused A/B before any broader claim.
