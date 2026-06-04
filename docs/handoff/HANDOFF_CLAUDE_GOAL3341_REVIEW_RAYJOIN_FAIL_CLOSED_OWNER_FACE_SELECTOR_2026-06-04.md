# Handoff: Claude Review Goal3341 RayJoin Fail-Closed Owner-Face Selector

This supersedes all earlier Goal3331/3334/3336/3338 RayJoin owner-face handoffs.

Please review the current chain through Goal3340 and write:

- `docs/reviews/goal3341_claude_review_rayjoin_fail_closed_owner_face_selector_2026-06-04.md`

## Scope

Review Goals 3320, 3321, 3322, 3324, 3326, 3327, 3328, 3329, 3330, 3332, 3333, 3335, 3337, 3339, and 3340.

Latest changes:

- Goal3337: `chains_to_incident_face_candidate_rows(...)` exposes generic incident face candidates without choosing ownership.
- Goal3339: `select_unique_owner_faces_from_incident_candidates(...)` selects only unique max incident faces and fails closed on ties by default.
- Goal3340: primitive catalog now points `candidate.closed_shape_topology_membership_count_2d` at Goal3339 and keeps the node unpromoted.
- Full local chain gate passed: `Ran 48 tests in 0.060s OK`.

## Review Questions

1. Is the owner-face chain app-agnostic, or does any helper smuggle RayJoin/CDB policy into RTDL?
2. Does the fail-closed selector correctly encode the current evidence: unique cases can proceed, tied RayJoin cases remain blocked?
3. Does the primitive catalog communicate this as candidate behavior rather than a promoted native primitive?
4. Are the tests enough for the current reference/helper stage?
5. What should be next: deterministic owner-face derivation, device owner-face filtering, or a richer topology event stream?

## Required Boundaries

- No release, public speedup, broad RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- Current fast PIP count remains validated-domain-only.
- Native engine must remain app-agnostic.
- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
