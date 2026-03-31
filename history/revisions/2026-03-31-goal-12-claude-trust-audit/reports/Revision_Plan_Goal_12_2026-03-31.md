# Goal 12 Revision Plan

**Date:** 2026-03-31
**Based on:** `trust_audit_2026-03-31.md` + Codex Iteration 1 Response

---

## Accepted Issues

All four discrepancies from the audit are accepted as revision-driving:

1. **`boundary_mode` is a no-op** — `api.py:114` accepts it, `lowering.py:152–154` validates it, but neither the CPU reference (`reference.py:201–212`) nor Embree C++ (`rtdl_embree.cpp:281–295`) reads or acts on it. A validated parameter that is silently dropped is worse than an unsupported one.

2. **Goal 10 BVH over-claim** — `run_embree()` for `segment_polygon_hitcount` and `point_nearest_segment` calls pure O(N×M) nested loops with no Embree API (`rtdl_embree.cpp:931–1023`). The lowering still emits `accel_kind: "bvh"` (`lowering.py:284, 348`). The claim does not match the implementation.

3. **LSI all-hits correctness bug** — `rtdl_embree.cpp:720–733` calls `rtcIntersect1` once per probe segment, returning at most one hit. Existing test cases (county slice, authored kernels) are all geometrically one-probe-one-hit, so the bug is latent but untested. If a probe segment intersects two or more build segments, results are silently incomplete.

4. **Goal 10 workloads excluded from baseline/evaluation** — `baseline_runner.py:40–48` raises `KeyError` for Goal 10 predicates; `evaluation_matrix.py` covers only 4 workloads. Goal 10 has a parallel test path that bypasses standard infrastructure.

---

## Revision Plan

### Issue 1 — Fix `boundary_mode` in execution paths

- In `reference.py`: pass `boundary_mode` to `_point_in_polygon`; add an edge-on-boundary branch controlled by it (inclusive = boundary counts as inside).
- In `rtdl_embree.cpp`: add a `boundary_inclusive` flag to the `point_in_polygon` C++ function; treat a winding-number or cross-product result of exactly 0 as inside when the flag is set.
- In `lowering.py`: forward the `boundary_mode` string into the plan JSON so the execution layer can read it.
- Keep the lowering validator that rejects values other than `"inclusive"` (only one mode is supported; the point is that the supported mode must be executable, not just validated at parse time).

### Issue 2 — Correct Goal 10 BVH over-claim

Option A (preferred, minimal scope): change `lowering.py:284, 348` to emit `accel_kind: "native_loop"` instead of `"bvh"` for the two Goal 10 predicates. Update the schema to accept `"native_loop"` as a valid enum value. Add a one-line note in the language doc for these predicates.

Option B (larger scope): implement actual Embree BVH geometry for `segment_polygon_hitcount` and `point_nearest_segment` in `rtdl_embree.cpp`, then leave `accel_kind: "bvh"` accurate. Only do this if BVH acceleration is planned; otherwise Option A is correct.

**Default: Option A.** The audit does not require BVH to be implemented, only that the label matches reality.

### Issue 3 — Fix LSI all-hits in Embree

- Replace the single `rtcIntersect1` call per probe segment (`rtdl_embree.cpp:720–733`) with an `rtcIntersect1`-in-a-loop pattern or with `rtcOccluded1` + geometry-ID fan-out. The standard Embree pattern for all-hits is to use an intersect callback that appends the hit and returns `false` to continue traversal (set `ray.tfar = hit.tfar` but do not terminate). Alternatively, use a filter function that appends and clears `tfar`.
- Add a regression test in `rtdsl_embree_test.py` with a probe segment that provably intersects two build segments. The test must assert that both pairs are returned.
- Confirm existing parity tests still pass after the change.

### Issue 4 — Extend baseline/evaluation to Goal 10

- Add `segment_polygon_hitcount` and `point_nearest_segment` entries to `infer_workload` and `load_representative_case` in `baseline_runner.py`.
- Add representative fixture cases for both workloads (small, deterministic, matches the format of existing county-based fixtures).
- Add both workloads to `evaluation_matrix.py` so they appear in the benchmark report.
- Do not redefine or re-freeze the existing four-workload baseline contracts — extend only.

---

## Acceptance Criteria

| # | Criterion | How to verify |
|---|---|---|
| 1a | `boundary_mode="inclusive"` causes boundary points to be classified as inside in CPU reference | Unit test: point exactly on a polygon edge returns `True` for `inclusive`, would otherwise be undefined |
| 1b | Same behavior in Embree C++ path | Embree parity test: same boundary point, same result as CPU |
| 2 | Goal 10 plan JSON contains `accel_kind: "native_loop"` (or equivalent accurate label); `"bvh"` is absent for those two predicates | Read generated plan JSON in test; assert key value |
| 2b | JSON schema accepts the new accel label without validation error | Existing schema validation test passes with updated golden |
| 3a | LSI Embree returns all pairs when one probe intersects two build segments | New regression test with multi-hit geometry; asserts full pair set |
| 3b | All existing LSI Embree parity and authored-kernel tests still pass | `make test` green |
| 4a | `baseline_runner.py` can run Goal 10 workloads without `KeyError` | `load_representative_case("segment_polygon_hitcount")` and `load_representative_case("point_nearest_segment")` succeed |
| 4b | `evaluation_matrix.py` produces entries for both Goal 10 workloads | Matrix length >= 15; both predicates present |
| 4c | Full test suite passes (`make test`) | 47+ tests green |

---

## Review Method

After Codex delivers the revision:

1. **Code diff review** — for each issue, read the changed lines at the cited locations and confirm the change matches the plan above.
2. **Test execution** — run `make test`; all tests must pass. Count must not decrease.
3. **New test spot-check** — for Issue 3 specifically, read the new regression test, confirm the geometry is genuinely multi-hit (two build segments visibly crossing the probe), and confirm the assertion checks both result pairs.
4. **Plan JSON spot-check** — run one Goal 10 kernel and read the emitted plan JSON; confirm `accel_kind` value.
5. **Boundary semantics spot-check** — run the CPU reference with a point on a polygon edge and confirm it returns `True`.

No new Gemini review round is required for this goal. Claude will perform the closure review against the criteria above.

---

Consensus to revise
