# Goal2646 RayDB RT-Core Typed-Buffer Update

Date: 2026-05-27

Status: internal engineering evidence only. Public speedup wording remains unauthorized until the RayDB RT path receives the required review/consensus.

## Purpose

RayDB had a correctness-valid RT-core lowering, but the first pod timings were misleadingly poor because the paper-shaped path rebuilt Python triangle/ray objects and per-row dense encodings before every OptiX call. That was not a useful test of RT cores.

This update keeps the engine app-agnostic and moves the RayDB app lowering onto typed packed host buffers:

- Python still owns RayDB semantics: row-to-triangle encoding, predicate-to-ray encoding, group-key mapping, and output interpretation.
- The native engine still sees only generic 3-D rays, triangles, primitive group ids, integer payloads, primitive-id deduplication, and grouped reductions.
- No RayDB, SQL, table, SSB, or query-plan vocabulary was added to the native engine.

## Code Changes

- `src/rtdsl/generic_primitives.py`
  - `run_generic_ray_triangle_primitive_grouped_i64_reduction_3d` now accepts typed `PackedRays` and `PackedTriangles` for the OptiX backend.
  - The CPU reference contract remains tuple/object based.

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
  - Added a packed RayDB paper workload builder using `pack_triangles_3d_from_arrays` and `pack_rays_3d_from_arrays`.
  - Replaced Python row-object triangle construction with typed packed buffers on the OptiX paper path.
  - Replaced Python generator dense-code mapping with NumPy `unique(..., return_inverse=True)` dense coding.

- `tests/goal2644_raydb_paper_rt_contract_test.py`
  - Added coverage that the packed workload preserves the paper shape without Python triangle objects.

## Pod Evidence

Pod command used:

```bash
ssh root@194.68.245.16 -p 22072 -i ~/.ssh/id_ed25519_rtdl_codex
```

Hardware and environment:

- GPU: NVIDIA RTX A5000, 24 GB
- Driver/CUDA from `nvidia-smi`: 565.57.01 / CUDA 12.7
- Source identity recorded by runner: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- OptiX build command: `make build-optix`
- Runtime library: `/workspace/rtdl_goal2645/build/librtdl_optix.so`

Focused pod tests:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl_goal2645/build/librtdl_optix.so \
  python3 -m unittest -v \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2645_raydb_rt_perf_runner_test
```

Result: 10 tests passed on pod, including the packed workload test and the OptiX paper-backend validation.

## Performance Results

Main seconds-scale command:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl_goal2645/build/librtdl_optix.so \
  python3 scripts/goal2645_raydb_rt_perf_pod.py \
  --skip-build-optix \
  --copies-ladder 250000 \
  --backends cpu_python_reference,paper_rt_optix \
  --modes count,sum,min,max,avg_as_sum_count \
  --repeat 2 --warmup 1 \
  --paper-cpu-max-copies 1 \
  --output-json docs/reports/goal2646_raydb_vectorized_cpu_vs_optix_250k_2026-05-27.json \
  --output-markdown docs/reports/goal2646_raydb_vectorized_cpu_vs_optix_250k_2026-05-27.md
```

2M-row result:

| Mode | CPU Python Reference Median | Paper RT OptiX Median | CPU / OptiX | Correct | RT Core |
|---|---:|---:|---:|---|---|
| count | 3.085382s | 1.874128s | 1.646x | yes | yes |
| sum | 2.997176s | 1.780184s | 1.684x | yes | yes |
| min | 3.223301s | 1.745981s | 1.846x | yes | yes |
| max | 3.177053s | 1.765843s | 1.799x | yes | yes |
| avg_as_sum_count | 3.083927s | 1.793880s | 1.719x | yes | yes |

800k-row result:

