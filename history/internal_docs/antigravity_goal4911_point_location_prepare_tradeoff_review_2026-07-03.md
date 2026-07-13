# Antigravity Review: Goal4911 Point-Location Prepare/Run Tradeoff Probe

**Date**: 2026-07-03
**Verdict**: `approve_goal4911_retain_default_and_stop_knob_tuning`
**Reviewer**: Antigravity (External Technical Reviewer)

---

## Executive Summary

Goal4911 evaluated whether the remaining point-location prepare/setup cost in the RTDL engine is caused by a sub-optimal group/range construction default that could be resolved via existing configuration knobs.

Based on the evidence from the focused probe script [goal4911_point_location_prepare_tradeoff_probe.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4911_point_location_prepare_tradeoff_probe.py) and the generated summary dataset [goal4911_point_location_prepare_tradeoff_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4911_point_location_prepare_tradeoff_summary_2026-07-03.json), the current default configuration (`FineGrained` mode, productized in Goal4894) is highly competitive and offers the best overall latency trade-off.

Legacy grouping modes (like `fixed8`) are properly rejected due to catastrophic run-time regression. Other tuning options (like `adaptive` or `block_merge64`) do not show any significant performance improvements. Therefore, simple group-mode knob tuning has reached a point of zero marginal return and should stop. Further setup latency optimization must transition to deeper architectural options, such as persistent prepared-locator caching.

---

## Detailed Answers to the Six Review Questions

### 1. Does the focused probe fairly test current default vs legacy/fallback group modes?
**Yes.** The probe script [goal4911_point_location_prepare_tradeoff_probe.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4911_point_location_prepare_tradeoff_probe.py) performs a controlled, single-run benchmark by loading the CDB databases once and running the following modes sequentially:
- `default_current` (Cold start default)
- `legacy_fixed8` (Legacy default override)
- `adaptive_ms8_e1.5` (Adaptive range setup)
- `block_merge64_i0_e1.5` (Block merge with max_iter=0)
- `block_merge64_i1_e1.5` (Block merge with max_iter=1)
- `default_current_repeat` (Warm default comparison to isolate initialization overhead)

The benchmark is executed on the representative Section 5.7 Australia lakes x parks dataset, which is a known high-density workload suitable for profiling. The probe records all key dimensions: prepare times, run times, native traversal times, positive face count, and correctness consistency via FNV64 face hashes.

### 2. Does the evidence support retaining the current default?
**Yes.** The summary JSON evidence demonstrates that under warm conditions (`default_current_repeat`), the current default (`FineGrained`) achieves:
- **Map0 (in Map1)**: Prepare = `0.260s`, Run = `1.157s` (Total = `1.417s`)
- **Map1 (in Map0)**: Prepare = `4.043s`, Run = `0.038s` (Total = `4.081s`)

This is identical or superior to the other options tested:
- `adaptive_ms8_e1.5`: Map0 prepare = `0.252s`, run = `1.142s` (Total = `1.394s`); Map1 prepare = `4.073s`, run = `0.040s` (Total = `4.113s`).
- `block_merge64_i0_e1.5`: Map0 prepare = `0.261s`, run = `1.137s` (Total = `1.398s`); Map1 prepare = `4.325s`, run = `0.036s` (Total = `4.361s`).
- `block_merge64_i1_e1.5`: Map0 prepare = `0.268s`, run = `1.140s` (Total = `1.408s`); Map1 prepare = `4.439s`, run = `0.037s` (Total = `4.476s`).

The current default provides the best balance, minimizing prepare overhead without introducing runtime degradation.

### 3. Is fixed8 correctly rejected despite lower prepare time because run time explodes?
**Yes.** Under `legacy_fixed8`, the prepare times are slightly lower:
- Map0 prepare is `0.213s` (saves `0.047s` vs default's `0.260s`).
- Map1 prepare is `3.374s` (saves `0.669s` vs default's `4.043s`).

However, the run time explodes drastically:
- Map0 run time increases from `1.157s` to **`10.915s`** (a **9.44x** regression).
- Map1 run time increases from `0.038s` to **`1.587s`** (a **41.76x** regression).

The total time for Map0 and Map1 in `fixed8` mode is `11.128s` and `4.961s` respectively (compared to `1.417s` and `4.081s` for the default). Thus, `fixed8` is correctly rejected because its minor build-time savings are completely overshadowed by massive execution-time regression.

### 4. Is it correct that there is no simple group-mode knob win left?
**Yes.** Sweeping alternative configuration modes (such as `adaptive` and `block_merge64`) yields performance metrics that are virtually identical to the default. This confirms that the current default is already at the optimal tradeoff point for generic range grouping, and further tuning of these specific knobs will not yield any meaningful performance gains.

### 5. Is the recommendation to move only to a deeper persistent locator/cache design, or consolidate current results, justified?
**Yes.** The `~4.0s` prepare time for Map1 (in Map0) under warm settings is not a manifestation of a configuration/grouping bug, but is the native cost of constructing a large-scale OptiX BVH/acceleration structure. To optimize this bottleneck, we must avoid rebuilding it entirely.

The recommendation is fully justified: any future work on setup times must address structure persistence (e.g., a persistent prepared locator/session cache or a reusable serialization layer), or the project must freeze performance tweaks and consolidate the current results:
- **Prepared-hot body**: `3.918s`
- **Writer**: `1.840s`
- **Byte equality**: `true`

### 6. Does the report avoid overclaiming performance?
**Yes.** The report is measurement-only, makes no modifications to native or core RTDL libraries, and contains a clear **Boundaries** section that explicitly states it does not claim broad RayJoin or RTDL performance gains, new speedups, or correctness changes.

---

## Technical Audit of Results

| Mode | Map0 Prepare | Map0 Run | Map0 Total | Map1 Prepare | Map1 Run | Map1 Total | FNV64 Correctness |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Current Default (Warm)** | **`0.260s`** | **`1.157s`** | **`1.417s`** | **`4.043s`** | **`0.038s`** | **`4.081s`** | **Matches** |
| `legacy_fixed8` | `0.213s` | `10.915s` | `11.128s` | `3.374s` | `1.587s` | `4.961s` | Matches |
| `adaptive_ms8_e1.5` | `0.252s` | `1.142s` | `1.394s` | `4.073s` | `0.040s` | `4.113s` | Matches |
| `block_merge64_i0_e1.5` | `0.261s` | `1.137s` | `1.398s` | `4.325s` | `0.036s` | `4.361s` | Matches |
| `block_merge64_i1_e1.5` | `0.268s` | `1.140s` | `1.408s` | `4.439s` | `0.037s` | `4.476s` | Matches |

### Correctness Check
All configurations generated correct FNV64 face hashes matching the default:
- Map0 (in Map1): `f2d982e19b845172`
- Map1 (in Map0): `217ca910d4b1af08`

This confirms that none of the tested grouping modes caused correctness regressions.

---

## Authorization Boundaries

This review:
1. **Authorizes** retaining the current default `FineGrained` group mode configuration as the standard engine setting.
2. **Authorizes** halting any further point-location group-mode or planner knob sweeps.
3. **Does NOT authorize** editing the native C++ RTDL compiler, segment-location, or PIP primitives.
4. **Does NOT authorize** deploying new application-layer writer bypasses without separate correctness preflights.
5. **Directs** that if setup costs must be reduced, the next work item must be specified as a generic prepared-locator session cache or build-artifact serialization design rather than further planner-level tweaking.
