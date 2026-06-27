# Reading Performance Results

RTDL reports performance at two levels:

- app rows, such as the 10 promoted benchmark apps;
- operator rows, such as fixed-radius, any-hit, grouped reduction, or AABB
  index queries.

Read each number with its denominator and scope.

## What To Check

For each ratio, look for:

- the exact operator surface or benchmark app row;
- the compared baseline;
- the metric, such as hot path, wall time, or phase time;
- the hardware path, such as NVIDIA OptiX / RT cores;
- the partner scope, such as Torch CUDA, CuPy, Numba, or RTDL native;
- the input scale.

## Current V4 Reading

The current app matrix has rows for V2.14, V3.0.2, and V4.0 on all 10 promoted
benchmark apps. It has two material hot-path rows over V2.14 and similar-speed or modest-gain rows elsewhere.

Most V4.0 measured operators are 1.2x-1.7x against their stated brute-force partner/CPU baselines. Point-group nearest witness and AABB all-ops are larger
scale-dependent algorithmic-complexity wins because they compare indexed
RT-style work against much less favorable alternatives.

The V4 custom predicate early-exit workflow measured `4.633x` against the
legacy materialized-device fallback for that workflow. It is a V4
operator-pushdown workflow result, separate from the legacy 10-app table.

## Practical Rule

Use exact rows. For example:

```text
Triangle counting measured 4.360x V4/V2.14 on the current NVIDIA RT-core hot
path.
```

Avoid summarizing the release as if every row has the same behavior. The useful
performance story is the table distribution:

- two material V4/V2.14 app rows;
- several similar-speed or modest-gain app rows;
- measured operator-level improvements where the operator surface applies;
- a separate V4-specific custom predicate workflow win.
