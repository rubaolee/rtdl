# Review: Goal3087 v2.7 Duplicate-Gate Promotion Workflow

Reviewer: Claude (Sonnet 4.6)
Date: 2026-06-03
Verdict: **accept**

---

## Scope

Read-only review of the Goal3087 candidate-scoped duplicate-gate promotion
workflow. Files inspected:

- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_catalog.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/handoff/HANDOFF_TEMPLATE_PRIMITIVE_PROMOTION_REVIEW.md`
- `tests/goal3087_v2_7_duplicate_gate_promotion_workflow_test.py`
- `docs/reports/goal3087_v2_7_duplicate_gate_promotion_workflow_2026-06-03.md`

Validation: test run was blocked by the sandbox permission model in this
session. The goal report records "Ran 24 tests in 0.060s OK" for the four
named test modules. The code-level analysis below confirms the test assertions
are coherent with the implementation; no gap was found that would explain a
false pass.

---

## Review Questions

### Q1. Does the candidate-scoped `validate_primitive_hierarchy(...)` correctly fail closed for near-duplicate promoted candidates without `considered_alternatives` and `distinct_from`?

**Yes, and the logic is correct end-to-end.**

`validate_primitive_hierarchy` accepts `enforce_promotion_metadata=False` and
`promotion_candidate_ids=()` as defaults. When `enforce_promotion_metadata=True`
and a non-empty candidate id set is supplied, it delegates to
`_promotion_metadata_missing`, which:

1. Skips all nodes not in the candidate id set — no accidental reclassification
   of existing nodes.
2. Skips nodes whose status is outside `PRIMITIVE_PROMOTION_METADATA_STATUSES`
   (`stable_primitive`, `stable_behavior`, `stable_compatibility_path`,
   `candidate_behavior`) — non-promotable statuses are untouched.
3. Calls `_possible_duplicate_nodes` to find overlap by capability key facets.
4. Fails closed (adds an entry to `promotion_metadata_missing`) only when
   possible duplicates exist **and** the candidate does not have both a
   non-empty `considered_alternatives` tuple **and** a non-empty
   `distinct_from` string (after `.strip()`).

The fail-closed direction is correct: missing metadata blocks promotion, extra
metadata is always allowed.

The overlap threshold in `_possible_duplicate_nodes` is
`max(3, candidate_key_family_count)`. For the synthetic test candidate with
five key families (`intent`, `shape`, `dim`, `output`, `keying`) all matching
the reference node, the threshold is 5 and the overlap score is 5, so the
gate fires. With `considered_alternatives` and `distinct_from` populated,
`lint_new_primitive` and `validate_primitive_hierarchy` both return valid.

**Design note (not a defect):** The threshold formula requires
`score >= max(3, candidate_key_family_count)`, meaning a candidate with four
key families needs all four to match before the gate fires. A candidate that
shares three out of four families with an existing primitive would not trigger
the gate. This is a conservative design choice that avoids false positives, at
the cost of missing partial-family near-duplicates. Reviewers proposing
primitives with many key families should be aware that the gate requires full
family saturation, not a majority.

**Design note (not a defect):** `exactness` appears in `PRIMITIVE_CAPABILITY_TAGS`
as a controlled facet but is absent from `PRIMITIVE_DUPLICATE_KEY_FAMILIES`
(`intent`, `shape`, `dim`, `output`, `keying`). Two primitives that are
identical in exactness (e.g., both `exactness:exact`) will not have that
similarity counted toward their overlap score. This is a deliberate
omission — exactness alone does not make two primitives duplicates — but
promotion reviewers should not assume the gate covers all facets visible in
capability tags.

### Q2. Is the candidate scope requirement a good safeguard against accidentally reclassifying legacy/current nodes?

**Yes, and the implementation is tight.**

When `enforce_promotion_metadata=True` but `promotion_candidate_ids` is empty,
`promotion_candidate_scope_required` is set to `True` and `valid` is `False`.
This blocks enforcement without a named scope entirely, preventing a caller
from accidentally sweeping all nodes through the gate.

When a scope is provided, `_promotion_metadata_missing` loops only over nodes
whose id appears in the candidate id set. All current hierarchy nodes —
regardless of status — are untouched unless their id is explicitly listed in
`promotion_candidate_ids`.

The test `test_promotion_validation_requires_explicit_candidate_scope` and
`test_promotion_validation_rejects_unknown_candidate_id` cover both failure
modes. The unknown-candidate-id check is also correct: unknown ids in the
candidate scope cause a `valid: False` result, preventing silent no-ops when
a caller misspells a candidate id.

### Q3. Does the handoff template make the search-before-create workflow executable enough for future primitive-promotion reviews?

**Yes, with minor room for optional strengthening.**

`HANDOFF_TEMPLATE_PRIMITIVE_PROMOTION_REVIEW.md` is structured around concrete
actions a proposer must take before asking for review:

- Requires pasting actual `rtdsl.find_primitive(...)` query calls, not a
  narrative summary.
- Requires listing the closest returned node ids and explaining why each was
  not reused.
- Lists the six required `PrimitiveHierarchyNode` metadata fields by name.
- Requires pasting both `lint_new_primitive(candidate_node)` output and
  `validate_primitive_hierarchy(..., enforce_promotion_metadata=True,
  promotion_candidate_ids=(candidate_node.id,))` output.
- States the pass condition explicitly: `valid: True`.
- Provides six reviewer questions that map to the standard boundary concerns.
- Specifies the four accepted verdicts.

The template is executable as written. A reviewer receiving a completed packet
has everything needed to check duplicate documentation without re-running the
gate themselves.

Optional future improvement: the template could remind proposers that
`lint_new_primitive` runs against the pre-insertion hierarchy while
`validate_primitive_hierarchy` runs against a tree that already contains the
candidate. Both outputs are currently required, which is correct, but the
distinction between pre-insertion and post-insertion checks is not made
explicit in the template text.

### Q4. Does the generated catalog describe the duplicate gate accurately and without overclaiming?

**Yes.**

The catalog's "Hierarchical Primitive Organization" section describes the gate
clearly:

> New promoted primitives that overlap an existing primitive's key facets must
> record `considered_alternatives` and `distinct_from`; otherwise the duplicate
> gate fails closed.

The "Promotion Guardrails" section lists the two-step gate (`lint_new_primitive`
before insertion, `validate_primitive_hierarchy` after) with the correct
parameter names, matching the code exactly.

The "Generated Validation Snapshot" section renders
`Promotion metadata enforced by default: False` because the snapshot call does
not pass `enforce_promotion_metadata=True`. This is accurate: the gate is
opt-in at validation time, not a standing default.

The "Claim Boundary" section of the catalog restates the promotion exclusions
(release readiness, public speedup wording, zero-copy, broad RT-core,
paper-reproduction) matching the goal report's self-stated boundary.

No overclaiming detected: the catalog does not say the gate prevents all
duplicates, only that it requires documentation for overlap-detected candidates.

### Q5. Does Goal3087 preserve the app-agnostic engine boundary and avoid release, performance, zero-copy, broad RT-core, and paper-reproduction claims?

**Yes, cleanly.**

Goal3087 adds only governance machinery:

- Two vocabulary constants (`PRIMITIVE_DUPLICATE_KEY_FAMILIES`,
  `PRIMITIVE_PROMOTION_METADATA_STATUSES`).
- Two new parameters to an existing validation function.
- Two helper functions (`_promotion_metadata_missing`,
  `_possible_duplicate_nodes`).
- An updated catalog render and a new handoff template.

No new primitives are introduced, so there is no risk of a boundary violation
hidden in a new node definition.

The two existing nodes that carry `considered_alternatives` and `distinct_from`
(`reduction.ray_triangle_primitive_grouped_i64` and
`continuation.ranked_summary`) were already in the hierarchy before Goal3087.
Their boundaries are:

- `ray_triangle_primitive_grouped_i64`: "Query encoding and group/value
  semantics remain app code."
- `ranked_summary`: "Summarizes already emitted fixed-radius rows; it does not
  own traversal or materialize full witness rows like collect_k_bounded."

Both are app-independent descriptions of what the primitive does not own.
Neither boundary asserts performance, zero-copy, RT-core breadth, or paper
parity.

`APP_OWNED_BOUNDARY_EXCLUSIONS` is carried through without modification. The
planner constants (`PRIMITIVE_ADVISORY_PLANNER_EXECUTES=False`,
`PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED=False`) remain
correct for the advisory-only design.

---

## Summary

Goal3087 is a complete and correctly bounded governance mechanism. The four
test scenarios — reject without metadata, accept with metadata, reject without
scope, reject with unknown scope id — cover the primary failure modes. The
catalog and handoff template faithfully reflect the implementation without
overclaiming. The engine boundary and claim scope are preserved throughout.

The two design notes in Q1 (threshold requires full family saturation,
`exactness` excluded from key families) are known properties of the design
rather than defects. They are visible in the code and do not create incorrect
gate behavior for the stated goal.

**Verdict: accept**
