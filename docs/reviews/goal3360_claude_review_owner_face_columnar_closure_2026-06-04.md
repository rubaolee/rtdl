# Goal3360: Claude Closure Review — Owner-Face Columnar Gap Closure (Goals 3358–3359)

Date: 2026-06-04
Reviewer: Claude (claude-sonnet-4-6), independent review
Commits: `6a47e36a` (Goal3358), `174deb39` (Goal3359)
Prior review: Goal3357 (commit `9f810c9f`), verdict `accept-with-boundary`
Verdict: **accept**

This does not authorize release, public speedup claims, RayJoin paper reproduction, RT-core speedup claims, true zero-copy claims, or RTDL-beats-RayJoin claims. The verdict covers the Python reference contract chain only.

---

## Review Questions

### Q1: Does Goal3358 close the real-artifact columnar fixture gap?

**Yes, completely.**

`goal3358_owner_face_columnar_known_mismatch_fixture_test.py` reads the real JSON artifacts from Goals 3328 and 3335 and drives the complete three-stage columnar pipeline:

1. `derive_owner_face_priority_columns_from_rank_signals` — builds priority columns from caller-supplied rank signals over the seven known county mismatch points
2. `select_owner_faces_from_incident_candidate_columns_with_priority_columns` — selects one owner face per point
3. `filter_closed_shape_membership_candidate_columns_by_owner_face_columns` — filters candidates and verifies exact shape ID recovery

`test_complete_columnar_pipeline_recovers_known_exact_rows` asserts that for every one of the seven mismatch points, the filtered output contains exactly the known exact shape IDs and no extras. `test_columnar_fixture_matches_row_reference` asserts full output equality between the columnar path and the row-mode reference path (`filter_closed_shape_membership_candidates_by_owner_face`). This is the cross-path parity proof that was missing.

The priority rank signal is deliberately supplied by the fixture test from the known `OWNER_FACE_BY_POINT` mapping. The report explicitly records this as intentional: RTDL does not infer CDB/RayJoin ownership policy. The fixture boundary is visible and correct.

**Gap 1 is closed.**

### Q2: Does Goal3359 adequately document and test `missing_topology = drop_candidate`?

**Yes, on three levels.**

1. **Contract descriptor**: `owner_face_priority_pipeline_contract()` now includes `"filter_policy": {"missing_owner": "fail_closed_by_default", "missing_topology": "drop_candidate", "topology_face_presence_columns": "gate_left_and_right_face_ids_when_present"}` (`closed_shape_topology.py:644–648`).

2. **Validator enforcement**: `validate_owner_face_priority_pipeline_contract()` explicitly checks `filter_policy.get("missing_topology") != "drop_candidate"` and `filter_policy.get("missing_owner") != "fail_closed_by_default"` at lines 703–708, raising `ValueError` if either value drifts. A future edit that changes these strings would fail immediately at validation time.

3. **Behavioral test**: `test_columnar_filter_drops_candidates_with_missing_topology` passes a candidate with `shape_id=100` against an empty topology sequence and asserts the output is entirely empty — i.e., the candidate is silently dropped, not an error. This correctly characterizes the behavior that was undocumented.

**Gap 2 is closed.**

### Q3: Are topology face-presence columns now tested adequately?

**Yes.**

`test_columnar_filter_honors_optional_topology_face_presence_columns` covers both sides of the gate:

- With `topology_has_left_faces=(0,)` and `owner_face_id=10` matching `left_face_id=10`, the left face is gated out — the candidate is excluded and the output is empty.
- With `topology_has_left_faces=(1,)` (same everything else), the left face is present — the candidate is included with `membership=1`.

The `topology_face_ids` row helper (`closed_shape_topology.py:54–66`) implements the gate as `int(row.get("has_left_face", 1)) and "left_face_id" in row`, so the default is inclusive (has_left_face defaults to 1 when absent), which is consistent with the columnar function's `topology_has_left_faces: Sequence[int] | None = None` defaulting to no override.

