# Antigravity Review: V4 Goal4648 Partner Promotion Contract With Numeric Bars

Date: 2026-06-25
Verdict: `accept_goal4648_complete`

## Rationale

Goal4648 is complete and ready to allow Goal4649 to start. The following items have been successfully verified:

1. **Code-Level Contracts**: The contract module at `src/rtdsl/v4_partner_promotion_contract.py` is implemented and exports `v4_partner_promotion_contracts()`, `v4_partner_promotion_contract()`, `v4_partner_promotion_candidate_allowed()`, and `V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS`.
2. **Unified Front Door**: The exports are properly exposed via `src/rtdsl/v4.py`.
3. **Numeric Bars Frozen**: Numeric bars are frozen in the contract module:
   - Correctness parity: `1.0` (100%)
   - Default representative speedup floor: `>= 1.20x`
   - Partner parity floor: `>= 0.98x`
   - Host materialization in hot path: `false`
4. **Candidate ID Isolation**:
   - CuPy candidate IDs are strictly defined (`cupy_grouped_reduction_device_columns_262144`, `cupy_grouped_reduction_device_columns_524288`, `cupy_segment_polygon_hitcount_prepared_scaling`, `cupy_hausdorff_witness_continuation`).
   - Numba candidate IDs are restricted to fixed continuation (`numba_component_union_current_v4_surface`) with arbitrary callbacks blocked.
5. **Fail-Closed Verification**: The planner catalog (`src/rtdsl/v4_operator_catalog.py`) correctly fails closed for unmeasured partners (such as CuPy requests returning `tier2_declared_unmeasured_partner` and pushdown recognizer returning `pushdown_fail_closed_unmeasured_partner`).
6. **Tests**: All 31 tests passed successfully under unittest, asserting correct regression logic.
7. **JSON Evidence**: The evidence JSON file `future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json` is syntactically valid and aligns perfectly with the code.

## Verification Questions Addressed

1. **Is Goal4648 complete enough to start Goal4649?** Yes. All contracts are defined and frozen in code, evidence JSON is generated, and tests pass.
2. **Are the CuPy device-array front-door contract and telemetry requirements concrete enough?** Yes, the CuPy contract enforces contiguous/column-major layout, caller-ownership, and defines required telemetry fields (correctness, speedup, parity, stream mode, output ownership, host materialization).
3. **Are the fixed Numba continuation boundaries concrete enough, with arbitrary callbacks still blocked?** Yes, `fixed_operator_only=True` and `arbitrary_callback_supported=False` are enforced by the contract.
4. **Are numeric bars frozen before measurement?** Yes, correctness parity (1.0), representative speedup floor (1.20), and partner parity floor (0.98) are codified.
5. **Does the code/test surface prevent partner migration or parity from becoming a fake V4 speed claim?** Yes, `partner_migration_counts_as_v4_speed_win=False` is hardcoded in the contracts and asserted in tests.
6. **Does current planner/catalog behavior still fail closed for unmeasured CuPy?** Yes, catalog planners return unmeasured status and fail closed for CuPy requests before certification.
7. **Are there any blocking issues before Goal4649 CuPy certification work starts?** None.

## Non-Authorization

This review does **NOT** authorize:
- public V4 release/tag wording;
- broad V4 speedup language;
- app-level V4-vs-V2.14/V3 claims;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- POD benchmark spending;
- treating partner migration or partner parity as V4 speed evidence.
