# Goal2007 Claude Review — Goal2006 Prepared CuPy Exact Filter Reuse

Date: 2026-05-14

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **accept-with-boundary**

---

## Scope

Independent read-only review of Goal2006 changes against six verification
criteria. No source modifications were made.

Files inspected:

- `src/rtdsl/partner_adapters.py`
- `scripts/goal1868_road_hazard_partner_priority_flags_pod_smoke.py`
- `scripts/goal1869_road_hazard_v2_partner_perf.py`
- `docs/reports/goal1886_segment_polygon_prepared_partner_reuse_2026-05-13.md`
- `docs/reports/goal1889_road_hazard_prepared_partner_reuse_2026-05-13.md`
- `docs/reports/goal2006_prepared_cupy_exact_filter_reuse_2026-05-14.md`
- `docs/reports/goal2006_pod_smoke/road_hazard_prepared_cupy_exact_filter_2048.json`
- `tests/goal2006_prepared_cupy_exact_filter_reuse_test.py`
- `tests/goal1886_segment_polygon_prepared_partner_reuse_test.py`
- `tests/goal1889_road_hazard_prepared_partner_reuse_perf_test.py`

---

## Criterion 1 — Native engine remains app-agnostic and candidate-only

PASS.

The `write_device_any_hit_all_witnesses` call flows through
`_PartnerPreparedTriangleScene.write_device_any_hit_all_witnesses` (adapter
line ~2335), which delegates directly to `self._native_scene.write_device_any_hit_all_witnesses`.
The native scene never receives triangle columns, app IDs, or road/hazard
semantics. All output metadata in `_segment_polygon_all_witness_columns_optix_partner_columns`
consistently records `"native_engine_row_contract": "generic_ray_primitive_candidate_witness_pairs"`.
The prepared-scene path (line 2016–2032) sets `scene_reuse_authorized = True`
and skips `scene.close()` but does not alter what the native call sees.

---

## Criterion 2 — Prepared-scene wrapper does not make native OptiX app-specific

PASS.

`_PartnerPreparedTriangleScene` (lines 2329–2345) stores
`polygon_triangle_columns` and `polygon_triangle_aabbs` on the Python wrapper
only. The native scene object is held in `self._native_scene` and receives only
generic ray/primitive arguments via the two delegated methods
(`write_device_any_hit_all_witnesses`, `write_device_any_hit_flags`).

One structural note: the `__getattr__` fallthrough at line 2341–2342 exposes
all native scene attributes through the wrapper. This is not a correctness
problem because the wrapper defines `polygon_triangle_columns` explicitly in
`__init__`, so attribute lookup on the wrapper finds it there before falling
through. The fallthrough is benign but means any future native attribute with
the same name would be silently shadowed by the wrapper copy. This is acceptable
given that the native scene's public surface is stable and opaque.

---

## Criterion 3 — CuPy prepared path retains enough geometry for exact filtering

PASS.

`prepare_segment_polygon_anyhit_optix_partner_device_scene` (lines 2348–2357)
stores both `polygon_triangle_columns` (fields: ids, x0, y0, x1, y1, x2, y2 as
float64) and `polygon_triangle_aabbs` on the wrapper.

`segment_polygon_hitcount_optix_prepared_partner_device_count_columns` (lines
2790–2877) retrieves `polygon_triangle_columns` from the wrapper via `getattr`
(line 2812) and, when CuPy and the columns are both available, calls
`_cupy_exact_segment_triangle_witness_pairs` (line 2814) with the full triangle
geometry.

The CuPy kernel function (lines 2255–2326) receives float64 triangle vertices
and float32 ray geometry and performs the exact 2D segment/triangle intersection
test on device before the partner-side unique-pair count. The retained geometry
is sufficient for this filter.

One observation: `_cupy_exact_segment_triangle_witness_pairs` sorts and
searchsorts triangle IDs on every call (lines 2288–2294). Since the triangles in
a prepared scene are fixed across repeated queries, this per-call sort is
unnecessary work. For the road-hazard workload at 2048 rows this overhead is
small, but for high-iteration workloads with large triangle counts the triangle
sort could be cached on the wrapper. This is a performance opportunity, not a
correctness issue. No code change is required for acceptance.

---

## Criterion 4 — Road-hazard scripts use float32 ray columns for OptiX ABI

PASS.

Both scripts build ray columns with `runtime["float32"]` for `ox`, `oy`, `dx`,
`dy`, and `tmax`:

- `goal1869_road_hazard_v2_partner_perf.py` lines 83–87
- `goal1868_road_hazard_partner_priority_flags_pod_smoke.py` lines 78–82

