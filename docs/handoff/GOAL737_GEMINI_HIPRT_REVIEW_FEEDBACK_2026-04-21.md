# Goal 737: Gemini HIPRT Review Feedback

Date: 2026-04-21

Please revise the HIPRT KNN fallback patch/report before we treat it as
accepted.

## What Looks Useful

The `_add_neighbor_rank(...)` change in `src/rtdsl/hiprt_runtime.py` is in the
right direction: returned neighbor rows should be sorted by query and distance
before assigning `neighbor_rank`.

The standalone script
`scripts/goal728_hiprt_knn_fallback_sort_test.py` passes locally and catches
the old out-of-order ranking issue.

## Required Corrections

1. The sort key should be deterministic for ties:

```python
key=lambda row: (
    int(row["query_id"]),
    float(row.get("distance", 0.0)),
    int(row["neighbor_id"]),
)
```

2. The report must not say this fully fixes HIPRT KNN correctness unless the
native HIPRT fixed-radius call is proven to return all in-radius candidates
before Python ranks them. Current wrappers call fixed-radius with `k_max=k`.
If the native side truncates to `k` before sorting, Python can only sort the
returned subset; it cannot recover nearer neighbors that were omitted by the
native buffer cap.

3. Replace or supplement the standalone script with a real unittest, or add it
to an existing test suite, so release gates can run it automatically.

4. Reword the report boundary:

- Acceptable: "This fixes deterministic ranking of returned HIPRT fallback KNN
  rows."
- Not acceptable yet: "This makes HIPRT KNN equivalent to a true priority
  queue" or "functionally complete KNN correctness" unless native candidate
  completeness is proven.

## Requested Next Step

Please update the code/test/report with the tie-breaker and the tighter
boundary, then provide the exact commands run. Do not expand this into a HIPRT
performance claim or AMD GPU validation claim.
