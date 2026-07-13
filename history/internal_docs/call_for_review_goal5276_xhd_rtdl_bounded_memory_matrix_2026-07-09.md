# Call For Review - Goal5276 X-HD RTDL Bounded Memory Matrix

Please strictly review Goal5276:

```text
history/internal_docs/goal5276_xhd_rtdl_bounded_memory_matrix_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
tests/goal5276_xhd_rtdl_bounded_memory_matrix_test.py
```

Context files:

```text
history/internal_docs/goal5275_xhd_native_memory_telemetry_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_tiny3d_native_memory_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
```

## Context

Goal5275 proved that the native OptiX cell-MBR route can report measured
`accel_output_bytes`, which the RTDL app maps to a status-bearing `BVH` memory
field.  Goal5276 gathers those artifacts into an RTDL memory matrix.

This is intentionally **not** an author Figure 11 reproduction.  The matrix is
bounded/pilot evidence and keeps `same_denominator_author_figure11=false`.

## Review Questions

1. Is it appropriate to call the Goal5276 artifact a "bounded RTDL memory
   matrix" rather than a Figure 11 reproduction?
2. Does the matrix honestly preserve status-bearing fields rather than flattening
   them into raw numbers?
3. Is the `BVH` field honest now that it is measured as native OptiX
   `accel_output_bytes`, while still saying this is not author Figure 11 parity?
4. Are `Grid`, `MBRs B`, and `WL` correctly kept as estimates rather than
   native allocator measurements?
5. Is `WL Heavy Peak` correctly left unavailable instead of zero or estimated?
6. Does the matrix correctly refuse author-vs-RTDL memory ratios and mark
   `same_denominator_author_figure11=false` for every row?
7. Is it acceptable that the current rows are bounded probes (tiny3D and
   sample256) rather than exact paper Figure 11 rows?
8. Does the helper stay app-owned and avoid adding X-HD/Figure-11 semantics to
   RTDL core?
9. Do the tests sufficiently guard against overclaiming Figure 11 reproduction
   or memory parity?
10. What should the next work be: peak/heavy-worklist telemetry, or an explicit
    review decision that RTDL's current route lacks an author-like heavy-worklist
    denominator and should remain non-comparable?

## Expected Answer Shape

```text
Verdict: approve_goal5276_rtdl_bounded_memory_matrix | approve_with_required_amendments | reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
```

Suggested approval label, if appropriate:

```text
approve_goal5276_xhd_rtdl_bounded_memory_matrix__figure11_still_not_reproduced
```
