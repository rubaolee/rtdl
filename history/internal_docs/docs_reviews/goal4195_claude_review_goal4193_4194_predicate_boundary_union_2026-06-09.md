# Goal4195: Claude Review — Goals4193–4194 Predicate-Aware Boundary Union

Date: 2026-06-09
Reviewer: Claude (claude-sonnet-4-6), external review role
Verdict: **accept-with-boundary**

---

## Artifacts Reviewed

- `docs/reports/goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4193_predicate_aware_boundary_union_candidate_primitive_2026-06-09.md`
- `docs/reports/goal4194_predicate_aware_boundary_union_reference_contract_2026-06-09.md`
- `src/rtdsl/primitive_hierarchy.py` — `continuation.predicate_aware_boundary_union` node
- `src/rtdsl/predicate_aware_boundary_union.py` — `predicate_aware_boundary_union_reference`
- `tests/goal4193_predicate_aware_boundary_union_candidate_test.py`
- `tests/goal4194_predicate_aware_boundary_union_reference_test.py`

---

## Q1: Does Goal4193 correctly register the candidate without app-specific policy?

**Yes.**

The node `continuation.predicate_aware_boundary_union` is placed in the `continuation`
layer with status `candidate_behavior`. The three fields that matter for the
generic-vs-app-specific boundary are correct:

- **`boundary`**: "Caller owns predicate meaning and app semantics; RTDL owns only
  generic predicate flags, component roots, boundary items, and deterministic
  assignment policy metadata."
- **`distinct_from`**: explicitly ends with "not an app-specific clustering or DBSCAN
  primitive."
- **`APP_OWNED_BOUNDARY_EXCLUSIONS`** (module-level constant): already includes
  "DBSCAN cluster expansion" as an app-owned exclusion.

The capability tags (`intent:components`, `shape:fixed_radius`, `output:columns`,
`output:grouped`, `exactness:exact`, `keying:by_query_id`) name only generic geometry
and output shapes. No tag encodes DBSCAN, epsilon, min-points, or cluster-expansion
policy.

The `depends_on` list correctly names `rows.fixed_radius_neighbor_rows` and
`continuation.fixed_radius_graph`, placing the node architecturally above the existing
graph continuation.

