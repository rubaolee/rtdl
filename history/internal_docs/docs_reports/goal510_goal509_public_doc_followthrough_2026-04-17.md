# Goal 510: Goal509 Public Documentation Follow-Through

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal509 added correctness-gated Linux performance evidence for the robot
collision screening and Barnes-Hut force approximation apps. Goal510 refreshes
the public documentation surface so users do not see only the older Hausdorff
performance story.

## Files Updated

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/tests/goal510_app_perf_doc_refresh_test.py`

## Corrections Made

- Front page now links Goal509 directly as robot/Barnes-Hut Linux performance
  evidence.
- v0.8 app summaries now state that robot collision has accepted CPU/Embree/OptiX
  evidence and that Vulkan is intentionally not exposed for that app because it
  fails per-edge hit-count parity.
- Barnes-Hut docs now state that CPU/Embree/OptiX/Vulkan pass the bounded
  candidate-generation evidence, but that full-app timing is dominated by
  Python opening-rule and force-reduction work.
- Release-facing examples now include backend commands for robot OptiX and
  Barnes-Hut Embree/OptiX/Vulkan, while preserving the unsupported robot Vulkan
  boundary.
- Capability and architecture docs now distinguish app-level candidate-row
  evidence from full robotics or full N-body solver claims.

## Non-Claims Preserved

- Goal510 does not make `v0.8` a released language line.
- Goal510 does not claim robot Vulkan support.
- Goal510 does not claim faithful Barnes-Hut acceleration or full N-body solver
  acceleration.
- Goal510 does not claim RT-core performance because Goal509 used GTX 1070
  evidence.

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal510_app_perf_doc_refresh_test tests.goal508_hausdorff_perf_doc_refresh_test tests.goal509_app_perf_harness_test -v
```

Result: `Ran 10 tests in 0.316s`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile tests/goal510_app_perf_doc_refresh_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal510 is accepted. The public docs are now consistent with Goal509's accepted
and rejected backend evidence.

## AI Review Consensus

- Claude review: `PASS`; public docs now honestly reflect Goal509's
  robot/Barnes-Hut performance evidence without overclaiming.
- Gemini Flash review: `ACCEPT`.
- Codex conclusion: `ACCEPT`; the public front page, tutorials, examples,
  architecture, and capability-boundary docs now carry the same Goal509 backend
  and performance boundaries.
