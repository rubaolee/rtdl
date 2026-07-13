# Call For Review: Goal5066 Aggregate Hierarchy Contract / Schema

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5066_aggregate_hierarchy_contract_schema_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5066_contract_schema_only_no_backend`
- `approve_with_required_amendments`
- `block_goal5066_contract_schema`

## Background

Goal5065 review approved the RT-BarnesHut hierarchy-traversal API direction only after amendments:

- no `BarnesHutOpening` public API name;
- manifest and status must not claim completed paper reproduction;
- narrow resident-kernel performance must be paired with broader prep+kernel envelope;
- next genericity proof must use a substantially different reducer/opening, not just another inverse-square force field.

Goal5066 is the first contract/schema-only step after that review. It should not implement a backend or migrate the app.

## Review Questions

1. Does the new public API avoid app identity names, especially the previously rejected `BarnesHutOpening`?
2. Is `SizeDistanceOpening(max_ratio=...)` a generic opening policy rather than an app-specific name?
3. Does `AggregateHierarchy3D` define a useful generic 3D hierarchy schema: point columns, node columns, topology columns, and optional continuation columns?
4. Are continuation columns clearly defined as zero-based node indices with `-1` as the missing sentinel?
5. Does the contract correctly support a non-force reducer (`aggregate_count`) so the next genericity proof is not just another inverse-square force-field case?
6. Does Goal5066 remain contract/schema-only, with no backend execution, native symbol, OptiX/CUDA rewrite, or app migration?
7. Do the metadata flags correctly refuse paper reproduction, whole-program speedup, and backend execution claims?
8. Are the fail-closed validations sufficient for malformed offsets, out-of-range indices, invalid continuation columns, and invalid opening parameters?
9. Did the changes preserve the existing RT-BarnesHut scaffold tests?
10. Is the proposed next step (`Goal5067`: app-owned adapter from author prepared-state dump to `AggregateHierarchy3D`) the right next step?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
