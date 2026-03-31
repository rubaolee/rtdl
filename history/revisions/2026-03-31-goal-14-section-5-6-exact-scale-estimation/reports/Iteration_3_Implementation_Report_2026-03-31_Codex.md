# Iteration 3 Implementation Report

Date: `2026-03-31`
Author: `Codex`

## Goal Update

Goal 14 has been narrowed from a one-hour local profile target to a five-minute local profile target for both `lsi` and `pip`.

The report still preserves the exact-scale Section 5.6 estimate as context, but that is no longer the operational run target.

## What Changed

- updated Goal 14 plan:
  - [goal_14_section_5_6_exact_scale_plan.md](/Users/rl2025/rtdl_python_only/docs/goal_14_section_5_6_exact_scale_plan.md)
- regenerated Goal 14 estimation report:
  - [goal_14_section_5_6_exact_scale_estimation_2026-03-31.md](/Users/rl2025/rtdl_python_only/docs/reports/goal_14_section_5_6_exact_scale_estimation_2026-03-31.md)
- updated generator:
  - [generate_goal14_section56_estimation.py](/Users/rl2025/rtdl_python_only/scripts/generate_goal14_section56_estimation.py)
- updated Section 5.6 runner so `lsi` and `pip` can be benchmarked independently:
  - [section_5_6_scalability.py](/Users/rl2025/rtdl_python_only/src/rtdsl/section_5_6_scalability.py)
- added regression coverage for single-workload Section 5.6 runs:
  - [section_5_6_scalability_test.py](/Users/rl2025/rtdl_python_only/tests/section_5_6_scalability_test.py)
- restored the published Section 5.6 analogue report after an earlier smoke-run overwrite:
  - [section_5_6_scalability_report_2026-03-31.md](/Users/rl2025/rtdl_python_only/docs/reports/section_5_6_scalability_report_2026-03-31.md)

## New Recommended Profiles

- `lsi`
  - fixed `R = 100,000`
  - varying `S = 100,000, 200,000, 300,000, 400,000, 500,000`
  - estimated total query-only time: `4.34 min`

- `pip`
  - fixed `R = 100,000`
  - varying `S = 2,000, 4,000, 6,000, 8,000, 10,000`
  - estimated total query-only time: `3.36 min`

## Why The Code Change Was Needed

The current Section 5.6 runner previously forced `lsi` and `pip` to share the same `R` and `S` profile in one invocation. That made the new Goal 14 target impossible to execute honestly, because `lsi` and `pip` now require different scale-down profiles to fit the five-minute budget.

The runner now accepts workload selection so the two workloads can be executed and reported independently while still using the same experiment machinery.

## Verification

- `PYTHONPATH=src:. python3 scripts/generate_goal14_section56_estimation.py`
- `PYTHONPATH=src:. python3 -m unittest tests.section_5_6_scalability_test`
- `PYTHONPATH=src:. python3 -m rtdsl.section_5_6_scalability --output-dir build/section_5_6_scalability --build-polygons 800 --probe-series 160,320,480,640,800 --iterations 2 --warmup 1 --workloads lsi,pip`

## Review Ask

Gemini should review whether:

- the five-minute profile recommendations are technically consistent with the current calibration model,
- the workload-filter runner change is justified and scoped correctly,
- the Goal 14 documentation is now honest about exact-scale context versus operational target,
- and Goal 14 can be updated by consensus to the five-minute local-profile target.
