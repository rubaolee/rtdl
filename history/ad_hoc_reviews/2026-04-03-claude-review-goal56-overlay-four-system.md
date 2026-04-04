## Review: Goal 56 Overlay Four-System Closure

---

### Verdict: **APPROVE**

---

### Verification Summary

**Acceptance criteria check (goal_56_overlay_four_system_closure.md §Acceptance):**

| Criterion | Status |
|---|---|
| 1. LKAU ⊲⊳ PKAU package used explicitly | ✓ |
| 2. Comparison contract defined before execution | ✓ (plan doc) |
| 3. PostGIS uses indexed query path | ✓ (all three plans: `uses_index: true`) |
| 4. All four systems parity-clean | ✓ SHA-256 `25debd83…` matches across C/Embree/OptiX |
| 5. Report updates Table 4 / Figure 15 position | ✓ (closure report §Conclusion) |
| 6. At least 2-AI consensus before publication | ✓ (Gemini + this review) |

**Row count sanity:** 73,920 = 280 × 264. Correct full cross-product. ✓

**Both reported OptiX fixes confirmed in code:**

- Fix 1 (GEOS-backed `covers`): `rtdl_optix.cpp:2043-2058` — `#if RTDL_OPTIX_HAS_GEOS` guard uses `right_geos.covers(ri, lxv, lyv)` / `left_geos.covers(li, rxv, ryv)`. Since parity was achieved, GEOS was compiled in on `192.168.1.20`.
- Fix 2 (double precision first-vertex): `rtdl_optix.cpp:2041-2052` — extraction from `double*` source as `double lxv/lyv/rxv/ryv`. This is unconditional. ✓

**Hash/sort consistency:** PostGIS `ORDER BY 1,2,3,4` with `presorted=True` matches backend sort key `(left_polygon_id, right_polygon_id, requires_lsi, requires_pip)`. ✓

**LSI SQL correctness:** Parametric segment intersection with bbox pre-filter (`l.geom && r.geom`), non-parallelism guard (`ABS(denom) >= 1e-7`), t/u both in `[0,1]`. Matches RTDL oracle semantics. ✓

**PIP SQL correctness:** UNION of (left first-vertex inside right polygon) ∪ (right first-vertex inside left polygon) with `ST_Covers`. Column aliasing verified correct for the symmetrical case. ✓

---

### Non-Blocking Cautions

1. **Dead-code guard** — `rtdl_optix.cpp:2038`: `if (gpu_flags[slot].requires_pip) continue;` is unreachable: the GPU `__anyhit__overlay_anyhit` (line 1073) only atomically ORs `requires_lsi`, never `requires_pip`. The guard is harmless but the comment is misleading.

2. **GEOS compile flag** — The correctness of the `requires_pip` supplement on a future build without GEOS (`RTDL_OPTIX_HAS_GEOS` undefined) falls back to `exact_point_in_polygon`. That path was the pre-fix path that caused failures. If OptiX is ever built without GEOS on a new host, the overlay result should be re-validated before acceptance.

3. **`county_soil_overlay_reference` as dispatch token** — `scripts/goal56_overlay_four_system.py:314` passes `county_soil_overlay_reference` as the workload reference for LKAU/PKAU data. This is consistent with the RTDL API design but is semantically surprising at the call site. No correctness issue given parity.
