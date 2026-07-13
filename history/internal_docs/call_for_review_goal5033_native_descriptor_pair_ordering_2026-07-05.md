# Call For Review: Goal5033 Native Descriptor Pair Ordering

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5033_native_descriptor_pair_ordering_result_2026-07-05.md
```

## Requested Verdict

```text
approve_goal5033_native_descriptor_ordering_scoped_device_default
```

or provide a stricter verdict.

## Review Questions

1. Did Goal5033 solve a generic ordering problem rather than add a RayJoin-specific core primitive?
2. Is reusing `run_cuda_lexsort_i64_f64_i64_i64_device` for descriptor pair ordering a valid generic continuation, given the app only supplies `(label_a, label_b, length)` columns?
3. Does the fallback to legacy Numba bitonic preserve compatibility without hiding the POD evidence?
4. Do the artifacts prove the native descriptor lexsort path was actually used (`downstream_consumer_partner` and `...native_lexsort... = true`)?
5. Are the structural anchors stable enough to compare against Goal5032?
6. Does the N-run matrix justify saying the device carrier now beats CPU carrier in the prepared LSI base-session query-batch writer-free binary regime?
7. Is it acceptable to recommend a scoped default switch for that regime only?
8. Does the report avoid overclaiming cold CLI, paper-text, author parity, or broad Section 5.7 performance?
9. What remaining bottleneck should be attacked next, if any, after descriptor ordering is no longer the blocking issue?

## Boundary To Enforce

If approved, the approval is only for:

```text
prepared LSI base-session + distinct chain-contiguous query batches + writer-free binary route
```

It must not be read as approval for:

```text
cold CLI one-shot
paper text output
author-performance parity
general RayJoin or Section 5.7 performance
```
