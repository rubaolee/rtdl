# Goal756 Prepared DB App Session Report

## Verdict

ACCEPT.

Goal756 adds a public prepared-session mode for the unified database analytics app so applications can prepare RTDL database datasets once and then run repeated warm queries without rebuilding the native prepared representation each time.

## Files Changed

- `/Users/rl2025/rtdl_python_only/examples/rtdl_v0_7_db_app_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_sales_risk_screening.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_database_analytics_app.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal756_db_prepared_session_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal756_prepared_db_app_session_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal756_db_prepared_session_perf_test.py`

## Consensus

- Codex plan and implementation: accept.
- Gemini Flash plan review: `ACCEPT`, no blockers, at `/Users/rl2025/rtdl_python_only/docs/reports/goal756_gemini_flash_plan_review_2026-04-22.md`.
- Windows Codex review request was posted to `/Volumes/192.168.1.20/extra-1/rtdl_codex_bridge/to_windows/GOAL756_WINDOWS_REVIEW_PREPARED_DB_APP_SESSION_PLAN.md`; no reply was present at report time.

## User Surface

Python:

```python
from examples import rtdl_database_analytics_app as db_app

with db_app.prepare_session("optix", scenario="sales_risk", copies=20000) as session:
    first = session.run(output_mode="summary")
    second = session.run(output_mode="summary")
```

CLI:

```bash
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py \
  --backend optix \
  --scenario sales_risk \
  --copies 20000 \
  --execution-mode prepared_session \
  --session-iterations 5 \
  --output-mode summary
```

Default CLI behavior remains one-shot mode.

## Correctness Evidence

macOS focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal756_prepared_db_app_session_test \
  tests.goal756_db_prepared_session_perf_test \
  tests.goal693_db_phase_profiler_test \
  tests.goal692_optix_app_correctness_transparency_test

Ran 17 tests in 3.017s
OK
```

Linux focused tests with native OptiX and Vulkan libraries rebuilt:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so \
python3 -m unittest -v \
  tests.goal756_prepared_db_app_session_test \
  tests.goal756_db_prepared_session_perf_test \
  tests.goal693_db_phase_profiler_test \
  tests.goal692_optix_app_correctness_transparency_test

Ran 17 tests in 5.822s
OK
```

## Linux Scaled Performance Evidence

Host: `lestat-lx1`, GTX 1070. This is backend behavior evidence only; the GTX 1070 has no RTX RT cores and must not be used as RTX RT-core speedup evidence.

Artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal756_db_prepared_session_sales_risk_linux_gtx1070_2026-04-22.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal756_db_prepared_session_regional_dashboard_linux_gtx1070_2026-04-22.json`

Configuration:

- `copies=20000`
- `iterations=5`
- backends: CPU, Embree, OptiX, Vulkan
- strict mode enabled

### Sales Risk

| Backend | One-Shot Total (s) | Prepare Once (s) | Warm Query Median (s) | One-Shot / Warm Median |
|---|---:|---:|---:|---:|
| CPU | 4.802544 | 0.027679 | 4.704218 | 1.02x |
| Embree | 0.698381 | 0.550223 | 0.108312 | 6.45x |
| OptiX | 1.343120 | 0.542440 | 0.204963 | 6.55x |
| Vulkan | 1.187405 | 0.543438 | 0.173390 | 6.85x |

### Regional Dashboard

| Backend | One-Shot Total (s) | Prepare Once (s) | Warm Query Median (s) | One-Shot / Warm Median |
|---|---:|---:|---:|---:|
| CPU Reference | 0.606709 | 0.045484 | 0.534817 | 1.13x |
| Embree | 0.921544 | 0.722948 | 0.155692 | 5.92x |
| OptiX | 1.580235 | 0.700288 | 0.313181 | 5.05x |
| Vulkan | 1.467845 | 0.698816 | 0.301709 | 4.87x |

## Main Finding

Prepared sessions make the DB app performance story clearer and more honest. The one-shot path includes app data expansion plus native dataset preparation, while the prepared-session path exposes the repeated-query behavior that applications actually want for dashboard and screening workloads.

For both DB scenarios, the RT backends show large one-shot-to-warm-query improvements once preparation is reused. Embree is fastest on this GTX 1070 Linux host for these two scaled DB scenarios, while OptiX and Vulkan show the same qualitative session benefit but remain limited by this non-RTX GPU and current implementation overhead.

## Boundaries

- This is not a DBMS feature. RTDL still does not provide SQL planning, indexes, transactions, durability, or storage management.
- This does not claim RTX RT-core acceleration because the Linux evidence came from GTX 1070.
- This goal does not rewrite native DB kernels. It fixes the measured Goal755 bottleneck by exposing prepared app sessions.
- Large output arrays are compacted in the profiler JSON to keep performance artifacts focused on counts, samples, and timing.
