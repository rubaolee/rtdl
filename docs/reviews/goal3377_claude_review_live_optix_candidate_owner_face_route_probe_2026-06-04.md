# Goal3377: Claude Review — Live OptiX Candidate Owner-Face Route Probe (Goal3376)

Date: 2026-06-04

**Verdict: accept**

This is an independent Claude review of Goal3376 (commits `ddc6962c`, `5d486542`). It is distinct from the Codex implementation and from the prior Claude review of Goal3372 (`docs/reviews/goal3373_claude_review_owner_face_cupy_route_fixture_probe_2026-06-04.md`).

---

## Review Question Responses

### 1. Does Goal3376 genuinely replace stored candidate-row input with RTDL/OptiX live `candidate_device_columns(...)` output?

**Yes. The replacement is genuine and verifiable from code and artifact.**

`run_probe()` in `scripts/goal3376_owner_face_cupy_optix_candidate_route_probe.py` calls:

```python
prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
candidate_columns = prepared.candidate_device_columns(points)
cupy_candidates = candidate_columns.as_cupy_columns()
candidate_point_ids = cupy_candidates["point_id"]
candidate_shape_ids = cupy_candidates["shape_id"]
```

This is the RTDL/OptiX live traversal path. No stored candidate row artifact is read; the only stored input is the expected-answer oracle from Goal3328 (`stored_exact_oracle_artifact_used_as_input: true`). The artifact records:

- `candidate_rows_from_optix_device_columns: true`
- `stored_candidate_artifact_used_as_input: false`

Goal3374's probe still read candidate rows from a stored artifact. Goal3376 replaces that with live output of `candidate_device_columns(points)`. The three-step progression is clean:
- Goal3372: stored candidates + stored topology + stored incident
- Goal3374: stored candidates + live CDB topology + live CDB incident
- Goal3376: **live OptiX candidates** + live CDB topology + live CDB incident

Each step isolates a single source transition, which is good practice.

### 2. Does the script keep native engine logic generic and app-agnostic, with owner-face policy remaining in the app/Python/CuPy continuation?

**Yes. Separation is maintained throughout.**

`prepare_point_closed_shape_membership_2d_optix(shapes)` and `candidate_device_columns(points)` produce a generic `(point_id, shape_id)` device-resident candidate stream. No owner-face logic, face priority ranking, or topology awareness is inside the OptiX path. The script then:

1. Masks the seven fixture points from the full 1429-row candidate stream in CuPy (`cp.isin`).
2. Derives topology and incident rows from the CDB at runtime (in Python, via `_runtime_metadata_columns()`).
3. Assigns `rank0` using the `OWNER_FACE_BY_POINT` constant — a Python-layer policy, not an engine inference.
4. Calls `rt.derive_owner_face_priority_columns_from_rank_signals()` and `rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy()` — both are app-layer `rt.*` entry points that introduce no RT-core dispatch.

One technical note: at line 83, `rank0` uses `10 + face_id` as the "not owner" rank for non-owner faces. This means the relative priority among non-owner faces is face_id-ordered rather than uniform. At this fixture scale this is harmless and the oracle confirms correctness, but this policy encoding should be revisited before generalization to all points where face_id distributions are unknown.

The `finally` block correctly closes `candidate_columns` and `prepared` even on error, which is appropriate resource management for device-resident objects.

### 3. Does the artifact honestly show the seven known boundary-extra points: live candidates include extras, owner-face continuation removes them, recovered shapes match exact?

**Yes. The artifact is fully honest and independently verifiable.**

The JSON records both `live_candidate_shape_ids_by_point` and `recovered_shape_ids_by_point` side-by-side, enabling a reader to verify the filtering effect without trusting the boolean summaries alone. The extras are visible:

| point_id | live candidate shape IDs | recovered exact shape IDs |
| ---: | --- | --- |
| 522 | 521, 522, 523 | 522, 523 |
| 523 | 521, 522, 523 | 522, 523 |
| 538 | 418, 535, 539, 540 | 535, 539 |
| 539 | 418, 535, 539, 540 | 535, 539 |
| 540 | 418, 535, 539, 540 | 418, 540 |
| 564 | 437, 559, 562, 565 | 562, 565 |
| 565 | 437, 559, 562, 565 | 562, 565 |

The live candidate stream contains the known boundary extras (521 for points 522/523; 540/535 overlap for points 538/539; 535 and 540 swapped for point 540; 437/559 for points 564/565). After the CuPy owner-face continuation, the recovered set matches the exact oracle exactly. Both `recovered_shapes_match_exact: true` and `selected_owner_faces_match_expected: true` are confirmed, with the full dicts recorded.

The topology lookup at line 153–154 raises a `ValueError` (not silently ignores) if a live candidate shape is missing from CDB topology. This is defensive and appropriate for this stage.

One boundary characteristic worth naming explicitly: for point 540, the live candidate set includes both 418 and 535 as extras alongside 539 and 540. The owner-face continuation correctly retains 418 and 540 (the exact answer) while discarding 535. This is the most geometrically ambiguous of the seven cases, and the fact that it resolves correctly via the CDB-derived topology path is meaningful evidence for the pipeline's correctness on boundary shapes.

### 4. Are the provenance fields and tests sufficient for this internal stage?

**Yes. Provenance is pinned to the correct depth.**

