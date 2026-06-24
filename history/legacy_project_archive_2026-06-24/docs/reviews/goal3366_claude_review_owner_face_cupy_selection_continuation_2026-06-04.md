# Goal3366: Claude Review — Owner-Face CuPy Selection Continuation (Goal3365)

Date: 2026-06-04
Reviewer: Claude (claude-sonnet-4-6), independent review — distinct from Codex implementation
Commit: `6196c991`
Prior review: Goal3363 (commit `4a007cea`), verdict `accept-with-boundary`
Gap closure: Goal3364 (`docs/reports/goal3364_owner_face_cupy_review_gap_closure_2026-06-04.md`)
Verdict: **accept-with-boundary**

This does not authorize release, public speedup claims, RayJoin paper reproduction claims, RT-core speedup claims, true zero-copy claims, or RTDL-beats-RayJoin claims. The verdict covers the CuPy device-column selection continuation only and does not promote this path to a device-lowered default.

---

## Review Questions

### Q1: Does `select_owner_faces_from_incident_candidate_columns_with_priority_cupy(...)` preserve the Python selector's core semantics?

**Yes — all four core semantics are correctly preserved.**

**Unique max wins:**
`cp.maximum.at(max_counts, inverse, incident_face_counts)` computes the per-group maximum count on device
(`closed_shape_topology.py:587–588`). `winner_mask = incident_face_counts == max_counts[inverse]` selects all rows at the maximum (`line 590`). `winner_counts = cp.bincount(inverse[winner_mask], minlength=point_count)` counts winners per group (`lines 591–593`). `unique_groups = winner_counts == 1` identifies groups with a single maximum winner (`line 594`). These correspond directly to the Python reference's `max_count = max(...)` and `len(winners) != 1` checks.

**Tied max requires explicit priority:**
`tied_winner_mask = winner_mask & (winner_counts[inverse] > 1)` identifies tied winner rows (`line 595`). The priority lookup uses `cp.searchsorted(sorted_priority_keys, incident_keys)` with an out-of-bounds guard (`lines 605–611`). `cp.minimum.at(min_priorities, inverse, priority_for_min)` computes the per-group minimum priority among tied winners (`lines 626–627`). `priority_winner_mask` at lines 628–632 selects rows whose priority equals the group minimum. This is semantically equivalent to the Python reference's `min_priority = min(...)` and `priority_winners = [row for row in count_winners if ...]` logic.

**Missing/tied priority fails closed by default:**
`ambiguity_policy="raise"` is the default (`line 500`). Missing priority detection at `lines 616–622` raises `ValueError("missing owner-face priority for one or more tied points")` before any output when `ambiguity_policy == "raise"`. Tied priority detection at `lines 633–641` raises `ValueError("ambiguous owner-face priority for one or more tied points")` similarly. The four status-code groups (unique, priority_resolved, missing_priority, ambiguous_priority_groups) are mutually exclusive by construction and exhaust all possible group outcomes — no group can fall through with status code 0.

**`emit_ambiguous` remains explicit:**
`selected_groups = unique_groups | priority_resolved_groups` is the base selection (`line 679`). Only when `ambiguity_policy == "emit_ambiguous"` does `selected_groups` expand to include `missing_priority_groups | ambiguous_priority_groups` (`line 681`). The "drop" branch at `line 683` (`selected_groups = selected_groups`) is a no-op that deliberately leaves the base intact, which is correct.

**One output-key divergence (must document before promotion):**
The CuPy selector returns `selection_status_code` (integer, CuPy array) while the Python columnar selector at `lines 469–477` returns `selection_status` (Python string). These are different output keys with different value types. Callers routing between the two paths must handle this translation explicitly. This is an intentional device-efficiency trade-off but is not yet documented in the function docstring or contract. It must be stated before this helper can be promoted beyond an optional continuation.

### Q2: Are the numeric `selection_status_code` outputs and label map a valid device-column substitute for Python status strings without hiding semantics from downstream callers?

**Yes, with the translation-layer caveat noted above.**

The four codes are:
- `1`: `unique_max_incident_face`
- `2`: `priority_tie_break`
- `3`: `missing_priority`
- `4`: `ambiguous_priority_tie`

