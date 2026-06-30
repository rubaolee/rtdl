# Handoff: External Review For Goal2972-2973 Toolchain Scope

Please perform an independent read-only review of the Goal2972 and Goal2973
v2.5 toolchain-scope work.

## Files To Read

- `docs/reports/goal2972_comparison_toolchain_scope_guard_2026-06-01.md`
- `docs/reports/goal2973_current_packet_with_comparison_toolchain_scope_2026-06-01.md`
- `scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2972_comparison_toolchain_scope_guard_test.py`
- `tests/goal2973_current_packet_with_comparison_toolchain_scope_test.py`
- `docs/reports/goal2973_current_packet_with_toolchain_scope_pod/goal2855_summary.json`
- `docs/reports/goal2973_current_packet_with_toolchain_scope_pod/goal2973_triage.json`

## Review Questions

1. Does Goal2972 correctly add a machine-readable comparison-toolchain scope
   guard without claiming compiler fairness?
2. Does Goal2973 correctly rerun the seven-app packet from clean source and
   preserve 7/7 pass, empty dirty artifacts, empty claim-boundary violations,
   zero performance targets, and `top_priority: null`?
3. Does the readiness gate now fail closed if the Goal2972 scope guard is lost
   or if compiler-fairness/public-speedup/release claims are flipped?
4. Is the boundary honest that this is same-commit/same-GPU/same-runner
   comparison evidence with visible toolchains, not a compiler-equivalence
   proof and not a second-architecture/multivendor check?
5. Are there any public-claim, release, app-specific-engine, or partner-choice
   leaks introduced by this change?

## Expected Output

Write a review file in `docs/reviews/`:

- Gemini: `docs/reviews/goal2974_gemini_review_goal2972_2973_toolchain_scope_2026-06-01.md`
- Claude: `docs/reviews/goal2975_claude_review_goal2972_2973_toolchain_scope_2026-06-01.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This review does not authorize v2.5 release, public speedup wording,
whole-app speedup wording, broad RT-core wording, true zero-copy wording,
package-install wording, paper reproduction, Triton preview auto-selection, or
app-specific native engine customization.
