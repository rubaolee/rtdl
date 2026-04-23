# Goal761 Pre-Cloud RTX Readiness

## Verdict

ACCEPT for pre-cloud preparation.

Cloud resources are unavailable until later, so this goal removes local ambiguity
before paid RTX timing. It does not claim any RTX speedup.

## What Changed

- `scripts/goal757_optix_fixed_radius_prepared_perf.py` now separates:
  - prepared OptiX native warm query timing;
  - Python count-row to app-summary postprocess timing;
  - validation/oracle timing;
  - optional `--skip-validation` for clean performance timing after correctness
    has been established.
- `scripts/goal756_db_prepared_session_perf.py` now reports a phase contract and
  scenario-provided prepare phases so DB app timing is not read as a single
  opaque number.
- `scripts/goal759_rtx_cloud_benchmark_manifest.py` now uses
  `--skip-validation` for the fixed-radius RTX benchmark entries, keeping native
  traversal/postprocess timing separate from correctness work.
- `scripts/goal761_rtx_cloud_run_all.py` adds one manifest-driven cloud runner
  that records git state, GPU metadata via `nvidia-smi`, Python version,
  command results, and the non-claim boundary.

## Cloud Command

After building the OptiX backend on an RTX-class machine, run:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --output-json docs/reports/goal761_rtx_cloud_run_all_summary.json
```

For a smoke check without running benchmarks:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --output-json docs/reports/goal761_rtx_cloud_run_all_dry_run_2026-04-22.json
```

## Candidate Scope

The runner executes the five Goal759 manifest entries:

| App | Path | Claim scope |
|---|---|---|
| `database_analytics` | `prepared_db_session_sales_risk` | prepared OptiX DB session behavior and interface-cost split |
| `database_analytics` | `prepared_db_session_regional_dashboard` | prepared OptiX DB session behavior and interface-cost split |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | prepared fixed-radius threshold summary traversal only |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | prepared fixed-radius core-flag traversal only |
| `robot_collision_screening` | `prepared_pose_flags` | prepared OptiX ray/triangle any-hit pose-flag summary |

Excluded apps remain excluded from RTX-core claims: Hausdorff, ANN, Barnes-Hut,
graph analytics, segment/polygon default paths, Apple-specific apps, and
HIPRT-specific apps.

## Verification

```text
python3 -m py_compile \
  scripts/goal756_db_prepared_session_perf.py \
  scripts/goal757_optix_fixed_radius_prepared_perf.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal761_rtx_cloud_run_all.py \
  tests/goal756_db_prepared_session_perf_test.py \
  tests/goal759_rtx_cloud_benchmark_manifest_test.py \
  tests/goal761_rtx_cloud_run_all_test.py
```

Passed.

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal756_db_prepared_session_perf_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal760_optix_robot_pose_flags_phase_profiler_test \
  tests.goal761_rtx_cloud_run_all_test

Ran 11 tests in 0.936s
OK
```

```text
git diff --check
```

Passed.

Dry-run artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal761_rtx_cloud_run_all_dry_run_2026-04-22.json`

## Boundary

This goal is pre-cloud tooling only. RTX speedup claims still require:

- an RTX-class GPU with RT cores, not GTX 1070;
- successful OptiX build from the tested commit;
- generated cloud JSON artifacts;
- review of phase timing and hardware metadata;
- independent release/performance review before public wording changes.
