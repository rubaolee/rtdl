I have all the information needed. Here is the review:

---

## Goal 97 Package Review — Technical Correctness / Demo

---

### 1. Verdict

**APPROVE-WITH-NOTES**

The package is technically correct and publishable as a correctness/demo goal. One structural gap in the test suite (no skip-guard for the CPU native oracle in hardware backend comparisons) should be documented before publishing; it is not a claim-surface defect but would produce confusing failures on partially available environments.

---

### 2. Findings

**Geometry construction — correct.**
The hit-count law is provably sound. Probe at `y = x_i + 0.5` intersects build segment for `x_j` (vertical, `y ∈ [0, x_j + 1]`) iff `x_i + 0.5 ≤ x_j + 1`, i.e., `x_i ≤ x_j` for nonneg integers. Therefore `hit_count(x_i) = |{j : x_j ≥ x_i}|`. The formula in `expected_hit_counts` (walking values descending, accumulating a running total) implements this law exactly. Spot-checked against the reported canonical case `(3,1,4,1,5,0,2,5) → (4,7,3,7,2,8,5,2)` — correct.

**Endpoint intersection at `x = 0` — handled correctly.**
The NVRTC `seg_intersect` uses `t < 0.0f || t > 1.0f` (inclusive at both endpoints). The probe for `x_i = 0` starts at `(0, 0.5)`, which is the left endpoint of the probe segment (`t = 0`). This is counted. The construction correctly handles the `x_j = 0` build case without the original endpoint-degeneracy problem stated in the design doc.

**Duplicate semantics — explicit and deterministic.**
Equal values produce identical hit counts. `stable_sort_from_hit_counts` breaks ties by `original_index`, matching Python's stable sort with the same key. `test_duplicate_order_is_stable` covers this directly.

**OptiX LSI `stdint.h` fix — confirmed in place.**
`kLsiKernelSrc` (line 734) uses only `unsigned int` — no `<stdint.h>` dependency. The five other NVRTC kernel strings (`kPipKernelSrc`, `kOverlayKernelSrc`, `kRayHitCountKernelSrc`, `kSegPolyHitcountKernelSrc`, `kPointNearestKernelSrc`) still carry `#include <stdint.h>`. That is outside Goal 97's scope and consistent with the fix description ("removed the device-kernel dependency on `stdint.h` for the `lsi` kernel").

**LSI anyhit traversal continuation — correct.**
`__anyhit__lsi_anyhit` records the intersection via `atomicAdd` and calls `optixIgnoreIntersection()` (line 824), continuing traversal. This is necessary for recording all intersections per probe. Correct.

**Test skip-guard gap — structural issue.**
`test_embree_small_case_matches_cpu_sort`, `test_vulkan_small_case_matches_cpu_sort`, and `test_optix_small_case_matches_cpu_sort` all call `run_goal97_backend("cpu", values)` as the reference. They are guarded by `@skipUnless(embree_available()/vulkan_available()/optix_available())` but are NOT guarded by `native_oracle_available()`. On an environment where Embree or Vulkan is present but the native CPU oracle is broken (e.g., the Mac's known `geos_c` link failure), these tests will hard-fail rather than skip. On Linux (where all 5 backends ran cleanly) this is a non-issue, but the test structure is fragile on partial stacks.

**10k scale test — formula only, no hardware.**
`test_formula_scales_to_10k` exercises the formula and sort derivation at 10k, not the hardware backends. Honest and appropriate for a demo goal. The assertion `max(hit_counts) == len(values)` is correct (value 0 appears in the `% 97` sequence, so its hit count equals n).

**Negative integer guard — enforced.**
`make_ray_hit_sort_case` raises `ValueError` on negative inputs. `expected_hit_counts` does the same. Tested explicitly. The boundary is clean and the design doc matches the code.

---

### 3. Agreement and Disagreement

**Agreement:**
- The claim that this is a correctness/demo goal (not a performance goal) is accurate and clearly stated in both the design doc and the report.
- The reported Linux parity result — all five backends producing identical hit counts and sort outputs for the canonical case — is consistent with the test structure and the now-fixed LSI kernel.
- The fix description ("removed `stdint.h` dependency from the LSI NVRTC kernel") is confirmed by the current state of `kLsiKernelSrc`.
- The accepted scope (nonneg integers, duplicates allowed, `(value, hit_count, original_index)` contract) matches the implementation precisely.

**Disagreement / caveats:**
- The report says "11 tests, OK, 4 skipped" on Mac. The 4 skips correspond to `test_cpu_native_matches_python_reference`, `test_embree_small_case_matches_cpu_sort`, `test_vulkan_small_case_matches_cpu_sort`, and `test_optix_small_case_matches_cpu_sort`. Embree, Vulkan, and OptiX tests are skipping on Mac correctly, but this means the skip-guard gap above is harmless on Mac only because those backends also happen to be unavailable. The gap is real and will surface on any Linux environment where exactly one hardware backend is installed but the native oracle is not.
- The report characterizes the `stdint.h` fix as specific to `lsi` without acknowledging that the other NVRTC kernels are in the same latent state. This is not a wrong claim, but the silence is worth noting for future maintainers.

---

### 4. Recommended next step

**Before publishing:** Add `native_oracle_available()` as a combined skip condition for the three hardware backend comparison tests, e.g.:

```python
@unittest.skipUnless(embree_available() and native_oracle_available(),
                     "Embree or native oracle not available")
def test_embree_small_case_matches_cpu_sort(self):
    ...
```

This is a one-line fix per test and makes the skip behavior correct on any partial hardware stack. Everything else — the geometry, the formula, the sorting semantics, the stdint fix, and the parity claim — is sound and publishable.