The `_cupy_exact_segment_triangle_witness_pairs` function calls
`.astype(cupy.float32, copy=False)` on the ray columns before passing them to
the kernel (lines 2307–2311), making the float32 contract explicit at the kernel
boundary. If the inputs are already float32 (as they now are after Goal2006),
the `copy=False` makes this a no-op rather than an extra allocation.

---

## Criterion 5 — Pod artifact supports only the narrow same-contract claim

PASS.

Artifact: `docs/reports/goal2006_pod_smoke/road_hazard_prepared_cupy_exact_filter_2048.json`

Verified fields:

| Field | Value | Expected |
| --- | --- | --- |
| `status` | `"pass"` | pass |
| `count` | `2048` | 2048 |
| `gpu` | `"NVIDIA RTX A5000, 570.211.01"` | A5000 |
| `parity.strict_priority_flags_match` | `true` | true |
| `partners.cupy.goal1889_prepared_reuse.prepared_scene_reused` | `true` | true |
| `partners.cupy.goal1889_prepared_reuse.witness_output_columns_reused` | `true` | true |
| `partners.cupy.goal1889_prepared_reuse.query_median_ratio_vs_v1_8_prepared_native` | `0.9225` | < 1.0 |
| `partners.cupy.goal1889_prepared_reuse.query_median_ratio_vs_goal1869_unprepared_partner` | `0.8175` | < 1.0 |
| `claim_boundary.v2_0_release_authorized` | `false` | false |
| `claim_boundary.whole_app_speedup_claim_authorized` | `false` | false |
| `claim_boundary.broad_rt_core_speedup_claim_authorized` | `false` | false |
| `claim_boundary.package_install_claim_authorized` | `false` | false |
| `claim_boundary.partner_output_columns_true_zero_copy_authorized` | `true` | true |

The artifact records only the CuPy prepared row (`--partners cupy`). Torch is
not included in this pod run, which is consistent with the Goal2006 scope
(CuPy-specific correction). The run used 5 iterations with count=2048 and
threshold=2.

One provenance note: `git_commit` is `"unknown"` because the pod ran a
workspace build without a resolvable HEAD commit; provenance is carried by
`source_commit_label: "cbbffaa9-plus-goal2006-prepared-cupy-exact"`. This is
weaker than a real hash (as used in the Goal1889 local smoke artifacts) but
acceptable as a smoke run for a narrow correction goal.

---

## Criterion 6 — Report does not overclaim

PASS.

The Goal2006 report (`docs/reports/goal2006_prepared_cupy_exact_filter_reuse_2026-05-14.md`)
carries `Status: pod-pass-with-boundary` and explicitly enumerates what the
evidence does not authorize:

- v2.0 release readiness
- broad RT-core speedup wording
- whole-app speedup wording outside this measured row
- package-install claims
- treating native candidate witness rows as exact app rows

The timing ratios stated in the report (1.08x vs v1.8 prepared, 1.22x vs
unprepared CuPy) are arithmetically consistent with the artifact values
(1/0.9225 ≈ 1.084, 1/0.8175 ≈ 1.223).

The Goal1889 report update (`docs/reports/goal1889_road_hazard_prepared_partner_reuse_2026-05-13.md`)
correctly attributes the Goal2006 pod follow-up, reproduces the same timing
table, and keeps the v2.0 release and broad-speedup gates blocked.

---

## Non-blocking Notes

1. **Per-call triangle sort** (`partner_adapters.py` lines 2288–2294): the
   argsort/searchsorted over triangle IDs is repeated on every call to
   `_cupy_exact_segment_triangle_witness_pairs`. For a prepared scene the
   triangle set is fixed; caching the sorted positions on `_PartnerPreparedTriangleScene`
   would eliminate this overhead across query iterations. No change needed for
   acceptance; worth filing as a follow-up optimization.

2. **`__getattr__` fallthrough** (`partner_adapters.py` lines 2341–2342):
   exposes all native attributes through the wrapper. Not a current defect, but
   a future native attribute name collision with a wrapper field would be silent.
   Acceptable given the stable native ABI.

3. **`git_commit: "unknown"` in artifact**: weaker provenance than a real commit
   hash. The label `cbbffaa9-plus-goal2006-prepared-cupy-exact` is human-readable
   but not machine-verifiable. The Goal1889 smoke artifacts embedded the actual
   commit hash; the pod approach here is consistent with other pod smoke runs.

---

## Summary

All six verification criteria pass. The implementation cleanly separates the
native engine (candidate-only, app-agnostic) from the Python/CuPy partner layer
(exact filtering, hit-count counting, road-hazard thresholding). The wrapper
retains the necessary triangle geometry without polluting the native call path.
The float32 ABI fix is confirmed in both scripts. The pod artifact and report
respect the narrow same-contract scope and block all overreach claims.

Verdict: **accept-with-boundary**. The three non-blocking notes above do not
require source changes before acceptance. The triangle sort optimization is a
worthwhile follow-up.
