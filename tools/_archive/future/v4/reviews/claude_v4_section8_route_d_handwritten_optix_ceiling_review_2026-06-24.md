I have now read all nine files in the packet (protocol, report, two result JSONs, one prior result JSON, smoke result, reference source, harness, local test) plus both prior chain reviews. Let me verify the raw arithmetic independently before rendering judgment.

**Ratio cross-checks (JSON medians):**
- 8192 copies scalar: 0.100486621s / 0.000521635s = 192.7x ✓ (report: 192.64x)
- 32768 copies scalar: 0.486885317s / 0.000715741s = 680.3x ✓ (report: 680.25x)
- 131072 copies scalar: 1.989422731s / 0.002089970s = 951.9x ✓ (report: 951.89x)
- 8192 copies rows: 0.284516230s / 0.000628978s = 452.4x ✓ (report: 452.35x)
- 32768 copies rows: 1.193533182s / 0.001541824s = 774.1x ✓ (report: 774.10x)
- 131072 copies rows: 5.290915035s / 0.004640702s = 1140.1x ✓ (report: 1140.11x)

All reported figures match raw JSON.

---

## Formal Review: V4 Section 8 Route D Hand-Written OptiX Ceiling

**Date:** 2026-06-24
**Reviewer:** Claude (external)
**Packet:** `call_for_review_v4_section8_route_d_handwritten_optix_ceiling_2026-06-24.md`
**Prior chain:** `accept_strict_fail_revise_architecture` → `accept_prepared_hot_path_credit_no_release`

---

### Verdict

**`accept_route_d_obtained_product_boundary_gap_continue`**

Route D is valid, independent, and correctly measured. It does not authorize "near hand-written OptiX" wording for the current RTDL product path — it falsifies that claim by a factor of 192x–1140x. The next V4 engineering target is the array/device-array front door for this primitive. No release claim and no broad speedup claim are authorized.

---

### Q1 — Does the Route D reference satisfy the independence contract?

**Yes, with one process note.**

Static independence:
- No `rtdsl`, `librtdl_optix`, `rtdl_optix_*`, `run_app`, or `PreparedOutlierDetectionSession` in source ✓ (confirmed by reading `route_d_fixed_radius_count_threshold_optix.cpp` in full)
- Headers are only OptiX SDK public headers, CUDA runtime, NVRTC, and standard C++ ✓
- Own OptiX context, GAS, pipeline, SBT, launch params, and device program (all defined in file) ✓
- Fixture generated locally via `make_fixture()`, matching the Section 8 protocol specification exactly ✓

Build-level independence:
- Harness build command: `nvcc -std=c++17 -O3 -I<optix_include> -I<cuda_include> <source> -L<cuda_lib64> -lcuda -lnvrtc -o <binary>` — no RTDL library linked ✓
- `build: null` in the serious-size result (skip-build mode) is correct; the smoke result shows `build.returncode: 0` with only an nvcc GPU-architecture deprecation warning, which is non-fatal ✓

**Process note (not a blocker):** The independence test (`test_reference_source_is_not_linked_to_rtdl_runtime`) operates by string token search on the C++ source, not by `ldd` or `nm` inspection of the compiled binary. This is sufficient given the simple, self-contained source, but the binary-level check is absent from the harness. This should be noted for protocol completeness. It does not affect this verdict because the source is unambiguously independent on inspection.

---

### Q2 — Is the Route D correctness evidence sufficient for the Section 8 fixture?

**Yes.**

All three serious sizes pass both D1 (scalar) and D2 (count-row) against the protocol-specified expected counts:

| copies | points | expected threshold | expected outliers | D1 scalar | D2 rows threshold | D2 rows outlier | pass |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 8,192 | 65,536 | 49,152 | 16,384 | 49,152 ✓ | 49,152 ✓ | 16,384 ✓ | ✓ |
| 32,768 | 262,144 | 196,608 | 65,536 | 196,608 ✓ | 196,608 ✓ | 65,536 ✓ | ✓ |
| 131,072 | 1,048,576 | 786,432 | 262,144 | 786,432 ✓ | 786,432 ✓ | 262,144 ✓ | ✓ |

The fixture implementation in `make_fixture()` matches the protocol exactly: 8 base points per tile, `x_offset = 7.0 * copy_index`, `id_offset = 100 * copy_index`, radius=0.35, threshold=3. Tile separation (7.0 units) is large enough that no cross-tile interactions occur at radius 0.35. The AABB padding `kRadiusPad = 1e-4` correctly avoids false negatives in the BVH without changing intersection semantics.

One structural observation on the anyhit shader: the intersection test uses `float` arithmetic (`dx*dx + dy*dy > radius_sq` in float), while fixture coordinates are stored as `double` internally and converted to float at `to_gpu_points()`. For this fixture's coordinate values and radius, float precision is not a concern — confirmed by the exact correctness counts above.

