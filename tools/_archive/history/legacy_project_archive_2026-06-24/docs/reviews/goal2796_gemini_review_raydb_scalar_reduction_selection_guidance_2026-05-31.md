# Goal2796 - RayDB Scalar Reduction Selection Guidance

Date: 2026-05-31

## Independent Gemini Review

This is an independent Gemini review, distinct from Codex authoring.

## Verdict

`accept-with-boundary`

## Findings

### 1. Does the artifact support the claim that Triton is correct but slower than Torch CUDA for RayDB-style scalar grouped reductions?

**Finding:** Yes.
The `docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json` artifact confirms functional correctness with `"all_correct": true` and `"correct_vs_torch_cuda": true` for all measured cases and modes. Performance data (`median_sec`) clearly shows that `raydb_triton_public_front_door` is consistently and significantly slower than `torch_cuda_baseline`. Calculated slowdown ratios (e.g., 38.04x for `segmented_count_i64` at 1K rows) align with the ranges reported in `docs/reports/goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md`.

### 2. Are the four guidance rows for `segmented_count_i64`, `segmented_sum_f64`, `segmented_min_f64`, and `segmented_max_f64` accurate and scoped correctly?

**Finding:** Yes.
The `src/rtdsl/v2_5_partner_selection_guidance.py` file contains `V25PartnerSelectionGuidanceRow` entries for these four operations. These entries accurately record:
- `operation` (e.g., "segmented_count_i64")
- `workload_shape` ("raydb_scalar_grouped_reduction_frontdoor")
- `measured_partner` ("triton")
- `comparison_partner` ("torch_cuda_same_contract_reduction")
- `evidence_goal` ("Goal2796")
- `artifact_path` ("docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json")
- `measured_partner_slower_min_ratio` and `measured_partner_slower_max_ratio` matching the report.

The scoping is correct, enforced by:
- The `__post_init__` method of `V25PartnerSelectionGuidanceRow` which raises `ValueError` if `auto_select_measured_partner_allowed`, `promoted_performance_path`, or any speedup/release claims are `True`.
- The `recommendation` string for each row explicitly states "Do not auto-select Triton...".
- The `validate_v2_5_partner_selection_guidance` function which verifies these constraints.

### 3. Does the RayDB app migration plan remain primitive-first rather than forcing Triton?

**Finding:** Yes.
In `src/rtdsl/v2_5_triton_app_migration.py`, the `raydb_style` `V25TritonBenchmarkAppPlan` entry:
- Sets `current_hot_path_partner` to `"primitive_first_fused_rtdl_for_grouped_scalar_reductions"`.
- Has `v2_5_status` and `first_port_action` fields that explicitly mention and reinforce the "primitive_first" approach.
- Includes `notes` that confirm Triton is slower than the prepared fused primitive.
The `tests/goal2796_raydb_scalar_reduction_selection_guidance_test.py` (`test_raydb_app_plan_integrates_scalar_guidance`) also verifies the presence of "primitive_first" in the app's status and action.

### 4. Do the tests prevent accidental auto-selection or performance promotion from this negative evidence?

**Finding:** Yes.
Multiple test files rigorously prevent such misinterpretations:
- `tests/goal2796_raydb_scalar_reduction_selection_guidance_test.py`: `test_guidance_blocks_auto_selection_for_scalar_reductions` asserts that `auto_select_partner_allowed` is `False` and that speedup/release claims are not authorized for Goal2796-specific guidance.
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`: `test_guidance_validates_and_keeps_claims_blocked` globally validates that `promoted_performance_path`, `public_speedup_claim_authorized`, etc., are `False`. `test_raydb_scalar_reductions_record_goal2796_negative_guidance` specifically checks these for Goal2796 rows.
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`: `test_migration_plan_consumes_partner_selection_guidance` and `test_raydb_scalar_reductions_record_goal2796_negative_guidance` ensure that the app migration plan also integrates this negative guidance and blocks auto-selection.
These tests, combined with the `__post_init__` dataclass validations, provide strong safeguards.

### 5. Does the report avoid public speedup, release, broad Triton, and whole-app overclaims?

**Finding:** Yes.
The `docs/reports/goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md` report includes a clear "Claim Boundary" section, explicitly listing "public speedup claims", "whole-app speedup claims", "release readiness", and "broad Triton-performance claims" as "Still blocked". The `raydb_triton_frontdoor_current.json` artifact also contains `"no_public_speedup_claim": true`. The `V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY` constant in `src/rtdsl/v2_5_partner_selection_guidance.py` and its propagation throughout the metadata further enforce these boundaries.
