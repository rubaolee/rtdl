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
- the partner scope, such as Torch CUDA, CuPy, Numba, or RTDL native.

## Current V4 Wording

Good:

```text
RTDL V4.0.0 is a published Python eDSL/operator-pushdown release with 10 measured
generic operator/workflow surfaces, a complete 10-app V2.14/V3.0.2/V4.0
NVIDIA RT-core matrix, and a constrained custom predicate early-exit workflow.
The app matrix has two material hot-path rows over V2.14 and similar-speed rows
elsewhere.
```

Good:

```text
The current app matrix has two material hot-path rows over V2.14 and
similar-speed control rows elsewhere; use the table distribution rather than a
blanket all-app phrase.
```

Good:

```text
The measured operator surface passed its stated floor against its stated
brute-force partner/CPU baseline on the RTX A5000 POD.
```

Good:

```text
The V4 fixed-radius count-threshold Torch CUDA surface recorded a 1.697x
representative scorecard ratio against the Torch brute-force/reference baseline.
```

Good:

```text
Most V4.0 measured operators are 1.2x-1.7x against their stated brute-force
partner/CPU baselines; point-group nearest witness and AABB all-ops are large
scale-dependent wins where the alternative is brute force or a slower
same-contract index control.
```

Good:

```text
The V4 custom predicate early-exit workflow measured 4.633x serious-scale
primary geomean versus the V2.14/V3.0.2 materialized-device fallback, with
correctness passing; this is a V4 operator-pushdown workflow claim, not a broad
all-app claim.
```

The short rule: exact rows are allowed; broad all-app claims are not.

Too broad:

```text
V4 makes every application faster.
```

Too broad:

```text
V4 is a formal app-level high-performance release.
```

Too broad:

```text
V4 has zero-copy support.
```

## Claim Boundaries

Allowed for V4.0.0:

- "RTDL V4.0.0 is a published Python eDSL/operator-pushdown release with 10
  measured generic operator/workflow surfaces";
- exact measured operator-surface results;
- exact constrained custom predicate early-exit workflow results;
- exact app-level ratios and the current decision label
  `complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim`;
- exact partner and hardware scope;
- exact denominator and scale for every representative ratio.

Keep these phrases out of broad public claims:

- broad V4 speedup wording;
- broad V4-over-V2.14 speedup wording;
- formal app-level high-performance release wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy wording;
- Tier-3 callback/PTX support wording;
- raw OptiX callback support wording;
- broad CuPy performance wording;
- embedding, C ABI, or non-Python host binding wording;
- unqualified "high-performance" or "near-OptiX" wording.
