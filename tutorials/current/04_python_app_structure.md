# Python App Structure

Status: current v2.14 source-tree tutorial.

Goal: write app code without pushing app semantics into the RTDL engine.

## The Split

```text
Python app:
  parse input
  name app concepts
  choose primitive
  validate result
  present the answer

RTDL primitive:
  consume typed columns
  run backend traversal or generic reduction
  return typed columns, flags, counts, rows, witnesses, or summaries
```

The app can call a result "clusters", "intersections", "nearest roads", or
"Hausdorff distance". The primitive should still be named by the generic
contract it executes.

## Minimal File Shape

A normal RTDL app usually has:

```text
1. input builder
2. CPU oracle or small correctness check
3. RTDL primitive call
4. optional partner continuation
5. result comparison
6. timing metadata
```

That shape keeps learner code inspectable and benchmark code auditable.

## Start With A Small Input

Always run a tiny input first. It should complete quickly and let you inspect
the result. Then increase the dataset and only then measure performance.

## App-Specific Code Is Allowed

RTDL does not forbid Python, NumPy, CuPy, Numba, C/C++, or CUDA code in the app.
The boundary is claim ownership:

- RTDL owns the reviewed primitive contract.
- The app owns custom continuation unless RTDL ships that continuation as a
  generic reviewed primitive.

## Next

Continue with [Partner Columns With CuPy Or Numba](05_partner_columns_cupy_numba.md).
