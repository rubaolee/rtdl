# Performance Wording Guide

RTDL examples can be correctness examples, capability examples, or measured
performance examples. Use wording that matches the evidence you are showing.

## Use Exact Wording

When discussing performance, include:

- the command or benchmark row;
- the compared backend or baseline;
- the measured metric;
- the hardware;
- whether the timing is setup, warmup, hot loop, phase total, or wall time.

## Prefer Scoped Sentences

Good:

```text
On this measured row, backend A completed the hot loop faster than backend B.
```

Too broad:

```text
The whole system is faster for every workload.
```

## Backend And Partner Choice

Backends and partners are explicit choices. Choose them because they match the
workload and dependency environment, then measure the exact route you plan to
describe.
