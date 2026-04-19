# Goal 565: HIPRT Prepared Ray/Triangle Performance Round

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal565_hiprt_perf`

Raw result file: `/Users/rl2025/rtdl_python_only/docs/reports/goal565_hiprt_prepared_ray_perf_linux_2026-04-18.json`

## Verdict

ACCEPT as one bounded HIPRT performance-improvement round.

The result confirms that HIPRT is slow primarily when each call pays setup,
geometry build, and runtime compilation costs. For the prepared 3D
ray/triangle workload, reusing the prepared HIPRT context reduces repeated
query latency from `0.5655s` one-shot HIPRT to `0.00206s` median prepared-query
time on the Linux GTX 1070 host, while preserving CPU reference parity.

This is a real performance mitigation for repeated-query applications. It is
not broad prepared coverage for all 18 v0.9 workloads.

## Workload

- Rays: `1024`
- Triangles: `2048`
- Repeats for prepared query: `5`
- Workload: 3D `ray_triangle_hit_count`
- Backend path: HIPRT/Orochi CUDA mode on Linux NVIDIA GTX 1070

## Commands

Build:

```bash
cd /tmp/rtdl_goal565_hiprt_perf
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-embree
```

Run:

```bash
cd /tmp/rtdl_goal565_hiprt_perf
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 scripts/goal565_hiprt_prepared_ray_perf.py \
  --rays 1024 \
  --triangles 2048 \
  --repeats 5 \
  --output docs/reports/goal565_hiprt_prepared_ray_perf_linux_2026-04-18.json
```

Local harness test:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal565_hiprt_prepared_ray_perf_test \
  tests.goal544_hiprt_docs_examples_test \
  tests.goal560_hiprt_backend_perf_compare_test
```

Result:

```text
Ran 5 tests in 0.329s
OK
```

## Results

| Path | Time s | Parity |
| --- | ---: | --- |
| CPU Python reference | 1.257806 | reference |
| Embree | 0.017699 | PASS |
| OptiX | 0.313755 | PASS |
| Vulkan | 0.417467 | PASS |
| HIPRT one-shot | 0.565511 | PASS |
| HIPRT prepare setup | 0.523847 | setup phase |
| HIPRT prepared query median | 0.002059 | PASS |
| HIPRT prepared query min | 0.001977 | PASS |
| HIPRT prepared query max | 0.002130 | PASS |

Derived result:

- HIPRT one-shot to prepared-query speedup: `274.71x`

## Interpretation

The earlier v0.9 cross-backend smoke comparison showed HIPRT cold-call latency
around `0.37-0.58s` across the small matrix. This goal explains and mitigates
that problem for the first prepared workload:

- one-time cost: HIPRT/Orochi context setup, geometry upload/build, and trace
  kernel compilation
- repeated-query cost: ray upload, already-built HIPRT traversal launch, row
  copy-back, and Python/ctypes overhead

The prepared-query median is faster than the measured Embree, OptiX, and Vulkan
one-shot paths for this specific larger repeated 3D ray/triangle fixture. That
is useful evidence for app shapes that reuse build geometry across many query
batches.

## Honesty Boundary

Allowed claims:

- Prepared HIPRT 3D ray/triangle queries are much faster than one-shot HIPRT on
  the tested repeated-query fixture.
- The prepared path preserves CPU reference parity.
- Prepared execution is the current recommended HIPRT performance path when
  build geometry is reused.

Disallowed claims:

- Do not claim broad prepared HIPRT support for all 18 v0.9 workloads.
- Do not claim AMD GPU validation.
- Do not claim RT-core speedup from this GTX 1070 result.
- Do not claim HIPRT is generally performance-leading across all workloads.

## Next Performance Work

The next performance goal should extend the prepared model to the most valuable
repeated-query families:

- 2D/3D nearest-neighbor build-point reuse
- segment/polygon build-geometry reuse
- bounded DB prepared table reuse
- graph prepared CSR reuse

Each should follow this goal's structure: separate prepare time from repeated
query time, prove row parity, and compare against Embree/OptiX/Vulkan without
claiming speedup outside the measured workload shape.
