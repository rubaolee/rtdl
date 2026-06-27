# Antigravity Re-Review: V4 Goal4648 Partner Promotion Contract (Post-Fix)

Date: 2026-06-25
Verdict: `accept_goal4648_complete`

## Rationale

This re-review verifies the implementation of RTDL V4 Goal4648 following the resolution of the fail-open allowlist bug in the partner promotion verification logic.

### 1. Fail-Open Allowlist Fix Verification
The function `v4_partner_promotion_candidate_allowed` in [v4_partner_promotion_contract.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_partner_promotion_contract.py) has been successfully fixed with an explicit partner check:
```python
    normalized_partner = str(partner).strip().lower()
    if normalized_partner not in {"cupy", "numba"}:
        return False
```
This prevents unauthorized partners (such as `torch` or arbitrary unknown strings) from incorrectly matching candidate IDs inside the loop over all contracts and returning `True`.

### 2. Test Coverage & Execution
Unit tests in [v4_goal4648_partner_promotion_contract_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4648_partner_promotion_contract_test.py) successfully cover the fail-closed behavior:
- Explicit checks that `torch` and `unknown` return `False` for candidate allowlist validation.
- Asserting that a bare Numba contract query without `fixed=True` raises `ValueError`.
- Asserting that Barnes-Hut is not an allowed candidate.

The test suite ran successfully (31 tests, OK):
```text
Ran 31 tests in 1.328s
OK
```

### 3. Claim Boundaries and Frozen Bars
- `partner_parity_counts_as_v4_speed_win` is set to `False` in the code, JSON evidence, and asserted across tests.
- `partner_migration_counts_as_v4_speed_win` is set to `False` in both contract instances, JSON evidence, and asserted across tests.
- All other non-authorization boundaries (`release_claim_authorized`, `broad_v4_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `cupy_performance_claim_authorized`, `arbitrary_numba_callback_claim_authorized`) are confirmed `False`.

### 4. JSON Evidence Alignment
The evidence file [v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json) is aligned with the source code constants and successfully reflects the test results.

---

## Verdict Summary
The verdict is **`accept_goal4648_complete`**. The contract is code-visible, the fail-open bug is fixed and verified, and all non-authorization flags are locked down. Goal4649 (CuPy certification) may proceed.
