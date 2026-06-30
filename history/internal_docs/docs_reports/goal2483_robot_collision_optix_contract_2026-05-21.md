# Goal2483 Robot-Collision OptiX Contract Parity

Date: 2026-05-21

Status: Complete with Codex, Gemini, and Claude consensus.

## Scope

Goal2483 completes the OptiX side of the Goal2481/Goal2482 app-agnostic
contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

Contract shape:

```text
prepared static 3D triangle scene
+ grouped finite 3D segment probes
-> byte-per-query-group uint8 flags
```

This is a generic RTDL primitive contract. The native OptiX engine does not
expose robot, collision, link, pose, joint, kinematic, or planner vocabulary for
this path. Application meaning remains in Python examples/tests.

## Implementation

Native OptiX ABI:

```text
rtdl_optix_static_triangle_scene_3d_create
rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags
rtdl_optix_static_triangle_scene_3d_destroy
```

Python API:

```text
PreparedOptixStaticTriangleScene3D
prepare_optix_static_triangle_scene_3d
run_optix_grouped_segment_any_hit_flags_3d
```

Implementation details:

- The static triangle set is uploaded once and prepared as a reusable OptiX GAS.
- Query segments are validated as finite, non-zero-length 3D segments.
- Query segments are converted to normalized 3D rays with segment length as
  `tmax`.
- OptiX returns internal per-segment any-hit records.
- Native host continuation reduces per-segment records to one `uint8` flag per
  query group.
- The Python wrapper records phase timing, precision metadata, transfer
  metadata, and claim boundaries.

## Pod Evidence

Pod access used:

```text
ssh root@69.30.85.236 -p 22190 -i ~/.ssh/id_ed25519_rtdl_codex
```

The user-provided `~/.ssh/id_ed25519` path was not present on this Mac; the
available working RTDL key was `~/.ssh/id_ed25519_rtdl_codex`.

Environment:

```text
GPU: NVIDIA RTX A5000
Driver: 570.211.01
CUDA: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: /workspace/vendor/optix-dev/include/optix.h
Source commit: a9193856547bf692069955a3dbaf6c3e00c09b1b
```

Artifact:

```text
docs/reports/goal2483_optix_contract_pod/summary.json
```

Build command captured by the artifact:

```text
make build-optix
```

Build result:

```text
returncode: 0
elapsed_sec: 28.197735376656055
output: build/librtdl_optix.so
```

The build emitted only the CUDA deprecation warning for offline compilation
architectures below `<compute/sm/lto>_75`.

## Runtime Parity

Goal2483 fixture expected flags:

```text
[1, 0, 1, 0, 1]
```

OptiX runtime probe result:

```text
[1, 0, 1, 0, 1]
```

Runtime probe metadata:

```text
backend: optix
contract: PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
flag_format: uint8_byte_per_query_group
triangle_count: 1
segment_count: 5
group_count: 5
prepared_scene_used: true
prepared_reused: true
```

Phase timing from the runtime probe:

```text
prepare_build: 0.13932712003588676
query_pack: 0.0002368837594985962
traversal: 0.000145477
output_postprocess: 0.00003285519778728485
```

The `traversal` timing is a backend phase timer for this ABI, not a pure RT-core
timer. It includes OptiX launch, stream synchronization, flag download, and the
native host group reduction before returning to Python. These timings are
smoke-scale correctness timings only. They do not authorize a public speedup
claim.

## Test Evidence

Goal2483 focused pod test:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2483_robot_collision_optix_contract_test
```

Result:

```text
Ran 6 tests in 1.012s
OK
```

Goal2479-2483 pod slice:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2479_robot_collision_benchmark_roadmap_test \
  tests.goal2480_robot_collision_cpu_reference_app_test \
  tests.goal2481_robot_collision_generic_contract_design_test \
  tests.goal2482_robot_collision_embree_contract_test \
  tests.goal2483_robot_collision_optix_contract_test
```

Result:

```text
Ran 29 tests in 1.779s
OK
```

Local checks before pod:

```text
Goal2483 local: Ran 6 tests in 0.018s, OK (skipped=1)
Goal2479-2483 local: Ran 29 tests in 0.169s, OK (skipped=1)
```

The local skip was the expected NVIDIA-only OptiX runtime test. On the pod,
that test ran and passed.

Post-consensus local checks:

```text
Goal2483 local: Ran 8 tests in 0.017s, OK (skipped=1)
Goal2479-2483 local: Ran 31 tests in 0.156s, OK (skipped=1)
```

## Claim Boundary

Goal2483 claims:

- Same-contract OptiX runtime parity for the smoke fixture.
- Native OptiX build succeeds on the recorded A5000 pod environment.
- The native OptiX implementation is app-vocabulary-free for this contract.
- The Python API exposes the same contract shape as the Goal2482 Embree path.

Goal2483 does not claim:

- paper reproduction;
- authors-code comparison;
- public speedup;
- exact solid contact;
- continuous or swept collision support;
- native robot/link/pose/planner/collision APIs;
- zero-copy query input or output;
- release or tag action.

## External Review

Gemini and Claude independently approved Goal2483 for closure. Their shared
non-blocking notes were resolved or documented before consensus:

- the stale WIP report was removed;
- the top-level pod claim-boundary schema now includes `row_witnesses: false`;
- the backend `traversal` timing semantics are documented as launch, sync, flag
  download, and native host group reduction, not as a pure RT-core timer.

Consensus artifact:

```text
docs/reviews/goal2483_codex_gemini_claude_consensus_robot_collision_optix_contract_2026-05-21.md
```

## Conclusion

Goal2483 is complete: the generic prepared 3D triangle scene plus grouped finite
3D segment any-hit flag contract now has both Embree and OptiX implementations
with same-fixture parity, NVIDIA pod evidence, and external review consensus.
