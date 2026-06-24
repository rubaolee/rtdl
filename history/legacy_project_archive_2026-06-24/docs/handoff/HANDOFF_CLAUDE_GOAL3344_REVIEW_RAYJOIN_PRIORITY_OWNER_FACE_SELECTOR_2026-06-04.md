# Handoff: Claude Review Goal3344 RayJoin Priority Owner-Face Selector

This supersedes all earlier Goal333x/3341 RayJoin owner-face review handoffs.

Please review the current chain through Goal3343 and write:

- `docs/reviews/goal3344_claude_review_rayjoin_priority_owner_face_selector_2026-06-04.md`

## Scope

Review Goals 3320, 3321, 3322, 3324, 3326, 3327, 3328, 3329, 3330, 3332, 3333, 3335, 3337, 3339, 3340, 3342, and 3343.

Latest state:

- Goal3337 exposes incident face candidate rows without choosing ownership.
- Goal3339 selects only unique maximum incident faces and fails closed on ties.
- Goal3342 adds an explicit-priority selector: higher incident count wins, tied counts require caller-supplied lower priority; missing/tied priorities fail closed.
- Goal3343 wires primitive discovery to the priority selector while keeping the primitive candidate/unpromoted.
- Local full chain gate: `Ran 54 tests in 0.061s OK`.
- Pod focused gate after fast-forward: `Ran 14 tests in 0.002s OK`.

## Review Questions

1. Is the owner-face selector chain app-agnostic?
2. Does Goal3342 correctly encode caller/data priority as explicit policy rather than engine inference?
3. Does this avoid overclaiming RayJoin correctness/performance while still making useful progress toward a future native/device primitive?
4. Is the primitive catalog wording honest and discoverable?
5. Should the next engineering target be device priority selector, deterministic priority derivation, or richer topology event streams?

## Boundaries

- No release, public speedup, broad RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- Current fast PIP count remains validated-domain-only.
- Native engine must remain app-agnostic and must not infer CDB/RayJoin ownership semantics.
- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
