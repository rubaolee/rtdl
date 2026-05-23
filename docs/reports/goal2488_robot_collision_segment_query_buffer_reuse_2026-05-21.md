# Goal2488 Robot-Collision Segment Query Buffer Reuse

Date: 2026-05-21

## Status

Goal2488 is complete as a host-buffer reuse slice for the robot-collision
segment-probe path, with local Embree validation and pod OptiX validation.

## What Changed

This goal adds an app-agnostic prepared query object for the existing
`PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1` contract:

- `PreparedGroupedSegmentQuery3D` owns the packed finite 3D segment array, the
  `uint32` group-offset array, and the `uint8` compact group-flag output buffer.
- Embree prepared static triangle scenes can run against the prepared query
  without repacking segment endpoints or reallocating the host output flag
  buffer per run.
- OptiX prepared static triangle scenes expose the same Python-level API and
  metadata, while preserving the current native transfer behavior.
- The robot-collision benchmark exposes `embree_prepared_buffers` and
  `optix_prepared_buffers` modes for this prepared-query path.

No native C++/CUDA files were changed. The native engine boundary remains
app-agnostic: the new runtime surface is expressed as grouped finite 3D segment
queries against a prepared static triangle scene, not as robot, collision,
link, pose, or planner vocabulary.

## Claim Boundary

The new path is a host-side reusable query buffer, not a device zero-copy
implementation. It does not claim true zero-copy, public speedup wording,
paper reproduction, or author-code comparison.

For OptiX, the prepared query avoids repeated Python-side packing and host
output allocation, but OptiX still uploads query segments per run and downloads
group flags through the current native ABI. Native device query/output buffer
reuse remains false in metadata.

## Why This Matters

Goal2485 showed that traversal was not the dominant cost in the robot-collision
prepared path: OptiX traversal was already much smaller than total prepared
runtime. The immediate engineering pressure is therefore outside RT traversal:
Python lowering, query packing, and host orchestration.

Goal2488 removes one of those overheads in a contract-preserving way. It is a
small but necessary step between prepared-scene reuse and a future
partner/device-column path.

## Validation

The regression coverage is in:

- `tests/goal2488_robot_collision_segment_query_buffer_reuse_test.py`

The tests verify:

- the prepared query descriptor is app-agnostic and host-scoped;
- Embree can run repeated queries using the same prepared query and output flag
  buffer;
- the CLI emits `embree_prepared_buffers` payloads with correct reuse metadata;
- active native Embree/OptiX source trees remain free of robot-collision app
  vocabulary; and
- this report records the no-zero-copy and no-native-change boundaries.

Local validation command:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2479_robot_collision_benchmark_roadmap_test \
  tests.goal2480_robot_collision_cpu_reference_app_test \
  tests.goal2481_robot_collision_generic_contract_design_test \
  tests.goal2482_robot_collision_embree_contract_test \
  tests.goal2483_robot_collision_optix_contract_test \
  tests.goal2484_robot_collision_prepared_reuse_test \
  tests.goal2485_robot_collision_performance_matrix_test \
  tests.goal2486_robot_collision_continuous_feasibility_test \
  tests.goal2487_robot_collision_project_closeout_test \
  tests.goal2488_robot_collision_segment_query_buffer_reuse_test
```

Result: `Ran 50 tests in 0.576s - OK (skipped=1)`.

Pod validation command shape:

```bash
ssh root@157.157.221.29 -p 23792 -i ~/.ssh/id_ed25519_rtdl_codex
cd /workspace/rtdl_python_only
export CUDA_PREFIX=/usr/local/cuda
export NVCC=/usr/local/cuda/bin/nvcc
export RTDL_NVCC=/usr/local/cuda/bin/nvcc
export OPTIX_PREFIX=/workspace/vendor/optix-dev
export RTDL_OPTIX_PTX_COMPILER=nvcc
export LD_LIBRARY_PATH=/workspace/rtdl_python_only/build:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
export PYTHONPATH=src:.
make build-optix OPTIX_PREFIX=$OPTIX_PREFIX CUDA_PREFIX=$CUDA_PREFIX NVCC=$NVCC
python3 examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py \
  --mode optix_prepared_buffers --dataset scaled --pose-count 64 --obstacle-count 16 --link-count 3 \
  --repeats 11 --warmup 3
```

Pod environment:

- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `570.133.07`
- CUDA toolkit used for build: `/usr/local/cuda`, `Build cuda_13.0.r13.0/compiler.36424714_0`
- OptiX headers: `/workspace/vendor/optix-dev`, commit
  `f60c1e44f18426f426a2ed948f28515b3cf67b8a`

Pod artifacts:

- `docs/reports/goal2488_robot_collision_segment_query_buffer_reuse_pod/summary.json`
- `docs/reports/goal2488_robot_collision_segment_query_buffer_reuse_pod/optix_prepared_scaled.json`
- `docs/reports/goal2488_robot_collision_segment_query_buffer_reuse_pod/optix_prepared_buffers_scaled.json`

External review note: Claude was attempted for this goal but hung without
producing output and was killed. Gemini was attempted with a shorter prompt but
failed during CLI authentication/network setup. Therefore, Goal2488 has local
plus pod Codex validation only and no external AI consensus artifact.

Local Embree timing snapshot, internal evidence only:

| Mode | Dataset Shape | Repeats/Warmup | Tail Median Total | Tail Median Query Pack | Tail Median Traversal |
| --- | --- | ---: | ---: | ---: | ---: |
| `embree_prepared` | scaled, 64 poses, 16 obstacles, 3 links | 11/3 | `0.0024446044999422156s` | `0.0023980625001058797s` | `0.000015208s` |
| `embree_prepared_buffers` | scaled, 64 poses, 16 obstacles, 3 links | 11/3 | `0.00003256249965488678s` | `0.0s` | `0.0000144165s` |

The local snapshot confirms the intended effect: the prepared-buffer mode
removes repeated Python query packing from the measured tail path while leaving
native traversal essentially unchanged. This is not public speedup wording and
is not public speedup wording.

Pod OptiX timing snapshot, internal evidence only:

| Mode | Dataset Shape | Repeats/Warmup | Tail Median Total | Tail Median Query Pack | Tail Median Traversal | Match Probe Reference |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `optix_prepared` | scaled, 64 poses, 16 obstacles, 3 links | 11/3 | `0.006281394511461258s` | `0.006091654300689697s` | `0.0000420195s` | yes |
| `optix_prepared_buffers` | scaled, 64 poses, 16 obstacles, 3 links | 11/3 | `0.00012390315532684326s` | `0.0s` | `0.0000357475s` | yes |

The same-pod internal ratio for `optix_prepared` over
`optix_prepared_buffers` is `50.69600120264582x` on this exact sampled-probe
path. This is internal subpath evidence only; it does not authorize public
whole-app speedup claims, author-code comparison claims, true zero-copy claims,
or native device-buffer-reuse claims. The prepared-buffer payload records
`host_query_output_buffers_reused=true` and
`native_query_output_buffers_reused=false`.

## Next Implementation Gate

The next implementation gate is a real device-column or native prepared-query
buffer path for OptiX. That work should explicitly decide ownership of device
query columns, device result buffers, synchronization, lifetime, and fallback
behavior before any zero-copy or device-buffer-reuse wording is allowed.
