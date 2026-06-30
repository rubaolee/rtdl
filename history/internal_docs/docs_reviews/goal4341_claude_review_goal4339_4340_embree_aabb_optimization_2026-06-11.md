I now have enough material to write the independent review. Let me compose it.

---

## Independent Review: Goal4339 / Goal4340 — Embree AABB Optimization

**Reviewer:** Claude Sonnet 4.6 (independent, no prior context on this branch)
**Date:** 2026-06-11
**Verdict:** **accept-with-boundary**

---

### 1. App-agnostic boundary

**Pass.**

No LibRTS-specific behavior entered the engine on either goal.

- The three new C++ symbols (`rtdl_embree_prepare_aabb_index_2d`, `rtdl_embree_count_prepared_aabb_index_2d`, `rtdl_embree_destroy_prepared_aabb_index_2d`) use generic struct types (`RtdlAabb2D`, `RtdlPoint`) with no application-domain naming.
- The Python class `PreparedEmbreeAabbIndex2D` lives in `embree_runtime.py`, not in any app module. It is registered in `__all__` under a generic name.
- `AABB_INDEX_2D_CONTRACT["app_boundary"]` reads `"app-name-free primitive; LibRTS, spatial joins, and collision broadphases may lower to it"` — that description is correct for the code as written.
- The benchmark app (`rtdl_librts_spatial_index_benchmark_app.py`) calls the generic `prepare_aabb_index_2d(backend="embree")` path; no LibRTS-specific dispatch happens inside the native library.
- Goal4339's `validate_reference` change touches only the measurement policy in the benchmark front door. The native primitive is unmodified.

---

### 2. AABB predicate correctness

**Pass — all three predicates are exact and correct.**

The callback in `rtdl_embree_api.cpp` (lines 767–791) applies three predicates after BVH broadphase:

**`point_contains`** — indexed box contains the query point:
```cpp
bool aabb2d_contains_point_query(const RtdlAabb2D& box, const RtdlAabb2D& point_query) {
  const double x = point_query.min_x;
  const double y = point_query.min_y;
  return box.min_x <= x && x <= box.max_x && box.min_y <= y && y <= box.max_y;
}
```
Point queries are converted to degenerate AABBs with `min_x = max_x = x, min_y = max_y = y` in `point_queries_as_aabbs()`. The predicate therefore reduces to `min_x <= x <= max_x && min_y <= y <= max_y`. This matches the reference Python `Aabb2D.contains_point()` exactly (inclusive bounds on both sides). ✓

**`range_contains`** — indexed outer box contains the query inner box:
```cpp
bool aabb2d_contains_aabb(const RtdlAabb2D& outer, const RtdlAabb2D& inner) {
  return outer.min_x <= inner.min_x && outer.min_y <= inner.min_y
      && outer.max_x >= inner.max_x && outer.max_y >= inner.max_y;
}
```
Applied as `aabb2d_contains_aabb(indexed, query)`. Matches the reference Python `Aabb2D.contains_box()` identically. ✓

**`range_intersects`** — indexed box intersects the query box:
```cpp
bool aabb2d_intersects_aabb(const RtdlAabb2D& left, const RtdlAabb2D& right) {
  return right.min_x <= left.max_x && right.max_x >= left.min_x
      && right.min_y <= left.max_y && right.max_y >= left.min_y;
}
```
Applied as `aabb2d_intersects_aabb(indexed, query)`. AABB intersection is symmetric; argument order does not affect correctness. Matches the reference Python `Aabb2D.intersects_box()`. ✓

The BVH bounds callback (`aabb2d_bounds`) adds `± kEps` for indexed boxes, which widens BVH candidate sets slightly, but the exact predicate is applied in the callback, so no false positives can reach the output. The epsilon only prevents false negatives from float rounding at BVH query time.

The `small_validated.json` shows `matches_cpu_reference=true` for a 64×64 fixture, which empirically confirms all three predicates agree with the CPU oracle on a real run.

---

### 3. Atomic callback counter safety

**Pass.**

The collision callback accumulates into:
```cpp
struct AabbCollisionCountState {
  ...
  std::atomic<size_t> count;
};
// in callback:
state->count.fetch_add(1, std::memory_order_relaxed);
// after rtcCollide returns:
*hit_count_out = state.count.load(std::memory_order_relaxed);
```

`memory_order_relaxed` is appropriate here because:
- Only atomic increment semantics are needed — no ordering with other memory is required between separate increments.
- The final `.load()` occurs only after `rtcCollide()` returns. Embree's `rtcCollide` guarantees all callbacks complete before the call returns, which provides the necessary happens-before edge. The relaxed load after that synchronization point sees the fully accumulated count.

The report explicitly documents the origin of this fix: "The first native count implementation used a plain `size_t`. The small repeated correctness row caught nondeterministic count changes, which indicated parallel callback execution." This is honest — the race was caught by testing, not assumed away.

The bounds check inside the callback (`collision.primID0 >= state->indexed_boxes->size()`) guards against invalid primitive IDs that Embree could theoretically deliver.

The aggregate initialization `AabbCollisionCountState state {&impl->indexed_boxes, &query_boxes, operation, 0}` correctly value-initializes the atomic to zero.

---

### 4. Fallback safety for older Embree libraries

**Pass with one documented quirk.**

The fallback mechanism in `aabb_index.py:_prepare_embree_aabb_index_2d()` (lines 1093–1128):