The JSON artifact records:
- `rtdl_commit: ddc6962c4c23d4bd9091f487d35f029b7b042ef7` — matches the implementation commit that adds the script (291 lines, confirmed via `git show --stat ddc6962c`).
- `gpu: NVIDIA RTX A5000, 580.126.09` — device name plus driver version.
- `cupy_version: 14.1.1`
- `optix_candidate_row_count: 1429` — full 512-chain county slice candidate count.
- `selected_candidate_row_count: 26` — seven-point subset.
- `optix_candidate_device_resident: true` — confirms the live device path was used.
- `optix_candidate_overflow: false` — confirms the 244736-capacity buffer was not exhausted.
- `optix_candidate_traversal_seconds: 0.000346161` — non-zero, consistent with real traversal.

The test (`tests/goal3376_owner_face_cupy_optix_candidate_route_probe_test.py`) pins all six key provenance values exactly:

```python
self.assertEqual(data["rtdl_commit"], "ddc6962c4c23d4bd9091f487d35f029b7b042ef7")
self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
self.assertEqual(data["cupy_version"], "14.1.1")
self.assertEqual(data["optix_candidate_row_count"], 1429)
self.assertEqual(data["selected_candidate_row_count"], 26)
self.assertFalse(data["optix_candidate_overflow"])
```

The commit recorded in the artifact (`ddc6962c`) is the probe-script commit. The evidence commit (`5d486542`) adds the artifact and test on top. This two-commit split is coherent and consistent with prior stepping stones (Goal3372/Goal3374 used the same pattern).

The test `test_report_and_script_keep_live_candidate_boundary_visible` performs text-level checks that the report and script carry the correct boundary vocabulary, which is a useful secondary guard against prose drift.

### 5. Are all claim boundaries safe?

**Yes. All seven claim-boundary flags are false, and the claims are negated in code, test, and prose.**

Goal3376 adds a seventh boundary flag (`native_default_route_authorized`) that was absent in Goal3372's artifact. This is an appropriate addition: the live-candidate path is one step closer to a default route, and explicitly negating the flag at this stage is the correct call.

The full boundary object in the JSON:

```json
"claim_boundary": {
  "native_default_route_authorized": false,
  "public_speedup_claim_authorized": false,
  "rayjoin_paper_reproduction_claim_authorized": false,
  "release_authorized": false,
  "rt_core_speedup_claim_authorized": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "true_zero_copy_claim_authorized": false
}
```

The test asserts `self.assertFalse(any(data["claim_boundary"].values()))`. The report's "Boundary" section lists all prohibitions individually in prose. The `interpretation` field in the JSON repeats the scope limitation. No prohibited claim appears anywhere in the reviewed files.

The traversal time (`0.000346161` seconds) is recorded as an observation but not surfaced as a speedup claim or comparative benchmark, which is correct.

### 6. What remains before route-scale promotion?

The report's "What remains blocked" section is accurate. This review adds specificity on each item:

1. **Remove the seven-point mask.** Lines 141–143 filter the 1429-row candidate stream to only the seven fixture points via `cp.isin(candidate_point_ids, selected_point_array)`. This mask must be removed before the route operates on all points. At full 512-chain scale, the selected candidate count will grow from 26 to 1429, and the incident/topology derivation path must handle the full scope without the fixture shortcut.

2. **Generalize owner-face priority policy.** `OWNER_FACE_BY_POINT` (module-level dict at lines 19–27) hard-codes the expected owner face for each of the seven fixture points. The `rank0` column (line 83) uses this dict to assign signal values. Before route-scale operation, the priority policy must be derived from CDB metadata or runtime inference rather than a pre-seeded fixture constant. The `KeyError` risk at line 83 is guarded by filtering incident rows to `selected_points` (which are exactly the dict keys), but this guard disappears when the mask is removed.

3. **Validate owner-face selection for all CDB points.** The current oracle (`goal3328` artifact) covers only the seven known mismatch points. A route-scale correctness test requires either a broader oracle or a correctness criterion derivable from the CDB itself.

4. **Default route selection.** The native-default-route flag is explicitly negated. The question of which path is taken when multiple routes are available (e.g., CuPy owner-face vs. direct exact match for non-mismatch points) is unresolved.

5. **Native lowering of the owner-face continuation.** `run_closed_shape_owner_face_priority_membership_pipeline_cupy` runs in Python/CuPy. Native lowering is not expected at this stage but is a prerequisite for any performance or zero-copy claim.

6. **All six original claim categories.** Release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, and true-zero-copy remain blocked. The `native_default_route_authorized: false` flag adds a seventh explicit block.

---

## Summary

Goal3376 completes the third and final source-replacement step in the fixture→runtime CDB→live OptiX progression. The script genuinely calls `candidate_device_columns(points)` and feeds its live device-resident output into the CuPy owner-face continuation. Engine logic remains generic and app-agnostic. The artifact honestly records the boundary-extra phenomenon — live candidates contain the known extras, owner-face filtering removes them, recovered shapes match the exact oracle — with both input and output dicts recorded for independent verification. Provenance is pinned to the correct commit, GPU, CuPy version, and candidate row counts. All seven claim-boundary flags are false, including the new `native_default_route_authorized` flag.

The seven-point mask and the `OWNER_FACE_BY_POINT` fixture constant are the correct stopping points at this stage. They are not defects; they are the explicit scope boundary that must be lifted before route-scale promotion.

**Verdict: accept**

This internal evidence record is complete for the live-candidate route probe stage. The clear next step is removing the seven-point mask and deriving owner-face priority policy from the CDB for all points.

---

*This is an independent Claude review. It does not authorize release, public performance claims, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route claims.*
