# Goal1105 Linux Current-Contract Baseline Execution

Date: 2026-04-29

## Scope

Goal1105 runs the Goal1101 current-contract non-OptiX baseline rows on the available Linux host `lx1` (`lestat@192.168.1.20`) and re-runs Goal1102 intake.

This is baseline evidence only. It does not authorize public RTX speedup claims.

## Environment

| Field | Value |
| --- | --- |
| Host | `lx1` |
| Platform | `Linux-6.17.0-20-generic-x86_64-with-glibc2.39` |
| Python | `3.12.3` |
| Embree | `4.3.0` |
| GEOS | available via system `libgeos_c` |
| Source commit | `cf22fb302bbd85afaa8ea6f9e2da26d278313635` |
| Remote checkout | `/tmp/rtdl_goal1105_baselines` |

The checkout was staged with `git archive HEAD` and `.rtdl_source_commit`, then verified with:

```bash
make build-embree
PYTHONPATH=src:. python3 -m unittest tests.goal1101_current_contract_non_optix_baseline_profiler_test tests.goal1102_current_contract_baseline_intake_test
```

The archive-mode focused tests passed: `10 tests OK, skipped=1`. The skip is expected because one test requires git metadata and the archive checkout intentionally has no `.git`.

## Completed Baselines

| Row | Backend | Status | Query count | Median native query (s) |
| --- | --- | --- | ---: | ---: |
| `barnes_hut_depth8_4096_embree_validation_baseline.json` | `embree` | `matches_oracle: true` | `4096` | `0.010342210996896029` |
| `facility_recentered_2_5m_cpu_oracle_baseline.json` | `cpu_oracle` | `matches_oracle: true` | `10000000` | `8.996512651909143` |
| `facility_recentered_2_5m_embree_baseline.json` | `embree` | `matches_oracle: true` | `10000000` | `29.806780943996273` |

Goal1102 intake after copyback:

- `ok_count: 3`
- `missing_count: 1`
- `blocked_count: 0`
- `overall_status: waiting_for_baseline_artifacts`
- `artifact_set_complete: false`
- `public_speedup_claim_authorized_count: 0`

## Failed Baseline Row

The Barnes-Hut depth-8 20M Embree timing row did not complete on this Linux host:

```bash
RTDL_SOURCE_COMMIT=$(cat .rtdl_source_commit) PYTHONPATH=src:. /usr/bin/time -v python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario barnes_hut_node_coverage --backend embree --body-count 20000000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json
```

Result:

- terminated by signal 9;
- elapsed wall time `7:08.77`;
- max RSS `15180436` KB;
- major page faults `691157`;
- no output artifact was written.

This is a host memory-boundary result. The row remains missing in Goal1102 intake.

## Interpretation

The Facility baselines are valid but also show why claim review must be separate and conservative:

- The direct CPU oracle is faster than the current Embree threshold path for this tiny build-set contract (`8.997 s` vs `29.807 s` median native query).
- Therefore the Facility RTX artifact cannot use Embree as the fastest non-OptiX baseline for a positive speedup claim without further review.

The Barnes-Hut validation row is valid, but the needed 20M same-contract Embree timing row is not available on this 16 GB Linux host. The next attempt needs either:

- a larger-memory Linux/Windows host;
- a chunked/resumable Barnes-Hut baseline design;
- or a smaller claim contract that has matching RTX and non-OptiX timing rows.

## Copied Evidence

- `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json`
- `docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_cpu_oracle_baseline.json`
- `docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_embree_baseline.json`
- `docs/reports/linux_goal1105_logs/barnes_hut_4096_embree_validation.log`
- `docs/reports/linux_goal1105_logs/facility_cpu_oracle.log`
- `docs/reports/linux_goal1105_logs/facility_embree.log`
- `docs/reports/linux_goal1105_logs/barnes_hut_20m_embree_timing.log`
- refreshed `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json`
- refreshed `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md`

## Boundary

Goal1105 does not authorize release, public README/front-page wording, or public RTX speedup claims. The baseline set remains incomplete because the Barnes-Hut 20M Embree timing row is missing.
