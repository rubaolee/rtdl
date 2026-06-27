# Goal2010 Claude Review: Goal2009 Prepared CuPy Triangle Lookup Cache

Date: 2026-05-14

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **accept**

---

## What Was Reviewed

- `src/rtdsl/partner_adapters.py` — cache implementation in `_PartnerPreparedTriangleScene` and `_cupy_exact_segment_triangle_witness_pairs`
- `docs/reports/goal2009_prepared_cupy_triangle_lookup_cache_2026-05-14.md`
- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_2048.json`
- `tests/goal2009_prepared_cupy_triangle_lookup_cache_test.py`

---

## Check 1: Cache Lives Only in the Python Partner Wrapper

**Pass.**

`_cupy_exact_filter_triangle_lookup_cache` is an instance attribute initialised on
`_PartnerPreparedTriangleScene.__init__` (line 2345). The native scene is accessed
only through two thin delegation methods (`write_device_any_hit_all_witnesses`,
`write_device_any_hit_flags`) and is never modified. The cache dict is pure Python
on the wrapper object; no field was added to or read from any native OptiX type.

The caller (line 2826) retrieves the cache with
`getattr(prepared_scene, "_cupy_exact_filter_triangle_lookup_cache", None)`, so the
unprepared path receives `None` and the function falls through to the existing full
sort unconditionally. The native scene remains app-agnostic.

---

## Check 2: Cache Safety and Exact-Filter Semantics

**Pass.**

The cache stores `sorted_triangle_pos` and `sorted_triangle_ids` — the argsort and
the reordered triangle ID array. Both are derived deterministically from
`triangle_ids`, which is extracted from `polygon_triangle_columns` at prepare time
and is immutable for the lifetime of the prepared scene. Reusing them across repeated
queries against the same prepared scene is correct.

Cache population logic (lines 2289–2300):

```
if triangle_lookup_cache is not None:
    sorted_triangle_pos = triangle_lookup_cache.get("sorted_triangle_pos")
    sorted_triangle_ids = triangle_lookup_cache.get("sorted_triangle_ids")
else:
    sorted_triangle_pos = None
    sorted_triangle_ids = None
if sorted_triangle_pos is None or sorted_triangle_ids is None:
    sorted_triangle_pos = cupy.argsort(triangle_ids)
    sorted_triangle_ids = triangle_ids[sorted_triangle_pos]
    if triangle_lookup_cache is not None:
        triangle_lookup_cache["sorted_triangle_pos"] = sorted_triangle_pos
        triangle_lookup_cache["sorted_triangle_ids"] = sorted_triangle_ids
```

The pattern is a correct read-through cache: computes on first miss, stores, reuses
on subsequent calls. The downstream `searchsorted` path (lines 2301–2304) and the
exact-filter kernel are unchanged; only the sort is skipped on cache hits. Semantics
of the exact filter are identical to the pre-cache path.

Each `_PartnerPreparedTriangleScene` instance owns an independent cache dict, so
multiple concurrently prepared scenes cannot share or corrupt each other's cached
arrays.

---

## Check 3: Pod Artifact Supports the Narrow Same-Contract Claim

**Pass.**

Artifact key fields cross-check against report numbers:

| Field | Artifact | Report |
| --- | ---: | ---: |
| `status` | `"pass"` | `pod-pass-with-boundary` |
| `count` | 2048 | 2048 |
| `strict_priority_flags_match` | `true` | "parity passed" |
| prepared-reuse median (s) | 0.0025192387 | 0.002519239 |
| `query_median_ratio_vs_v1_8_prepared_native` | 0.7243 | 0.724x |
| unprepared-cupy `ratio_vs_v1_8_prepared_native` | 0.9167 | 0.917x |

Derived figures are consistent: 1/0.724 ≈ 1.38x speedup vs v1.8 prepared; 0.790
ratio vs unprepared CuPy ≈ 1.27x speedup — both match the report's prose.

Claim boundary flags in artifact:

| Flag | Value |
| --- | --- |
| `v2_0_release_authorized` | `false` |
| `broad_rt_core_speedup_claim_authorized` | `false` |
| `whole_app_speedup_claim_authorized` | `false` |
| `package_install_claim_authorized` | `false` |
| `same_contract_timing_row` | `true` |
| `partner_output_columns_true_zero_copy_authorized` | `true` |

All boundary flags align correctly.

---

## Check 4: Report Does Not Overclaim

**Pass.**

The report boundary section explicitly states:

> "This is still a narrow same-contract road-hazard prepared CuPy timing row. It
> does not authorize v2.0 release readiness, broad RT-core speedup wording,
> package-install claims, or general whole-app speedup claims."

No language in the report body asserts general speedup, whole-app improvement, or
release readiness. The 1.38x and 1.27x figures are correctly scoped to the
count-2048 road-hazard same-contract row.

---

## Minor Observations (Non-Blocking)

- The first unprepared-CuPy sample (0.186 s) is a JIT warmup outlier; the median
  correctly ignores it. This is expected and consistent with prior road-hazard perf
  rows.
- The cache holds CuPy GPU arrays for the lifetime of the `_PartnerPreparedTriangleScene`
  object. GPU memory is reclaimed when the wrapper is garbage-collected. No leak
  risk within normal single-session prepared-scene usage.
- `git_commit` in the artifact is `"unknown"`. This has appeared in prior artifacts
  and is a pre-existing gap in the perf script; not introduced by Goal2009.

---

## Summary

Goal2009 is a clean, minimal optimization. The triangle-lookup cache is correctly
scoped to the Python partner wrapper, does not touch native OptiX internals, is safe
for repeated prepared-scene use, and leaves exact-filter semantics unchanged. Pod
evidence is internally consistent, parity passed, and the report's boundary
language is accurate. No overclaiming found.

**Verdict: accept**
