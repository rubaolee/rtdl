## Verdict: APPROVE-WITH-NOTES

---

## Findings

**Code matches the document.** The patch is already in place and is structurally exactly what the proposal describes:

- `polygon_intersect` callback (`rtdl_embree.cpp:836–846`): only calls `state->candidate_polygon_indices->insert(args->primID)` and returns — no truth decision in the callback.
- `positive_only` branch (`1007–1055`): collects candidates → `std::sort` for determinism → GEOS `covers()` per candidate → emits only exact positive rows.
- GEOS `GeosPreparedPolygonSet` is pre-built once outside the point loop (`line 1021`), not reconstructed per point — correct.
- Non-GEOS fallback still exists (`line 1048`) and would re-expose the original inaccuracy. This is an honest limitation, not a hidden defect.

**The ray choice is sound.** A single upward ray from the point (`dir = {0.0, 1.0}`) correctly covers all polygons whose bounding box contains `point.x` and extends above `point.y`. Any polygon that truly contains the point satisfies both conditions. No false negatives in candidate generation.

**The `static_cast<void>(state->point)` at line 844** is a no-op suppressing a stale unused-variable warning. Harmless but signals the callback field is dead weight — `PipQueryState::point` is no longer used anywhere in the callback.

---

## Agreement and Disagreement

**Agreement:**
- The diagnosis of stable false positives (row count too high, 39215 vs 39073) being systematic rather than noisy is correct.
- The repair philosophy — traversal narrows, exact test owns truth — is the right structure.
- The acceptance criteria (parity first, then timing, then claim) are appropriate and honest.
- The pessimism about serial performance (`rtcIntersect1` per point, no SIMD packet queries) is accurate.
- "This cannot be published as an Embree performance package" before parity is confirmed is the right call.

**Disagreement / Imprecision:**
- The document frames the bug as purely *architectural*: "mixing candidate discovery and truth finalization in the callback." That framing is incomplete. The deeper cause is that the pre-patch callback was calling the local `point_in_polygon(...)` for exact truth, and that local function produces different results than GEOS for edge cases. The architecture change is good, but the *real* fix is GEOS replacing the local implementation. The non-GEOS fallback path (`line 1048`) would reproduce the same false-positive pattern on a non-GEOS build — the document does not make this explicit.
- The document asserts what the pre-patch callback did without quoting the pre-patch code. That claim cannot be verified from the current file. It is plausible given the `static_cast<void>(state->point)` remnant, but it is stated as certain fact.

---

## Recommended Next Step

Run the exact-source Linux measurement (`scripts/goal77_runtime_cache_measurement.py`, backend `embree`) on the `county_zipcode` positive-hit `pip` surface against the current patched binary on `lestat-lx1`. Confirm row count == 39073 and digest matches PostGIS before any performance claim is attempted. If parity is not restored, the first thing to investigate is whether the Linux build has GEOS available (i.e., `RTDL_EMBREE_HAS_GEOS == 1`), since the non-GEOS fallback path is still potentially wrong.
