# Goal3856: Triangle Counting RT-Graph Scale Route Correction

Date: 2026-06-08

## Purpose

Goal3855 identified `triangle_counting` as the next real hot bottleneck in the
current 10-app scale profile. The registry row still executed:

```text
--mode run --backend optix --output-mode summary --optix-graph-mode native --copies 2048
```

That path reports `optix_performance.class = "host_indexed_fallback"` and does
not consume the command's `--repeat` / `--warmup` arguments. In other words, the
scale profile was timing an older graph fixture path, not the RT-Graph-style
generic ray/triangle summary route that the benchmark app already exposes.

## Change

This goal adds an explicit `--rt-graph-copies` knob for the RT-Graph generic
modes and points the current scale-profile registry at:

```text
--mode rt_graph_2a1_generic_rt
--backend optix
--fixture degree_oriented_two_triangles
--rt-graph-copies 2048
--detail summary
--repeat 3
--warmup 1
```

The fixture copier repeats the selected fixture as disjoint graph copies. It is
only active for fixture inputs; `--edge-file` inputs reject `--rt-graph-copies`
values other than `1`.

## A5000 Evidence

Artifact:

- `docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/summary.json`
- `docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/outputs/triangle_counting_optix_rt_graph_2a1_scale_default_2048.stdout.json`

The focused runner passed with one selected row:

| Field | Value |
| --- | ---: |
| row id | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` |
| process elapsed | `1.501799185 s` |
| stderr bytes | `0` |
| stdout bytes | `8487` |
| claim-flag violations | `0` |
| all pass | `true` |

The benchmark payload confirms the intended route:

| Field | Value |
| --- | ---: |
| mode | `rt_graph_2a1_generic_rt` |
| native symbol | `rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum` |
| RT-core path label | `generic_prepared_triangle_scene_3d_any_hit_weighted_sum` |
| fixture copies | `2048` |
| primitive count | `10240` |
| ray count | `4096` |
| oracle triangle count | `4096` |
| RTDL weighted count | `4096` |
| rows materialized | `false` |
| query repeat / warmup | `3 / 1` |
| prepared scene reused | `true` |

Phase timing from the payload:

| Phase | Time |
| --- | ---: |
| build contract | `69.437 ms` |
| build geometry | `4.648 ms` |
| prepare scene | `513.549 ms` |
| median hot query | `0.214 ms` |
| min / max hot query | `0.200 ms / 0.343 ms` |
| total payload time | `679.303 ms` |

## Interpretation

This is a route correction, not a public same-contract speedup claim. The prior
Goal3855 triangle row measured the older `mode=run` fallback and reported a hot
`query_raw_view_sec` near `0.896843 s`. That number is useful as a bottleneck
diagnosis, but it is not the approved RT-Graph 2A1 benchmark contract.

The corrected row measures the intended generic prepared ray/triangle summary
contract. It keeps app-owned graph orientation and two-hop interpretation in
Python, and the native side sees only generic triangles, rays, optional weights,
and a scalar weighted-hit summary.

The process elapsed is still dominated by process startup, imports, contract
construction, and scene preparation. The hot query median is now a real prepared
OptiX traversal measurement, but this goal does not authorize release, broad
RT-core speedup, paper-reproduction, true-zero-copy, or whole-app speedup claims.

## Files Changed

- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/`
- `tests/goal3856_triangle_counting_rt_graph_scale_route_test.py`

## Validation

Local:

```text
PYTHONPATH=src:. py -3 -m unittest tests.goal3828_current_benchmark_scale_profile_registry_test
```

Pod:

```text
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so \
RTDL_OPTIX_LIB=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so \
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --only triangle_counting \
  --output-json docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/summary.json \
  --output-dir docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/outputs \
  --heartbeat-sec 15
```

