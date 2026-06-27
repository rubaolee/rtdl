# Goal1034 SciPy-Enabled Local Baseline Smoke

Date: 2026-04-26

## Verdict

Status: `smoke_pass_no_speedup_claim`.

After Goal1033 added a real SciPy/cKDTree threshold-count helper, a local venv was created at `.venv-rtdl-scipy` and SciPy was installed there. The system/Homebrew Python environment was not modified.

The Goal1031 smoke runner was then executed through the venv.

## Command

```bash
. .venv-rtdl-scipy/bin/activate && \
PYTHONPATH=src:. python scripts/goal1031_local_baseline_smoke_runner.py \
  --mode smoke \
  --timeout-sec 60 \
  --output-json docs/reports/goal1034_local_baseline_smoke_with_scipy_2026-04-26.json \
  --output-md docs/reports/goal1034_local_baseline_smoke_with_scipy_2026-04-26.md
```

## Result

Final status: `ok`

Optional dependency gaps: `0`

| App | CPU | Embree | SciPy | Notes |
|---|---|---|---|---|
| `outlier_detection` | `ok` | `ok` | `ok` | SciPy summary mode reports `scipy_ckdtree_threshold_count`. |
| `dbscan_clustering` | `ok` | `ok` | `ok` | SciPy summary mode reports `scipy_ckdtree_threshold_count`. |
| `service_coverage_gaps` | `ok` | `ok` | `ok` | SciPy cKDTree path now available in venv. |
| `event_hotspot_screening` | `ok` | `ok` | `ok` | SciPy cKDTree path now available in venv. |

## Boundary

This is a smoke-scale run with `--copies` rewritten to `50`. It checks command health and dependency readiness only. It is not same-scale baseline evidence and does not authorize speedup claims.

The next step is full-scale or scale-ramped same-semantics baseline timing, still separated from public claim authorization.