1. If `embree_aabb_index_2d_available()` returns True → use `PreparedEmbreeAabbIndex2D` (native AABB collision path).
2. Otherwise → fall back to the columnar conjunctive-scan primitive over `{min_x, min_y, max_x, max_y}` fields.

`embree_aabb_index_2d_available()` checks for all three symbol names in the loaded library. The `EmbreeAabbIndex2D.count()` method dispatches on `getattr(self.prepared, "native_aabb_index", False)` to tell the two routes apart — a clean duck-typed dispatch.

**Quirk (minor, not a safety issue):** On an Embree 3 build, the three new symbols are still declared in `rtdl_embree_prelude.h` (unconditionally) and exported from the library. `embree_aabb_index_2d_available()` would therefore return `True`. However, the C++ implementation of `rtdl_embree_count_prepared_aabb_index_2d` guards with `#if RTDL_EMBREE_API_MAJOR >= 4` and throws: `"native Embree AABB_INDEX_QUERY_2D count path requires Embree 4 collision support"`. So the availability check would return True on Embree 3, construction would succeed, but `count()` would raise a `RuntimeError` with a clear message.

This is a minor inconsistency (availability says "yes", runtime says "no"), but it is non-critical: the error is clear and actionable, modern deployments use Embree 4, and the fallback to columnar scan is only available when the symbols are absent (older library without the symbols at all, not Embree 3 with symbols that throw). A reviewer note: if Embree 3 support must be preserved, `embree_aabb_index_2d_available()` should check the Embree version number, not just symbol presence. This is not a blocking issue.

The columnar fallback itself is the same code that existed before Goal4340 and has its own correctness validation history.

---

### 5. Claim boundary correctness

**Pass.**

**3740.9x improvement vs. columnar fallback:**
- Pre-Goal4340 (columnar scan): `query_median_sec = 43.764849884` on local Linux
- Post-Goal4340 (native AABB collision): `query_median_sec = 0.011698941` on same host
- Ratio: `43.764849884 / 0.011698941 ≈ 3740.9x` — arithmetic checks out.

This comparison is same-host, same fixture (1024×1024, `operation=all`). It represents an algorithm-level improvement: the old path lowered AABB queries through a generic columnar conjunctive scan over encoded ray boxes, which is `O(rays × candidate rows)` and deeply suboptimal for spatial index queries. The new path uses a BVH collision traversal, which is the correct algorithm shape. The 3740.9x figure is legitimate as a comparison of those two algorithm choices on the same workload.

The report boundary is explicit and complete: it does not authorize public release, public speedup wording, paper reproduction wording, broad CPU-vs-GPU claims, NVIDIA RT-core claims, automatic partner selection, or app-specific native-engine logic. The `claim_boundary` field in `small_validated.json` matches this.

**18.8x OptiX vs. Embree (query-median only):**
- OptiX RTX 4000 Ada pod: `query_median_sec = 0.000622335`
- Embree CPU local Linux: `query_median_sec = 0.011698941`
- Ratio: `0.011698941 / 0.000622335 ≈ 18.8x` — arithmetic checks out.

The comparison is cross-hardware (different hosts, different hardware generations). The elapsed totals (0.265s OptiX vs. 0.033s Embree) are dominated by the 0.262s OptiX scene-prepare phase, which is excluded from the query-median comparison. The JSON `claim_boundary` field correctly states "query-median comparison only, not a full system or paper reproduction claim." This is a properly scoped data point.

Both figures require the `--skip-counts` flag (and hence `matches_cpu_reference=null` for the large rows) and are not standalone performance claims. The small validated row (`matches_cpu_reference=true`, 64×64) establishes correctness independently from the performance rows.

---

### Summary of findings

| Criterion | Finding |
|---|---|
| App-agnostic boundary | ✓ No app-specific behavior in native engine |
| AABB predicate correctness | ✓ All three predicates exact and match reference |
| Atomic callback counter | ✓ `std::atomic<size_t>` + relaxed is correct for this pattern |
| Fallback safety | ✓ Safe; one minor Embree-3/symbol-presence quirk (non-blocking) |
| Performance claim boundaries | ✓ 3740.9x is same-host algorithmic; 18.8x is properly bounded cross-hardware |

---

### Verdict: **accept-with-boundary**

The implementation is technically correct on all reviewed dimensions. Predicates, threading model, fallback design, and public API exports are clean. The report boundaries throughout (in code comments, JSON artifacts, and the `.md` reports) are honest and complete.

The "with-boundary" qualifier reflects:

1. **Embree 3 availability quirk** — `embree_aabb_index_2d_available()` returns `True` on Embree 3 (symbols present) but `count()` subsequently throws. Not a safety issue, but the availability predicate is misleading for Embree 3 deployments. If Embree 3 matters, the check should verify version too.

2. **3740.9x is an algorithmic comparison, not a benchmark** — The columnar-scan baseline was not designed to be a competitive AABB index implementation; it was a generic primitive reused as a stopgap. The speedup is real and defensible within the report's scope, but it should not be surfaced without that context. The reports correctly contain it.

3. **18.8x OptiX/Embree figure is a single data point on non-equivalent hardware** — Scene preparation amortization, memory bandwidth, and host/device transfer costs vary significantly across workloads. The figure is properly bounded in the evidence files, but should not be promoted without that scope language.

These are boundary conditions on the evidence package, not correctness defects. The code is safe to merge as-is. Any future public use of the performance figures should carry the claim-boundary language from the reports.
