I now have enough to render the full review. Here is my critical assessment:

---

## Critical Review: V4 Goal4636 Threshold-Summary Target Protocol
**Date:** 2026-06-25

---

### Q1 — Is `fixed_radius_threshold_summary_2d` a valid generic V4 operator target, or is it too tied to Hausdorff/XHD?

**Finding: Marginally generic — acceptable, but the distinction from the existing `count_threshold` surface is thin.**

The semantic gap between `FIXED_RADIUS_COUNT_THRESHOLD_2D` (per-point boolean column: is each point's neighbor count ≥ threshold?) and `FIXED_RADIUS_THRESHOLD_REACHED_COUNT_2D` (directed set-level scalar boolean: has the entire A→B sweep found sufficient coverage?) is real. The output contract is `generic_prepared_optix_scalar_threshold_count_2d` — a global directed scalar, not a per-row array. This parallels the distinction between `any_hit_flags` (per-ray column) and `any_hit_weighted_sum` (global scalar), which were accepted as separate continuation classes.

However, this operator sits closer to the Hausdorff/XHD application domain than any currently measured surface. No other benchmark in the coverage audit has an obvious use for a `directed_a_to_b / directed_b_to_a` pair-level threshold scalar. The claim that this is "generic" rests on the abstract possibility that set-coverage checks appear in other apps (containment, proximity matching). That is plausible but not demonstrated.

**Conclusion:** Acceptable as a target-selection predeclaration. Not a ground for rejection. The continuation class distinction from `count_threshold` is real. The goal must not be promoted post-POD with wording that implies this operator covers any app beyond the prepared-runner Hausdorff workflow.

---

### Q2 — Is `rtdl_native_prepared_runner` scope acceptable as measured V4 coverage expansion?

**Finding: This is the primary structural concern. The scope is honest, but the catalog promotion path for it is undefined.**

Every currently measured Tier-2 surface uses a framework partner label (`torch`, or `numba` for Goal4635). The `measured_partners` field in the catalog schema is typed around framework labels. The Goal4636 target declares `partner_scope: ("rtdl_native_prepared_runner",)` — which is not a framework integration partner; it is the native OptiX execution path itself.

This means:
- The resulting catalog entry would have no framework as a `measured_partner`.
- `measured_partners: ("rtdl_native_prepared_runner",)` is not defined in the current catalog schema — the planner's `plan_v4_operator_request` function only validates `torch`, `cupy`, `numba` as legal partners.
- No `plan_v4_operator_request` call with `partner="rtdl_native_prepared_runner"` would succeed; the planner would raise `ValueError`.

The coverage value is real: the productized prepared runner IS the V4 execution path for the Hausdorff/XHD threshold workflow, and measuring it at serious scale (262144 copies, 1M+ points per side, 5 repeats) is genuine evidence. But the catalog schema as written cannot correctly represent `rtdl_native_prepared_runner` as a `measured_partners` entry.

**Required Amendment (must be resolved before catalog promotion, not before POD gate):**

Before any post-POD catalog promotion, the promotion protocol must:
1. Define explicitly how `rtdl_native_prepared_runner` is represented in the catalog (either as a first-class partner label alongside torch/cupy/numba, or as a separate `prepared_runner_scope` field distinct from `measured_partners`).
2. Ensure the planner and catalog validation logic accepts this scope label without treating it as an unmeasured partner.
3. Mark the resulting catalog entry with a scope class annotation (e.g., `native_prepared_runner_scope` vs `device_array_scope`) so it is not confused with device-array front-door surfaces.

This amendment does not block running the POD gate. It is a precondition for catalog promotion if the gate passes.

---

### Q3 — Are the promotion thresholds material?

**Finding: Yes, but one threshold deserves a materiality note.**

- `runner_vs_embree_phase_total >= 1.20x`: Material. The V3 boundary data (boundary test, 262144 copies) showed `query_optix_over_embree = 1.864x` and `wall_optix_over_embree = 1.258x` for the legacy mode at repeat=1/warmup=0. The productized runner at repeat=5/warmup=1 should match or exceed this in phase-total.
- `runner_vs_embree_wrapper_wall >= 1.20x`: This is the tighter floor. The V3 boundary test recorded `wall = 1.258x` at 262144 copies with no warmup and a single repeat. With warmup=1 and repeat=5, the amortized wrapper-wall measurement should be cleaner, but Python overhead still competes. The 1.20x floor is defensible at this scale and repeat count.
- `runner_vs_legacy phase-total >= 0.98x` and `wrapper_wall >= 0.98x`: These are no-regression floors, not speedup floors. Appropriate — the runner adds prepared-session overhead not present in legacy mode.

The runner script `failed_checks_for` does **not** check `runner_vs_embree` speedup as a hard check — it only checks the no-regression vs legacy. The 1.20x vs Embree floors are declared in the target dataclass and validated in `validate_v4_goal4636_threshold_summary_target()` as dataclass-level invariants, but they do not appear in `failed_checks_for()`. This gap should be flagged: if the POD gate passes but the runner beats Embree by only 1.18x, the dataclass validation would have already rejected this scenario in the target's gate definition — but the runner script's `failed_checks` array would not catch it independently.

**Required Amendment (minor, structural):** The runner script's `failed_checks_for` should include a check that `runner_vs_embree phase_total speedup >= 1.20x`. Currently only `runner_vs_legacy` regression floors are hard-checked in the runner script.

---

### Q4 — Is it correct that target selection does not add a measured catalog surface before POD evidence?

**Finding: Yes, this is correctly maintained.**

The status `goal4636_threshold_summary_target_predeclared_pending_pod_gate_not_measured` is enforced in three places:
1. `validate_v4_goal4636_threshold_summary_target()` raises if `measured_catalog_promotion_authorized` is true.
2. The test `test_target_is_not_catalog_promotion_before_pod_gate` asserts `fixed_radius_threshold_summary_2d` is absent from `V4_TIER2_OPERATOR_SURFACES`.
3. The coverage audit's `hausdorff_xhd` row remains `partial_measured_operator_coverage` and its `next_action` field says "do not use as the second release gate before a clearer same-contract operator target" — unchanged by this target predeclaration.

The separation is sound. No measured surface is added. No catalog promotion occurs. The target-selection step is correctly bounded.

---

### Q5 — If approved, may Codex run the POD gate with `--require-rt-hardware` next?

**Conditionally yes, subject to the required amendment being tracked but not blocking the POD gate itself.**

The POD command is correctly formed:
- `--copies 262144`: yields 1,048,576 points per side — above the serious floor.
- `--repeat 5 --warmup 1`: materially exceeds the repeat=1 blocker from the V3 boundary.
- `--timeout-sec 7200`: adequate for a 5-repeat, 1M-point run.
- `--require-rt-hardware`: correct gate; the harness fails closed if hardware is absent.
- All three variants (Embree, legacy, runner) are exercised; oracle match is checked for all.
- Both directed legs (a_to_b, b_to_a) must report runtime execution and residency.
- Step-3 audit is required for both legs.
- Threshold rows must not be materialized on host.

Pre-POD local validation is claimed as complete (5 + 7 + 42 tests OK). The dry-run confirmed 3 variants, 0 failed checks.

**One caveat**: The runner script `failed_checks_for` omits a hard check for `runner_vs_embree >= 1.20x` (see Q3). The POD gate may technically pass the harness's `failed_checks` list even if the Embree speedup floor is not met, because that floor is not in `failed_checks_for`. The runner script should be patched before or alongside the POD run to close this gap.

---

## Required Amendments Summary

1. **(Pre-promotion, not pre-POD)** Define `rtdl_native_prepared_runner` as a first-class scope label in the catalog schema, distinct from `torch/cupy/numba` framework partners, before any post-POD catalog promotion step. The current `plan_v4_operator_request` would reject this label.

2. **(Structural, should be fixed before or alongside the POD run)** Add a hard check for `runner_vs_embree_phase_total_speedup >= 1.20x` in `v3_phoenix_hausdorff_threshold_runner_pod_ab.py`'s `failed_checks_for()`. The 1.20x floor is declared in the target dataclass but is not surfaced in the harness's `failed_checks` array, creating a gap where the gate could report `failed_checks: []` while the Embree speedup floor is actually missed.

---

## Non-Authorization Confirmation

This review does not authorize:
- V4 release or release candidate
- Broad V4 speedup or all-benchmark speedup
- Whole-Hausdorff speedup
- Measured catalog promotion (pending POD evidence)
- CuPy performance
- Tier-3 support
- True zero-copy
- C ABI / embedding / non-Python host claims
- Hausdorff-native or other app-specific kernels

---

## Verdict

**`approve_with_required_amendments`**

The target selection is valid. `threshold_summary` is a real continuation class distinct from the existing `count_threshold` surface; the `rtdl_native_prepared_runner` scope is honest about what is being measured; the 1.20x Embree floor is material; no catalog promotion occurs before POD. The two required amendments are structural — one must be resolved before catalog promotion, and one should be patched into the runner script before POD execution. Neither blocks target approval. POD may proceed once Amendment 2 (the `failed_checks_for` Embree floor gap) is patched.
