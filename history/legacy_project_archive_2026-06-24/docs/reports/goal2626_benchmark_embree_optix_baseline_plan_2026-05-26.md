# Goal2626 Benchmark App Embree vs OptiX Baseline Plan

## Purpose

Goal2626 establishes an internal per-app baseline across promoted benchmark apps
before the next runtime direction: using Triton or Numba as a partner path
without adding new C++ for app-level continuation work.

This is not a public speedup-claim artifact. It is a controlled engineering
baseline that answers:

- where Embree and OptiX already have same-contract comparable rows;
- where the promoted app is currently OptiX-only or lacks an Embree front door;
- which cases still depend on app-internal timings versus process-wall fallback;
- what the next partner path must beat or preserve.

## Runner

The runner is:

```bash
PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --case-repeat 3 \
  --build-native
```

Expected outputs:

- `docs/reports/goal2626_benchmark_embree_optix_baseline_pod/summary.json`
- `docs/reports/goal2626_benchmark_embree_optix_baseline_pod/summary.md`

Use `--scale quick --dry-run` for command validation only. Use `--scale large`
only when the pod budget allows long-running cases.

## Benchmark App Coverage

The manifest covers the 10 promoted benchmark apps from
`docs/application_catalog.md`:

1. Hausdorff / X-HD-style
2. Spatial RayJoin-style
3. RT-DBSCAN-style
4. Robot collision
5. RayDB-style grouped aggregate
6. Barnes-Hut / RT-BarnesHut-style
7. LibRTS-style spatial index
8. RTNN neighbor search
9. Triangle counting
10. Bounded contact witness / contact-manifold

Unsupported rows are intentionally preserved in the summary. They are coverage
gaps, not failed performance results.

## Interpretation Rules

- Compare only rows with the same `app_id` and `comparison_group`.
- Treat `process_wall_median_sec` as a weak metric because it includes Python
  startup and import time.
- Prefer app-internal timing paths when available.
- Do not use this artifact for broad public speedup wording without separate
  review and consensus.
- Use the results as a before/after baseline for Triton/Numba partner work.

## Expected Design Insights

The baseline should separate three categories:

- Comparable Embree vs OptiX primitive rows already exist. These are the first
  regression tests for Triton/Numba partner changes.
- OptiX-only promoted rows exist. These identify missing CPU/Embree fallback
  contracts or intentionally RT-core-only research slices.
- Apps with only process-wall fallback need app-internal timing cleanup before
  their numbers can support precise engineering claims.

## Local Verification

The runner manifest and ratio rules are covered by:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2626_benchmark_embree_optix_baseline_test
```
