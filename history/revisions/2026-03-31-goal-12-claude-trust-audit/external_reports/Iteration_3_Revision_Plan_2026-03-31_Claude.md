Written from the Claude CLI response to the Goal 12 revision-planning prompt.

## Accepted Issues

All four discrepancies are accepted for this round:

1. `boundary_mode` is currently a no-op in execution semantics
2. Goal 10 workloads over-claim BVH / Embree acceleration
3. LSI all-hits behavior requires an explicit correctness check
4. Goal 10 workloads are absent from the standard baseline/evaluation infrastructure

## Revision Plan

- Issue 1
  - thread `boundary_mode` into the CPU path in `reference.py`
  - make inclusive-boundary behavior explicit in both `reference.py` and `rtdl_embree.cpp`
  - ensure the runtime path does not silently discard the option
- Issue 2
  - change Goal 10 lowering to report `accel_kind="native_loop"` rather than `bvh`
  - update the plan schema to allow that backend-plan value
  - update docs to explain the local backend strategy honestly
- Issue 3
  - verify LSI all-hits behavior with a multi-hit regression case
  - if needed, replace the single-hit assumption in the local Embree path
- Issue 4
  - extend `baseline_runner.py` and `evaluation_matrix.py` to cover the two Goal 10 workloads
  - bring the standard local benchmark/reporting surface in line with the current workload surface

## Acceptance Criteria

Claude’s plan summary required binary closure checks around:

- explicit boundary-mode semantics
- honest Goal 10 backend labels
- schema support for revised lowering
- regression protection for LSI all-hits behavior
- Goal 10 inclusion in the standard local baseline/evaluation path
- green test suite and parity checks on the revised snapshot

## Review Method

Final review should use:

- code diff inspection
- `make test`
- targeted spot-checks for the revised areas

Consensus to revise
