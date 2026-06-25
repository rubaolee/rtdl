# Performance Wording Guide

RTDL examples can be correctness examples, capability examples, or measured
performance examples. Use wording that matches the evidence you are showing.

## Use Exact Wording

When discussing performance, include:

- the exact operator surface or benchmark row;
- the compared baseline;
- the measured metric;
- the hardware and driver scope;
- whether timing is setup, warmup, hot loop, phase total, or wall time;
- the partner scope, such as Torch CUDA, Numba, or RTDL native.

## Current V4 Wording

Good:

```text
On the frozen Goal4639 scorecard, the measured operator surface passed its
stated floor against its stated brute-force partner/CPU baseline on the RTX
A5000 POD.
```

Good:

```text
The V4 fixed-radius count-threshold Torch CUDA surface recorded a 1.697x
representative scorecard ratio against the Torch brute-force/reference baseline
in the Goal4639 run.
```

Good:

```text
Most V4.0 measured operators are 1.2x-1.7x against their stated brute-force
partner/CPU baselines; point-group nearest witness and AABB all-ops are large
scale-dependent wins where the alternative is brute force or a slower
same-contract index control.
```

Too broad:

```text
V4 makes every application faster.
```

Too broad:

```text
V4 has zero-copy support.
```

## Claim Boundaries

Allowed for V4.0.0:

- "RTDL V4.0.0 is a bounded operator release for 8 documented generic RT-core
  operators that beat their stated brute-force partner/CPU baselines";
- exact measured operator-surface results;
- exact Goal4639 scorecard summary;
- exact partner and hardware scope;
- exact denominator and scale for every representative ratio;

Not allowed:

- broad V4 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy wording;
- Tier-3 callback/PTX support wording;
- raw OptiX callback support wording;
- CuPy performance wording;
- embedding, C ABI, or non-Python host binding wording.
- unqualified "high-performance" or "near-OptiX" wording.
