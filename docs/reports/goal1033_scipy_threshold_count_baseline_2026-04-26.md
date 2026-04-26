# Goal1033 SciPy Threshold-Count Baseline

Date: 2026-04-26

## Verdict

Status: `implemented_no_speedup_claim`.

Goal1033 adds a real SciPy/cKDTree fixed-radius threshold-count baseline helper and wires it into the compact scalar outlier and DBSCAN app modes.

This supersedes the temporary Goal1032 classification for `outlier_detection` and `dbscan_clustering`: they are structurally `baseline_ready` again, but this Mac still has an optional SciPy dependency gap until SciPy is installed.

## Problem

Goal1032 found that these commands passed without SciPy installed:

```bash
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py --backend scipy --copies 20000 --output-mode density_count
PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py --backend scipy --copies 20000 --output-mode core_count
```

That meant they were using analytic/oracle scalar shortcuts, not real SciPy cKDTree baselines.

## Implementation

Added:

- `rtdsl.run_scipy_fixed_radius_count_threshold(...)`

The helper:

- loads SciPy cKDTree through the existing optional dependency path,
- counts fixed-radius candidates per query,
- applies the same `k_max` cap used by RTDL fixed-radius workloads,
- emits compact rows: `query_id`, `neighbor_count`, `threshold_reached`.

Updated apps:

- `examples/rtdl_outlier_detection_app.py`
  - `--backend scipy --output-mode density_count` now calls the SciPy threshold-count helper.
- `examples/rtdl_dbscan_clustering_app.py`
  - `--backend scipy --output-mode core_count` now calls the SciPy threshold-count helper.

Updated manifest:

- `outlier_detection`: restored to `baseline_ready`.
- `dbscan_clustering`: restored to `baseline_ready`.
- Current manifest counts: `baseline_ready: 4`, `baseline_partial: 13`.

## Local Environment Result

SciPy is not installed on this Mac:

```text
ModuleNotFoundError("No module named 'scipy'")
```

After the implementation, the outlier/DBSCAN SciPy compact commands correctly fail with:

```text
RuntimeError: SciPy is not installed; install scipy to run the cKDTree external baseline
```

The Goal1031 smoke runner classifies those as `optional_dependency_unavailable`, not as successful SciPy baselines.

## Tests

Passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests/goal1030_local_baseline_manifest_test.py \
  tests/goal1031_local_baseline_smoke_runner_test.py \
  tests/goal1033_scipy_threshold_count_baseline_test.py
```

## Boundary

This goal creates a real external-baseline path. It does not execute full-scale baselines and does not authorize speedup claims.

The next claim-gate step still requires installing SciPy or running on an environment with SciPy, executing same-scale baselines, and comparing against RTX artifacts under the public wording matrix.
