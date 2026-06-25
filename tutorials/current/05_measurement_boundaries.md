# Measurement Boundaries

RTDL V4 performance text must be specific.

Use:

- the exact operator surface or scorecard row;
- the compared baseline;
- the measured metric;
- the hardware and driver;
- the partner scope;
- whether timing is setup, warmup, hot loop, phase total, or wall time.

The Goal4639 scorecard passed for documented operator surfaces. That supports
exact surface-level wording, not broad whole-application claims.

Do not say:

```text
V4 makes all RTDL apps faster.
```

Do say:

```text
On the Goal4639 RTX A5000 scorecard, the AABB all-ops count surface recorded a
164.716x representative ratio in its documented same-contract-family gate.
```

For the full rule, read
[../../docs/learn/performance_wording.md](../../docs/learn/performance_wording.md).
