# Goal2581 LibRTS OptiX Range-Intersects Path

Date: 2026-05-24

## Purpose

Goal2581 closes the missing `range_intersects` operation for the RTDL
LibRTS-style benchmark without adding LibRTS-specific native code.

The implemented native surface remains the generic primitive
`AABB_INDEX_QUERY_2D`, now supporting count-only:

- `point_contains`: indexed box contains query point.
- `range_contains`: indexed box contains query box.
- `range_intersects`: indexed box intersects query box.

## Implementation

`range_intersects` uses the LibRTS-style two-pass traversal pattern, but under
generic names and contracts:

- Forward pass: trace each query-box diagonal through the indexed-box GAS.
- Backward pass: trace each indexed-box anti-diagonal through the query-box GAS.
- Exact refinement: the intersection shader uses segment-vs-box predicates.
- Duplicate suppression: the backward pass counts only pairs not already found
  by the query-diagonal pass.

The packed-query ABI now accepts an operation code, so the same prepared
box-query buffer can execute either `range_contains` or `range_intersects`.
Prepared box-query buffers also build their own query GAS for the backward pass.

No native symbol or kernel name contains `LibRTS`.

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

## Correctness

Focused local tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2574_librts_spatial_index_benchmark_app_test \
  tests.goal2575_librts_rtspatial_pod_evidence_test \
  tests.goal2576_generic_aabb_index_primitive_test \
  tests.goal2577_librts_rtspatial_mutation_pod_evidence_test \
  tests.goal2578_librts_paperlike_authors_pod_evidence_test \
  tests.goal2579_librts_status_matrix_test \
  tests.goal2580_optix_aabb_index_native_symbol_test \
  tests.goal2581_librts_optix_range_intersects_pod_evidence_test
```

Result: 29 tests passed.

Pod checks:

- `make build-optix` passed.
- `tests.goal2580_optix_aabb_index_native_symbol_test` passed.
- The `optix_aabb_index --dataset tiny --operation all` CLI path returned
  counts `{point_contains: 6, range_contains: 2, range_intersects: 6}`.
- Prepared-query and host-staged OptiX counts matched CPU on tiny,
  `uniform_64_32`, and `uniform_256_128` fixtures for all three operations.
- Paper-like OptiX counts matched the authors-code evidence counts for all
  measured 10k/100k/1M rows.

## Performance

Fixture: RTDL-generated paper-like uniform WKT-equivalent data, seed `2025`,
1,000 queries, max indexed-box width/height `0.005`, max query-box width/height
`0.005`.

Authors-code numbers are from
`docs/reports/goal2578_librts_paperlike_uniform_authors_pod_evidence_2026-05-24.json`.

| Case | Operation | Count | RTSpatial ms | RTDL prepared-query median ms | RTDL / RTSpatial |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10k x 1k | point_contains | 54 | 0.064 | 0.0511 | 0.80x |
| 10k x 1k | range_contains | 4 | 0.068 | 0.0515 | 0.76x |
| 10k x 1k | range_intersects | 250 | 0.380 | 0.0873 | 0.23x |
| 100k x 1k | point_contains | 613 | 0.074 | 0.0528 | 0.71x |
| 100k x 1k | range_contains | 66 | 0.069 | 0.0571 | 0.83x |
| 100k x 1k | range_intersects | 2,477 | 0.441 | 0.1244 | 0.28x |
| 1M x 1k | point_contains | 6,251 | 0.099 | 0.0983 | 0.99x |
| 1M x 1k | range_contains | 693 | 0.106 | 0.0889 | 0.84x |
| 1M x 1k | range_intersects | 25,079 | 0.620 | 0.4049 | 0.65x |

Interpretation:

- The previously missing `range_intersects` native path is now correct on the
  tested fixtures and faster than the authors-code query rows for this
  paper-like generated slice.
- `range_intersects` costs more than the other two operations because it uses
  two OptiX launches and traverses both the indexed-box GAS and query-box GAS.
- Prepared query buffers are still the fair steady-state comparison. Host-query
  packing/upload and scene preparation are separate phases.
- The 1M point row is effectively at parity with authors-code; the main new win
  is closing `range_intersects`, not improving every old row.

## Boundaries

This evidence does not close the full LibRTS paper reproduction:

- Mutation operations remain authors-code evidence plus CPU reference in RTDL,
  not native RTDL OptiX update support.
- These fixtures are paper-like RTDL-generated uniform data, not exact paper
  artifact datasets.
- The comparison is count-only and assumes query buffers are already resident on
  the GPU.
- Public speedup wording still requires final review/consensus if used outside
  internal benchmark notes.
