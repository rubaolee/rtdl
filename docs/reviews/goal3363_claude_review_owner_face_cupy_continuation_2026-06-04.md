# Goal3363: Claude Review — Owner-Face CuPy Filter Continuation (Goal3362)

Date: 2026-06-04
Reviewer: Claude (claude-sonnet-4-6), independent review
Commit: `4a007cea`
Prior review: Goal3360 (commit `174deb39`), verdict `accept`
Verdict: **accept-with-boundary**

This does not authorize release, public speedup claims, RayJoin paper reproduction, RT-core speedup claims, true zero-copy claims, or RTDL-beats-RayJoin claims. The verdict covers the CuPy device-column continuation only; it does not promote this path to a device-lowered default.

---

## Review Questions

### Q1: Is the CuPy continuation app-agnostic and compatible with the owner-face contract?

**Yes.**

The function `filter_closed_shape_membership_candidate_columns_by_owner_face_cupy` (`closed_shape_topology.py:550`) accepts only generic columns: candidate point/shape IDs, topology shape/face columns, and owner point/face columns. It contains no reference to CDB, RayJoin, GIS, or any application-specific policy. The function docstring reads "CuPy device-column continuation for owner-face membership filtering" and does not claim app-specific semantics.

The contract registration is correct. `owner_face_priority_pipeline_contract()` (`closed_shape_topology.py:759–763`) lists this helper under `optional_columnar_pipeline_helpers`, and `validate_owner_face_priority_pipeline_contract()` (`closed_shape_topology.py:848–858`) explicitly asserts that `"filter_closed_shape_membership_candidate_columns_by_owner_face_cupy"` is present in `columnar_helpers`, raising `ValueError` on drift. The `__init__.py` export at line 603 is present and correct.

The `native_engine_may_infer_app_ownership: False` flag on the contract is correct and validated. The CuPy continuation does not change this boundary.

### Q2: Does it preserve the important fail-closed semantics from the Python columnar reference?

**Yes, with two documented semantic restrictions noted below.**

**Missing owner — default fail-closed**: `missing_owner_policy="raise"` is the default (`closed_shape_topology.py:557`). When the owner lookup at line 637 finds any candidate whose owner is not present in `owner_point_ids`, it raises `KeyError("missing owner face id for one or more point ids")` before returning any output. The check fires on the full candidate batch, not per-row, which is consistent with a device-path approach. Tested by `test_cupy_filter_fails_closed_on_missing_or_duplicate_owner`.

**Duplicate owner point IDs — default rejection**: `require_unique_owner_point=True` is the default (`closed_shape_topology.py:562`). The uniqueness check at lines 623–628 runs a `cp.any(sorted_owner_points[1:] == sorted_owner_points[:-1])` comparison after sorting, raising `ValueError("owner point ids must be unique for the CuPy filter")` on violation. Tested by the same test.

**Missing topology — drop, not raise**: Consistent with the Python reference. Missing topology candidates produce `topology_found=False` at line 655–658 and are excluded from `keep` at line 666. Tested by `test_cupy_filter_honors_missing_topology_and_face_presence`.

**Optional face-presence gating**: `topology_has_left_faces` / `topology_has_right_faces` default to all-ones when `None` (lines 594–605), matching the Python reference's `row.get("has_left_face", 1)` default. The gate at lines 664–665 is correct:
```python
matches_left = has_left & (left_faces == owner_faces)
matches_right = has_right & (right_faces == owner_faces)
```
Tested by the face-presence test.

**`searchsorted` boundary safety**: The `owner_safe_pos = cp.minimum(owner_pos, owner_count - 1)` pattern (`closed_shape_topology.py:630`) and `topology_safe_pos = cp.minimum(topology_pos, topology_count - 1)` pattern (`line 654`) correctly prevent out-of-bounds device memory access before checking the actual match condition. This is correct.

### Q3: Is the pod evidence sufficient for this internal device-continuation step?

**Yes, for this stage.**

The pod evidence (`docs/reports/goal3362_owner_face_cupy_filter_continuation_2026-06-04.md`) records:

- Host: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000
- Driver: 580.126.09
- CuPy: 14.1.1
- Initial pre-commit run: 15 tests across four related test files, `OK` in 8.593s
- Committed-code rerun at `ea7a247f`: 5 Goal3362-specific tests, `OK` in 0.657s (current committed commit is `4a007cea` after evidence refresh)

The two-run structure is adequate: the wider 15-test run confirms no regression against Goal3358, 3359, and 3361; the 5-test committed-code rerun confirms the committed code itself is what ran. The runtime of 8.593s on a GPU for 15 tests confirms CuPy-using paths actually executed (not all skip-guarded). The committed-code rerun's 0.657s for 5 tests at `ea7a247f` confirms the correct revision.

The evidence is sufficient for an internal device-continuation step. It is not sufficient for promoting this path to a device-lowered default or for any public performance claim.

### Q4: Are the boundary statements clear enough?

**Yes.**

The report (`docs/reports/goal3362_owner_face_cupy_filter_continuation_2026-06-04.md`) contains all required phrases: "not native RT traversal", "does not authorize release", "pod evidence required". The test `test_report_keeps_cupy_continuation_boundary_visible` asserts these strings at lines 108–114, ensuring the report cannot drift silently.

The contract's `claim_boundary` at `closed_shape_topology.py:787–795` has all six flags set to `False` and is enforced by `validate_owner_face_priority_pipeline_contract()` at line 860. The `native_lowering_status: "blocked_until_contract_stable_and_validated"` at line 782 is present.

One minor observation: the function docstring is minimal — it reads "CuPy device-column continuation for owner-face membership filtering" without an explicit "not native RT traversal" statement. The contract, report, and test enforce this boundary adequately, so this is not a pre-lowering blocker.