All four are non-zero and distinct, leaving no ambiguity between statuses. The label map `OWNER_FACE_SELECTION_STATUS_CODES` at `closed_shape_topology.py:9–14` is returned in the output as `"selection_status_code_labels": dict(OWNER_FACE_SELECTION_STATUS_CODES)` (`line 691`). This is a host Python dict, appropriate for metadata that callers decode on the host. Downstream code can decode status codes by key lookup against this map rather than by magic numbers.

The test `test_cupy_selector_matches_columnar_reference_with_status_codes` correctly verifies the two-way correspondence: it runs both the Python columnar selector and the CuPy selector on the same input and asserts that the numeric codes correspond to the expected label names via `codes["priority_tie_break"]` and `codes["unique_max_incident_face"]`. This is a sound parity check.

The `status_by_group` array is initialized to zero and then overwritten by status code assignments at `lines 654–666`. Since all four group types are mutually exclusive and exhaustive, no output row will carry status code 0. Groups excluded from `selected_groups` are never emitted regardless of their status code value.

### Q3: Are the duplicate incident/priority pair restrictions, dense int64 pair-key overflow guard, and CuPy empty-mask guard sufficient?

**Yes — all three guards are correctly implemented.**

**Duplicate incident pair restriction:**
`cp.sort(incident_keys)` followed by `cp.any(sorted_incident_keys[1:] == sorted_incident_keys[:-1])` at `lines 563–568` detects duplicates by comparing adjacent elements in the sorted key array. This is a standard device-side uniqueness check. Guarded by `require_unique_incident_pair=True` (default) and `incident_count > 1` (avoids the slice operation on a single-row array).

**Duplicate priority pair restriction:**
The priority keys are already sorted via `cp.argsort(priority_keys, kind="stable")` at `line 572` for the searchsorted lookup. The duplicate check at `lines 575–580` reuses `sorted_priority_keys` from that sort, which is correct and avoids a redundant sort.

**Overflow guard:**
The pair-key formula is `(point_id + point_offset) * base + (face_id + face_offset)` where `base = max_face_key + 1`. The maximum key value is `max_point_key * base + max_face_key`. The check at `line 555`:
```python
if base <= 0 or max_point_key > (int64_max - max_face_key) // base:
    raise OverflowError(...)
```
correctly guards against key overflow in Python integer arithmetic (CuPy scalars are extracted via `.item()` at lines 546–549, so the arithmetic is Python-native and does not overflow). The offsets `point_offset` and `face_offset` shift all IDs to non-negative before key encoding, which ensures the formula is valid for negative point or face IDs. The combined `all_faces` and `all_points` computation at `lines 537–549` correctly pools incident and priority ID ranges together for offset and base computation.

**Empty-mask guard:**
The early return at `lines 525–533` fires when `incident_count == 0` and returns correctly typed empty CuPy int64 arrays for all output columns, plus the label map. This prevents all subsequent device operations (including `cp.unique`, which would produce an empty array but with potential shape edge cases) from executing.

**`grouped_mask_count` inner function:**
The `cp.any(mask).item()` guard at `line 598` short-circuits `cp.bincount` when the mask is all-False, returning a zero vector. This is correct and avoids a degenerate `cp.bincount` call on an empty index set.

### Q4: Does the contract/export/report wording keep the path app-agnostic?

**Yes — all six forbidden claims are blocked and enforced.**

The function accepts only generic columns: incident point ids, incident face ids, incident face counts, priority point ids, priority face ids, and priority values. No application name, CDB identifier, RayJoin reference, or GIS policy is mentioned anywhere in the function signature, docstring, or implementation.

The `owner_face_priority_pipeline_contract()` at `closed_shape_topology.py:981–1048` lists `select_owner_faces_from_incident_candidate_columns_with_priority_cupy` under `optional_columnar_pipeline_helpers` (`line 1012`). The `validate_owner_face_priority_pipeline_contract()` validator at `lines 1067–1122` explicitly asserts this helper's presence in `columnar_helpers` and raises `ValueError` on drift (`lines 1106–1118`).

The `claim_boundary` at `lines 1040–1047` has all six flags set to `False`:
- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False`
- `rtdl_beats_rayjoin_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

