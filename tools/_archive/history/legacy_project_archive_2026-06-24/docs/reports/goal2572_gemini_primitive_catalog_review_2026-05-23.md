VERDICT: ACCEPT

The documentation in `docs/rtdl_primitive_catalog.md` and the report in `docs/reports/goal2572_primitive_catalog_and_promotion_rules_2026-05-23.md` are highly accurate and well-aligned with `src/rtdsl/v1_5_migration_inventory.py` and `src/rtdsl/grouped_reduction.py`.

- **Primitive/App-Code Boundary**: Accurately distinguishes between app-independent primitives (e.g., `ANY_HIT`, `group_sum_i64`) and domain-specific logic (e.g., DBSCAN expansion, Robot pose sampling). This is reinforced by the `claim_boundary` metadata in `grouped_reduction.py` and the `boundary` field in the migration inventory.
- **Behavior/Maturity Organization**: Layers match the source-of-truth constants (Stable Core, Stable Scalar, Experimental, and Shared Substrate). Counts of primitives (4 stable generic, 6 scalar, 1 experimental, 8 grouped-reduction) match the code exactly.
- **User Selection Guide**: Provides a valid mapping of behavioral needs to the current primitive surface.
- **Benchmark-App Injection History**: Correctly identifies the apps that drove primitive requirements (RT-DBSCAN, Robot collision, RayDB-style, Barnes-Hut) while maintaining the engine/app boundary.
- **Overclaim Blocks**: Rigorously maintained. Both the docs and the source code (`v1_5_generic_migration_blockers`, `GroupedReductionSpec.to_metadata`) explicitly block public speedup wording, public release authorization, and external ABI stability.

Validation test `tests/goal2572_primitive_catalog_test.py` successfully verifies these alignments.
