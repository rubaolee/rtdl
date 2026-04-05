Now I have sufficient data. Here is the audit:

---

## Milestone-Level Technical Audit — RTDL Published State (2026-04-05)

---

### Verdict

**State: Publishable core, two open gaps worth fixing before any performance claim involving Vulkan's prepared path, and one long-standing latent API defect to acknowledge or remove.**

The OptiX and Embree backends are production-grade at the accepted exact-source long-workload surface. Vulkan is parity-clean but carries a silent performance regression in its prepared-execution cache key path, and `chains_to_polygon_refs` in `datasets.py` has a broken `vertex_offset` that has been known since Goal 28C and remains unaddressed.

---

### Findings

**F1 — Vulkan prepared-cache identity fastpath is missing (`vulkan_runtime.py:282–311`)**

`vulkan_runtime._prepared_execution_cache_key` calls `_normalize_records` for every input on every invocation — including on a cache hit. `embree_runtime` and `optix_runtime` both import and use `_identity_cache_token` (`runtime.py:23`), which builds the cache key from `id(payload)` and `len(payload)` for canonical typed tuples, skipping normalization entirely on repeated calls. The Vulkan path pays the normalization cost unconditionally. The `goal80` fast-path test (`tests/goal80_runtime_identity_fastpath_test.py`) has cases for Embree and OptiX but no Vulkan case. This is a behavioral gap, not a correctness bug, but it undermines the prepared-cache speedup that is the whole point of the warm-path story.

**F2 — `chains_to_polygon_refs` has a broken `vertex_offset` (`datasets.py:688`)**

The `vertex_offset` field is assigned the loop `index` (0, 1, 2, …) rather than a cumulative vertex count. The actual `vertex_count` value stored per face is the number of chains referencing that face, not the number of vertices. This was flagged by Claude during Goal 28C review, acknowledged as outside that goal's execution path, and never closed. The function is exported from `__init__.py` and called in `apps/rtdl_python_demo.py` and `tests/rtdsl_py_test.py`. Its tests (`rtdsl_py_test.py:167–168`) only assert `len(...)`, which passes whether or not the field values are correct.

**F3 — `boundary_mode='exclusive'` silently unsupported on all three backends**

All three Python runtimes (`embree_runtime.py:632`, `optix_runtime.py:503`, `vulkan_runtime.py:354`) reject `boundary_mode != "inclusive"` with a `ValueError`. The DSL itself accepts `boundary_mode` as a compile-time option. A caller who compiles a kernel with `boundary_mode="exclusive"` and routes it to any native backend gets a runtime error with no indication that this was never implemented. There is no test that confirms `exclusive` is rejected cleanly.

**F4 — Vulkan is not performance-competitive at the accepted exact-source surface (confirmed, not a bug)**

Goal 89 numbers: Vulkan warm-prepared: ~6.15 s vs. PostGIS ~3.05 s; Vulkan repeated raw-input best: ~6.71 s vs. PostGIS ~3.09 s. OptiX/Embree both win at ~1.09–1.77 s. This is a correct and honest characterization, but the paper performance table needs to explicitly footnote Vulkan's role (coverage/portability, not performance).

**F5 — Vulkan GLSL shaders compile at first-call runtime via shaderc (`rtdl_vulkan.cpp:7–9`)**

SPIR-V compilation is paid once per workload type per process, cached in static singletons. This is intentional and documented in the file header. However, there is no test that measures or bounds this first-call JIT cost, and it contributes to Vulkan's 16 s first-run cold time (Goal 89). The cost is real but currently invisible in the test suite.

---

### Confirmed Strengths

- **ABI consistency**: All three C++ backends (`rtdl_optix.cpp`, `rtdl_embree.cpp`, `rtdl_vulkan.cpp`) share identical struct layouts for all five input types and all six output row types. The Python ctypes bindings match exactly. No padding or alignment surprises observed.
- **All six workloads fully implemented on all three backends**: `segment_intersection`, `point_in_polygon`, `overlay_compose`, `ray_triangle_hit_count`, `segment_polygon_hitcount`, `point_nearest_segment` — all present in native code, Python binding dispatch tables, and `_SUPPORTED_PREDICATES` guards.
- **Oracle trust envelope is clean**: Goal 75 confirmed Python mini oracle (15/15) and native C oracle (12/12) both match PostGIS on `lsi`, `pip` (full-matrix and positive-hits), and overlay-seed.
- **Exact-source long-workload wins are real**: Goal 84/89 accepted prepared and repeated raw-input boundaries for both OptiX and Embree against PostGIS. Parity flags are `true` on all accepted runs.
- **Prepared-cache LRU logic is correct in all three backends** (8-entry cap, `move_to_end` on hit, `popitem(last=False)` on overflow).
- **No TODO/FIXME/HACK annotations anywhere in native source** (grep clean across all three `.cpp` files).
- **Dataset tooling is solid**: `load_cdb`, `parse_cdb_text`, `slice_cdb_dataset`, `arcgis_pages_to_cdb`, `overpass_elements_to_cdb`, and `write_cdb` are all implemented and export-correct. `chains_to_segments`, `chains_to_polygons`, and `chains_to_probe_points` correctly pre-pack on construction.
- **Vulkan unit test suite is complete** (`rtdsl_vulkan_test.py`: 17 test methods covering all six workloads, cache reuse, raw mode, PIP variants, and error paths).

---

### Missing Tests

| Gap | Where to add |
|-----|-------------|
| Vulkan identity fastpath (no `_normalize_records` on canonical tuple cache hit) | Add to `tests/goal80_runtime_identity_fastpath_test.py` as `test_vulkan_identity_fast_path_skips_normalize_on_repeated_tuple_inputs` |
| `boundary_mode='exclusive'` rejected cleanly by all three backends | New test or extend `dsl_negative_test.py` |
| `chains_to_polygon_refs` field values — `vertex_offset` and `vertex_count` are correct | Extend `tests/rtdsl_py_test.py` beyond `len()` check |
| Vulkan first-call cold time is bounded (SPIR-V JIT cost) | Timing smoke test in `rtdsl_vulkan_test.py` or dedicated goal |

---

### Missing Docs

| Gap | Where it matters |
|-----|-----------------|
| No doc states that `boundary_mode='exclusive'` is unimplemented on all backends | `docs/rtdl/dsl_reference.md` or `workload_cookbook.md` |
| Vulkan's prepared-cache behavior is not documented to differ from Embree/OptiX | `docs/rtdl/workload_cookbook.md` or inline docstring in `vulkan_runtime.py` |
| `chains_to_polygon_refs` has no docstring explaining what `vertex_offset` means or whether it is correct | `datasets.py:677` |
| Paper performance discussion (Figures 13–15, Table comparisons) does not yet have an explicit footnote distinguishing Vulkan's correctness-only role from OptiX/Embree's performance role | `paper/rtdl_rayjoin_2026/main.tex` |

---

### Recommended Next Step

**Fix the Vulkan identity fastpath (F1).** Apply the same `_identity_cache_token` pattern already in `embree_runtime._prepared_execution_cache_key` to `vulkan_runtime._prepared_execution_cache_key`, import `_identity_cache_token` from `runtime`, and add the corresponding `goal80`-style test. This closes the only behavioral asymmetry between backends in the warm prepared-execution path, and makes the Vulkan prepared-cache story consistent with the already-accepted Embree/OptiX story before any further Vulkan performance work is done.

After that, triage `chains_to_polygon_refs` (F2): either fix the `vertex_offset` computation to be cumulative and update the test to assert field values, or deprecate and remove the function if it is genuinely unused on any real execution path (it currently appears only in a demo script and a count-only test).
