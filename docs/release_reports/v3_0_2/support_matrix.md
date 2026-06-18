# RTDL v3.0.2 Support Matrix

Status: released support boundary for `v3.0.2`.

This matrix summarizes the V3.0.2 public support boundary. It is a
release-level map, not a substitute for feature-specific docs or benchmark
artifacts.

## Programming Surfaces

| Surface | Status | Boundary |
| --- | --- | --- |
| Kernel DSL | Supported source-tree learning surface | Best for teaching `input -> traverse -> refine -> emit`; not every performance route is authored as `@rt.kernel`. |
| Primitive/prepared front doors | Current recommended performance surface | Use when a generic primitive returns the needed compact result or prepared state is useful. |
| Partner continuation | Supported when explicit | CuPy, Numba, NumPy, CPU, or app-owned continuations remain user/app code unless RTDL ships and reviews the exact contract. |
| Embedding / C ABI / SDK | V4.0 scope | Existing artifacts are historical or preparatory only; they are not V3.0.2 release criteria or success claims. |
| Stable packaged SDK | Deferred to V4 | No PyPI/wheel/stable SDK claim in v3.0.2. |
| Generated bindings | Deferred to V4 | Generated language packages are not released. |

## Benchmark App Route Matrix

| App | V3 route class | Partner policy | Release stance |
| --- | --- | --- | --- |
| Hausdorff / X-HD | primitive-first | primitive-only | Current route closed; no broad X-HD or whole-system superiority claim. |
| Spatial RayJoin | mixed explicit | user-chosen, evidence-bound | Current route closed; no full RayJoin paper or 8/8 Section 5.7 reproduction claim. |
| RT-DBSCAN | mixed explicit | CuPy/Numba route choice by contract | Current route closed; no DBSCAN-native engine ABI or automatic route selection. |
| Robot collision | no-partner prepared primitive | none on promoted route | Current route closed; no planner or exact solid-collision claim. |
| Contact manifold | no-partner prepared primitive | none on promoted route | Current route closed; no full physics contact generator claim. |
| RayDB-style | primitive-first | primitive-only for fused reductions | Current route closed; not SQL, SSB, or a DBMS. |
| Barnes-Hut | mixed explicit | scale-dependent CPU/Numba, Numba CUDA, or RTDL/OptiX+partner evidence | Current route classification closed; no Barnes-Hut RT-core speedup claim. |
| LibRTS spatial index | no-partner prepared primitive | none on promoted route | Current route closed; not full mutable LibRTS. |
| RTNN | mixed explicit | CuPy/Numba bridge when resident continuation is used | Current route closed; no full RTNN paper or ANN-index claim. |
| Triangle counting | primitive-first scalar plus explicit construction/replay choices | CuPy/Numba choices are route-specific | Current route closed; no RT-Graph paper speedup claim. |

## Engine And Partner Reading

| Area | v3.0.2 support reading |
| --- | --- |
| CPU reference | Portable correctness and learning lane. |
| Embree | CPU RT backend and same-contract baseline where configured. |
| OptiX | NVIDIA RT backend where `RTDL_OPTIX_LIBRARY` points at a built library. |
| Vulkan, HIPRT, Apple RT | Preserved proof or compatibility surfaces where documented; not V3.0.2 performance-release targets. |
| CuPy | Mature CUDA-array continuation partner for selected measured contracts. |
| Numba | Python-source CPU/CUDA continuation partner and no-C++ reference lane for selected contracts. |
| NumPy | CPU data preparation, oracle, and lowering support. |

## Non-Claims

Do not use this support matrix to claim:

- broad speedup across all workloads;
- whole-application acceleration for all ten apps;
- package-install or stable SDK support;
- automatic partner or backend selection;
- arbitrary partner-code acceleration;
- RTDL superiority over specialized paper code;
- public true-zero-copy or complete device residency;
- AMD or Intel GPU performance.
