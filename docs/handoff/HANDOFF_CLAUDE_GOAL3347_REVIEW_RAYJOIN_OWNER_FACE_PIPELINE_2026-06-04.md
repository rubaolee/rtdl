# Handoff: Claude Review Goal3347 RayJoin Owner-Face Pipeline

This supersedes earlier Goal333x/334x RayJoin owner-face review handoffs. Please review through Goal3346.

Expected review output:

- `docs/reviews/goal3347_claude_review_rayjoin_owner_face_pipeline_2026-06-04.md`

## Scope

Review Goals 3320, 3321, 3322, 3324, 3326, 3327, 3328, 3329, 3330, 3332, 3333, 3335, 3337, 3339, 3340, 3342, 3343, 3345, and 3346.

Current state:

- Fast PIP count remains validated-domain-only.
- Extra county shape ids are diagnosed and topology-adjacent.
- Generic incident face candidates are exposed.
- Unique-max owner-face selection fails closed on ties.
- Explicit priority rows can break ties, but priorities are caller/data policy.
- The priority-selected owner-face mapping feeds the generic membership filter and recovers the known exact rows for seven mismatching points.
- Primitive catalog points to the pipeline report while keeping the node `candidate_behavior`.

Validation:

- Local full chain: `Ran 59 tests in 0.063s OK`.
- Pod focused chain after fast-forward: `Ran 17 tests in 0.002s OK`.

## Review Questions

1. Is the whole chain app-agnostic?
2. Does the priority pipeline make progress without pretending RTDL has automatic RayJoin/CDB ownership derivation?
3. Are the current tests adequate for a Python reference pipeline?
4. Does catalog wiring avoid premature primitive promotion?
5. What should the next engineering step be before native/device lowering?

## Required Boundaries

- No release, public speedup, broad RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- Native engine must not infer CDB/RayJoin ownership semantics.
- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
