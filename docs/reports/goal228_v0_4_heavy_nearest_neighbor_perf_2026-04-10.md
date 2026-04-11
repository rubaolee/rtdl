# Goal 228 Report: Heavy v0.4 Nearest-Neighbor Performance Comparison

Date: 2026-04-10
Status: implemented

## Summary

This goal adds an indexed PostGIS preparation path and a heavy Linux benchmark
for the reopened `v0.4` nearest-neighbor workloads across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- indexed `postgis`

The benchmark uses Natural Earth populated places as the real-world-derived
point corpus, tiles it deterministically into heavier cases, and measures each
backend in a timed window of at least `10` seconds.

PostGIS is used as the external comparison baseline, but the report now
separates:

- row-identity agreement
- row-count mismatches
- distance-epsilon differences

That distinction matters because the GPU paths are `float_approx`, while
PostGIS uses double-precision distance evaluation.

## Files Updated

- `/Users/rl2025/rtdl_python_only/src/rtdsl/external_baselines.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/goal228_v0_4_nearest_neighbor_perf.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal228_v0_4_nearest_neighbor_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal201_fixed_radius_neighbors_external_baselines_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal207_knn_rows_external_baselines_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal228_v0_4_nearest_neighbor_perf_harness_test.py`
- `/Users/rl2025/rtdl_python_only/docs/goal_228_v0_4_heavy_nearest_neighbor_perf.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_summary_2026-04-10.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_summary_2026-04-10.md`

## Benchmark Setup

Linux host:

- `lestat-lx1`
- `8` CPU cores
- `15 GiB` RAM
- `NVIDIA GeForce GTX 1070` with `8192 MiB`
- PostgreSQL `16.13`

Dataset:

- Natural Earth populated places:
  - `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places_simple.geojson`
- base point count:
  - `7342`

Workload sizes:

- `fixed_radius_neighbors`
  - `copies=16`
  - `query_stride=4`
  - query points: `29368`
  - search points: `117472`
- `knn_rows`
  - `copies=1`
  - `query_stride=16`
  - query points: `459`
  - search points: `7342`

Measurement rule:

- each backend/workload combination ran until at least `10.0` seconds of timed
  samples accumulated

PostGIS execution rule:

- temp point tables are created once
- GiST indexes are built on `geom`
- `ANALYZE` is run
- timed measurements cover indexed query execution, not repeated table loading

## Verification

Local narrow verification:

- `PYTHONPATH=src:. python3 -m unittest tests.goal201_fixed_radius_neighbors_external_baselines_test tests.goal207_knn_rows_external_baselines_test tests.goal228_v0_4_nearest_neighbor_perf_harness_test`
  - `Ran 18 tests`
  - `OK`
- `python3 -m compileall src/rtdsl scripts/goal228_v0_4_nearest_neighbor_perf.py`
  - `OK`

Linux execution:

- `make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev`
  - passed
- `make build-vulkan`
  - passed
- `PYTHONPATH=src:. python3 scripts/goal228_v0_4_nearest_neighbor_perf.py --min-seconds 10 --output-dir build/goal228_v0_4_nearest_neighbor_perf`
  - passed

## Results

### fixed_radius_neighbors

PostGIS ground-truth rows:

- `45632`

Performance:

- PostGIS:
  - median `834.03 ms`
  - iterations `12`
- CPU:
  - median `3633.902 ms`
  - iterations `3`
- Embree:
  - median `66.937 ms`
  - iterations `147`
- OptiX:
  - median `125.383 ms`
  - iterations `75`
- Vulkan:
  - median `118.369 ms`
  - iterations `81`

Correctness against PostGIS:

- CPU:
  - exact row count match
  - exact row identity match
- Embree:
  - exact row count match
  - exact row identity match
  - max distance error `0.0`
- OptiX:
  - exact row count match
  - exact row identity match
  - max distance error `0.0`
- Vulkan:
  - exact row count match
  - exact row identity match
  - max distance error `0.0`

### knn_rows

PostGIS ground-truth rows:

- `1377`

Performance:

- PostGIS:
  - median `3158.1 ms`
  - iterations `4`
- CPU:
  - median `197.423 ms`
  - iterations `51`
- Embree:
  - median `628.572 ms`
  - iterations `16`
- OptiX:
  - median `10.565 ms`
  - iterations `918`
- Vulkan:
  - median `10.599 ms`
  - iterations `931`

Correctness against PostGIS:

- CPU:
  - exact row count match
  - exact row identity match
  - max distance error `0.0`
- Embree:
  - exact row count match
  - exact row identity match
  - max distance error `0.0`
- OptiX:
  - exact row count match
  - exact row identity match
  - max distance error `1.0643e-05`
- Vulkan:
  - exact row count match
  - exact row identity match
  - max distance error `1.0643e-05`

## Analysis

Main positive findings:

- `fixed_radius_neighbors` is now genuinely fast on accelerated backends.
  Embree is the strongest backend here, and both GPU backends are also much
  faster than CPU and PostGIS.
- the shared accelerated `fixed_radius_neighbors` boundary bug exposed by the
  first heavy run is now fixed.
  The refreshed heavy rerun shows full row-count and row-identity parity across
  CPU, Embree, OptiX, Vulkan, and indexed PostGIS.
- `knn_rows` is where the GPU line clearly pays off.
  OptiX and Vulkan are effectively tied and are about:
  - `18x` faster than CPU
  - `59x` to `60x` faster than PostGIS
- Indexed PostGIS is a credible external comparison path now.
  This is no longer a naive scan baseline.

Most important weaknesses:

- `knn_rows` on Embree remains a weak spot.
  It is correct, but materially slower than CPU and far behind both GPU
  backends on this case.
- GPU `knn_rows` distances are stable and very fast, but their strict
  double-precision parity against PostGIS still fails because they are
  `float_approx` paths.

## Recommended Next Work

1. Fix the shared accelerated `fixed_radius_neighbors` boundary issue.
   This is now complete and should remain covered by the new large-coordinate
   boundary regression tests plus the refreshed heavy Linux benchmark.
2. Keep OptiX and Vulkan as the primary optimization path for `knn_rows`.
   The heavy benchmark says clearly that GPU is the right direction for this
   workload family.
3. Revisit the Embree `knn_rows` implementation.
   It is correct, but not competitive enough to be the main accelerated story
   for nearest-neighbor ranking.
4. Keep indexed PostGIS in the benchmark suite as an external credibility
   anchor, but do not treat it as a performance target to beat only by tiny
   margins.
   The current GPU gap is already meaningful.

## Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_summary_2026-04-10.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_summary_2026-04-10.md`
