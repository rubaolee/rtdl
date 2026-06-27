# Goal679: Linux GPU Backend Release Gate

Status: PASS

Date: 2026-04-20

## Scope

Goal679 runs the remaining Linux backend gate after the local Goal678 gate.
The objective is to validate the current optimization tree on the Linux GPU
host with fresh OptiX, Vulkan, and HIPRT builds.

This gate validates the repeated 2D visibility / any-hit / count optimization
round from Goals671-675. It does not validate Apple RT, because Apple RT is a
macOS backend and was covered by the local Apple M4 gates.

## Host

| Field | Value |
| --- | --- |
| Hostname | `lx1` |
| Sync path | `/tmp/rtdl_goal679` |
| Python | `Python 3.12.3` |
| GPU | `NVIDIA GeForce GTX 1070` |
| Driver | `580.126.09` |
| GPU memory | `8192 MiB` |

Important boundary: GTX 1070 has no NVIDIA RT cores. These Linux measurements
validate backend integration and repeated-query behavior on this host, but they
are not RT-core speedup evidence.

## Fresh Build Gate

The current macOS working tree, including uncommitted tracked and untracked
Goal671-679 files, was synced to `/tmp/rtdl_goal679` with stale `build/`
artifacts excluded. The backend libraries were rebuilt from that synced source.

| Backend | Command | Result | Version probe |
| --- | --- | --- | --- |
| OptiX | `make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc` | PASS | `(9, 0, 0)` |
| Vulkan | `make build-vulkan` | PASS | `(0, 1, 0)` |
| HIPRT | `make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54` | PASS | `(2, 2, 15109972)` |

The HIPRT build emitted only an upstream Orochi warning about an ignored
`fread` return value; the library built successfully.

## Focused Native Correctness Gate

Command:

```text
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so \
RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so \
LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-} \
PYTHONPATH=src:. python3 -m unittest \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal675_vulkan_prepared_anyhit_2d_test \
  tests.goal636_backend_any_hit_dispatch_test \
  tests.goal639_hiprt_native_any_hit_test -v
```

Result:

```text
Ran 30 tests in 10.864s
OK (skipped=2)
```

The two skips are expected Apple RT skips on Linux.

Covered native checks include:

- OptiX prepared 2D any-hit count and packed-ray count symbols;
- HIPRT prepared 2D any-hit correctness and scene reuse;
- Vulkan prepared 2D any-hit correctness, scene reuse, and packed-ray support;
- backend any-hit dispatch across Embree, OptiX, Vulkan, and HIPRT;
- HIPRT native 2D and 3D any-hit symbol and parity checks.

## Performance Sanity

The same fresh Linux tree ran a compact repeated-query sanity benchmark:

- rays: `4096`
- triangles: `1024`
- expected any-hit count: `4096`
- all backends returned the expected count for direct and prepared paths

| Backend | Direct median | Prepared/prepacked median | Count parity |
| --- | ---: | ---: | --- |
| OptiX | `0.0035153299977537245 s` | `0.00005833699833601713 s` | `4096 / 4096` |
| HIPRT | `0.5688568009936716 s` | `0.0057718300085980445 s` | `4096 / 4096` |
| Vulkan | `0.009350006002932787 s` | `0.004641148989321664 s` | `4096 / 4096` |

Interpretation:

- OptiX shows a strong prepared/prepacked scalar-count win on this repeated
  visibility/count case.
- HIPRT shows a large repeated-query setup/JIT/BVH reuse win, but this is
  HIPRT/Orochi CUDA on NVIDIA, not AMD GPU validation.
- Vulkan shows a smaller but real prepared/prepacked win.

The first direct samples for OptiX and Vulkan include cold setup/compilation
effects. The reported direct median is over three direct calls, so the warm
behavior still dominates the median.

## Honesty Boundaries

Allowed:

- The current tree builds and passes the focused native Linux OptiX, Vulkan,
  and HIPRT gate.
- The repeated 2D visibility/count optimization direction remains supported by
  fresh Linux measurements.

Not allowed:

- claiming RT-core speedup from the GTX 1070 host;
- claiming AMD GPU validation from HIPRT/Orochi CUDA evidence;
- applying this visibility/count performance result to DB workloads, graph
  workloads, one-shot calls, or full emitted-row output;
- claiming Vulkan tuple-ray prepared calls are faster without prepacked rays.

## Artifacts

Raw JSON:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal679_linux_gpu_backend_release_gate_2026-04-20.json
```

## Verdict

PASS.

The Linux GPU backend gate is sufficient for the current cross-engine
prepared/prepacked visibility/count optimization round. The next step is
external/AI review of Goal678 and Goal679 if this work is going into a release
decision.