### Q5: What must be fixed before any next device/native lowering step?

Four items require attention before this continuation can be promoted:

**Item 1 — Output deduplication divergence (must document).**
The Python reference (`filter_closed_shape_membership_candidates_by_owner_face`, `closed_shape_topology.py:91–115`) uses `seen: set[tuple[int, int]] = set()` to deduplicate `(point_id, shape_id)` pairs in the output. The CuPy continuation (`closed_shape_topology.py:550–673`) has no deduplication step. For input without duplicate candidate pairs, results match and the test passes. If a caller passes duplicate `(point_id, shape_id)` candidate pairs, the CuPy output would contain duplicates where the Python reference would not. This semantic divergence must be explicitly documented in the contract's `filter_policy` or function docstring before this continuation can be selected by default, so callers are aware of the precondition.

**Item 2 — Negative face ID exclusion divergence (must document).**
The Python row helper `topology_face_ids` (`closed_shape_topology.py:54–66`) excludes face IDs where `left < 0` or `right < 0`. The CuPy continuation compares `left_faces == owner_faces` and `right_faces == owner_faces` directly with no `>= 0` guard at lines 664–665. If a topology row carries `left_face_id=-1` and an owner row carries `owner_face_id=-1`, the CuPy continuation would produce a spurious match that the Python reference would reject. For real data with valid non-negative face IDs, results match. This precondition must be documented.

**Item 3 — `require_unique_owner_point` semantic restriction vs. Python reference (must document).**
The Python reference supports `owner_face_ids_by_point: Mapping[int, int | Iterable[int]]`, meaning a single point may have multiple allowed owner faces. The CuPy continuation's `searchsorted` lookup is inherently single-face-per-point and enforces this via `require_unique_owner_point=True`. This is a narrower contract. Callers using multiple owner faces per point must fall back to the Python columnar reference. This must be stated explicitly in the function docstring and acknowledged in any promotion gate criteria.

**Item 4 — `cp.where` tie resolution when both faces match (minor, document).**
When both `matches_left` and `matches_right` are true for a single candidate (meaning the owner face ID equals both the left and right face ID of a topology row), the CuPy version returns `left_faces` via `cp.where(matches_left, left_faces, right_faces)` at line 667. The Python reference returns `min(matched_faces)` which would return the smaller of the two face IDs. For the common case where `left_face_id != right_face_id`, or when they are equal, the results agree. The divergence only matters when `left_face_id != right_face_id` and both equal `owner_face_id`, which is geometrically unusual. Still worth noting in the contract.

---

## Behavioral Verification

| Check | Result |
|-------|--------|
| CuPy input normalization (`cp.asarray`) accepts both numpy/cupy arrays | Confirmed — lines 573–579 |
| Empty-candidate early return | Correct — lines 607–614, returns CuPy empty arrays |
| Empty-owner-table produces all-missing mask | Correct — lines 616–618 |
| Empty-topology-table produces all-missing topology mask | Correct — lines 640–645 |
| `owner_safe_pos` OOB prevention before match check | Correct — lines 630–634 |
| `topology_safe_pos` OOB prevention before match check | Correct — lines 653–658 |
| Missing-owner `raise` fires before output | Correct — line 637 |
| Duplicate-owner check on sorted array | Correct — lines 623–628 |
| Topology face-presence gating default (all-ones) | Correct — lines 594–601 |
| Output arrays are CuPy device arrays | Correct — lines 668–673 |
| Contract registration and validator enforcement | Correct — `closed_shape_topology.py:759, 848` |
| Export in `__init__.py` | Correct — line 603 |

---

## Boundary Re-Checks

| Claim | Status |
|-------|--------|
| Release authorized | `False` — confirmed in contract and report |
| Public speedup claim | `False` — confirmed |
| RayJoin paper reproduction claim | `False` — confirmed |
| RTDL-beats-RayJoin claim | `False` — confirmed |
| Broad RT-core speedup claim | `False` — confirmed |
| True zero-copy claim | `False` — confirmed |
| Native engine may infer app ownership | `False` — enforced by validator |
| Native engine may invent priority | `False` — enforced by validator |
| Native lowering status | `blocked_until_contract_stable_and_validated` |
| Is this native RT traversal | No — CuPy device-column continuation only |

---

## Verdict

**accept-with-boundary**

Goal3362 correctly implements the owner-face membership filter as a CuPy device-column continuation. The core fail-closed semantics are preserved: missing owner rows raise by default, duplicate owner point IDs raise by default, missing topology rows are silently dropped, and topology face-presence columns gate correctly. The contract registration and validator enforcement are in place. Pod evidence on an NVIDIA RTX A5000 with CuPy 14.1.1 confirms the committed code passes all five tests.

The `accept-with-boundary` verdict (rather than `accept`) is issued because four semantic divergences from the Python reference exist and are not yet documented in the contract or function docstring: no output deduplication, no negative face ID exclusion, the `require_unique_owner_point` single-face-per-point restriction, and the `cp.where` tie resolution. None of these diverge on well-formed input (the tested cases), but all four must be stated explicitly as preconditions or documented divergences before this continuation can be promoted to a device-lowered default path.

**Required before any promotion gate:**

1. Document the no-output-deduplication precondition (callers must not pass duplicate `(point_id, shape_id)` pairs).
2. Document the no-negative-face-ID precondition (topology face IDs must be non-negative).
3. Document the single-owner-face-per-point restriction vs. the Python reference.
4. Document the `cp.where` left-face priority when both faces match (or fix to use `cp.minimum`).

None of these block the current internal device-continuation designation. All must be resolved before this path is selected by default or promoted past its current `optional_columnar_pipeline_helper` status.