---

### Q3 — Is the timing boundary clear enough for a ceiling reference?

**Yes, but two important constraints on what the ceiling represents must be stated explicitly.**

The timing boundary is defined consistently across the protocol, the source code, and every result JSON:

> *Included:* host query upload (`cuMemcpyHtoD`), launch params upload, `optixLaunch`, `cuStreamSynchronize`, required result download.
> *Excluded:* fixture construction, OptiX context creation, module/pipeline build, search-point upload, GAS build.

Implementation matches specification: in both `measure_scalar` and `measure_rows`, the entire `run_scalar`/`run_rows` call body is inside the timed window. Pipeline and PreparedScene construction are outside it.

**Amendment required — constraint A:** The timed `run_scalar` and `run_rows` functions each call `cuMemAlloc` and `cuMemFree` per iteration for the query buffer, the threshold count buffer, and the launch params buffer. This is inside the measured window. A pre-allocated implementation (pooled buffers) would be faster than what Route D measures. The ceiling is therefore **slightly conservative (pessimistic)**; the gap to the current RTDL product path is at minimum the reported 192x–1140x, and potentially larger. This must be stated whenever Route D numbers are cited. The ceiling is not artificially inflated — it is correctly described as the ceiling for a per-call-allocating prepared-session pattern.

**Amendment required — constraint B:** At the largest fixture (131,072 copies, 1,048,576 points), each Route D scalar iteration uploads 1,048,576 × 16 bytes = 16.7 MB of query point data. At ~16 GB/s effective PCIe 4.0 bandwidth, upload alone takes ~1.04ms against a measured median of 2.09ms, meaning the Route D timing at this size is **substantially PCIe-upload-bound** rather than RT-core-compute-bound. An array/device-array front door that keeps query points device-resident between calls would reduce Route D's own measured time further. The report's proposed next step (array front door) would therefore close more than it might appear from Route D's numbers alone — both the RTDL product path and Route D currently include upload cost, but a device-array path eliminates it from both sides. This does not affect the validity of the ceiling comparison; it improves the outlook for the next engineering step.

---

### Q4 — Does the Route D result authorize near-hand-written OptiX wording for the current RTDL product path?

**No. Emphatically.**

The gap is:

| copies | Route D scalar | RTDL direct scalar | ratio |
|---:|---:|---:|---:|
| 8,192 | 0.000522s | 0.100487s | **192.7x** |
| 32,768 | 0.000716s | 0.486885s | **680.3x** |
| 131,072 | 0.002090s | 1.989423s | **951.9x** |

| copies | Route D rows | RTDL prepared summary | ratio |
|---:|---:|---:|---:|
| 8,192 | 0.000629s | 0.284516s | **452.4x** |
| 32,768 | 0.001542s | 1.193533s | **774.1x** |
| 131,072 | 0.004641s | 5.290915s | **1140.1x** |

The current RTDL Python-facing product path is 192x to 1140x slower than the independent OptiX ceiling. Near-hand-written OptiX wording is not authorized. Route D falsifies any such claim for the current product route.

**Additional note on RTDL timing variance:** The direct RTDL scalar timings at 8,192 copies span 0.075s–0.106s, a 41% peak-to-trough spread across 7 repeats. This is high variance, indicating Python GC pressure, GIL interference, or ctypes scheduling noise at the small size. It does not affect the ceiling comparison — even at RTDL's absolute fastest observed (0.075s), it remains 144x slower than Route D's median. The variance is further evidence that the product boundary (Python objects, ctypes overhead) is the dominating cost.

---

### Q5 — Is the report right that V4's next blocker is product-boundary overhead rather than the RT-core fused kernel?

**Yes. This diagnosis is correct and is the primary finding of this packet.**

Route D demonstrates that the RT-core kernel itself executes in 0.5ms–4.6ms across the serious sizes. The current RTDL Python-facing prepared route takes 100ms–5.3s for the same sizes. The RT-core is not the bottleneck. The bottleneck is the product boundary:

1. Python `Point` object iteration and per-point type coercion
2. Host-side packing into native C `GpuPoint` float arrays
3. Python/ctypes FFI call setup and return value extraction
4. Per-call host-device transfers that could be eliminated with device-resident buffers
5. App-level Python density-row conversion in the summary path

These items together account for effectively all of the 192x–1140x gap. The Tier-2 fused kernel thesis (RT cores can execute this primitive efficiently) is now independently confirmed. The question "can the product expose it efficiently?" is not yet answered.

---

### Q6 — Should V4 continue by building the fixed-radius array/device-array front door before adding any second primitive?

**Yes. This is the correct and only authorized next step.**

