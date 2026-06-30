# Handoff: Claude Review For Goal3520 v2.8 Claim-Boundary And Stale-Doc Audit

Please perform an independent read-only review of Goal3520.

## Files To Inspect

- `docs/reports/goal3520_v2_8_claim_boundary_and_stale_doc_audit_2026-06-05.md`
- `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py`
- `docs/research/future_version_to_do_list.md`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- Active learner Markdown surface: `README.md`, `docs/README.md`, `docs/learn/*.md`, `docs/tutorials/*.md`, and `examples/v2_0/research_benchmarks/**/README.md`

## Suggested Checks

Run, or manually equivalent-check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3520_v2_8_claim_boundary_stale_audit_test tests.goal3519_v2_8_learner_docs_cleanup_test tests.goal3518_v2_8_benchmark_matrix_test
rg -n "v2\.x|release package|full rayjoin reproduction is authorized|rtdl beats rayjoin is authorized|true zero-copy authorized|public speedup claim authorized" README.md docs/README.md docs/learn docs/tutorials examples/v2_0/research_benchmarks docs/research/future_version_to_do_list.md
```

The second command should have no output. Negative boundary language such as "not authorized" is allowed, but positive authorization wording is not.

## Questions

1. Does Goal3520 correctly close stale user-facing `v2.x` / `v2.5` wording in visible CLI/docstring paths without renaming compatibility/protocol helpers unsafely?
2. Does the active learner Markdown surface remain v2.8-current and free of release-package, broad-speedup, true-zero-copy, full RayJoin/paper-reproduction, hidden-partner-selection, or app-specific-native-engine overclaims?
3. Are the remaining `v2_5` / `v2_6` Python names legitimately quarantined as compatibility/protocol debt, with enough future-work documentation to defer rather than block?
4. Is `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py` a meaningful fail-closed guard, or does it miss a material stale-doc / claim-boundary risk?
5. Does this goal authorize release or public claims in any way? It should not.

## Required Output

Write your review to:

`docs/reviews/goal3520_claude_review_v2_8_claim_boundary_stale_audit_2026-06-05.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
