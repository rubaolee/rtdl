# Measurement Boundaries

RTDL V4 performance text must be specific.

Use:

- the exact operator surface or scorecard row;
- the compared baseline;
- the measured metric;
- the hardware and driver;
- the partner scope;
- whether timing is setup, warmup, hot loop, phase total, or wall time.

The V4 operator scorecard passed for documented operator surfaces. That
supports exact surface-level wording, not broad whole-application claims.

The custom predicate early-exit workflow supports a real V4 operator-pushdown
performance claim: constrained Numba predicate, RTDL-owned early-exit action,
and 4.633x serious-scale primary geomean versus the V2.14/V3.0.2
materialized-device fallback.

The current app-level V2.14/V3.0.2/V4 comparison is complete for the 10 promoted
benchmark apps on NVIDIA RT-core rows. It supports bounded wording: two material
hot-path rows over V2.14 and similar-speed control rows elsewhere.
Treat V4.0.0 as a published eDSL/operator-pushdown release and V2/V3 superset,
not as a blanket claim that every promoted benchmark app is faster.

Do not say:

```text
V4 makes all RTDL apps faster.
```

Do not say:

```text
V4 is a formal app-level high-performance release.
```

Do say:

```text
On the RTX A5000 operator scorecard, the AABB all-ops count surface recorded a
164.716x representative ratio in its documented same-contract-family gate.
```

Do say:

```text
The current app-level summary keeps the public claim bounded: current V4
evidence supports a complete matrix with bounded material wins, not broad
all-app high-performance wording.
```

Do say:

```text
The V4 custom predicate early-exit workflow measured 4.633x serious-scale
primary geomean versus the materialized-device fallback, with correctness
passing.
```

For the full rule, read
[../../docs/learn/performance_wording.md](../../docs/learn/performance_wording.md).