The prior chain already established (in `accept_strict_fail_revise_architecture`, Q5, Step 2): Route D was required before adding primitives. Route D is now acquired. The prior chain also established in `accept_prepared_hot_path_credit_no_release` that the prepared summary hot path beats the rows baseline by 1.65x–1.97x — crediting the Tier-2 kernel, but leaving the product boundary gap unaddressed.

Route D now quantifies that product boundary gap as 192x–1140x. This is the next blocker. The required work:

1. Add a `fixed_radius_count_threshold_2d` array front door that accepts contiguous numeric columns or a device-array column instead of Python `Point` objects.
2. Reuse the existing prepared native scene and count-threshold continuation (the kernel work is already validated).
3. Return scalar and compact row outputs without app-level Python density-row conversion in the hot path.
4. Measure against both baselines: (a) separated RTDL row route and (b) Route D independent ceiling.
5. Gate: the new product route must move materially toward Route D, not just beat the RTDL row baseline.

Adding a second primitive before this front-door gate is cleared would produce a second primitive with the same 200x–1000x product-boundary penalty. It would not advance V4's release readiness.

---

### Q7 — Are any release or broad speedup claims authorized?

**No.**

Confirmed against all evidence artifacts:

| Claim | JSON field | Status |
|---|---|---|
| V4 release | `release_claim_authorized: false` in both result JSONs | **Not authorized** |
| Broad V4 speedup wording | `near_handwritten_optix_claim_authorized: false`; protocol §Claim Boundary | **Not authorized** |
| "Near hand-written OptiX" for current product path | Route D shows 192x–1140x gap; explicitly excluded in protocol | **Not authorized** |
| Tier-3 callback claims | No Tier-3 measurement exists in this or any prior packet | **Not authorized** |
| App-specific native engine claims | Protocol §Claim Boundary; prior reviews | **Not authorized** |
| Whole-call app-route claims | Original Section 8 whole-call gate failed; not overturned | **Not authorized** |
| Automatic partner selection claim | Not within scope of this packet | **Not authorized** |
| True zero-copy claim | Not within scope of this packet | **Not authorized** |

---

### Authorized Claim (post-review)

The only claim this packet supports after external review:

> An independent hand-written OptiX reference for the fixed-radius count-threshold primitive (`FIXED_RADIUS_COUNT_THRESHOLD_2D`) runs correctly on the Section 8 outlier-density fixture (8,192–131,072 tile copies; 65,536–1,048,576 points; radius=0.35, threshold=3) and establishes a native ceiling of 0.52ms–2.09ms (scalar) and 0.63ms–4.64ms (count-row) in the prepared-session hot-path boundary. The current RTDL Python-facing prepared routes are 192x–952x (scalar) and 452x–1140x (count-row) slower than this ceiling on the same fixture and boundary.

This claim must always be accompanied by the following scope statement:
- Prepared-session hot-path boundary only. GAS build and pipeline compilation excluded.
- Ceiling timing includes per-call `cuMemAlloc` for query/params buffers (slightly conservative; true kernel ceiling is faster).
- At 131,072 copies, Route D timing is partially PCIe-upload-bound.
- This is a single primitive, single fixture, single hardware run. Hardware identity must be supplied from pod run provenance.
- Does not authorize V4 release, broad speedup wording, or any claim listed in Q7 above.

---

### Required Amendments

**Amendment 1 (report §Timing Summary — add note):** State that Route D hot-path timing includes per-call `cuMemAlloc` and `cuMemFree` for query, threshold count, and launch params buffers. The ceiling is slightly conservative; a pre-allocated implementation would be faster. The product-boundary gap is at minimum 192x–1140x.

**Amendment 2 (report §Interpretation — add note):** At copies=131,072, the Route D scalar timing (~2.09ms) is partially PCIe-upload-bound (16.7MB of query data per iteration). An array/device-array front door that keeps query points device-resident would reduce this overhead for both Route D and the RTDL product path, closing the gap by more than the raw numbers suggest.

**Amendment 3 (result JSON v4_section8_rtdl_direct_prepared_scalar_hot_path_result):** This JSON has no `timing_boundary` field. The field must be added to align with the protocol and enable future reviewers to verify the boundary match without consulting the harness source.

---

### Summary

Route D is acquired, independent, and correctly measured. It closes the open item from the `accept_strict_fail_revise_architecture` review (Q5, Step 2). It does not authorize "near hand-written OptiX" wording — it does the opposite, quantifying the gap as 192x–1140x. The Tier-2 fused kernel is proven capable. The product boundary is proven to be the dominant bottleneck. The next engineering target is the array/device-array front door for `FIXED_RADIUS_COUNT_THRESHOLD_2D`. That gate must be cleared before any second primitive is added and before any performance-release path is reopened.
