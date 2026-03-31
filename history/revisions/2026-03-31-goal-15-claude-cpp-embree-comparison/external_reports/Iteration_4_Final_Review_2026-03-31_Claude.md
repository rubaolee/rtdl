## Goal 15 First Slice Review

### What the slice actually does

Both native executables (`goal15_lsi_native.cpp`, `goal15_pip_native.cpp`) are thin C++ CSV wrappers that call `rtdl_embree_run_lsi` / `rtdl_embree_run_pip` — the same C API already exposed by `src/native/rtdl_embree.cpp`. They measure only the call into that function, not file I/O. The Python harness generates synthetic fixtures once, runs all three paths against the same data, sorts and string-compares pair lists, and writes timing JSON.

### Correctness review

**LSI fixture:** `build_lsi_dataset(200, 120)` produces 120 horizontal and 200 vertical segments on a 0.25-unit grid; every horizontal crosses every vertical → 120×200 = 24,000 expected pairs. Confirmed.

**PIP fixture:** `build_pip_dataset(200, 120)` produces 120 points each placed at the center of `polygons[idx % 200]` → exactly 120 inside-matches. Confirmed.

**`pair_rows` default:** `row.get("contains", 1) == 1` defaults to `1` when the key is absent (correct for LSI rows that carry no boolean). PIP filters on the explicit field. Correct.

**Polygon CSV parsing:** `goal15_pip_native.cpp` hardcodes `vertex_count=4` and checks `fields.size() != 9` (id + 4 vertex pairs). The harness always writes exactly 4-vertex quads. Consistent.

### Scope boundary assessment

Both the report (`goal15_cpp_embree_comparison_2026-03-31.md`) and the iteration report clearly state this is not an independent algorithmic comparison — correctness agreement is structurally guaranteed because all three paths call the same C implementation. The measurement captures Python/RTDL host-path overhead exclusively. This is correctly documented and not overclaimed.

### Test assessment

`goal15_compare_test.py` asserts all four match booleans and that both native timings are positive. It is minimal but appropriate — asserting performance ratios would be fragile and is out of scope for this slice.

### Blockers

None. The implementation is consistent with its stated scope. No false correctness claims, no misleading performance interpretation, fixture sizes are non-trivial and deterministic, and the boundary is disclosed in all relevant artifacts.

---

Goal 15 first comparison slice accepted by consensus
