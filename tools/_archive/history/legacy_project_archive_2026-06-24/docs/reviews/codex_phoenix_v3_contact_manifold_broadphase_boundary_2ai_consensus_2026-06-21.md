# Codex Consensus - Phoenix V3 Contact Manifold Broadphase Boundary

Status: Claude + Codex consensus complete; no M7 promotion.

Date: 2026-06-21.

## Inputs

```text
docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md
docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.json
tutorials/current/15_contact_manifold_broadphase_boundary.md
docs/reviews/claude_phoenix_v3_contact_manifold_broadphase_boundary_review_2026-06-21.md
```

## Decision

Codex accepts Claude's verdict.

Contact Manifold broadphase remains a rebuild boundary lesson:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
full_contact_solver_claim_authorized: false
physics_solver_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

The row is useful because `matches_cpu_reference: true` and phase validation
accepts the v2.4 contract. It is not M7 because wall timing is slower, V2.14
paired rows are parity/regression, AABB-index preparation is a large OptiX
cost, overflow behavior beyond the exact capacity row is not validated, and the
full solver remains app-owned.

## Fixes Applied

- Added `query_metric_scope` to keep `1.235x` bound to query-only broadphase
  row emission.
- Added explicit M7 blockers for AABB index preparation and overflow-path
  validation.
- Strengthened tests for blocker completeness and semantic `<1.0` wall/index
  preparation conditions.

## Goal-Level Decision Audit

Decision: close the Contact Manifold boundary review as reviewed not-M7
evidence.

1. Was I foolish?

   No. This keeps the correct witness/pass evidence while refusing to turn a
   query-only signal into full contact-solver performance wording.

2. If yes, what actions made the decision foolish?

   Not applicable. It would be foolish to index the row as
   `contact_manifold: 1.235x` without the query-only scope, wall regression,
   and app-owned solver boundary.

3. Was there another path?

   Yes. Tune AABB-index preparation immediately. That may be future engineering
   work, but the current release-boundary fix is to prevent overclaim.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep Contact out of M7 and require a future candidate to fix wall
   timing, AABB index preparation, overflow validation, and full-solver scope.
