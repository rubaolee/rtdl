# Goal 464: External Review — v0.7 Linux Fresh-Checkout Validation

Date: 2026-04-16
Reviewer: Claude (external, independent)
Verdict: ACCEPT

## Scope Reviewed

- `docs/goal_464_v0_7_linux_fresh_checkout_validation.md`
- `docs/reports/goal464_v0_7_linux_fresh_checkout_validation_2026-04-16.md`
- `docs/reports/goal464_v0_7_linux_fresh_checkout_validation_review_2026-04-16.md`
- `docs/reports/goal464_linux_fresh_columnar_repeated_query_perf_2026-04-16.json`
- `docs/reports/goal464_linux_fresh_postgresql_index_audit_2026-04-16.json`
- `docs/reports/goal464_linux_fresh_rtdl_vs_postgresql_rebase_2026-04-16.json`
- `docs/reports/goal464_linux_fresh_app_demo_output_2026-04-16.json`
- `docs/reports/goal464_linux_fresh_kernel_demo_output_2026-04-16.json`

## Findings

### Acceptance Criteria

All eight acceptance criteria from the goal spec are met:

1. **rtdsl import**: confirmed on fresh checkout.
2. **Backend runtime probes**: Embree immediately available at v4.3.0; OptiX and Vulkan required
   fresh-checkout builds (`make build-optix`, `make build-vulkan`) and succeeded at v9.0.0 and
   v0.1.0 respectively. This is the correct fresh-checkout sequence.
3. **PostgreSQL + psycopg2**: PostgreSQL 16.13 accepting local socket connections, psycopg2 ok.
4. **Correctness tests**: 13 focused DB tests passed (skipped=2, expected); 29
   prepared-dataset/columnar-transfer tests passed.
5. **Demos**: both app-level and kernel-form demos ran to completion on Linux, selecting `embree`
   via auto backend. Both returned promo row_ids 3, 4, 5, 7 for the conjunctive scan — consistent
   across demos.
6. **Fresh performance artifacts**: three raw JSON files present and readable under `docs/reports/`.
7. **GPU caveat**: GTX 1070 has no RT cores — stated clearly and correctly. The report does not
   overstate the performance claim.
8. **Git index**: staged path count after validation = 0. No staging, commit, tag, push, merge, or
   release action performed.

### Data Cross-Checks

**Hash consistency**: All RTDL/PostgreSQL row hashes match across all three workloads
(`conjunctive_scan`, `grouped_count`, `grouped_sum`) and all three backends (Embree, OptiX,
Vulkan) in the columnar perf JSON and the rebase JSON (`hash_match: true` for all nine
combinations).

**Report table vs raw JSON**: Report summary figures agree with the underlying JSON values to the
precision shown. Spot-checked:
- `conjunctive_scan/embree`: prepare 0.983 s, median query 0.0183 s, total 1.165 s, PG median
  0.0383 s, query speedup 2.10x, total speedup 10.86x — all match JSON.
- `grouped_count/optix`: query speedup 4.19x, total speedup 11.51x — match JSON.
- `grouped_sum/vulkan`: query speedup 2.97x, total speedup 13.78x — match JSON.

**Rebase table vs rebase JSON**: Figures agree. Spot-checked:
- `conjunctive_scan/embree`: 0.98x query, 8.61x total — match JSON (0.9764x, 8.606x).
- `grouped_sum/optix`: 3.08x query, 9.84x total — match JSON (3.082x, 9.837x).

**PostgreSQL index audit**: Best-mode selections in the index audit JSON (conjunctive_scan:
composite query / covering total; grouped_count: composite/composite; grouped_sum: no_index query
/ composite total) are consistent with the main report and the rebase JSON source evidence.

**Cold-start spikes**: First-sample query times for OptiX (~0.45 s vs ~0.013 s steady) and Vulkan
(~0.36 s vs ~0.014 s steady) reflect expected GPU cold-start. The report correctly uses median,
which excludes the first sample.

### No Blocking Issues

The validation report is honest about scope (bounded kernels, no SQL engine, no DBMS, no RT-core
hardware acceleration on the test machine). The comparison boundary — RTDL prepared columnar total
vs PostgreSQL setup-plus-repeated-query — is clearly stated and consistently applied.

## Verdict

ACCEPT. Goal 464 is a valid Linux fresh-checkout validation of the v0.7 DB package. All acceptance
criteria are satisfied. The performance artifacts are internally consistent and the report does not
overstate its claims. No release movement is authorized by this goal.
