# RTDL v2.14 Public Wording Boundaries

Status: current public wording rule.

Use this page when writing README text, papers, talks, benchmark summaries, or
project pages.

## Safe Wording

```text
Selected prepared, traversal-heavy RTDL/OptiX benchmark rows show strong
speedups over same-contract non-RT baselines in v2.14 evidence.
```

```text
RTDL v2.14 supports explicit partner continuation with CuPy, Numba, NumPy, or
application-owned code when the RTDL primitive does not finish the whole app.
```

```text
Benchmark app rows are contract-specific. Each row names the primitive,
baseline, partner policy, dataset scale, and claim boundary.
```

## Blocked Wording

Do not write:

```text
RTDL accelerates all benchmark apps.
```

```text
RTDL is faster than RayJoin, RTNN, LibRTS, or Barnes-Hut as complete systems.
```

```text
RTDL automatically accelerates arbitrary CuPy or Numba programs.
```

```text
RTDL v2.14 includes archived experimental APIs.
```

## Publication Checklist

Before publishing a speedup, name:

- the exact row or app contract;
- the RTDL primitive or composition;
- the backend;
- the partner, if any;
- the dataset scale;
- the baseline;
- whether the number is hot-query, cold-total, or end-to-end app time.

If any item is missing, use compatibility, capability, or coverage wording
instead of performance wording.
