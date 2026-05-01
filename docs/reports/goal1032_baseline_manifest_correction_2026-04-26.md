# Goal1032 Baseline Manifest Correction

Date: 2026-04-26

## Verdict

Status: `corrected_no_speedup_claim`.

This goal corrects the Goal1030/Goal1031 local baseline classification after a smoke-run audit found that two apparent SciPy commands were not real SciPy baselines.

## Problem Found

The original Goal1030 manifest marked four entries as `baseline_ready`:

- `outlier_detection`
- `dbscan_clustering`
- `service_coverage_gaps`
- `event_hotspot_screening`

During Goal1031 follow-up inspection, `python3 -c "import scipy"` showed SciPy is not installed locally. The service and hotspot SciPy commands failed as expected. However, the outlier and DBSCAN `--backend scipy` compact scalar commands still passed.

That pass was not real SciPy evidence. In the current app implementation, compact scalar modes:

- `outlier_detection --output-mode density_count`
- `dbscan_clustering --output-mode core_count`

use analytic/oracle scalar shortcuts for non-OptiX backends rather than a SciPy cKDTree baseline. Therefore those commands cannot be counted as SciPy baseline readiness.

## Correction Applied

`scripts/goal1030_local_baseline_manifest.py` now classifies:

- `outlier_detection`: `baseline_partial`
- `dbscan_clustering`: `baseline_partial`

Their SciPy commands were removed from the manifest. Their reasons now explicitly state that compact scalar SciPy is not a real cKDTree baseline and needs a dedicated extractor.

The current manifest status counts are:

- `baseline_ready`: `2`
- `baseline_partial`: `15`

The two remaining ready entries are:

- `service_coverage_gaps`
- `event_hotspot_screening`

Both still have optional SciPy dependency gaps on this local machine, because SciPy is not installed. CPU and Embree smoke commands pass.

## Smoke Runner Result After Correction

`docs/reports/goal1031_local_baseline_smoke_2026-04-26.md` was regenerated after correction.

Final status: `ok_with_optional_dependency_gaps`

Rows:

- `service_coverage_gaps`: CPU and Embree pass; SciPy optional dependency unavailable.
- `event_hotspot_screening`: CPU and Embree pass; SciPy optional dependency unavailable.

## Tests

Passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests/goal1030_local_baseline_manifest_test.py \
  tests/goal1031_local_baseline_smoke_runner_test.py
```

## Boundary

This correction does not authorize speedup claims. It tightens the baseline-readiness classification so future same-semantics comparison work does not accidentally treat oracle shortcuts as external SciPy baselines.

## Next Work

1. Add dedicated SciPy/cKDTree baseline extractors for outlier and DBSCAN compact scalar semantics, or document SciPy as unavailable for those compact claim gates.
2. Install SciPy locally or run SciPy baselines on a Linux environment where SciPy is available.
3. Keep CPU/Embree baseline extraction separate from external SciPy/PostGIS/PostgreSQL baseline extraction.