The validator at `lines 1119–1121` confirms all boundary flags remain False: `if not isinstance(boundary, Mapping) or any(bool(value) for value in boundary.values()): raise ValueError(...)`.

The `__init__.py` export at `line 610` is present and correct.

The report (`goal3365_owner_face_cupy_selection_continuation_2026-06-04.md`) contains the required phrases: "not native RT traversal", "does not authorize release", "partner-device continuation". The test `test_report_keeps_selector_boundary_visible` at `lines 117–125` asserts all required boundary strings, including the hardware identifier and both test run lines, preventing silent report drift.

No release, public speedup, RayJoin reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin wording is present anywhere in the reviewed files.

### Q5: Is the pod evidence sufficient for this internal device-continuation step?

**Yes, for this stage.**

The evidence (`docs/reports/goal3365_owner_face_cupy_selection_continuation_2026-06-04.md`) records:

- Host: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1

Focused 26-test run across Goal3365, 3364, 3362, 3354, and 3355 tests: `Ran 26 tests in 1.230s OK`. The 1.230s runtime for 26 tests confirms live CuPy/CUDA execution — a skip-guarded all-CPU run would complete in under 0.2s for this test count.

Full 85-test owner-face family rerun: `Ran 85 tests in 0.687s OK`. The faster total time for the larger run is explained by CUDA context reuse: the 26-test focused run incurs CUDA context initialization overhead, while the 85-test run likely benefits from an already-warmed context or a higher ratio of non-CuPy tests diluting the per-test time. Both runtimes are internally consistent with real device execution.

The focused run covers the correct set: the new Goal3365 selection tests, the Goal3364 gap-closure hardening tests, the Goal3362 filter continuation tests, and the two columnar front-door tests (Goal3354, Goal3355). This confirms no regression against the prior acceptance baseline.

The evidence is sufficient for an internal device-continuation step. It is not sufficient for promoting this helper to a device-lowered default or for any public performance claim.

### Q6: What must be fixed before the owner-face selection/filter pair can be promoted toward a default device-lowered path?

Six items must be addressed. None block the current internal device-continuation designation.

**Item 1 — Output key divergence must be documented (high priority before promotion).**
`select_owner_faces_from_incident_candidate_columns_with_priority_cupy` returns `selection_status_code` (integer CuPy array) while the Python columnar reference returns `selection_status` (Python string). These are different output keys. Callers routing between the two paths must translate explicitly. This semantic divergence must be stated in the function docstring and acknowledged in the contract's `optional_columnar_pipeline_helpers` entry or the `promotion_requirements` tuple at `closed_shape_topology.py:1033–1039`.

**Item 2 — "drop" policy parity test is missing.**
The test suite covers `raise` (default) and `emit_ambiguous` policies, but no test verifies that `ambiguity_policy="drop"` correctly excludes missing-priority and ambiguous groups while preserving unique and priority-resolved groups. This gap in parity coverage must be closed before promotion.

**Item 3 — End-to-end selection → filter pipeline parity test is missing.**
The selection stage (`select_owner_faces_from_incident_candidate_columns_with_priority_cupy`) and the filter stage (`filter_closed_shape_membership_candidate_columns_by_owner_face_cupy`) are now both device-resident, but no test exercises them as a combined pipeline. Before promoting the full owner-face pipeline to a device-lowered default, at least one test must verify that the CuPy selector output (`point_id`, `owner_face_id` columns, status code 1 or 2) feeds correctly into the CuPy filter.

**Item 4 — Only two status-code paths covered by the parity test.**
`test_cupy_selector_matches_columnar_reference_with_status_codes` exercises unique-max and priority-tie-break outcomes. The missing-priority and ambiguous-priority-tie paths are only tested for fail-closed/emit behavior, not for output-column parity against the Python columnar reference. For a promotion gate, parity checks across all four status-code paths are required.

**Item 5 — Goal3364 filter divergences: single-owner-face-per-point restriction remains.**
As documented in Goal3364, the CuPy filter continues to enforce single-owner-face-per-point semantics. This is now stated in the contract's `filter_policy`, but no test verifies that callers who construct owner-face output from the CuPy selector (which also produces one face per point) are correctly handled. This is low risk in the current architecture but should be verified in an integration test.