One minor observation: the contract field `topology_face_presence_columns` is checked by the test (`test_contract_documents_missing_topology_drop_policy`) but is not asserted by `validate_owner_face_priority_pipeline_contract()`. The validator enforces `missing_topology` and `missing_owner` but does not check `topology_face_presence_columns`. This means the field's value could drift from `"gate_left_and_right_face_ids_when_present"` without the validator catching it, though the test would catch it. This is a trivial future hardening opportunity, not a pre-lowering blocker.

**Gap 3 is closed.**

### Q4: Is conflicting owner-face selection fail-closed coverage sufficient?

**Yes.**

`test_conflicting_owner_face_selection_rows_remain_fail_closed` calls `rt.owner_face_ids_by_point_from_selection_rows` with two rows carrying the same `point_id=1` but different `owner_face_id` values (10 and 20) and asserts `ValueError` with the message `"conflicting owner face"`. This matches the guard at `closed_shape_topology.py:570–572`. The error message pattern is narrow enough to confirm the specific guard fires rather than a generic exception.

**Gap 4 is closed.**

### Q5: What remains blocked before native/device lowering?

All pre-lowering blockers from Goal3357 are now resolved at the Python reference contract level. The following remain blocked at the next-stage level and are correctly carried forward in Goal3359's report:

| Blocker | Status |
|---------|--------|
| Native/device lowering | Blocked — `native_lowering_status: "blocked_until_contract_stable_and_validated"` in contract |
| Pod/native evidence for any OptiX-path implementation | Blocked |
| External review of post-3358/3359 closure state | This review closes that item |
| Release or public performance wording | Blocked |
| RayJoin paper reproduction wording | Blocked |
| RTDL-beats-RayJoin wording | Blocked |
| Broad RT-core speedup wording | Blocked |
| True zero-copy wording | Blocked |
| Automatic owner-face derivation | Blocked |
| Native engine inferring ownership policy | Prohibited by contract and validator |

---

## Closure Map Verification

| Goal3357 finding | Closed by | Mechanism verified |
|------------------|-----------|--------------------|
| Missing end-to-end columnar fixture over seven known mismatch points | Goal3358 | Exact-row recovery test + cross-path parity test against real artifacts |
| Silent topology-missing drop undocumented | Goal3359 | Contract field + validator enforcement + behavioral test |
| Optional topology face-presence columns untested in columnar filter | Goal3359 | Two-sided gate test (has_left_face=0 excludes, =1 includes) |
| Conflicting owner-face selection rows uncovered | Goal3359 | ValueError raised with `"conflicting owner face"` message verified |

All four gaps are closed.

---

## Boundary Re-Checks

| Claim | Status |
|-------|--------|
| Release authorized | `False` — confirmed in contract and both reports |
| Public speedup claim | `False` — confirmed |
| RayJoin paper reproduction claim | `False` — confirmed |
| RTDL-beats-RayJoin claim | `False` — confirmed |
| Broad RT-core speedup claim | `False` — confirmed |
| True zero-copy claim | `False` — confirmed |
| Native engine may infer ownership | `False` — enforced by validator at `closed_shape_topology.py:694–696` |
| Native engine may invent priority | `False` — enforced by validator at `closed_shape_topology.py:700–702` |
| Native lowering status | `blocked_until_contract_stable_and_validated` |

---

## Verdict

**accept**

Goals 3358–3359 close all four pre-lowering gaps identified in the Goal3357 `accept-with-boundary` verdict. The Python reference contract is now internally complete:

- The real-artifact columnar fixture provides exact-row recovery over all seven known county mismatch points and cross-path parity proof between the columnar and row-mode paths.
- The `missing_topology = drop_candidate` behavior is documented in the contract descriptor, locked by the validator, and covered by a behavioral test.
- Optional topology face-presence columns are tested with both inclusive and exclusive gating behavior.
- The conflicting owner-face selection fail-closed guard is covered by an explicit test.

The contract's claim boundaries remain fully blocked. The native engine is prohibited from inferring ownership or inventing priority by the validated contract. No release, performance, or paper-reproduction claim authorization follows from this verdict.

The next required gate before promoting beyond the Python reference contract is pod/native evidence for any device-lowered implementation.
