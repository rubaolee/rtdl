# Goal2483 Consensus: Robot Collision OptiX Contract

Date: 2026-05-21

Consensus: Approved

Goal2483 is complete.

## Reviewed Artifacts

- `docs/reports/goal2483_robot_collision_optix_contract_2026-05-21.md`
- `docs/reports/goal2483_optix_contract_pod/summary.json`
- `docs/reviews/goal2483_gemini_review_robot_collision_optix_contract_2026-05-21.md`
- `docs/reviews/goal2483_claude_review_robot_collision_optix_contract_2026-05-21.md`
- `scripts/goal2483_optix_contract_pod_runner.py`
- `tests/goal2483_robot_collision_optix_contract_test.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`

## Consensus Finding

Codex, Gemini, and Claude agree that Goal2483 satisfies the Goal2481 contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

The accepted implementation is a generic prepared static 3D triangle scene plus
grouped finite 3D segment any-hit flags on OptiX. It mirrors the Goal2482 Embree
contract surface and does not introduce native robot, collision, link, pose,
joint, kinematic, or planner APIs.

## Review Results

Gemini:

- Verdict: Approved
- Blocking Issues: None
- Main non-blocking notes: backend `traversal` timing is not pure RT-core time;
  top-level and runtime claim-boundary schemas should match; stale WIP report
  should be removed.

Claude:

- Verdict: Approved
- Blocking Issues: None
- Main non-blocking notes: same as Gemini: clarify the traversal timer, align
  claim-boundary fields, and remove the stale WIP artifact.

Codex disposition:

- Removed `docs/reports/goal2483_optix_contract_wip_2026-05-21.md`.
- Added `row_witnesses: false` to the top-level pod claim-boundary schema and
  updated the pod runner so future regenerated artifacts preserve the field.
- Documented that the current `traversal` timing covers OptiX launch, stream
  synchronization, flag download, and native host group reduction before Python
  receives the result. The value remains smoke-scale correctness timing only.

## Accepted Evidence

- The OptiX backend builds on the recorded NVIDIA RTX A5000 pod.
- Pod access used `ssh root@69.30.85.236 -p 22190 -i ~/.ssh/id_ed25519_rtdl_codex`.
- `make build-optix` returned 0 on the pod.
- The runtime probe returned the expected flags `[1, 0, 1, 0, 1]`.
- The Goal2483 focused pod suite passed: `Ran 6 tests in 1.012s, OK`.
- The Goal2479-2483 pod slice passed: `Ran 29 tests in 1.779s, OK`.
- Active native Embree and OptiX files remain free of forbidden app vocabulary.
- The final report and pod artifact explicitly block public speedup, paper
  reproduction, exact solid contact, continuous/swept support, native app API,
  row-witness, and release/tag claims.

## Claim Boundary

Goal2483 still does not claim:

- paper reproduction;
- authors-code comparison;
- public speedup;
- exact solid contact;
- continuous or swept collision support;
- row witnesses;
- native robot, link, pose, planner, or collision API support;
- zero-copy query input or output;
- release/tag action.

## Next Step

Goal2484 can proceed either by adding Python-side robot-collision benchmark
lowering on top of this generic Embree/OptiX contract or by expanding the next
contract only if the benchmark requires a primitive that cannot be represented
as grouped finite segment any-hit flags.
