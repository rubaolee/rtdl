## Review Memo — Goal 40/41 Native Oracle

### Strengths

**Clean C ABI.** `rtdl_oracle.cpp` uses `extern "C"` throughout with stable POD structs, making the Python `ctypes` binding straightforward and resilient to C++ ABI changes. All output buffers are `malloc`-owned and freed through a single `rtdl_oracle_free_rows` entry point, so ownership is unambiguous.

**Uniform error propagation.** `handle_native_call` in [`rtdl_oracle.cpp`](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp) plus `_check_status` in [`oracle_runtime.py`](/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py) create a coherent error path: C++ exceptions are caught, serialized into a fixed-size `char*` buffer, and re-raised as Python `RuntimeError`. The repeated `finally: library.rtdl_oracle_free_rows(rows_ptr)` pattern prevents leaks on exception paths.

**Sparse-path optimization in LSI.** `oracle_lsi` in [`rtdl_oracle.cpp`](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp) sorts both sides by `min_x` and maintains an active list, converting the naive O(M×N) cross-product into a practical sweep with bounding-box pre-rejection. This is directly responsible for the large sparse-case speedup.

**Deterministic tie-breaking in nearest-segment.** The `point_nearest_segment` loop in [`rtdl_oracle.cpp`](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp) breaks distance ties by `segment.id`, matching the Python reference and keeping cross-oracle comparisons stable.

**Honest reporting.** The Goal 40 and Goal 41 reports acknowledge the dense-output regression and correctly identify Python dict materialization as the bottleneck rather than overclaiming the native path.

### Findings

**F1 — Struct padding risk on `_RtdlTriangle` and `_RtdlRay2D`.**  
Both C++ structs lead with a `uint32_t id` followed immediately by `double` fields in [`rtdl_oracle.cpp`](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp). On x86-64 the compiler inserts implicit padding after `id` to align the first `double`. The `ctypes` mirrors in [`oracle_runtime.py`](/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py) rely on platform ABI matching rather than making the layout contract explicit. A `static_assert` plus a comment would make the contract clearer.

**F2 — `oracle_overlay` uses linear scans over `lsi_hits`, `left_in_right`, and `right_in_left` inside an O(L×R) double loop.**  
In [`rtdl_oracle.cpp`](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp), the overlay composition logic does repeated linear scans over previously materialized hit arrays. This is acceptable for the current oracle role, but it scales poorly on larger overlay cases.

**F3 — `_ensure_oracle_library` trusts `CXX` from the environment.**  
[`oracle_runtime.py`](/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py) passes `os.environ.get("CXX", ...)` into `subprocess.run`. The list-form call avoids shell injection, but the compiler path is still user-controlled.

**F4 — `_load_oracle_library` caches one library instance for the whole process.**  
[`oracle_runtime.py`](/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py) uses `@functools.lru_cache(maxsize=1)`, so a changed library configuration in the same process would not be reloaded automatically.

**F5 — `point_in_polygon` uses an unnecessary denominator guard branch.**  
The ray-casting expression in [`rtdl_oracle.cpp`](/Users/rl2025/rtdl_python_only/src/native/rtdl_oracle.cpp) includes a near-zero denominator fallback. The outer crossing predicate should already prevent that case, so the branch is effectively unreachable, but the fallback value would be numerically bad if reached.

### Performance Framing

Claude agreed with the current framing:

- sparse-result cases show the meaningful gain from moving the oracle core to C++
- dense-result cases are still limited by Python dict construction on the return path
- the Linux exact-source timings show the oracle is still a correctness reference, not a production-speed engine

### Final Verdict

Claude’s conclusion was that the implementation is solid for its stated purpose:

- a correctness oracle replacing the Python simulator core
- verified on both Mac and Linux against Embree

The findings above were judged non-blocking for the current oracle role, but relevant if the oracle is later promoted into a higher-throughput path.
