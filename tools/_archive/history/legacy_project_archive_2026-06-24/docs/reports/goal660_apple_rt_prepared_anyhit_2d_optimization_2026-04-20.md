# Goal660: Apple RT Prepared 2D Any-Hit Optimization

Date: 2026-04-20

Status: implemented and locally validated

## Problem

The first Goal659 Mac visibility/collision benchmark showed that Apple RT 2D any-hit was correct but not fast enough:

- one-shot Apple RT rebuilt MPS prism acceleration structures inside every call;
- repeated visibility/collision apps usually keep the obstacle field fixed and submit many ray batches;
- therefore the fair application shape needs a prepared Apple RT dataset, not only one-shot execution.

## Change

Added a prepared Apple RT 2D any-hit API:

- native prepare: `rtdl_apple_rt_prepare_ray_anyhit_2d`
- native run: `rtdl_apple_rt_run_prepared_ray_anyhit_2d`
- native destroy: `rtdl_apple_rt_destroy_prepared_ray_anyhit_2d`
- Python wrapper: `rt.prepare_apple_rt_ray_triangle_any_hit_2d(...)`

The prepared handle builds and retains MPS prism acceleration structures for obstacle triangles. Each query run uploads only the ray batch and reuses the prepared obstacle chunks.

## Benchmark Result

The Goal659 benchmark now reports:

- `apple_rt`: one-shot Apple RT
- `apple_rt_prepared_query`: prepared Apple RT query time after obstacle setup
- `embree`: mature RTDL baseline
- `shapely_strtree`: existing Shapely/GEOS baseline

CPU/oracle remains hidden and is used only for correctness parity.

| Case | Apple RT one-shot | Apple RT prepared-query | Embree | Shapely/GEOS |
| --- | ---: | ---: | ---: | ---: |
| dense small, 512 rays / 128 tris | 0.014132 s | 0.003323 s | 0.000387 s | 0.004405 s |
| dense medium, 2048 rays / 512 tris | 0.021635 s | 0.013302 s | 0.000844 s | 0.017987 s |
| dense large, 8192 rays / 2048 tris | 0.094030 s | 0.057786 s | 0.003228 s | 0.072857 s |
| sparse small, 512 rays / 128 tris | 0.007903 s | 0.001602 s | 0.000196 s | 0.004460 s |
| sparse medium, 2048 rays / 512 tris | 0.014692 s | 0.007751 s | 0.000846 s | 0.012525 s |
| sparse large, 8192 rays / 2048 tris | 0.055594 s | 0.033757 s | 0.002870 s | 0.048831 s |

## Interpretation

The prepared Apple RT path is now faster than the Shapely/GEOS STRtree baseline on all measured cases in this run.

It is still slower than Embree by roughly one order of magnitude or more. Therefore the correct public claim is:

- Apple RT has a real, correctness-clean, prepared-query visibility/collision path on this Mac.
- Prepared Apple RT now beats the tested Shapely/GEOS baseline for these generated workloads.
- Embree remains the fastest local baseline and the mature performance reference.

## Validation

Commands run:

```bash
make build-apple-rt
PYTHONPATH=src:. python3 -m unittest -v tests.goal578_apple_rt_backend_test tests.goal652_apple_rt_2d_anyhit_native_test tests.goal659_mac_visibility_collision_perf_test
PYTHONPATH=src:. build/goal659_shapely_venv/bin/python scripts/goal659_mac_visibility_collision_perf.py --warmups 1 --repeats 3
PYTHONPATH=src:. build/goal659_shapely_venv/bin/python scripts/goal659_mac_visibility_collision_perf.py --warmups 1 --repeats 3 --scale dense_blocked:large,8192,1024 --scale sparse_clear:large,8192,1024 --json-out docs/reports/goal659_mac_visibility_collision_perf_large_2026-04-20.json --md-out docs/reports/goal659_mac_visibility_collision_perf_large_2026-04-20.md
```

Focused tests passed:

- `13` tests OK

Report artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal659_mac_visibility_collision_perf_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal659_mac_visibility_collision_perf_large_2026-04-20.md`
