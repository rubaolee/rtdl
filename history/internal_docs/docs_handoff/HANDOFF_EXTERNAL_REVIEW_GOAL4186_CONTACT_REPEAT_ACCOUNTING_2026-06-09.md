# External Review Handoff: Goal4186 Contact Native Collect Repeat Accounting

Please perform an independent read-only review of Goal4186.

## Files To Inspect

- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `tests/goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test.py`
- `docs/reports/goal4185_short_row_stress_calibration_rtx4000ada_2026-06-09.md`
- `tests/goal4185_short_row_stress_calibration_test.py`
- `docs/reports/goal4186_contact_native_collect_repeat_accounting_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4186_contact_native_collect_repeat_accounting_rtx4000ada/contact_manifold_optix_grid64_repeat10000.stdout.json`
- `tests/goal4186_contact_native_collect_repeat_accounting_test.py`

## Review Questions

1. Does Goal4186 correctly fix the `native_collect_k` repeat-accounting gap found by Goal4185?
2. Does the old `native_collect_elapsed_sec` field remain compatibility-safe as a median-style value while the new aggregate fields expose claim-auditable repeated timing?
3. Does the RTX 4000 Ada artifact prove the contact row now has second-level aggregate timing without changing app semantics?
4. Does the implementation keep the native engine app-agnostic, using only `rtdl_optix_collect_k_bounded_i64` and keeping contact/collision interpretation outside RTDL?
5. Does the report avoid public speedup, release, broad acceleration, and zero-copy overclaims?

## Expected Output

Write one review file:

- Claude: `docs/reviews/goal4187_claude_review_goal4186_contact_repeat_accounting_2026-06-09.md`
- Gemini: `docs/reviews/goal4188_gemini_review_goal4186_contact_repeat_accounting_2026-06-09.md`

Use one of the established verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Suggested Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4186_contact_native_collect_repeat_accounting_test tests.goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test tests.goal4185_short_row_stress_calibration_test
```

This is a measurement-hardening review, not a release authorization review.
