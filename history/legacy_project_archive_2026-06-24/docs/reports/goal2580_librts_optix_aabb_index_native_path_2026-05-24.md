# Goal2580 LibRTS RTDL OptiX AABB Index Path

Date: 2026-05-24

## Purpose

Goal2580 improves the RTDL LibRTS benchmark solution toward authors-code
NVIDIA RT-core performance without adding LibRTS-specific native code.

The implemented native surface is the generic primitive
`AABB_INDEX_QUERY_2D`, not a `LibRTS` ABI. It currently supports count-only:

- `point_contains`: indexed box contains query point.
- `range_contains`: indexed box contains query box.

`range_intersects` is intentionally unsupported in the native OptiX path for
now. Correct LibRTS-style rectangle intersection requires forward and backward
traversal. A single center-ray or diagonal shortcut would be incorrect.

## Implementation

New generic OptiX ABI symbols:

- `rtdl_optix_prepare_aabb_index_2d`
- `rtdl_optix_count_prepared_aabb_index_2d`
- `rtdl_optix_prepare_aabb_point_queries_2d`
- `rtdl_optix_prepare_aabb_box_queries_2d`
- `rtdl_optix_count_prepared_aabb_index_2d_packed_queries`
- `rtdl_optix_destroy_prepared_aabb_queries_2d`
- `rtdl_optix_destroy_prepared_aabb_index_2d`

The first count path accepts host-staged query arrays. The second path prepares
GPU-resident query buffers and reuses them across repeated queries. That second
path is the fair comparison against authors-code steady-state query timing.

The LibRTS benchmark app now has an `optix_aabb_index` mode that calls the
generic primitive.

## Evidence Environment

Pod:

- SSH: `root@203.57.40.169 -p 10212 -i ~/.ssh/id_ed25519_rtdl_codex`
- Host: `2f2405dbb885`
- GPU: NVIDIA RTX A5000
- Driver: `565.57.01`
- CUDA: `/usr/local/cuda-12.6`
- OptiX SDK: `/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64`
- Base commit: `802b4940c682a5cf38fff29f12630274db5a70e5`
- State: local uncommitted overlay synced to pod for validation

Build command:

```bash
CUDA_PREFIX=/usr/local/cuda-12.6 \
OPTIX_PREFIX=/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 \
make build-optix
```

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2574_librts_spatial_index_benchmark_app_test \
  tests.goal2576_generic_aabb_index_primitive_test \
  tests.goal2580_optix_aabb_index_native_symbol_test
```

Pod smoke result: prepared-query `point_contains` and `range_contains` matched
CPU counts on the tiny fixture.

## Performance

Fixture: RTDL-generated paper-like uniform WKT-equivalent data, seed `2025`,
1,000 queries, max indexed-box width/height `0.005`, max query-box width/height
`0.005`.

Authors-code numbers are from
`docs/reports/goal2578_librts_paperlike_uniform_authors_pod_evidence_2026-05-24.json`.

| Case | Operation | Count | RTSpatial ms | RTDL prepared-query median ms | RTDL / RTSpatial |
|---|---:|---:|---:|---:|---:|
| 10k x 1k | point_contains | 54 | 0.064 | 0.0556 | 0.87x |
| 10k x 1k | range_contains | 4 | 0.068 | 0.0530 | 0.78x |
| 100k x 1k | point_contains | 613 | 0.074 | 0.0570 | 0.77x |
| 100k x 1k | range_contains | 66 | 0.069 | 0.0555 | 0.80x |
| 1M x 1k | point_contains | 6,251 | 0.099 | 0.0906 | 0.92x |
| 1M x 1k | range_contains | 693 | 0.106 | 0.0791 | 0.75x |

Interpretation:

- With GPU-resident prepared query buffers, RTDL is within authors-code query
  time and is faster on these measured prepared-query subpaths.
- Without prepared query buffers, the same native traversal was roughly 1 ms
  for point queries and 2.4 ms for range contains, so eliminating repeated
  host-query packing and upload was necessary.
- Scene/index preparation is still separate from query timing and costs
  hundreds of milliseconds to seconds depending on data size and first-use
  context/JIT overhead.

## Boundaries

This evidence does not close the full LibRTS benchmark:

- `range_intersects` remains open.
- Mutation operations remain authors-code evidence plus CPU reference in RTDL,
  not native RTDL OptiX update support.
- These fixtures are paper-like RTDL-generated uniform data, not exact paper
  artifact datasets.
- Public speedup wording still requires final review/consensus if used outside
  internal benchmark notes.
