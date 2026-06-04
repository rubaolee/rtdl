# Goal3373: Claude Review — Owner-Face CuPy Route Fixture Probe (Goal3372)

Date: 2026-06-04

**Verdict: accept**

This is an independent Claude review of Goal3372. It is distinct from the Codex implementation (commits `ef36541e`, `71a24af8`) and from the prior Gemini review of Goal3367-3369 (`docs/reviews/goal3370_gemini_review_owner_face_cupy_pipeline_closure_2026-06-04.md`).

---

## Review Question Responses

### 1. Does the script correctly run the composed CuPy owner-face selector+filter over the stored topology/incident artifacts without adding native/app-specific engine logic?

**Yes, with one observation.**

`scripts/goal3372_owner_face_cupy_route_fixture_probe.py` cleanly separates fixture loading from pipeline invocation:

- `_build_fixture_columns()` reads the stored JSON artifacts (`goal3328` topology, `goal3335` incident) and constructs generic columnar tuples (point IDs, face IDs, counts, candidate shape IDs, topology rows).
- The `rank0` assignment inside `_build_fixture_columns()` uses `OWNER_FACE_BY_POINT` to derive fixture-specific rank signals (`0` for the known owner face, `10 + face_id` otherwise). This is caller-supplied priority, not engine-inferred ownership — the policy is expressed in the fixture data, not inside the pipeline.
- `rt.derive_owner_face_priority_columns_from_rank_signals()` and `rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy()` are the only `rt.*` entry points called. Neither introduces native/device traversal logic. No BVH, no RT-core dispatch, no app-specific mismatch handling.

The one observation: `OWNER_FACE_BY_POINT` is a module-level constant rather than being loaded from the incident artifact. This is appropriate for a route fixture probe — the expected owner faces are the fixture definition — but it means the script will fail loudly (KeyError at line 46) if the incident artifact contains point IDs not in the dict. For a seven-point fixture that is fully controlled, this is acceptable. It should be noted before any generalization to runtime-derived inputs.

### 2. Does the JSON artifact honestly prove only the seven-point route fixture: owner faces match expected, recovered shape ids match exact, and claim boundaries are all false?

**Yes. The artifact is fully honest and fully inspectable.**

The JSON (`docs/reports/goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.json`) records:

- `selected_owner_faces_match_expected: true` — all seven points (522, 523, 538, 539, 540, 564, 565) have the expected owner face.
- `recovered_shapes_match_exact: true` — recovered shape IDs match exact for all seven points.
- Both the `selected_owner_face_by_point` and `expected_owner_face_by_point` dicts are written side-by-side; a reader can verify the match without trusting the boolean summary alone.
- Both `recovered_shape_ids_by_point` and `exact_shape_ids_by_point` dicts are likewise side-by-side.
- All six `claim_boundary` fields are `false`: `release_authorized`, `public_speedup_claim_authorized`, `rayjoin_paper_reproduction_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`, `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`.
- The `interpretation` field explicitly limits scope: "Route-fixture probe only: validates the app-layer owner-face CuPy continuation over stored RayJoin/CDB mismatch artifacts; it is not native RT traversal or a paper reproduction claim."

The scale is modest and honest: 7 points, 21 incident rows, 26 candidate rows, 11 topology rows. No inflated scale claims.

### 3. Is the commit/hardware provenance adequate for this internal evidence: commit `ef36541ed81695d79c39cdc8c08ac37fc154f4e9`, RTX A5000, CuPy 14.1.1?

**Yes.**

The JSON artifact records:
- `rtdl_commit: ef36541ed81695d79c39cdc8c08ac37fc154f4e9` — confirmed as the commit that added the probe script (`git show --stat ef36541e` shows `goal3372_owner_face_cupy_route_fixture_probe.py` added, 191 lines).
- `gpu: NVIDIA RTX A5000, 580.126.09` — driver version included alongside device name.
- `cupy_version: 14.1.1`

The test (`tests/goal3372_owner_face_cupy_route_fixture_probe_test.py`) pins all three values exactly:

```python
self.assertEqual(data["rtdl_commit"], "ef36541ed81695d79c39cdc8c08ac37fc154f4e9")
self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
self.assertEqual(data["cupy_version"], "14.1.1")
```

This is the appropriate provenance depth for an internal seven-point route fixture. The commit recorded in the artifact (`ef36541e`) is the probe script commit; the evidence commit (`71a24af8`) adds the artifact and test on top. This split is coherent: the artifact was produced by the script at `ef36541e`, then committed in `71a24af8`. No discrepancy.

### 4. Does the report avoid release, public speedup, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, and RTDL-beats-RayJoin claims?

**Yes. All six categories are explicitly disclaimed and negated in the artifact.**

The report (`docs/reports/goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.md`) status line reads:

> "This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims."

The "Boundary" section repeats all six prohibitions individually. The JSON `claim_boundary` object negates all six programmatically, and the test verifies `self.assertFalse(any(data["claim_boundary"].values()))`. The boundary wording test also checks `report` and `script` text for the key phrases:

- `"route-fixture probe"` in report
- `"not native RT traversal"` in report
- `"does not authorize release"` in report
- `"RayJoin paper reproduction wording"` in report
- `"true zero-copy wording"` in report
- `"Route-fixture probe only"` in script
- `"rayjoin_paper_reproduction_claim_authorized"` in script

No prohibited claim appears anywhere in the reviewed files.

### 5. What remains before moving from stored route fixture to runtime-derived CDB topology/incident integration?

The report's "Next Step" correctly identifies the direction. This review adds detail:

1. **CDB data loader:** The script currently defaults to two hardcoded artifact paths (`goal3328` topology, `goal3335` incident). Moving to runtime-derived columns requires a loader that reads the live CDB case and produces the same column schema at query time.

2. **Input-set generalization:** `OWNER_FACE_BY_POINT` is a hard fixture constant. Runtime integration must either load expected owner faces from CDB metadata or treat them as validation-only and allow the pipeline to select without pre-seeded expectations.

3. **Regression parity test:** A test that runs both stored-artifact and runtime-derived paths and asserts identical output is needed to confirm no regression when moving off fixture inputs.

4. **Overhead measurement:** The report names "reduces host-side mismatch handling overhead" as a goal. This requires a comparative benchmark (host-side reference vs. CuPy path) with a bounded scale to justify the path. No such measurement exists yet; it is not expected at this stage but must precede any promotion claim.

5. **Exact-count authority preservation:** Verification that runtime-derived incident and topology columns preserve exact-count semantics under concurrent CDB writes or partial cache states.

6. **Blocked items unchanged from Goal3369:** Native/device lowering of the full pipeline, default selection of the composed CuPy helper, and all six claim categories remain blocked.

---

## Summary

Goal3372 adds a well-scoped, honest runnable route-fixture probe that exercises the composed CuPy owner-face selector+filter over stored artifacts. The script introduces no engine logic. The artifact is fully inspectable, the provenance is pinned to exact commit+GPU+driver+CuPy, and all six claim categories are negated in code, test, and prose. The seven-point fixture results are consistent with Goal3369 (which validated the same pipeline in a unit test).

**Verdict: accept**

This internal evidence record is complete for the route-fixture stage. The clear next step is bounded runtime CDB integration per the report's "Next Step" section.
