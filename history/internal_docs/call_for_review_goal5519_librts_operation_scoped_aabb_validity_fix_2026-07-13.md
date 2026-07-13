# Call For Review: Goal5519 LibRTS Operation-Scoped AABB Validity Fix

Please strictly review Goal5519 as a generic RTDL semantic regression fix.

## Files

- `history/internal_docs/goal5519_librts_operation_scoped_aabb_validity_fix_result_2026-07-13.md`
- `Paper-reproduction-apps/librts-paper/results/goal5519_operation_scoped_aabb_validity_fix_gate.json`
- `Paper-reproduction-apps/librts-paper/build_goal5519_librts_operation_scoped_aabb_validity_gate.py`
- `Paper-reproduction-apps/librts-paper/tools/goal5519_range_contains_semantic_audit.py`
- `Paper-reproduction-apps/librts-paper/tools/goal5519_range_contains_cached_count_probe.py`
- `Paper-reproduction-apps/librts-paper/tools/goal5519_operation_scoped_validity_probe.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/aabb_index.py`
- `tests/goal5519_librts_operation_scoped_aabb_validity_fix_test.py`

## Review questions

1. Does the exact input identity support the original `101418` versus
   `101339` disagreement?
2. Does the float32 audit account for exactly 79 omitted matches?
3. Does the same-column native A/B isolate the Goal5508 validity guard?
4. Is the author source audit consistent with operation-specific validity?
5. Is retaining the failed two-row author subset as a negative control honest?
6. Is strict validity now scoped only to `range_intersects`?
7. Does the three-operation hardware fixture behaviorally distinguish the
   contract?
8. Does the corrected full exact case match the author count?
9. Do the prefix and degenerate range-intersects regressions preserve Goal5508?
10. Is the implementation app-neutral and free of LibRTS identity?
11. Are relation, matrix, performance, figure, full-paper, zero-copy,
    author-parity, and Embree claims correctly left closed?

## Requested answer shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-11:
```
