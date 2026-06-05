# Handoff: Claude Review For Goal3524 v2.8 vs v2.3 Same-Runner OptiX Results

Please perform an independent review of Goal3524 and write the review to:

`docs/reviews/goal3525_claude_review_goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md`

## Files To Read

- `docs/reports/goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md`
- `docs/reports/goal3524_pod_artifacts/goal3524_compact_results.json`
- `tests/goal3524_v2_8_vs_v2_3_same_runner_optix_results_test.py`
- `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_2026-06-05.md`
- `tests/goal3523_v2_8_vs_v2_3_same_contract_comparison_test.py`

## Review Questions

1. Does Goal3524 honestly distinguish the accepted v2.3 evidence commit
   `2a28365d0246d51f3e3322b546f8a68c58632db4` from the literal `v2.3` tag?
2. Does the compact artifact support the reported 11-row same-runner OptiX
   table on RTX A5000?
3. Does the report keep the Barnes-Hut regression visible instead of hiding it
   behind the positive geometric mean?
4. Are the weak-row rerun interpretations fair, especially Barnes-Hut,
   robot collision, RayDB count, contact manifold, and triangle counting?
5. Does the report avoid public speedup, release, whole-app, broad RT-core,
   true-zero-copy, package-install, and paper-reproduction claims?
6. Is this enough internal evidence for a same-runner OptiX slice, and what
   remains before any final v2.8 public comparison or release narrative?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict is `accept-with-boundary` unless you find a material
artifact/report/test mismatch.

Please lead with findings by severity, then verdict, then required-before-next
steps. Do not edit source files except the requested review file.
