# Goal1075 Gemini Review Report

Date: 2026-04-28

## Review of Goal1075: Barnes-Hut Rich Node-Coverage Contract

This review assesses Goal1075 based on the provided criteria, examining code, tests, and documentation.

### Criteria 1: Correctly preserves the old Barnes-Hut one-level contract by default.

**Verdict: ACCEPT.**

The `scripts/goal887_prepared_decision_phase_profiler.py` explicitly uses `barnes_app.build_one_level_quadtree(bodies)` when both `--barnes-tree-depth` and `--hit-threshold` are set to their default value of `1`. This behavior is also documented in `docs/reports/goal1075_barnes_hut_rich_contract_design_2026-04-28.md`, confirming that the prior one-level contract is preserved by default.

### Criteria 2: Adds a richer fixed-depth node-coverage contract with `--barnes-tree-depth` and `--hit-threshold`.

**Verdict: ACCEPT.**

`examples/rtdl_barnes_hut_force_app.py` introduces `build_fixed_depth_quadtree_cells` which builds a quadtree to a specified depth, and `node_coverage_oracle` now supports a configurable `threshold`. The profiler script `scripts/goal887_prepared_decision_phase_profiler.py` correctly integrates these new capabilities via the `--barnes-tree-depth` and `--hit-threshold` command-line arguments. Unit tests in `tests/goal887_prepared_decision_phase_profiler_test.py` (specifically `test_barnes_hut_rich_contract_uses_depth_and_hit_threshold` and `test_barnes_hut_rich_contract_cli_flags_are_recorded`) confirm that these parameters are correctly processed and influence the resulting node structure and oracle evaluation.

### Criteria 3: Dry-run evidence is meaningful for local preparation.

**Verdict: ACCEPT.**

The `docs/reports/goal1075_barnes_hut_rich_contract_dry_run_2026-04-28.json` artifact, generated as described in `docs/reports/goal1075_barnes_hut_rich_contract_design_2026-04-28.md`, provides clear evidence of the new contract's functionality. It showcases how specific `barnes_tree_depth` (6) and `hit_threshold` (4) parameters lead to a significantly larger `node_count` (4096) compared to the old contract. The oracle decision `all_bodies_have_node_candidate: true` and the CPU reference time validate the local operation of the new contract, confirming that the changes are working as intended before any cloud deployment.

### Criteria 4: Boundaries correctly avoid public RTX speedup claims.

**Verdict: ACCEPT.**

Multiple sources clearly define and reinforce the boundaries:
- `scripts/goal887_prepared_decision_phase_profiler.py`'s `_cloud_claim_contract` function explicitly lists what is *not* claimed by the Barnes-Hut node-coverage scenario.
- The "Boundary" section in `docs/reports/goal1075_barnes_hut_rich_contract_design_2026-04-28.md` states this is "local contract preparation only" and "does not ... authorize public RTX speedup claims."
- `docs/reports/goal1071_rtx_pod_scale_up_result_2026-04-28.md` and `docs/handoff/REFRESH_LOCAL_2026-04-13.md` further emphasize that `--backend optix` alone does not constitute a public RTX speedup claim and that explicit authorization is required for any public wording.

The project maintains a consistent and cautious stance on RTX speedup claims, ensuring that this local contract enhancement does not inadvertently create such claims.

## Overall Verdict: ACCEPT

Goal1075 successfully implements a richer, configurable Barnes-Hut node-coverage contract while preserving the existing one-level contract's behavior by default. The changes are well-supported by code, tests, and comprehensive documentation. The dry-run evidence is meaningful, and strict boundaries are maintained to prevent unauthorized public RTX speedup claims. The goal effectively addresses the limitations identified in Goal1071 regarding the utility of the previous contract for RTX timing.
