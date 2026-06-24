# Claude Review Record: V4.0 Release Candidate

Date: 2026-06-24

Reviewer: Claude Sonnet 4.6

Raw output: `future/v4/reviews/claude_v4_0_release_candidate_review_2026-06-24.raw.md`

## Verdict

`approve_with_required_amendments`

This is not release authorization.

## Required Amendments

1. Enumerate and link `v4_review_debt_open` so it is resolvable.
2. Establish a clean-commit rerun protocol instead of relying only on one POD
   snapshot.
3. Document that closest-hit grouped argmin does not carry a public
   `true_zero_copy_authorized` claim.
4. Harden `partner="cupy"` planning so an unmeasured partner cannot look like a
   routable V4.0 API surface.
5. Extend the catalog regression gate to reject per-example payloads that emit
   forbidden CuPy performance, embedding/C-ABI, or non-Python host binding
   claim flags.

## Amendments Applied In This Turn

- Review debt tracker: `future/v4/reviews/review_debt_v4_0_release_candidate_2026-06-24.md`
- Rerun protocol: `future/v4/release_rerun_protocol_2026-06-24.md`
- Grouped-argmin boundary docs: `future/v4/ray_triangle_device_array_frontdoor.md`
- CuPy planner hardening: `src/rtdsl/v4_operator_catalog.py`
- Per-example forbidden-claim checks: `scripts/v4_catalog_regression_gate.py`

## Remaining Release Blockers

- release decision record not obtained
- V4 review debt must be closed or explicitly waived in the release decision
  record

## Non-Authorization

This review record does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
