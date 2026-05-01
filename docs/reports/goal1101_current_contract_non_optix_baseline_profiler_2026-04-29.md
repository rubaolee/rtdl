# Goal1101 Current-Contract Non-OptiX Baseline Profiler

Date: 2026-04-29

## Scope

Goal1101 adds a replayable profiler for the same-current-contract non-OptiX baselines required by Goal1100.

It covers:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`
- `barnes_hut_force_app / node_coverage_prepared_rich`

## Added Surface

| File | Purpose |
| --- | --- |
| `scripts/goal1101_current_contract_non_optix_baseline_profiler.py` | Emits JSON baseline artifacts for `cpu_oracle` and `embree` current-contract runs. |
| `scripts/goal1101_current_contract_non_optix_baseline_runner.sh` | Replays the four intended claim-review baseline rows. |
| `tests/goal1101_current_contract_non_optix_baseline_profiler_test.py` | Checks CPU-oracle output, Embree prepared-threshold API usage, CLI output, and no-claim boundary. |

## Runner Rows

| Row | Backend | Contract |
| --- | --- | --- |
| Facility recentered CPU oracle | `cpu_oracle` | 2.5M copies, 10M queries, radius 1.0 |
| Facility recentered Embree | `embree` | 2.5M copies, 10M queries, radius 1.0 |
| Barnes-Hut validation | `embree` | 4,096 bodies, depth 8, radius 0.1, threshold 4 |
| Barnes-Hut timing | `embree` | 20M bodies, depth 8, radius 0.1, threshold 4, timing-only |

## Local Smoke

Small local smoke runs passed on macOS:

| Smoke | Result |
| --- | --- |
| Facility recentered Embree, 1 copy | `matches_oracle: true` |
| Barnes-Hut Embree, 8 bodies | `matches_oracle: true` |
| Facility recentered CPU oracle, 1 copy | `matches_oracle: true` |

## Boundary

Goal1101 does not run OptiX and does not authorize public RTX speedup claims. Its output is baseline evidence for later intake and 2+ AI review. Public wording remains blocked until the generated baseline artifacts are reviewed against the current RTX A5000 artifacts.
