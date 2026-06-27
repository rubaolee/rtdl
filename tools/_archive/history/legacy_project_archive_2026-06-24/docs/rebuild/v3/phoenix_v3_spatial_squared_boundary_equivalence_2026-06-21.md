# Phoenix V3 Spatial Squared-Boundary Equivalence

Status: `spatial_guarded_squared_boundary_equivalence_pass_not_release`.

This packet supports the Spatial guarded squared-boundary candidate by
checking the old sqrt-based boundary predicate against a guarded squared
fast path with sqrt fallback near threshold cases.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added: 0
```

## Result

- Deterministic cases: `1260`
- Random cases: `200000`
- Total cases: `201260`
- Guarded mismatches: `0`
- Pure squared mismatches recorded: `10`

## Scope

A pure squared predicate is not treated as equivalent: deterministic endpoint-adjacent cases showed floating-point disagreement with the old sqrt/along-epsilon predicate.

The guarded predicate uses squared comparisons only when the value is outside a small threshold band. Cases near the threshold fall back to the old sqrt/along-epsilon predicate.

Guard tolerance: `1e-06`.

This packet checks the predicate algebra in Python double precision and records the same branch structure. It is supporting evidence, not a standalone CUDA compiler proof.

## Goal-Level Decision Audit

Decision: Add independent predicate-equivalence evidence before any M7 promotion decision.

1. Was I foolish? No. This strengthens correctness review without changing runtime defaults or claiming release.
2. If yes, what actions made the decision foolish? The foolish action would be to rely only on one benchmark count and skip predicate-level equivalence evidence before asking for external review.
3. Was there another path? Wait for external review. That is still required, but it would leave an obvious correctness question unanswered.
4. Can I now try a different path? Use a guarded squared fast path with sqrt fallback near thresholds, provide deterministic endpoint/interior cases plus seeded random model checks, then keep the candidate pending external review.
