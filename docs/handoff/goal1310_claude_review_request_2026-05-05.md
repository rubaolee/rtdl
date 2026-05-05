# Goal1310 Claude Review Request: v1.5 Jaccard `COLLECT_K_BOUNDED`

Please review the Goal1310 v1.5 Jaccard bounded-collection policy in `/Users/rl2025/rtdl_python_only`.

Read these files:

- `docs/reports/goal1310_v1_5_jaccard_collect_k_bounded_policy_2026-05-05.md`
- `src/rtdsl/bounded_collection_contracts.py`
- `src/rtdsl/polygon_primitives.py`
- `src/rtdsl/primitive_contract_schema.py`
- `src/rtdsl/v1_5_migration_inventory.py`
- `tests/goal1310_v1_5_jaccard_collect_k_bounded_contract_test.py`
- `tests/goal1280_v1_4_polygon_jaccard_diagnostic_contract_test.py`

Judge whether:

1. `COLLECT_K_BOUNDED` is kept experimental/diagnostic and not promoted to a stable v1.5 primitive.
2. The policy correctly fails closed on overflow and rejects silent truncation.
3. Jaccard score reduction remains blocked unless complete candidate coverage is proven.
4. Public speedup wording remains blocked.
5. The inventory accurately says policy is defined but native fail-closed collection and score reduction are still unfinished.

Write your review to:

`docs/reports/goal1310_claude_review_2026-05-05.md`

Use sections:

- Verdict
- Findings
- Risks
- Required Fixes
- Conclusion

Do not modify source code.
