# Primitive Promotion Review Handoff Template

Status: reusable v2.7 governance template. This is a template, not a review and
not a release authorization.

## Candidate

- Candidate node id:
- Candidate title:
- Candidate status:
- Candidate layer:
- Proposed source changes:
- Expected public or internal surface:

## Search Before Create

Paste the exact discovery queries run before proposing the primitive:

```python
rtdsl.find_primitive(intent="...", shape="...", dim="...", output="...", keying="...")
rtdsl.find_primitive(text="...")
```

List the closest existing node ids returned by those queries:

- `existing.node.id`: why it was not reused.

## Required Promotion Metadata

The candidate `PrimitiveHierarchyNode` must include:

- `considered_alternatives=(...)`
- `distinct_from="one clear sentence explaining why the nearest existing primitive does not suffice"`
- controlled `capability_tags`
- `reference_path`
- explicit `backends`
- explicit `partner_ops` when partner continuation is part of the contract

## Required Gate Output

Paste both gate outputs into the goal report or review packet:

```python
rtdsl.lint_new_primitive(candidate_node)
rtdsl.validate_primitive_hierarchy(
    candidate_tree,
    enforce_promotion_metadata=True,
    promotion_candidate_ids=(candidate_node.id,),
)
```

The candidate-scoped validation must be `valid: True`. If it is false because
of `promotion_metadata_missing`, either reuse the existing primitive or update
`considered_alternatives` and `distinct_from` before asking for review.

## Reviewer Questions

1. Does the candidate preserve app-independent semantics?
2. Were the discovery queries sufficient to find likely alternatives?
3. Do `considered_alternatives` and `distinct_from` honestly explain why this
   is not a duplicate?
4. Are backend and partner roles explicit without hidden auto-selection?
5. Are determinism, tolerance, capacity, overflow, and claim boundaries stated?
6. Does the packet avoid release, public speedup, zero-copy, broad RT-core, and
   paper-reproduction claims unless separately authorized?

## Output

Write the review to `docs/reviews/goalXXXX_<reviewer>_primitive_promotion_review_YYYY-MM-DD.md`
and use one of the accepted verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
