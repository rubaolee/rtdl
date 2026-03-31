The file write is awaiting your permission. Here is the full revision plan in the meantime:

---

# Goal 12 — Concrete Revision Plan (2026-03-31, Claude)

## 1. Discrepancy Classification: Code vs. Docs vs. Tests

| # | Discrepancy | Code | Docs | Tests |
|---|---|:---:|:---:|:---:|
| D1 | `boundary_mode` no-op in execution | **yes** | no | **yes** |
| D2 | Goal 10 emits `accel_kind:"bvh"` — no Embree used | **yes** | **yes** | no |
| D3 | LSI Embree returns only closest-hit, not all-hits | **yes** | no | **yes** |
| D4 | `baseline_runner` / `evaluation_matrix` exclude Goal 10 | **yes** | no | no |
| D5 | Review-depth process inconsistency | no | no | no |

**D5 is process-only.** Docs-only fixes are rejected for D1, D3, and D4 — all four substantive discrepancies require code changes.

---

## 2. Prioritized Implementation Plan

### Priority 1 — D3: Fix LSI Embree All-Hits Correctness Bug
**Files:** `rtdl_embree.cpp`, `rtdsl_embree_test.py`

This is the highest priority because it silently drops correct results.

1. **`rtdl_embree.cpp:720–733` and `:555–566`** — Replace the single `rtcIntersect1` call with an all-hits strategy. Standard Embree approach: register an intersection filter callback that appends each hit to a buffer and resets `hit.geomID = RTC_INVALID_GEOMETRY_ID` to continue traversal rather than terminating.

2. **`rtdsl_embree_test.py`** — Add one test where a single probe segment intersects two or more distinct build segments. The test must assert all intersecting build-segment IDs appear in the result. This test must fail on the current code before the fix.

### Priority 2 — D1: Make `boundary_mode` Explicit in Execution Paths
**Files:** `reference.py`, `rtdl_embree.cpp`, test file (simulator or Embree)

1. **`reference.py:201–212` — `_point_in_polygon`:** Thread `boundary_mode` into the function body. For `"inclusive"`, points on edges must return inside. Raise `ValueError` for unsupported values.

2. **`rtdl_embree.cpp:281–295` — C++ `point_in_polygon`:** Add epsilon-based boundary check for `"inclusive"` mode; pass the mode through from the query context.

3. **Test file:** Add a test with a point exactly on a polygon edge asserting `"inclusive"` classifies it as inside.

### Priority 3 — D2: Correct `accel_kind` for Goal 10 Workloads
**Files:** `lowering.py`, `schemas/rayjoin_plan.schema.json`, docs

1. **`lowering.py:284` and `:348`** — Change `accel_kind: "bvh"` to `accel_kind: "native_loop"` for both Goal 10 workloads.

2. **`schemas/rayjoin_plan.schema.json`** — Add `"native_loop"` to the `accel_kind` enum.

3. **Docs** — Correct any claims of BVH acceleration for Goal 10 workloads. Regenerate golden files that embed `accel_kind`.

### Priority 4 — D4: Extend Baseline and Evaluation Infrastructure to Goal 10
**Files:** `baseline_runner.py`, `evaluation_matrix.py`, `baseline_contracts.py`

1. **`baseline_runner.py:40–48`** — Add `"segment_polygon_hitcount"` and `"point_nearest_segment"` to `infer_workload` and `load_representative_case`. Synthetic datasets (same scale as `goal10_workloads_test.py`) are sufficient.

2. **`evaluation_matrix.py`** — Add `EvaluationEntry` objects for both Goal 10 workloads (CPU backend minimum; Embree entries desirable but not required for closure).

---

## 3. Exact Acceptance Criteria for Final Closure

The round is closed when **all ten** of the following are confirmed:

| # | Criterion | Verification |
|---|---|---|
| AC-1 | Multi-hit test present in `rtdsl_embree_test.py` | `grep "multi_hit\|all_hit" rtdsl_embree_test.py` returns a function |
| AC-2 | LSI callback continues traversal past first hit | LSI section of `rtdl_embree.cpp` shows continue-traversal strategy, not single `rtcIntersect1` |
| AC-3 | `reference.py` `_point_in_polygon` consumes `boundary_mode` | `grep -n "boundary_mode" reference.py` returns a line inside the function body |
| AC-4 | `rtdl_embree.cpp` PIP C++ function reads `boundary_mode` | `grep -n "boundary_mode" rtdl_embree.cpp` hits inside `point_in_polygon` |
| AC-5 | Boundary-point semantic test exists | `grep -n "boundary\|on_edge" <test_file>` returns a test case |
| AC-6 | `lowering.py` emits `"native_loop"` for Goal 10 | `grep -n "native_loop" lowering.py` at former `"bvh"` positions |
| AC-7 | Schema accepts `"native_loop"` | `grep "native_loop" schemas/rayjoin_plan.schema.json` in `accel_kind` enum |
| AC-8 | `baseline_runner.py` handles Goal 10 without exception | `grep -n "segment_polygon_hitcount\|point_nearest_segment" baseline_runner.py` in both functions |
| AC-9 | `evaluation_matrix.py` contains Goal 10 entries | `grep -n "segment_polygon_hitcount\|point_nearest_segment" evaluation_matrix.py` |
| AC-10 | All tests pass | `make test` exits 0; Embree tests may skip but must not error |

---

## 4. How I Will Review the Revised Repository

1. **Read changed files at cited line numbers** — not keyword-only; logic must be sound. LSI all-hits: verify the filter callback actually continues traversal. `reference.py` boundary mode: verify the condition correctly includes edge-points, not just passes the parameter.

2. **Check for introduced regressions** — read adjacent code around each change location to confirm unrelated dispatch paths (PIP, Overlay, ray-tri) are unaffected.

3. **Verify test body adequacy** — for AC-1 and AC-5, read the full test body to confirm the assertion exercises the semantic being protected, not just that the test exists.

4. **Spot-check schema consistency** — confirm `"native_loop"` is in the correct `accel_kind` enum position and no `"bvh"` references remain for Goal 10 workload kinds.

5. **Enumerate test file coverage** — confirm which test files exercise each changed component, and ask Codex to supply `make test` output if AC-10 is ambiguous.

6. **Issue final verdict** — all 10 AC met with no new gaps introduced: `done-consensus`. Any partial or new gap: targeted second iteration with a short blocking list.

---

Consensus to revise