| Mode | CPU Python Reference Median | Paper RT OptiX Median | CPU / OptiX | Correct | RT Core |
|---|---:|---:|---:|---|---|
| count | 1.239575s | 0.702730s | 1.764x | yes | yes |
| sum | 1.225437s | 0.666197s | 1.839x | yes | yes |
| min | 1.272574s | 0.680978s | 1.869x | yes | yes |
| max | 1.294969s | 0.657970s | 1.968x | yes | yes |
| avg_as_sum_count | 1.246759s | 0.693491s | 1.798x | yes | yes |

## Interpretation

The RayDB path now demonstrates real RT-core acceleration for the paper-shaped encoding. The end-to-end OptiX path beats the CPU Python grouped aggregate oracle by roughly 1.6x to 2.0x on the tested 800k and 2M row workloads.

The native RT traversal itself is faster than the full app timing suggests. At 800k rows, the runner recorded native traversal around 0.15s to 0.21s, while end-to-end app time was around 0.66s to 0.70s. The remaining gap is mostly Python/NumPy lowering and host-buffer construction, not RT traversal.

## Remaining Debt

The next runtime improvement should be generic, not RayDB-specific:

1. Add a prepared device-resident primitive-payload context for `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`.
2. Keep primitive group ids and primitive values device-resident across repeated queries/reductions.
3. Add a prepared query mode that reports cold build, prepared build, and query-only timings separately.
4. Keep the native ABI vocabulary generic: rays, triangles, primitive ids, group ids, values, deduplication, and reductions only.

This is the correct continuation of the broader technical debt item: move more continuation/reduction work device-resident without app-specific native kernels.

## Follow-Up Debt Slice Implemented

After the typed-buffer perf matrix, a generic prepared primitive-payload ABI was
added:

- `rtdl_optix_primitive_grouped_i64_payload_3d_create`
- `rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction`
- `rtdl_optix_primitive_grouped_i64_payload_3d_destroy`
- Python wrapper: `prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d`

The ABI is still app-agnostic. It stores only primitive group ids and primitive
integer payload values on device. The app still owns RayDB encoding and result
interpretation.

Direct pod validation used the same RTX A5000 pod and `librtdl_optix.so` rebuilt
from the current source tree. The check prepared a 1,000-copy RayDB paper-shaped
workload, ran `sum`, and matched the CPU oracle. The returned transfer metadata
reported:

- `prepared_primitive_payload_on_device: true`
- `primitive_group_ids_uploaded_each_run: false`
- `primitive_values_uploaded_each_run: false`
- `query_rays_uploaded_each_run: true`

This closes the first part of the device-resident grouped payload debt. The next
step is benchmark-runner support for cold-build, prepared-build, and query-only
timing rows, plus optional prepared ray batches so repeated RayDB queries can
avoid both payload upload and query-ray upload.

Prepared query timing was then recorded by:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl_goal2645/build/librtdl_optix.so \
  python3 scripts/goal2646_raydb_prepared_payload_perf_pod.py \
  --copies-ladder 250000 \
  --modes count,sum,min,max,avg_as_sum_count \
  --repeat 3 --warmup 1 \
  --output-json docs/reports/goal2646_raydb_prepared_payload_query_perf_250k_2026-05-27.json \
  --output-markdown docs/reports/goal2646_raydb_prepared_payload_query_perf_250k_2026-05-27.md
```

2M-row prepared payload query-only result:

| Mode | Workload Build | Scene/Payload Prepare | Prepared Query Median | Correct | RT Core |
|---|---:|---:|---:|---|---|
| count | 0.887277s | 0.512687s | 0.471953s | yes | yes |
| sum | 1.012094s | 0.122992s | 0.358819s | yes | yes |
| min | 0.893524s | 0.108545s | 0.357411s | yes | yes |
| max | 0.885291s | 0.106278s | 0.359761s | yes | yes |
| avg_as_sum_count | 0.883030s | 0.108919s | 0.370539s | yes | yes |

This shows the RayDB paper-shaped workload now has three explicit timing
regions: Python lowering/build, generic prepared RT state, and repeated RT query
execution. The remaining gap to close is query-ray device residency and broader
partner-owned column inputs, not app-specific native database logic.
