# Goal2590 Generic 3-D Device-Column RT-Side Optimization

Date: 2026-05-24

## Scope

This change adds a generic OptiX 3-D triangle/ray device-column ABI for compact
summary queries. It is intentionally app-agnostic: native code sees only
triangle columns, ray columns, and optional uint64 ray weights. RT-Graph
triangle-counting semantics remain in the Python benchmark adapter.

Implemented generic surfaces:

- `prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns)`
- `PreparedOptixStaticTriangleScene3D.ray_any_hit_weighted_sum_device_columns(ray_columns, ray_weights)`
- `PreparedOptixStaticTriangleScene3D.ray_hit_count_sum_device_columns(ray_columns)`
- GPU-side packing from partner-resident 3-D triangle and ray columns into
  RTDL internal OptiX layouts.

Also changed host bulk 2-D/3-D ray/triangle packers to keep their structured
NumPy owner buffer alive and use `from_buffer` rather than `from_buffer_copy`.

## Pod Environment

Pod SSH used:

```text
ssh root@203.57.40.104 -p 10001 -i ~/.ssh/id_ed25519_rtdl_codex
```

Observed environment:

- GPU: NVIDIA RTX A5000
- Driver: 550.127.05
- CUDA toolkit used for build: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/NVIDIA-OptiX-SDK-7.7.0-linux64-x86_64`
- CuPy venv: `/root/rtdl_cupy_venv`

The pod initially failed new NVRTC PTX loading because CUDA 12.8 user-space was
paired with a 550 driver. The installed `cuda-compat-12-8` package was a tiny
575 placeholder with no compatibility libraries. I installed the real
`cuda-compat-12-8=570.211.01-0ubuntu1` package and ran GPU evidence with:

```text
LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
```

## Validation

Local Mac:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/__init__.py examples/v2_0/research_benchmarks/triangle_counting/rt_graph_contract.py examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py tests/goal2589_rt_graph_triangle_contract_test.py
PYTHONPATH=src:. python3 -m unittest tests.goal2589_rt_graph_triangle_contract_test tests.goal2586_triangle_counting_benchmark_boundary_test
```

Result: 15 tests passed, 3 skipped.

Pod:

```text
make build-optix OPTIX_PREFIX=/root/vendor/NVIDIA-OptiX-SDK-7.7.0-linux64-x86_64 CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. /root/rtdl_cupy_venv/bin/python -m unittest tests.goal2589_rt_graph_triangle_contract_test tests.goal2586_triangle_counting_benchmark_boundary_test
```

Result: native OptiX build succeeded; 15 tests passed.

## RT-Graph Performance

Input: `build/goal2589_more_probes/k4_cliques_100000.edge`

Shape:

- RT-2A1: 600,000 triangle primitives, 300,000 rays
- RT-1A2: 400,000 triangle primitives, 600,000 rays
- All runs matched the RT-Graph triangle-count oracle.

Median over 3 measured CuPy partner runs after one warmup:

| Mode | Path | Total ms | Build contract ms | Build geometry ms | Run backend ms | Native traversal ms |
|---|---:|---:|---:|---:|---:|---:|
| RT-2A1 | new device-column CuPy partner | 30.408 | 22.077 | 0.546 | 7.816 | 0.283 |
| RT-1A2 | new device-column CuPy partner | 27.476 | 17.671 | 2.800 | 7.043 | 0.420 |

Current non-partner host-packed path on the same input and pod:

| Mode | Path | Total ms | Build contract ms | Build geometry ms | Run backend ms | Native traversal ms |
|---|---:|---:|---:|---:|---:|---:|
| RT-2A1 | host contract + host packed arrays | 3611.658 | 2741.964 | 236.735 | 388.002 | 0.299 |
| RT-1A2 | host contract + host packed arrays | 3347.408 | 2816.320 | 211.890 | 90.138 | 0.437 |

Previously recorded CuPy partner host-packed medians before this device-column
optimization on the same K4 x 100k shape were approximately:

| Mode | Previous CuPy total ms | Previous build geometry ms | Previous run backend ms |
|---|---:|---:|---:|
| RT-2A1 | 162.544 | 97.026 | 28.200 |
| RT-1A2 | 171.575 | 119.204 | 27.641 |

Interpretation: the main gain is eliminating host materialization of RT geometry
after CuPy preprocessing. Native traversal time was already sub-millisecond; the
optimization removes Python/CPU packing and host-to-device upload pressure around
the RT query.

## Other Affected App Check

Direct search showed the other benchmark app using the prepared 3-D static
triangle scene is robot collision. It does not use the new device-column ABI,
but it shares the prepared scene implementation, so it was checked for OptiX
regression.

Command:

```text
PYTHONPATH=src:. /root/rtdl_cupy_venv/bin/python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --mode optix_prepared_device_count --dataset scaled --pose-count 256 --obstacle-count 64 --link-count 4 --repeats 3 --warmup 1
```

Result:

- Shape: 128 static obstacle triangles, 9,216 query segments, 1,024 query groups
- Correctness: all measured runs matched the probe reference
- Tail median total run time: 0.089 ms
- Tail median traversal: 0.0368 ms
- No regression was observed on this direct 3-D static-scene consumer.

## Claim Boundary

This is internal benchmark evidence, not public speedup wording. Public claims
still require external review and consensus under the project rules. The
optimization is behavior-based and app-name-free in native code; RT-Graph uses it
through benchmark-owned Python lowering only.
