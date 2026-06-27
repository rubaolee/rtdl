# Goal 163: OptiX Correctness Reaudit

## Why

After the visual-demo OptiX hitcount mismatch, the correct response is not just
to patch that one case. We need a bounded retest over the historical
OptiX-related task surface to know whether current `main` is still coherent.

Because OptiX is a deterministic geometric-query backend in RTDL, any mismatch
against accepted CPU/reference behavior is a real correctness problem.

## Goal

Reaudit the OptiX-related task surface on a fresh Linux clone after the
`ray_tri_hitcount` parity repair.

## Scope

The reaudit covers:

- historical OptiX validation and benchmark test modules
- OptiX baseline/backend closure test modules
- OptiX-facing Jaccard surface tests
- the new Goal 162 visual-demo OptiX parity test
- one post-fix visual-demo smoke rerun on Linux

## Acceptance

- rerun the bounded OptiX-related unittest slice on a fresh Linux clone
- record the exact module set and result
- rerun the visual-demo OptiX smoke case and record parity
- write the current honesty boundary if the fix is correctness-first rather than
  a pure native-only closure
- obtain review coverage with at least one Claude or Gemini review before
  closure