**Item 6 — `native_lowering_status` must advance only after parity items above are closed.**
The current `native_lowering_status: "blocked_until_contract_stable_and_validated"` at `closed_shape_topology.py:1033` is correct. Promotion must not advance this status until items 1–5 are resolved and a cross-contract parity review is completed.

---

## Behavioral Verification

| Check | Result |
|-------|--------|
| CuPy input normalization accepts numpy/cupy/list arrays | Correct — `cp.asarray(..., dtype=cp.int64)` at lines 507–512 |
| Empty incident input early return (status codes included in empty output) | Correct — lines 525–533 |
| `priority_count == 0` path initializes `priority_found` to all-False | Correct — lines 613–614 |
| `max_counts` initialized to int64 min before `cp.maximum.at` | Correct — line 587 uses `-9223372036854775808` |
| `priority_inf` sentinel for non-tied rows in `priority_for_min` | Correct — line 624–625, uses `int64_max` |
| `min_priorities` correctly initialized to `priority_inf` before `cp.minimum.at` | Correct — line 626 |
| `owner_face_by_group` initialized to `-1` for unresolved groups | Correct — line 643 |
| Status code groups are mutually exclusive and exhaustive | Verified — see Q1 analysis |
| `candidate_count_by_group` matches Python reference for all four statuses | Correct — lines 668–677 |
| `selected_groups` gates output for all three policy variants | Correct — lines 679–683 |
| Overflow guard uses Python integer arithmetic (no device overflow risk) | Correct — CuPy scalars extracted via `.item()` before arithmetic |
| `grouped_mask_count` short-circuits on all-False mask | Correct — lines 597–602 |
| Contract registration and validator enforcement for the CuPy selector | Correct — `closed_shape_topology.py:1010–1118` |
| Export in `__init__.py` | Correct — line 610 |

---

## Boundary Re-Checks

| Claim | Status |
|-------|--------|
| Release authorized | `False` — confirmed in contract, report, and test |
| Public speedup claim | `False` — confirmed |
| RayJoin paper reproduction claim | `False` — confirmed |
| RTDL-beats-RayJoin claim | `False` — confirmed |
| Broad RT-core speedup claim | `False` — confirmed |
| True zero-copy claim | `False` — confirmed |
| Native engine may infer app ownership | `False` — enforced by validator |
| Native engine may invent priority | `False` — enforced by validator |
| Native lowering status | `blocked_until_contract_stable_and_validated` |
| Is this native RT traversal | No — CuPy device-column continuation only |
| Is this a release artifact | No — internal v2.8 partner-device continuation |

---

## Verdict

**accept-with-boundary**

Goal3365 correctly implements the owner-face selection stage as a CuPy device-column continuation. All four core semantics of the Python selector are preserved: unique max wins, tied max requires explicit priority, missing or tied priority fails closed by default, and `emit_ambiguous` is opt-in. The numeric status codes are transparent via the returned label map, the duplicate pair restrictions are in place for both incident and priority inputs, the int64 pair-key overflow guard correctly uses Python-native integer arithmetic after scalar extraction, and the empty-input guard returns correctly typed empty arrays. The contract, validator, and report all maintain the required claim boundaries with no forbidden wording present.

The `accept-with-boundary` verdict is issued because the output key divergence (`selection_status_code` vs `selection_status`) is not yet documented in the function docstring or contract promotion requirements, no test covers `ambiguity_policy="drop"` parity, no end-to-end selection-then-filter pipeline test exists, and the parity check against the Python columnar reference covers only two of the four status-code paths.

**Required before any promotion gate:**

1. Document the `selection_status_code` vs `selection_status` output key divergence in the function docstring and contract `promotion_requirements`.
2. Add a `ambiguity_policy="drop"` parity test against the Python columnar reference.
3. Add an end-to-end test combining `select_owner_faces_from_incident_candidate_columns_with_priority_cupy` and `filter_closed_shape_membership_candidate_columns_by_owner_face_cupy` in a single pipeline run.
4. Extend the columnar reference parity test to cover missing-priority and ambiguous-priority-tie output columns (not just fail-closed behavior).

None of these block the current internal device-continuation designation. All must be resolved before this helper is selected by default or promoted past its current `optional_columnar_pipeline_helper` status.
