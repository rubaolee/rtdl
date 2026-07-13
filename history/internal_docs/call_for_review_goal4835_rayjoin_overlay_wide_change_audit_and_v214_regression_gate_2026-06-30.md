# Call For Review: Goal4835 RayJoin Overlay Wide-Change Audit and v2.14 Regression Gate

Date: 2026-06-30

## Requested Verdict Labels

Choose one:

- `approve_goal4835_focused_gate_passed_but_v214_wide_gate_not_green`
- `request_amendments_goal4835`
- `fail_redo_goal4835`

## Files To Review

- `history/internal_docs/goal4835_rayjoin_overlay_wide_change_audit_and_v214_regression_gate_2026-06-30.md`
- `history/internal_docs/goal4833_review_ingest_goal4834_compliance_note_2026-06-30.md`
- `history/internal_docs/goal4834_completion_report_2026-06-30.md`
- `history/internal_docs/antigravity_goal4834_patched_author_sos_contract_review_2026-06-30.md`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/rayjoin_overlay.py`
- `tests/goal4834_rayjoin_sos_synthetic_contract_test.py`
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`

## Review Questions

1. Does Goal4835 correctly separate the approved directed point-location SoS
   core repair from the broader `rayjoin_overlay.py` changes?

2. Is the classification of per-map midpoint face storage as a product
   data-model fix still justified?

3. Is the classification of non-finite midpoint filtering as a general native
   point-location input-invariant repair justified, rather than a hidden
   RayJoin-only workaround?

4. Are scaled coordinate materialization and rational midpoint projection
   correctly treated as contract-alignment candidates, not as proof of full
   Section 5.7 reproduction?

5. Is the current intersection sorting change still only partially approved /
   not release-complete until a chain-30138 or equivalent minimal reproducer is
   built?

6. Does the RayJoin-focused gate result (`38 tests OK`) support the local
   correctness-repair line?

7. Does the v2.14-wide matrix result (`264 tests`, `13 errors`, `16 skipped`)
   correctly block any "full product regression green" claim?

8. Are the two observed wide-matrix failure classes correctly described as
   stale `examples.internal` imports and Windows Embree compile/link failures,
   rather than proof that the RayJoin SoS comparator is wrong?

9. Are the proposed next goals (regression-harness cleanup, Linux/OptiX
   confirmation, chain-30138 minimal reproducer, deterministic County x Zipcode
   comparison) the right continuation?

10. Should Goal4835 close with
    `completed_rayjoin_focused_gate_passed__wide_change_audit_done__v214_wide_regression_not_green`?

## Non-Authorization

This review must not authorize:

- broad Section 5.7 reproduction claims;
- full eight-pair claims;
- performance win claims;
- public release wording;
- Embree conclusions;
- promotion of `rayjoin_overlay.py` sorting changes as proven without a
  minimal reproducer;
- treating the focused RayJoin gate as a full v2.14 product regression gate.
