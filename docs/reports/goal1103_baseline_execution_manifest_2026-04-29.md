# Goal1103 Baseline Execution Manifest

Date: 2026-04-29

Valid: `true`

Goal1103 is an execution manifest only. It does not run full baselines, does not start cloud, and does not authorize public RTX speedup claims.

Recommended next local action: `run_barnes_hut_validation_embree_then_goal1102_intake`

## Rows

| Order | Name | Risk | Current Mac recommendation | Expected artifact |
| ---: | --- | --- | --- | --- |
| 1 | `barnes_hut_validation_embree` | `moderate` | `safe_to_run` | `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json` |
| 2 | `facility_cpu_oracle` | `high` | `prefer_linux_or_windows_large_ram` | `docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_cpu_oracle_baseline.json` |
| 3 | `facility_embree` | `high` | `prefer_linux_or_windows_large_ram` | `docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_embree_baseline.json` |
| 4 | `barnes_hut_timing_embree` | `very_high` | `do_not_run_on_16gb_mac_without_user_approval` | `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json` |

## Commands

### barnes_hut_validation_embree

Small validated baseline row needed before interpreting the Barnes-Hut 20M timing row.

```bash
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario barnes_hut_node_coverage --backend embree --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json
```

### facility_cpu_oracle

Same-current-contract CPU oracle timing for the 10M-query facility row; 2.5M copies expands to 10M customers because the fixture has four customers per copy.

```bash
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario facility_service_coverage_recentered --backend cpu_oracle --copies 2500000 --iterations 3 --radius 1.0 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_cpu_oracle_baseline.json
```

### facility_embree

Same-current-contract Embree baseline for the 10M-query facility row; 2.5M copies expands to 10M customers and may allocate and scan large query arrays.

```bash
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario facility_service_coverage_recentered --backend embree --copies 2500000 --iterations 3 --radius 1.0 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_embree_baseline.json
```

### barnes_hut_timing_embree

Large timing-only baseline paired with the validated Barnes-Hut row; likely too memory-heavy for a 16 GB laptop.

```bash
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario barnes_hut_node_coverage --backend embree --body-count 20000000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json
```

## Boundary

Goal1103 is an execution manifest only. It does not run full baselines, does not start cloud, and does not authorize public RTX speedup claims.
