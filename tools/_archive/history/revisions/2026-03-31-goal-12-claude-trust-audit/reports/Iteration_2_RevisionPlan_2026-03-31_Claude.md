# Goal 12 — Concrete Revision Plan (2026-03-31, Claude)

**Round:** Goal 12, Iteration 2  
**Author:** Claude (claude-sonnet-4-6), acting as audit lead  
**Source reports:**
- `external_reports/trust_audit_2026-03-31.md` (Claude audit)
- `reports/Iteration_1_Response_2026-03-31_Codex.md` (Codex agreement)

Both parties agree on all four discrepancies. No contested claims. Plan proceeds.

---

## 1. Discrepancy Triage — Code vs. Docs vs. Tests

| # | Discrepancy | Code | Docs | Tests | Rationale |
|---|---|:---:|:---:|:---:|---|
| D1 | `boundary_mode` silently dropped | **yes** | no | **yes** | Root cause is in execution paths; doc note already exists |
| D2 | Goal 10 `accel_kind: "bvh"` over-claim | **yes** | no | no | Lowering emits wrong enum value; docs already have caveat |
| D3 | LSI Embree returns only one hit per probe (all-hits bug) | **yes** | no | **yes** | Latent correctness bug; existing tests too small to catch it |
| D4 | Goal 10 workloads absent from baseline/evaluation infrastructure | **yes** | no | **yes** | Gap in runner + matrix; no doc change needed |

Doc-only patches were already applied in Goal 11. The remaining work is exclusively code and test changes.

---

## 2. Prioritized Implementation Plan

### P1 — LSI Embree all-hits correctness (D3) `rtdl_embree.cpp`

**Why first:** This is a correctness bug on a production execution path, not a naming issue. If it goes undetected through further development it will corrupt query results silently.

**Changes:**

1. Replace the `rtcIntersect1` call in the LSI probe loop with `rtcOccluded1`-driven iteration **or** switch to a user-geometry approach that accumulates all hits via repeated intersection queries. The standard Embree pattern for all-hits is: call `rtcIntersect1`, record the hit, mark that geometry inactive (or exclude it), repeat until no hit is returned. Implement this accumulation loop.
2. Add a regression test in `rtdsl_embree_test.py`: construct a probe segment that geometrically crosses **two or more** build segments, assert that all crossing pairs are returned, not just one. Name it `test_lsi_multi_hit_probe`.

**Files:** `rtdl_embree.cpp` (probe loop ~line 720–733), `rtdsl_embree_test.py`

---

### P2 — `boundary_mode` made explicit in execution (D1)

**Why second:** A parameter that is accepted at the API boundary, validated, and then silently discarded misleads callers about what they are controlling. The fix is narrow.

**Changes:**

1. In `reference.py`: thread `boundary_mode` into `_point_in_polygon`. For `"inclusive"`, the existing ray-casting result is correct; add an explicit `boundary_mode` parameter and an `assert boundary_mode == "inclusive"` guard (or raise) so the intent is code-visible. Do not change behavior.
2. In `rtdl_embree.cpp`: add a `boundary_mode` string field to the PIP query struct and thread it to the `point_in_polygon` C++ function. For `"inclusive"`, keep existing behavior. Add an assertion or early-return error for any other value (future-proofing).
3. No DSL or schema changes required — `"inclusive"` is the only valid value, already enforced by lowering.

**Files:** `reference.py` (~line 201), `rtdl_embree.cpp` (~line 281–295)

---

### P3 — Goal 10 `accel_kind` corrected in lowering (D2)

**Why third:** A plan JSON that says `accel_kind: "bvh"` for a pure nested-loop implementation is a false contract — it will mislead any downstream tooling that reads plan JSON. One-line fix.

**Changes:**

1. In `lowering.py`, change both `accel_kind: "bvh"` emissions for `segment_polygon_hitcount` and `point_nearest_segment` to `accel_kind: "native_loop"` (or `"nested_loop"` — pick one and apply consistently).
2. Update `rayjoin_plan.schema.json` to add `"native_loop"` (or chosen name) to the `accel_kind` enum.
3. Update golden files for Goal 10 workloads if they encode `accel_kind`.

**Files:** `lowering.py` (lines 284, 348), `rayjoin_plan.schema.json`, any golden files under `tests/golden/`

---

