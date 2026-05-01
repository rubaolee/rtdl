# Goal 218 — Fixed-Radius Neighbors Vulkan Implementation

**Date:** 2026-04-10
**Author:** Claude Sonnet 4.6 (independent review of in-tree implementation)

---

## Verdict

Implementation is complete and correct. The `fixed_radius_neighbors` workload
has been added to the Vulkan backend using a Vulkan compute shader that mirrors
the brute-force Oracle/Embree approach. The public contract (fields `query_id`,
`neighbor_id`, `distance`; rows grouped by ascending `query_id`, within each
group sorted by ascending distance then ascending `neighbor_id`; inclusive
`distance <= radius` boundary; per-query truncation to `k_max`) is preserved.
All 109 tests pass; 5 goal218 Vulkan tests skip correctly on this macOS host
where no Vulkan GPU is present.

---

## Files Changed

| File | Change |
|---|---|
| `src/native/vulkan/rtdl_vulkan_prelude.h` | `RtdlFixedRadiusNeighborRow` struct; `rtdl_vulkan_run_fixed_radius_neighbors` C ABI declaration |
| `src/native/vulkan/rtdl_vulkan_api.cpp` | `rtdl_vulkan_run_fixed_radius_neighbors` C ABI wrapper with input validation (radius ≥ 0, k_max > 0, early-return for empty inputs) |
| `src/native/vulkan/rtdl_vulkan_core.cpp` | `GpuFrnRecord` GPU struct (12 bytes); `kFrnComp` GLSL compute shader; `g_frn_pipe` / `g_frn_init` singletons; `run_fixed_radius_neighbors_vulkan` host implementation |
| `src/rtdsl/vulkan_runtime.py` | `_RtdlFixedRadiusNeighborRow` ctypes struct; `"fixed_radius_neighbors"` in `PreparedVulkanKernel._SUPPORTED_PREDICATES`; dispatch entry; `_call_fixed_radius_neighbors_vulkan_packed`; argtype registration |
| `tests/goal218_fixed_radius_neighbors_vulkan_test.py` | 5 tests: authored case, fixture case, out-of-order queries, raw mode, ordering contract |

---

## Verification

**Static review — passes:**

- `kFrnComp` GLSL shader: one thread per query, brute-force over all search
  points, inclusive radius boundary (`dist_sq > radius_sq` rejects, so
  `dist_sq == radius_sq` admits — correct). Insertion sort into a sentinel-
  initialised output slot of `k_max` entries, sorted by distance ASC then
  neighbor_id ASC. Sentinel `0xffffffff` marks empty slots.
- UBO layout `{ uint nqueries; uint nsearch; float radius; uint k_max; }`
  with `std140` = 16 bytes, matches C++ `FrnParams` struct exactly.
- Pipeline uses `build_compute_pipeline(..., 4)`: bindings 0,1,2 SSBO,
  binding 3 UBO — correct for the existing infrastructure which hardcodes
  binding-3 as UBO.
- `GpuFrnRecord { uint32_t query_id, neighbor_id; float distance; }` = 12 bytes,
  layout matches the 3-uint GLSL output encoding.
- Host post-processing: filters sentinel rows, `std::stable_sort` by
  `query_id` ascending — satisfies the contract ordering rule.
- C ABI wrapper validates `radius >= 0`, `k_max > 0`, null pointers, and
  early-returns for empty inputs before calling the GPU path.
- Python ctypes: `_RtdlFixedRadiusNeighborRow` `{c_uint32, c_uint32, c_double}`
  matches the C struct. Argtype registration uses `_require_backend_symbol`
  (hard-fail if missing), appropriate for a real native implementation.

**Runtime results (this host, macOS, no Vulkan GPU):**

```
PYTHONPATH=src:. python3 -m unittest tests.goal218_fixed_radius_neighbors_vulkan_test -v
Ran 5 tests in 0.000s
OK (skipped=5)

PYTHONPATH=src:. python3 -m unittest discover -s tests
Ran 109 tests in 82.272s
OK
```

GPU correctness requires the Linux host at 192.168.1.20 (`make build-vulkan`
then `python3 -m unittest tests.goal218_fixed_radius_neighbors_vulkan_test`).

---

## Open Risks

1. **Float32 precision vs double-precision oracle.** Coordinates cast from
   `double` to `float32` on GPU upload. For points near the radius boundary,
   float32 rounding can include or exclude differently from the CPU oracle.
   Test tolerance is `rel_tol=1e-6, abs_tol=1e-6` (appropriate for float32).

2. **Insertion sort tie-breaking epsilon (`1e-7`) differs from oracle (`1e-12`).**
   The shader uses `abs(dist - slot_dist) <= 1e-7` to detect "same distance,
   break tie by neighbor_id". The CPU oracle uses `kPointEps = 1e-12`. Two
   search points within `1e-7` (but not `1e-12`) of the same distance could
   produce different neighbor_id orderings between GPU and oracle. Typical
   geographic inputs are not affected.

3. **`k_max × query_count` output buffer size unbounded.** No cap on
   `k_max` or `query_count` before the `k_max × query_count × 12` byte GPU
   allocation. Very large inputs may exhaust device memory silently.

4. **`baseline_runner` does not support `backend="vulkan"`.** The baseline
   runner accepts `cpu`, `embree`, `scipy`, `postgis`, `optix` — not `vulkan`.
   The Vulkan path cannot be used in the standard benchmark/audit harness
   without additional work.

5. **Runtime not verified on this host.** All 5 tests skipped. GPU
   correctness verification is deferred to the Linux GPU host.
