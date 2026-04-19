# Goal 568 External Review: HIPRT Prepared DB Table Reuse

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6

**Verdict: ACCEPT**

---

## Implementation Correctness

**PASS.**

`PreparedDbTable` is a well-formed RAII struct: it owns the HIPRT runtime, row-value device buffer, AABB geometry, function table, and compiled match kernel. The destructor calls `hiprtDestroyFuncTable` and `hiprtDestroyGeometry` in the correct order. Copy constructor and copy-assignment are deleted, preventing double-free. The Python `PreparedHiprtDbTable` wrapper adds `close()` and `__enter__`/`__exit__` to enforce deterministic cleanup.

AABB placement at `x = float(i)` with `eps = 0.25f` is correct. At 100k rows `float(99999)` still has 5 significant digits, well within float precision, so the epsilon is sufficient and the fix is properly motivated.

The empty-table path is handled at the Python layer (returns an empty object before calling native), consistent with how other prepared HIPRT types handle zero-element inputs.

Text field encoding into integer domains at prepare time, with reverse-map decode at query time, is logically sound for the bounded-table scope this feature targets.

---

## Test Coverage

**PASS.**

The test suite covers:

- Direct `PreparedHiprtDbTable` reuse across three distinct predicate sets for `conjunctive_scan`.
- `grouped_count` and `grouped_sum` with text group-key decoding against CPU reference.
- High-level `rt.prepare_hiprt(...)` for all three kernel types.
- Empty prepared table (all three workloads return empty results, no crash).
- Regression guard for existing one-shot HIPRT DB parity (`goal559` suite).

14 tests pass cleanly. All prepared results are validated against the CPU Python reference.

---

## Performance / PostgreSQL Comparison Honesty

**PASS — comparison is fair and correctly disclosed.**

The perf script measures:

| Phase | HIPRT | PostgreSQL |
|---|---|---|
| Setup (one-time) | `prepare_seconds` — single timed call | `setup_seconds` — single timed call covering table create + index |
| Query (repeated) | `query_seconds` — median of N iterations | `query_seconds` — median of N iterations |

Both sides have a one-time setup cost and a per-query cost measured identically. The speedup figure (`~745–1039x vs one-shot`) is computed as `one_shot_seconds / query_seconds`, which is the correct formula and represents the actual elimination of per-query rebuild overhead.

The `matches_cpu` field in the JSON is `true` for every backend including PostgreSQL, confirming correctness parity, not just timing.

The "Honest Interpretation" section correctly limits the claim to:
- A bounded synthetic 100k-row fixture, not a general database benchmark.
- No NVIDIA RT cores (HIPRT/CUDA path only, no hardware acceleration).
- Aggregation still host-side after GPU row candidate discovery.
- PostgreSQL remains the correct system for persistence, SQL planning, concurrency, joins, and unbounded tables.

These disclosures are accurate and complete. No overclaiming.

---

## No Blockers

All stated non-blocking limits (host-side aggregation, fixed string domain, synthetic fixture, no RT cores) are accurately characterized and do not affect the correctness or the scoped performance claim.

---

## Summary

Goal 568 correctly implements prepared HIPRT DB table reuse for `conjunctive_scan`, `grouped_count`, and `grouped_sum`. The implementation is RAII-correct, the test coverage is complete, and the performance comparison against CPU/Embree/OptiX/Vulkan/PostgreSQL is honest and properly scoped. **ACCEPT.**
