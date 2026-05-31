# Goal2783 Independent Review — App Migration Selection Guidance

**Reviewer:** Claude (claude-sonnet-4-6)
**Date:** 2026-05-31
**Verdict: `accept`**

---

## Files Reviewed

- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `docs/reports/goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md`
- `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`

---

## Review Question Responses

### 1. Does Goal2783 correctly wire Goal2782's measured negative guidance into the v2.5 app migration plan?

Yes, the wiring is correct and structural. `V25TritonBenchmarkAppPlan.to_metadata()` calls `plan_v2_5_partner_selection(operation, workload_shape)` for each entry in `measured_selection_shapes` and stores the results as `partner_selection_guidance` plus a `measured_negative_preview_guidance_count`. The two affected app rows are the only rows that carry non-empty `measured_selection_shapes`:

- `rtnn`: `("grouped_topk_f64", "dense_exact_topk_candidate_ranking")` — maps to the Goal2780 guidance row.
- `barnes_hut`: `("grouped_vector_sum_f64x2", "dense_grouped_vector_sum_2d")` — maps to the Goal2781 guidance row.

All remaining apps default to `measured_selection_shapes=()`, returning `partner_selection_guidance: ()` and count 0. The top-level plan carries `partner_selection_guidance_version`, `partner_selection_guidance_integrated: True`, and `auto_select_preview_partner_allowed: False`.

### 2. Do the RTNN and Barnes-Hut rows point to the right operations, workload shapes, and evidence goals?

Yes.

**RTNN:**
- Operation: `grouped_topk_f64` — matches the pod metadata field `v2_5_partner_continuation_operation` in `goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`.
- Workload shape: `dense_exact_topk_candidate_ranking` — consistent with the two larger pod cases (256×512×k=8 and 512×1024×k=8).
- Evidence goal: `Goal2780` — confirmed by pod `"goal": "Goal2780"`.
- Ratio range in guidance: 47.28x–150.90x — pod rows show 47.28x, 150.90x, and 143.50x. The min/max bracket is accurate.
- App first-port action correctly names grouped argmin for top-1 cases and defers dense exact top-k to Torch/CuPy or another explicitly selected partner.

**Barnes-Hut:**
- Operation: `grouped_vector_sum_f64x2` — matches pod metadata `v2_5_partner_continuation_operation` in `goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`.
- Workload shape: `dense_grouped_vector_sum_2d` — consistent with 512/4096/8192-group pod rows.
- Evidence goal: `Goal2781` — confirmed by pod `"goal": "Goal2781"`.
- Ratio range in guidance: 4.09x–16.59x — pod rows show 16.59x (512 groups), 6.72x (4096 groups), and 4.09x (8192 groups). The min/max bracket is accurate.
- App notes correctly say never to embed inverse-square force law inside the engine or Triton primitive contract. The first-port action correctly names Torch scatter-add as the measured better same-contract branch.

### 3. Does the planner remain advisory only and block preview-partner auto-select?

Yes, at multiple layers:

- `V25PartnerSelectionGuidanceRow.__post_init__` raises `ValueError` if `auto_select_measured_partner_allowed=True`, making the constraint enforcement structural, not conventional.
- `plan_v2_5_partner_selection()` returns `auto_select_partner_allowed: False` for both the `measured_negative_preview_guidance` path and the `no_measured_guidance` fail-closed default.
- The top-level guidance dict carries `planner_policy: "advisory_only_explicit_app_partner_choice"`, `no_partner_forced: True`, and `preview_kernel_available_does_not_imply_auto_select: True`.
- `validate_v2_5_triton_benchmark_app_migration_plan()` checks `auto_select_preview_partner_allowed` at both the plan level and per-app level, and also walks per-app guidance entries to confirm that any `measured_negative_preview_guidance` status is paired with `auto_select_partner_allowed: False`.

No path through the planner can produce a positive auto-select signal for a preview partner.

### 4. Does this keep the native RTDL/OptiX traversal boundary intact?

Yes. Several checks converge:

- The top-level plan `claim_boundary` explicitly states: "not authorization to replace RTDL/OptiX traversal with partner code."
- `V25PartnerSelectionGuidanceRow.__post_init__` raises if `promoted_performance_path=True` or any speedup-claim flag is set.
- Both pod artifacts carry `native_engine_row_contract: "not_called_partner_reference_only"` (Goal2780) and `"not_called_partner_continuation_only"` (Goal2781), confirming the measured paths never invoke RT traversal.
- Neither the RTNN nor Barnes-Hut app rows carry `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, or `promoted_performance_path` fields set to anything other than `False`.
- The v2.5 status strings for RTNN (`covered_but_dense_topk_has_goal2780_negative_triton_selection_guidance`) and Barnes-Hut (`covered_but_dense_vector_sum_has_goal2781_negative_triton_selection_guidance`) accurately reflect coverage with a block, not promotion.

### 5. Are the tests and report sufficient for this metadata/planner step?

Yes, and appropriately scoped.

The Goal2783 test suite (`goal2783_v2_5_app_migration_selection_guidance_test.py`) covers:
- End-to-end plan validation via `validate_v2_5_triton_benchmark_app_migration_plan()`.
- Per-app RTNN guidance: operation name, evidence goal, guidance status, recommendation text, count, and auto-select block.
- Per-app Barnes-Hut guidance: same checks mirrored.
- Apps without negative guidance: confirms empty guidance tuple, count=0, and auto-select still blocked — preventing false positive guidance injection.
- Document presence checks: report, consensus, and this review file all read and tested for required content.

The Goal2782 test suite (also re-reviewed here) additionally verifies artifact file existence on disk for both pod JSON paths, ratio bounds from actual pod measurements, and that guidance symbols are available but not `__all__`-exported.

Neither suite requires new pod evidence; both correctly reuse Goal2780 and Goal2781 artifacts. The report's `PENDING` status for the local test run is expected — the suite depends on this review file existing, which it now does.

No pod is appropriate for this goal. No new kernel timing was collected; only planner metadata was updated.

---

## Observations

**Minor naming inconsistency (non-blocking):** The `V25TieredBenchmarkManifestRow` for Barnes-Hut lists `"grouped_vector_sum"` (without the `_f64x2` suffix) in `required_partner_operations`, while the app plan row correctly uses `"grouped_vector_sum_f64x2"`. The manifest validator does not check operation names against `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`, so this is cosmetic. The app plan row is the authoritative contract-carrying structure.

**RTNN manifest required_partner_operations:** Lists `"bounded_topk_or_ranked_summary"` as a conceptual placeholder, which is not a concrete protocol operation. This is consistent with how the manifest is used (aspirational scoping, not contract enforcement) but worth documenting if the manifest validator gains operation-name checks in the future.

Both observations are informational and do not affect correctness.

---

## Verdict

**`accept`**

Goal2783 correctly wires Goal2782's machine-readable negative guidance into the v2.5 app migration planner. RTNN and Barnes-Hut both point to the right operations, workload shapes, and evidence goals, with ratio ranges that match the pod artifacts exactly. The advisory-only, fail-closed planner design is enforced structurally at the dataclass, function, and validator levels — not just by convention. The RTDL/OptiX traversal boundary is protected at multiple independent layers. Tests are sufficient for a metadata/planner step with no new kernel timing.
