# Goal1128 Embree DB Compact-Summary Optimization

Date: 2026-04-29

This goal reduces local DB app interface overhead by making Embree prepared DB
datasets expose the same compact-summary wrapper surface already used by the
OptiX path. It does not add new RTX evidence, does not authorize public DB
speedup wording, and does not change the DB claim boundary.

## Change

`PreparedEmbreeDbDataset` now exposes:

- `conjunctive_scan_count(predicates)`
- `grouped_count_summary(query)`
- `grouped_sum_summary(query)`

The public DB apps already prefer these methods when available in
`--output-mode compact_summary`, so the change removes row materialization from
the Embree compact-summary app path without changing app-level APIs.

## Local Evidence

Command before/after:

`PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario all --copies 10000 --iterations 3 --output-mode compact_summary`

| Artifact | Median warm query sec | Row-materializing operations | Compact-summary operations | Status |
| --- | ---: | ---: | ---: | --- |
| `docs/reports/goal1128_db_local_embree_compact_summary_probe_2026-04-29.json` | `0.06926129199564457` | `6` | `0` | `needs_interface_tuning` |
| `docs/reports/goal1128_db_local_embree_compact_summary_after_2026-04-29.json` | `0.03890262497588992` | `0` | `6` | `needs_native_counter_artifact` |

Observed local warm-query improvement: `1.78x`.

## Interpretation

This is a real local interface-path improvement for the DB app, especially for
Embree and same-machine development. It does not by itself improve OptiX, and it
may make Embree baselines stronger. For NVIDIA public wording, the next useful
DB step remains an OptiX-specific fused compact-summary path or cleaner native
phase counters before spending cloud time.

## Verification

Focused DB compact-summary suite:

`PYTHONPATH=src:. python3 -m unittest tests.goal1128_embree_db_compact_summary_contract_test tests.goal850_optix_db_grouped_summary_fastpath_test tests.goal851_optix_db_sales_grouped_summary_fastpath_test tests.goal954_database_native_continuation_contract_test -v`

Result: 11 tests OK.

## Boundary

This goal improves a native CPU ray-tracing backend app path. It is not an RTX
RT-core public speedup claim and does not move `database_analytics` from
`public_wording_not_reviewed`.
