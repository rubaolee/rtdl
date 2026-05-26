All three files are confirmed. Here is the verdict for each issue:

---

**Issue 1 — Pre-dedup capacity rule undocumented**

RESOLVED. The 2x bidirectional-pass rule is now documented in three places:

- `aabb_index.py:301–309` — docstring on `aabb_intersection_pair_rows_2d`: *"row_capacity must accommodate the raw pre-deduplication bidirectional-pass hit count, which can be up to twice the final unique pair count."*
- `goal2623_optix_aabb_intersection_pair_rows_2026-05-25.md:40–45` — Overflow contract section states the same rule.
- `contact_manifold/README.md:60–61` — Promotion State section explicitly warns app authors.

---

**Issue 2 — Missing GPU overflow regression test**

RESOLVED. `tests/goal2623_optix_aabb_pair_rows_test.py:121–129` adds `test_optix_pair_rows_fail_closed_on_capacity_overflow`, decorated `@unittest.skipUnless(_optix_library_available(), ...)`. On GPU hardware it fires `aabb_intersection_pair_rows_2d(..., backend="optix", row_capacity=1)` and asserts `RuntimeError` matching `"failure_mode=fail_closed_overflow"`. The report explicitly describes this as a "GPU-skipped OptiX overflow regression test."

---

**Issue 3 — Missing RtdlAabbPairRow layout static_assert**

RESOLVED. `rtdl_optix_prelude.h:105–107` now has three `static_assert`s immediately after the struct definition:

```cpp
static_assert(offsetof(RtdlAabbPairRow, query_id)   == 0, ...);
static_assert(offsetof(RtdlAabbPairRow, indexed_id) == 4, ...);
static_assert(sizeof(RtdlAabbPairRow) == 8,              ...);
```

The test file cross-checks this at line 57 (`assertIn("static_assert(sizeof(RtdlAabbPairRow) == 8", prelude)`).

---

**Verdict: ACCEPT**

All three low-severity issues from the prior review are addressed with concrete code changes, not just documentation.
