# Goal3840 Current Benchmark Adequacy After Goal3838

Date: 2026-06-08

Status: internal metadata cleanup; no new runtime artifact.

## Purpose

Goal3838 added current A5000 evidence that RayJoin public-CDB LSI and overlay
active-count rows now have no-RawKernel Numba scalar-count references. That
closed the partner-coverage gap left after Goal3834's PIP-only Numba baseline.

Goal3840 updates the programmatic current benchmark adequacy metadata so the
advisory API tells the same story as the learner docs:

```python
import rtdsl as rt
rt.current_benchmark_adequacy()
```

## Metadata Change

The current adequacy version is now:

`rtdl.v2_10.benchmark_adequacy_after_goal3838.v1`

The spatial RayJoin row now records:

- Goal3834 no-RawKernel Numba PIP scalar-count reference;
- Goal3838 no-RawKernel Numba LSI and overlay active-count references;
- Goal3838 count parity across Numba, CuPy, and RTDL/OptiX;
- RTDL/OptiX remains the recommended primitive-first route for LSI/overlay
  scalar contracts because it is about `260x` faster than the Numba/CuPy dense
  partner baselines on the bounded public-CDB packet.

## Claim Boundary

This cleanup does not authorize:

- release action;
- public speedup wording;
- RayJoin paper reproduction claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner selection.

It only keeps internal advisory metadata consistent with the current evidence.
