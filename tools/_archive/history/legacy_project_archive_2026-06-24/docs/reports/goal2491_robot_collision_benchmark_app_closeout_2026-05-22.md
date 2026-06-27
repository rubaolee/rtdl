# Goal2491: Robot-Collision Benchmark App Closeout

Date: 2026-05-22

## Status

Goal2491 closes the robot-collision benchmark app as a bounded RTDL benchmark.
The benchmark is finished for the current project scope: sampled discrete feasibility
via grouped finite 3D segment probes against static triangle obstacles.

This is not a robotics-paper reproduction and not a general robot-collision
engine. It is a benchmark app that forced useful RTDL language/runtime
reconstruction while preserving the app-agnostic native-engine boundary.

## Supported Contract

The supported contract is:

- app-level Python lowers robot poses and link samples into grouped finite 3D
  segment probes;
- native Embree and OptiX evaluate grouped segment any-hit flags against a
  prepared static triangle scene;
- the result is a compact per-group feasibility flag list or, for screening,
  a scalar flagged-group count;
- correctness is checked against the deterministic sampled probe reference.

## Unsupported Contract

The closeout explicitly does not claim:

- continuous or swept-volume collision;
- exact solid-contact collision;
- paper reproduction;
- authors-code comparison;
- public speedup wording;
- true zero-copy;
- package-install support;
- no robot-specific native ABI;
- robot/link/pose/planner/collision native ABI.

## What This Benchmark Added to RTDL

Robot collision forced RTDL to support repeated dynamic query workloads where
the static scene is reusable but query geometry changes by app state. The main
language/runtime improvements are:

- generic grouped finite 3D segment query contract;
- prepared static triangle scene reuse for Embree and OptiX;
- reusable host query/output buffers;
- native OptiX device-resident grouped segment query buffers;
- OptiX compact group-flag any-hit continuation with no per-segment record
  materialization;
- count-only result mode for screening workloads;
- phase-separated benchmark telemetry for query packing, traversal, and output
  postprocess;
- tests that prevent app vocabulary from entering active native engines.

## Final Matrix

Final pod matrix command:

```bash
ssh root@157.157.221.29 -p 23792 -i ~/.ssh/id_ed25519_rtdl_codex
cd /workspace/rtdl_python_only
CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc \
RTDL_NVCC=/usr/local/cuda/bin/nvcc OPTIX_PREFIX=/workspace/vendor/optix-dev \
LD_LIBRARY_PATH=/workspace/rtdl_python_only/build:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-} \
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py \
  --matrix --final-matrix --dataset scaled --pose-count 64 --obstacle-count 16 --link-count 3 \
  --repeats 7 --warmup 2
```

Pod environment:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 570.133.07
- CUDA: 13.0 (`/usr/local/cuda`)
- OptiX headers: `/workspace/vendor/optix-dev`
- Dataset: `scaled`
- Shape: 64 poses, 3 links, 16 obstacles, 32 static triangles, 192 query groups,
  1728 finite segment probes
- Protocol: 7 repeats, first 2 warmup rows dropped

Pod final matrix:

| Mode | Backend | Status | Tail Median Total (s) | Correctness |
| --- | --- | --- | ---: | --- |
| `cpu_reference` | Python | ok | 0.3339872658252716 | reference |
| `embree_prepared` | Embree | ok | 0.008597038686275482 | matches sampled probe |
| `embree_prepared_buffers` | Embree | ok | 0.00010654330253601074 | matches sampled probe |
| `optix_prepared` | OptiX | ok | 0.006283417344093323 | matches sampled probe |
| `optix_prepared_buffers` | OptiX | ok | 0.0001258254051208496 | matches sampled probe |
| `optix_prepared_device_buffers` | OptiX | ok | 0.00008090585470199585 | matches sampled probe |
| `optix_prepared_device_count` | OptiX | ok | 0.00005284696817398071 | count matches sampled probe |

Supplemental local Embree matrix:

| Mode | Backend | Status | Tail Median Total (s) |
| --- | --- | --- | ---: |
| `cpu_reference` | Python | ok | 0.12318500000037602 |
| `embree_prepared` | Embree | ok | 0.0024144580002030125 |
| `embree_prepared_buffers` | Embree | ok | 0.00003295799979241565 |

The local matrix was collected with `.venv-rtdl-scipy/bin/python` because the
default Mac `python3` environment does not include `numpy`, which the Embree
runtime imports.

## Performance Interpretation

The matrix confirms the benchmark's core engineering lesson: for this app
shape, repeated query packing and result materialization dominate the naive
prepared path more than RT traversal itself.

Measured internal ratios on the pod:

- `optix_prepared / optix_prepared_buffers = 49.937588820464235x`
- `optix_prepared_buffers / optix_prepared_device_buffers = 1.5552076618473156x`
- `optix_prepared_device_buffers / optix_prepared_device_count = 1.5309460031016495x`
- `embree_prepared / embree_prepared_buffers = 80.69055944055944x`

These are internal exact-subpath ratios only. They do not authorize public speedup claims
because they are not whole-application claims, not authors-code
comparisons, and not reviewed public wording.

## Native Boundary

Active native Embree and OptiX files remain free of robot, collision, link,
pose, joint, kinematic, and planner vocabulary. Native APIs are expressed as
generic RTDL primitives: prepared static triangle scenes, grouped finite segment
queries, any-hit flags, and count-style reductions.

The benchmark app owns domain lowering and semantics. Native engines own only
generic traversal/result primitives.

## Final Conclusion

The robot-collision benchmark app is finished for this RTDL cycle. It has
served its purpose: it exposed repeated-query overhead and pushed RTDL toward
prepared query reuse, native device-resident query buffers, and scalar result
consumption.

The correct claim is narrow: RTDL now has reusable generic primitives for
sampled feasibility screening over static triangle scenes with grouped finite
segment queries, backed by Embree and OptiX evidence. The correct claim is not
that RTDL is a general robot-collision solver.

## Deferred Work

Future work should be separate from this benchmark closeout:

- true device-side scalar reduction for count-only results;
- partner/device-column handoff for zero-copy-style pipelines;
- continuous or swept collision;
- paper/authors-code comparison after official code and datasets are scoped;
- a different benchmark app, such as RayDB, to force different RTDL pressure.

## Artifacts

- `docs/reports/goal2491_robot_collision_finish_pod/summary.json`
- `docs/reports/goal2491_robot_collision_finish_pod/pod_final_matrix.json`
- `docs/reports/goal2491_robot_collision_finish_local_matrix.json`

## Consensus

Goal2491 requires at least 2-AI consensus before final project closure. Public
wording or broader speedup claims would require 3-AI consensus.
