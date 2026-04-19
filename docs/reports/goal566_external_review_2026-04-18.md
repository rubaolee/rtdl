# Goal 566 External Review: HIPRT Prepared 3D Fixed-Radius Nearest-Neighbor Performance

Date: 2026-04-18
Reviewer: Claude (external review pass — re-review after doc fixes)
Verdict: **ACCEPT**

---

## Correctness

**PASS.**

The C++ implementation (`PreparedFixedRadiusNeighbors3D` in `src/native/rtdl_hiprt.cpp`) correctly stores all persistent build-side state: HIPRT runtime/context, uploaded search-point device buffer, expanded AABB device buffer, radius params buffer, AABB geometry handle, function table referencing `intersectRtdlPointRadius3D`, and compiled `RtdlFixedRadiusNeighbors3DKernel`. Prepared query calls only re-upload query points and launch the already-compiled kernel — the design intent is correctly realised.

The custom intersector (`intersectRtdlPointRadius3D`) computes squared Euclidean distance between the ray origin and the candidate point, accepts the hit only when `dist_sq <= radius * radius`, and sets `hit.t = sqrt(dist_sq)`. This is the correct fixed-radius predicate for 3D points encoded as AABBs.

The Python layer (`prepare_hiprt_fixed_radius_neighbors_3d` in `src/rtdsl/hiprt_runtime.py`) validates non-negative radius, handles the empty-search-set edge case by returning an `empty=True` sentinel, and plumbs through to the C ABI correctly. The high-level `rt.prepare_hiprt` dispatch in `hiprt_runtime.py` routes `fixed_radius_neighbors` kernels to `prepare_hiprt_fixed_radius_neighbors_3d` appropriately.

Tests in `tests/goal566_hiprt_prepared_nn_test.py` cover:
- `test_direct_prepared_helper_matches_cpu_reference_for_multiple_batches` — exercises `prepare_hiprt_fixed_radius_neighbors_3d` directly across two query batches.
- `test_prepared_kernel_matches_cpu_reference_for_multiple_batches` — exercises the public `rt.prepare_hiprt` API across two query batches.

Both tests compare per-row `(query_id, neighbor_id, distance)` against the CPU Python reference with `rel_tol=1e-6, abs_tol=1e-6`. The fixture geometry (5 search points, 2-element query batches, radius=1.0, k_max=3) is small but geometrically non-trivial: some query points have 2–3 neighbours within radius, one has 0. The multi-batch structure ensures BVH reuse is actually exercised across calls.

One minor gap (carried from prior review): neither test verifies the empty-search-set sentinel path. This is not a blocker.

---

## Performance-Claim Honesty

**PASS.**

The JSON report (`goal566_hiprt_prepared_nn_perf_linux_2026-04-18.json`) is internally consistent. Key observations:

- All backends (CPU, Embree, OptiX, Vulkan, HIPRT one-shot, HIPRT prepared) report 2238 output rows, confirming cross-backend parity on the fixture.
- The speedup denominator (HIPRT one-shot, 0.5981 s) and numerator (prepared query median, 0.003533 s) yield exactly the reported 169.30x figure.
- The first prepared-query run (0.01276 s) is notably slower than runs 2–5 (0.0034–0.0038 s), consistent with GPU kernel cache warming. The median (0.003533 s) is computed over all 5 runs and excludes nothing; it lands at run 4, which is representative of the steady state. This is honest — no cherry-picking.
- One-shot baselines are each measured with a single repeat (`repeats=1` for non-prepared paths in the script). The reported one-shot figures are therefore single-sample, not medians. The 169x claim is real in sign and order of magnitude but should be understood as lower-bounded by one-shot variability. This is an acceptable limitation for a benchmark whose goal is to characterise the prepared-query path, not to race one-shot backends against each other.
- The `honesty_boundary` field in the JSON explicitly excludes: 2D neighbors, KNN ranking helpers, graph CSR, DB tables, AMD GPU hardware, RT-core speedup. The performance report text repeats these exclusions. The performance claim is appropriately scoped.

---

## Release-Doc Consistency

**PASS — all four previously-failing locations are now corrected.**

The prior review (REJECT) cited four stale locations across three files. Each has been verified fixed:

| File | Previous stale claim | Current text | Status |
|---|---|---|---|
| `docs/capability_boundaries.md:109–110` | "limited to prepared 3D ray/triangle hit-count path" | "currently covers prepared 3D ray/triangle hit-count and prepared 3D fixed-radius nearest-neighbor paths" | FIXED |
| `docs/capability_boundaries.md:238–239` | "beyond the 3D ray/triangle prepared path" | "beyond the prepared 3D ray/triangle and 3D fixed-radius nearest-neighbor paths" | FIXED |
| `docs/current_architecture.md:92–95` | "covers Ray3D probes against Triangle3D build geometry … per-ray hit-count rows" (only) | adds "plus Point3D probe batches against prepared Point3D build sets for fixed-radius nearest-neighbor rows" | FIXED |
| `docs/rtdl_feature_guide.md:179–180` | "limited to the prepared 3D ray/triangle hit-count path" | "currently covers prepared 3D ray/triangle hit-count and prepared 3D fixed-radius nearest-neighbor paths" | FIXED |

The remaining seven public-facing docs were also verified clean:

- `README.md` — mentions both `ray_triangle_hit_count` and `fixed_radius_neighbors` under `prepare_hiprt`; correct.
- `docs/quick_tutorial.md` — lists both; correct.
- `docs/current_architecture.md` — fixed (above); correct.
- `docs/rtdl_feature_guide.md` — fixed (above); correct.
- `docs/capability_boundaries.md` — fixed (above); correct.
- `docs/release_facing_examples.md` — lists both under HIPRT candidate boundary; correct.
- `docs/release_reports/v0_9/support_matrix.md` — describes `prepare_hiprt` as covering both 3D `ray_triangle_hit_count` reuse and 3D `fixed_radius_neighbors` reuse; correct.

No public-facing doc retains the stale ray/triangle-only claim.

---

## Summary

| Dimension | Result |
|---|---|
| C++ implementation structure | PASS |
| Custom intersector (`intersectRtdlPointRadius3D`) | PASS |
| Python API layer | PASS |
| `__init__.py` / `__all__` exports | PASS |
| Test coverage (parity + multi-batch reuse) | PASS |
| Perf benchmark internal consistency | PASS |
| Speedup claim honesty | PASS |
| Honesty boundary declarations | PASS |
| Release-doc consistency | **PASS** |

**ACCEPT.** All required doc fixes from the prior review are in place. The implementation is correct, the performance claim is honestly bounded, and no public documentation retains the stale ray/triangle-only boundary for `prepare_hiprt`.
