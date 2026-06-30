# Goal740 DB Sales-Risk Prepared Dataset Reuse

Date: 2026-04-21

## Scope

Goal740 removes repeated native DB preparation from the sales-risk half of the
unified database app when the selected backend is Embree, OptiX, or Vulkan.

Changed file:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_sales_risk_screening.py`

The app still exposes the same public behavior. CPU paths still use the
portable reference/oracle runners. Native backends now prepare one bounded DB
dataset and reuse it for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Why This Matters

Before Goal740, `sales_risk_screening` called three separate native DB kernels.
Each native call could rebuild or repack native state. That made the unified DB
app more interface/preparation dominated than necessary.

The new native path aligns sales-risk behavior with the regional dashboard
path: one prepared native dataset, then repeated query calls.

## Correctness

Focused local validation:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal739_db_app_scaled_summary_test \
  tests.goal693_db_phase_profiler_test \
  -v
```

Result: `7 tests OK`.

The existing Goal739 Embree parity test covers the unified DB app after this
change and confirms scaled Embree summaries still match CPU reference.

## macOS Performance Evidence

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py \
  --apps database_analytics \
  --copies 1024 \
  --threads 1,auto \
  --warmups 1 \
  --min-sample-sec 0.5 \
  --max-repeats 8 \
  --output docs/reports/goal740_db_prepared_sales_embree_perf_macos_2026-04-21.json
```

Result file:

`/Users/rl2025/rtdl_python_only/docs/reports/goal740_db_prepared_sales_embree_perf_macos_2026-04-21.json`

Observed app-level wall-clock result on this Mac:

| Copies | CPU reference elapsed | Embree 1 thread median | Embree auto median | Auto vs 1 thread |
| --- | ---: | ---: | ---: | ---: |
| 1024 | 0.160 s | 0.177 s | 0.153 s | 1.16x |

Previous Goal739 result on the same app shape:

| Copies | CPU reference elapsed | Embree 1 thread median | Embree auto median | Auto vs 1 thread |
| --- | ---: | ---: | ---: | ---: |
| 1024 | 0.164 s | 0.281 s | 0.230 s | 1.22x |

The improvement is mostly from avoiding repeated native preparation in the
sales-risk scenario. It is not evidence that RTDL is a DBMS, SQL engine, or
general replacement for a columnar database.

## Honest Boundary

This is a real app-level DB optimization for native RTDL DB backends. The
bounded claim is:

- The unified DB app now reuses prepared native DB datasets in both DB
  scenarios.
- Embree auto-threaded app-level timing is now slightly faster than the CPU
  Python reference on this Mac at 1024 copies.
- The evidence is local and app-fixture-specific; Linux/PostgreSQL comparisons
  remain the broader DB performance gate.

Remaining bottlenecks:

- Python still constructs repeated fixture rows.
- Native rows are still materialized into Python dictionaries.
- The app still performs Python post-processing and JSON output.
- The sales-risk and regional-dashboard scenarios prepare separate datasets
  because they are separate app tables.
