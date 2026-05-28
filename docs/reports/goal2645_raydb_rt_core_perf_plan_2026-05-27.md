# Goal2645 RayDB RT-Core Performance Plan

Status: pod-ready plan; no public performance claim yet.

## Purpose

RayDB must not remain a partner-resident grouped-reduction row in the benchmark
portfolio. The RayDB paper and reference code use OptiX ray/triangle traversal:
rows are encoded as triangle primitives, predicate scans become +Z rays, any-hit
programs observe primitive IDs, duplicate primitive hits are suppressed, and
grouped aggregates are finalized from the hit primitive set.

Goal2644 added that shape to RTDL as an app-agnostic primitive:
`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`. Goal2645 measures it on a
CUDA/OptiX pod.

## Exact Runner

Use:

```bash
PYTHONPATH=src:. python3 scripts/goal2645_raydb_rt_perf_pod.py \
  --copies-ladder 1,100,1000,10000 \
  --repeat 3 \
  --warmup 1
```

The runner builds `librtdl_optix.so` with `make build-optix` unless
`--skip-build-optix` is passed.

Default artifacts:

- `docs/reports/goal2645_raydb_rt_perf_pod_2026-05-27.json`
- `docs/reports/goal2645_raydb_rt_perf_pod_2026-05-27.md`

## Required Evidence

Each performance row must include:

- script path;
- JSON artifact path;
- git commit and dirty-status snapshot;
- hardware from `nvidia-smi`;
- CUDA compiler version from `nvcc --version`;
- backend name;
- exact mode and copy count;
- output contract;
- correctness against the CPU columnar oracle;
- `rt_core_accelerated=true` for `paper_rt_optix`;
- native symbol
  `rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction`.

## Claim Boundary

The native runtime receives only 3-D rays, triangles, primitive group IDs,
primitive i64 values, a dedup flag, and a grouped reduction operation. Python
owns RayDB query encoding and result interpretation. The engine must not contain
RayDB, SQL, table, SSB, database, or query-plan vocabulary.

`performance_claim_authorized` remains `false` until pod results are reviewed.
