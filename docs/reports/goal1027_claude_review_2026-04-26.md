**ACCEPT**

All four criteria pass:

1. **Stale v0.9.5 expectation updated** — test method renamed to `test_history_public_indexes_include_current_v096_and_v095_release_rows`; now asserts `"through the \`v0.9.6\` release"`, `Goal1023`, and v0.9.6 dashboard row.

2. **v0.9.5 historical rows preserved** — test still asserts `"- \`v0.9.5\`"`, `Goal647`/`Goal646`/`Goal645` COMPLETE_HISTORY entries, and `| v0.9.5 | 2026-04-20 | accepted |` in revision_dashboard.

3. **v0.9 matrix current-boundary link updated** — `support_matrix.md` line 10 reads `../v0_9_6/support_matrix.md`; `test_historical_v09_matrix_points_to_current_release_boundary` asserts that exact string.

4. **No release/cloud/speedup claims** — report boundary section explicitly states "does not run cloud, tag, release, or authorize public RTX speedup claims"; `support_matrix.md` retains its existing non-claim language (no AMD GPU, no RT-core speedup, etc.).
