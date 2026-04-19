# Goal606 External Review — Apple RT Native 3D Point-Neighborhood

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6 (external review pass)
Verdict: **ACCEPT**

---

## What was reviewed

- `docs/reports/goal606_v0_9_3_apple_rt_point_neighbor_3d_native_2026-04-19.md`
- `src/native/rtdl_apple_rt.mm` (lines 1334–1583, `rtdl_apple_rt_run_fixed_radius_neighbors_3d`)
- `src/rtdsl/apple_rt_runtime.py` (full file)
- `tests/goal606_apple_rt_point_neighbor_3d_native_test.py` (full file)

---

## Native implementation — verified genuine

`rtdl_apple_rt_run_fixed_radius_neighbors_3d` is a real MPS-backed implementation, not a stub.

**Encoding approach (correct):**
- Each 3D search point is tessellated into 12 triangles forming an axis-aligned box of side `2 * radius` in all three dimensions.
- Each query fires a short z-directed ray from `(query.x, query.y, query.z - radius)` with direction `(0, 0, 2*radius + ε)` and `maxDistance = 1.000001`. This ray traverses the full z-depth of any candidate box. Because the ray has no x/y displacement, the GPU hit test is equivalent to: `query.x ∈ [point.x-r, point.x+r]` ∧ `query.y ∈ [point.y-r, point.y+r]` ∧ `query.z ∈ [point.z-r, point.z+r]`.
- CPU exact refinement then computes Euclidean distance (`point_distance_3d`) and rejects over-approximated cube candidates, enforcing true spherical radius.
- The masked multi-pass chunk scheme (`chunk_size = 32`, bit-per-search-point) is structurally identical to the established 2D path.

**bounded_knn_rows (3D):** delegates to `fixed_radius_neighbors_3d_apple_rt` with the caller-supplied `radius`/`k_max`, then applies `_rank_neighbor_rows`. Correct.

**knn_rows (3D):** uses `_combined_point3d_radius` (diagonal of the combined bounding box plus `1e-9`) as a conservative catch-all radius, then ranks to `k`. Conservative but provably complete; consistent with the existing 2D approach.

---

## Contract claims — verified accurate

`_APPLE_RT_SUPPORT_NOTES` lists `native_candidate_discovery: "shape_dependent"` and `native_shapes: ("Point2D/Point2D", "Point3D/Point3D")` for all three predicates. This matches the actual dispatch table in `run_apple_rt`. No polygon, graph, or DB workload is claimed or implied anywhere.

`fixed_radius_neighbors_3d_apple_rt` is correctly exported from `__init__.py`.

---

## Tests — adequate for a correctness-first step

Four tests in `Goal606AppleRtPointNeighbor3DNativeTest`:

| Test | Coverage |
|---|---|
| `test_fixed_radius_native_only_matches_cpu` | 3D fixed-radius via kernel dispatch (`native_only=True`) vs CPU reference |
| `test_bounded_knn_native_only_matches_cpu` | 3D bounded-kNN via kernel dispatch vs CPU reference |
| `test_knn_native_only_matches_cpu` | 3D kNN via kernel dispatch vs CPU reference |
| `test_direct_fixed_radius_helper_matches_cpu` | direct `fixed_radius_neighbors_3d_apple_rt` helper vs CPU reference |

The test case uses two query points and four search points with non-trivial x/y/z separations, exercising all three axes. `native_only=True` ensures the MPS path is taken, not the CPU fallback. Parity assertion uses `assertAlmostEqual` (5 decimal places) for distances and exact equality for IDs/ranks — appropriate given float32 GPU arithmetic.

---

## One cosmetic issue (non-blocking)

`apple_rt_predicate_mode` at `apple_rt_runtime.py:825` returns the string `"native_mps_rt_2d_else_cpu_reference_compat"` for all three point-neighborhood predicates. This label predates 3D support and is now misleading. It is an internal introspection string only (not part of the public support matrix or dispatch contract), so it does not affect correctness or claims. Worth updating in a follow-on cleanup.

---

## Summary

Goal606 genuinely adds Apple MPS RT-backed 3D point-neighborhood candidate discovery for `fixed_radius_neighbors`, `bounded_knn_rows`, and `knn_rows` on `Point3D/Point3D` inputs. The native encoding (axis-aligned cube as 12 triangles + z-ray) is architecturally sound, CPU refinement enforces exact Euclidean semantics, and the contract table is accurate. No polygon, graph, or DB coverage is claimed. The cosmetic mode string issue is noted but does not block acceptance.

**ACCEPT**