### P4 — Goal 10 workloads added to baseline/evaluation infrastructure (D4)

**Why last:** Lowest risk, no correctness impact. Extends existing machinery.

**Changes:**

1. In `baseline_runner.py`: extend `infer_workload` and `load_representative_case` to handle `"segment_polygon_hitcount"` and `"point_nearest_segment"` predicates. Supply representative fixture cases (can reuse the smallest fixtures already used in `goal10_workloads_test.py`).
2. In `evaluation_matrix.py`: add entries for the two Goal 10 workloads (CPU backend, `native_loop` accel, at least 1 case each).
3. In `baseline_contracts.py`: add contract entries for both Goal 10 workloads analogous to the existing four.
4. Ensure the evaluation report pipeline (`evaluation_report.py`) does not hardcode a 4-workload assumption; if it does, extend it.

**Files:** `baseline_runner.py`, `evaluation_matrix.py`, `baseline_contracts.py`, `evaluation_report.py`

---

## 3. Acceptance Criteria for Final Closure

All of the following must be true simultaneously before Goal 12 is closed:

### Code criteria

| ID | Criterion | Verified by |
|---|---|---|
| AC-1 | `rtdl_embree.cpp` LSI probe loop returns **all** intersecting pairs, not just the geometrically closest | `test_lsi_multi_hit_probe` passes |
| AC-2 | `reference.py _point_in_polygon` has an explicit `boundary_mode` parameter; for `"inclusive"` behavior is unchanged | Read `reference.py` + existing PIP tests green |
| AC-3 | `rtdl_embree.cpp` PIP path receives and asserts `boundary_mode`; no silent drop | Read `rtdl_embree.cpp` + existing Embree PIP tests green |
| AC-4 | `lowering.py` emits `accel_kind: "native_loop"` (or equivalent non-BVH label) for both Goal 10 workloads | `grep accel_kind lowering.py` shows correct value |
| AC-5 | `rayjoin_plan.schema.json` accepts the new `accel_kind` value | Schema validation tests green |
| AC-6 | `baseline_runner.py` does not raise for Goal 10 predicates | `infer_workload("segment_polygon_hitcount")` returns without error |
| AC-7 | `evaluation_matrix.py` includes entries for both Goal 10 workloads | Count of `EvaluationEntry` objects ≥ 15 |

### Test criteria

| ID | Criterion |
|---|---|
| TC-1 | `test_lsi_multi_hit_probe` exists in `rtdsl_embree_test.py`, is not skipped when Embree is present, and passes |
| TC-2 | Full test suite (`make test`) passes at 47+ tests green with zero failures |
| TC-3 | No test is deleted, renamed, or weakened to achieve the above |

### Non-regression criteria

| ID | Criterion |
|---|---|
| NR-1 | All four original workload parity results in `baseline_contracts.py` still pass |
| NR-2 | All existing golden files either unchanged or regenerated with a documented reason |
| NR-3 | The evaluation report pipeline (`make evaluate` or equivalent) completes without error |

---

## 4. Post-Revision Review Method

After Codex delivers the revision, I (Claude) will perform the following review in order:

**Step 1 — Diff audit**  
Read the full git diff from the Goal 11 commit through the new revision commit. Confirm every changed file is in scope; flag any out-of-scope change for explanation.

**Step 2 — AC verification (file:line)**  
For each of the 7 code acceptance criteria above, cite the exact `file:line` that satisfies it. No criterion is closed on description alone.

**Step 3 — Test count and names**  
Run (or read the output of) `make test`. Confirm:
- TC-1: `test_lsi_multi_hit_probe` appears in the run and passes
- TC-2: total passing count ≥ original count (no regressions)
- TC-3: no test file has a reduced test count vs. Goal 11

**Step 4 — Schema round-trip**  
Confirm that a Goal 10 plan JSON generated by the new lowering validates against the updated schema. Cite the test that covers this.

**Step 5 — Baseline runner smoke check**  
Read `baseline_runner.py` and confirm `infer_workload` and `load_representative_case` handle both new predicates without raising. If `make baseline` or equivalent is available, confirm it exits 0.

**Step 6 — Final verdict**  
If all ACs pass: close Goal 12 as `done-consensus`.  
If any AC fails: issue a specific blocking finding with file:line and required change, do not issue a partial consensus.

---

Consensus to revise
