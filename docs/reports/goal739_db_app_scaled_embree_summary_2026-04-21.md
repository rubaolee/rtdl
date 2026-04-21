# Goal739 DB App Scaled Embree Summary

Date: 2026-04-21

## Scope

Goal739 makes the public database analytics app scalable for Embree app-level
characterization without changing the default tutorial behavior.

Changed files:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_v0_7_db_app_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_sales_risk_screening.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_database_analytics_app.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal714_embree_app_thread_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal739_db_app_scaled_summary_test.py`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`

## User-Facing Change

Default commands remain unchanged and still emit full beginner-friendly JSON:

```bash
PYTHONPATH=src:. python3 examples/rtdl_database_analytics_app.py --backend cpu_python_reference
```

New scalable summary mode:

```bash
PYTHONPATH=src:. python3 examples/rtdl_database_analytics_app.py \
  --backend embree \
  --copies 1024 \
  --output-mode summary
```

`--copies N` repeats the deterministic order tables with unique row IDs.
`--output-mode summary` keeps aggregate app answers and omits full scan/grouped
row lists from the JSON payload.

## Correctness

Focused local validation:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal739_db_app_scaled_summary_test \
  tests.goal693_db_phase_profiler_test \
  tests.goal686_app_catalog_cleanup_test \
  -v
```

Result: `12 tests OK`.

The new Goal739 tests validate:

- regional dashboard scaled summary math;
- sales-risk scaled summary math;
- default full-output behavior remains present;
- Embree scaled summaries match CPU reference when Embree is available.

## macOS Embree Evidence

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py \
  --apps database_analytics \
  --copies 1024 \
  --threads 1,auto \
  --warmups 1 \
  --min-sample-sec 0.5 \
  --max-repeats 8 \
  --output docs/reports/goal739_db_embree_scaled_app_perf_macos_2026-04-21.json
```

Result file:

`/Users/rl2025/rtdl_python_only/docs/reports/goal739_db_embree_scaled_app_perf_macos_2026-04-21.json`

Observed app-level wall-clock result on this Mac:

| Copies | CPU reference elapsed | Embree 1 thread median | Embree auto median | Auto vs 1 thread |
| --- | ---: | ---: | ---: | ---: |
| 1024 | 0.164 s | 0.281 s | 0.230 s | 1.22x |

## Honest Boundary

This improves the app surface and makes DB app measurements repeatable at a
larger fixture scale. It does not make the DB app a strong Embree speedup
claim. On this Mac, Embree auto-threading is faster than Embree single-thread
for the scaled app, but the CPU reference remains faster at this size.

The likely bottlenecks remain:

- repeated native dataset preparation;
- row materialization for scan and grouped aggregate results;
- app-level Python post-processing;
- duplicated execution of regional dashboard and sales-risk scenarios.

The valid claim is:

- the public DB app now supports scalable deterministic fixtures;
- Embree scaled summaries match CPU reference summaries;
- Embree auto-threading shows useful internal improvement over Embree
  single-thread, but further DB-native/interface optimization is needed before
  claiming app-level performance leadership.
