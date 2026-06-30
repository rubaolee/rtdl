# Goal2126 Public Hausdorff Dataset Perf Harness

Date: 2026-05-16

Status: harness ready; public-data fetch smoke complete; pod timing still pending.

## Purpose

Goal2123 proved that the X-HD-inspired RTDL/OptiX grouped-reduced nearest-witness path can beat the independent CuPy all-pairs exact point-set Hausdorff baseline on large synthetic 2D point sets. Goal2126 moves the next test away from synthetic data by preparing a reproducible public-data harness using the Stanford 3D Scanning Repository.

This is not yet the exact X-HD paper dataset claim. The X-HD repository references local files under `/local/storage/shared/HDDatasets`, and those data files are not shipped in that repository. Goal2126 therefore starts with public Stanford scan archives that can be fetched directly.

## Public Datasets

The harness downloads and parses:

- Stanford Dragon reconstruction: `https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz`
- Stanford Happy Buddha reconstruction: `https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz`

The script locates `dragon_vrip.ply` and `happy_vrip.ply`, parses PLY vertex coordinates, samples deterministic vertex subsets, normalizes them, and projects vertices to XY for the current RTDL 2D exact point-set Hausdorff primitive.

This projected 2D result is exact for the projected vertex point sets, but it is not a substitute for true 3D mesh/surface Hausdorff distance. Projection can change nearest-neighbor relationships and can hide depth-separated structure. A later 3D point-group or surface-aware primitive is required before we can make X-HD-style 3D geometry claims.

## Harness

Script:

- `scripts/goal2126_public_hausdorff_dataset_perf.py`

No-network unit test:

- `tests/goal2126_public_hausdorff_dataset_perf_test.py`

Fetch-smoke artifact:

- `docs/reports/goal2126_public_hausdorff_dataset_fetch_smoke_2026-05-16.json`

The harness emits two public-data cases:

- `stanford_dragon_xy_shifted`: Dragon vertices projected to XY and compared with a deterministic shifted copy.
- `stanford_dragon_vs_happy_xy`: Dragon and Happy Buddha vertices independently normalized and projected to XY.

## Early-Break Clarification

The current winning Goal2123 path did not win by using an unfair early break.

- The CuPy RawKernel baseline scans all target tiles for each source point, computes the exact nearest target for every source, then reduces the maximum nearest distance. It does not use pruning or early termination.
- The RTDL/OptiX grouped-reduced path used for the large-speedup evidence is also exact for the tested 2D point sets. It uses grouped target bounds in an OptiX acceleration structure, scans points inside visited groups, and performs a device-side max-nearest reduction. It was run with `seed_with_threshold=False`, so the threshold-search early-termination path was not part of the measured large synthetic speedup.
- There is a threshold helper elsewhere in the Hausdorff experiment code that can call `optixTerminateRay()`, but that helper is a bounded/decision path and not the exact reduced path used for the accepted Goal2123 performance table.

The real algorithmic difference is therefore:

- CuPy baseline: dense all-pairs target scan.
- RTDL/OptiX path: RT-accelerated BVH traversal over generic point-group bounds plus CUDA/SM scanning inside candidate groups plus on-device reduction to avoid per-query row materialization.

## Claim Boundary

Allowed after this goal:

- The public Stanford scan archives can be fetched, extracted, parsed, sampled, and projected into reproducible 2D point-set HD cases.
- The harness is ready to run CuPy versus RTDL/OptiX grouped-reduced timings on a pod.

Not allowed yet:

- No public-dataset speedup claim until pod timings exist.
- No exact X-HD paper dataset claim.
- No 3D mesh/surface Hausdorff claim. This harness projects public 3D vertices to XY because the current RTDL grouped-reduced nearest-witness primitive is 2D.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2126_public_hausdorff_dataset_perf_test
Ran 3 tests in 0.112s
OK

py -3 -m py_compile scripts\goal2126_public_hausdorff_dataset_perf.py tests\goal2126_public_hausdorff_dataset_perf_test.py
OK
```

Fetch smoke:

```text
$env:PYTHONPATH='src;.'; py -3 scripts\goal2126_public_hausdorff_dataset_perf.py --sample-count 2048 --skip-cupy --skip-rtdl --json-out docs\reports\goal2126_public_hausdorff_dataset_fetch_smoke_2026-05-16.json
```

Result: both Stanford archives were downloaded or reused from cache, extracted, parsed, and sampled into the two expected cases.

## Next Pod Command

After syncing this commit to a GPU pod with OptiX built:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so" \
python3 scripts/goal2126_public_hausdorff_dataset_perf.py \
  --sample-count 131072 \
  --json-out docs/reports/goal2126_public_hausdorff_dataset_perf_pod_2026-05-16.json
```

If that row is stable, run larger sample counts such as `262144` and `524288` with explicit timeouts and progress logging.