**One note** on style: `continuation.fixed_radius_graph` appears in both `depends_on`
and `considered_alternatives`. A node cannot simultaneously be a direct architectural
dependency and a rejected alternative in the same sense. The intent is clear (the
predicate-aware continuation *extends* the graph continuation rather than replacing it),
but the `considered_alternatives` entry creates mild ambiguity. This does not affect
correctness or the boundary claim, but the description in `distinct_from` ("Extends
fixed_radius_graph with caller-supplied predicate flags…") is the right framing, and
the `considered_alternatives` entry for `fixed_radius_graph` could be removed in a
future cleanup without loss of information.

The hierarchy validation with `require_discovery_metadata=True` is satisfied: the node
has non-empty `capability_tags`, `aliases`, `intent_phrases`, `reference_path`, and
`backends`.

---

## Q2: Does Goal4194 provide a suitable deterministic reference contract?

**Yes.**

`predicate_aware_boundary_union_reference` is a pure-Python union-find implementation
that:

1. Performs union only on predicate-true–predicate-true candidate pairs.
2. Collects candidate component roots for each boundary item (predicate-false item
   with at least one predicate-true neighbor).
3. Assigns boundary items to `min(roots)` under the `lowest_component_root` policy.

The output dictionary carries explicit contract fields including
`PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_VERSION`, `status =
"reference_contract_candidate_not_promoted"`, and policy metadata flags
(`native_engine_app_specific_logic: False`, `route_promotion_authorized: False`).

The reference contract is suitable as a same-contract oracle. Its main function is
to provide a deterministic, executable specification that a native or partner
implementation can be compared against without requiring the reference to be fast.
It fulfills that role.

---

## Q3: Is `lowest_component_root` a reasonable first oracle policy?

**Yes, with the following rationale.**

The `lowest_component_root` policy is implemented as:

```python
lower_root = min(left_root, right_root)
higher_root = max(left_root, right_root)
parent[higher_root] = lower_root
```

This ensures that every component's canonical root is the numerically smallest
original index in the component, regardless of the order in which pairs are processed
(path compression preserves this because path compression only shortens paths to the
already-established root; it does not change which root is canonical).

For boundary assignment, `min(roots)` over the set of neighboring component roots
is therefore stable across any pair ordering. The determinism test in Goal4194
confirms this with a manually permuted pair list that produces identical
`component_labels`.

Manual trace of the canonical test case confirms all asserted values:

| Field | Expected | Verified |
|---|---|---|
| `component_labels` | `(0,0,0,0,4,-1)` | ✓ |
| `component_sizes` | `(1,4)` | ✓ |
| `component_count` | `2` | ✓ |
| `true_true_pair_count` | `2` | ✓ |
| `boundary_pair_count` | `2` | ✓ |
| `ignored_false_false_pair_count` | `1` | ✓ |
| `boundary_assigned_count` | `1` | ✓ |
| `unassigned_count` | `1` | ✓ |
| `boundary_candidate_component_counts` | `((3,2),)` | ✓ |

The policy is restrictive enough to be useful as an oracle but not so restrictive
that it encodes application semantics. DBSCAN border assignment is
application-defined and remains outside the primitive.

---

## Q4: Are the claim boundaries honest?

**Yes across all checked dimensions.**

| Boundary dimension | Goal4193 | Goal4194 |
|---|---|---|
| Route promotion | "does not implement the primitive" / "does not authorize" | "does not promote the primitive" |
| Release wording | Not claimed | Not claimed |
| Public speedup claim | Not claimed | Not claimed |
| True-zero-copy claim | Not claimed | Not claimed |
| App-specific native-engine logic | Explicitly excluded by boundary field | `native_engine_app_specific_logic: False` in output dict |

The module `predicate_aware_boundary_union.py` was checked for app-specific terms.
The lowercase text of the file contains neither "dbscan", "epsilon", nor "min-points".
The version constant is `rtdl.predicate_aware_boundary_union.reference.v1` and the
status constant is `reference_contract_candidate_not_promoted` — both correctly
reflect the candidate standing.

Goal4190 (the motivating probe) reported a maximum of `1.056x` speedup on the
single-pass predicate direct-status route at 4M points and explicitly stated
"this is not a major win and should not become a default route." Goals 4193–4194
do not cite this as a speedup claim.

---

## Q5: What is required before promotion?

Goal4193 already enumerates the acceptance bar. This review ratifies and restates it
as the promotion gate:

1. **Same-contract component-size parity** against the current grouped-stream Numba
   route on at least one dense and one sparse RTX pod profile, when
   `policy_bound_component_sizes` is the contract.

2. **Counts-only parity** when border tie-breaks are explicitly outside the contract
   (i.e. matching `core_noise_assigned_counts_only` signatures as Goal4190 demonstrated
   is already achievable by the simpler direct-status routes).

3. **Deterministic boundary-assignment metadata** surfaced to the caller, not
   absorbed into native internals.

4. **No app-specific native ABI names** in any promoted implementation — no
   `dbscan`, `epsilon`, `min_pts`, or equivalent tokens in engine symbol names or
   internal dispatch keys.

5. **No hidden route selection** — the boundary-assignment policy must be an
   explicit, caller-visible parameter in any promoted interface.

6. **External review of the implementation** before the node status is advanced
   beyond `candidate_behavior`.

---

## Summary

Goals 4193 and 4194 are internally consistent, boundary-honest, and correctly
scoped as candidate (not promoted) artifacts. The reference contract is mathematically
correct and deterministically testable. The primitive registration in the hierarchy
does not introduce app-specific logic, does not authorize route promotion, and does not
make performance or release claims.

**Verdict: accept-with-boundary.**

The boundary is the promotion gate enumerated in Q5. No source code changes are
required or authorized by this review.
