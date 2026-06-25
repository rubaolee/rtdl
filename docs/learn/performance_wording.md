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
stated floor on the RTX A5000 POD.
```

Good:

```text
The V4 fixed-radius count-threshold Torch CUDA surface recorded a 1.697x
representative scorecard ratio in the Goal4639 run.
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

- "RTDL V4.0.0 is the formal high-performance generic RT-core operator release";
- exact measured operator-surface results;
- exact Goal4639 scorecard summary;
- exact partner and hardware scope;

Not allowed:

- broad V4 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy wording;
- Tier-3 callback/PTX support wording;
- raw OptiX callback support wording;
- CuPy performance wording;
- embedding, C ABI, or non-Python host binding wording.
