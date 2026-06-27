# Claude Review: Goal3385/3386 Boundary-Event Signal Route

**Date:** 2026-06-04

**Reviewer:** Claude (Sonnet 4.6)

**Verdict: `accept-with-boundary`**

---

## Scope

Read-only external review of Goals 3385 and 3386. Source files inspected:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal3385_selective_boundary_event_cupy_filter_2026-06-04.md`
- `tests/goal3385_selective_boundary_event_cupy_filter_test.py`
- `scripts/goal3386_boundary_event_signal_selective_route_probe.py`
- `docs/reports/goal3386_boundary_event_signal_selective_route_probe_2026-06-04.json`
- `docs/reports/goal3386_boundary_event_signal_selective_route_probe_2026-06-04.md`
- `tests/goal3386_boundary_event_signal_selective_route_probe_test.py`
- `docs/reviews/goal3384_claude_review_owner_face_ambiguity_signal_negative_probe_2026-06-04.md`

---

## Q1: Is the Goal3385 helper genuinely app-agnostic and safe as a generic continuation? Does it avoid inferring ambiguous points or app ownership?

**Pass.**

`run_selective_closed_shape_boundary_event_membership_pipeline_cupy`
(lines 1095–1219 of `closed_shape_topology.py`) is a mechanical partitioning
primitive. It has no knowledge of RayJoin, CDB, GIS, or owner-face semantics.

The critical design invariant is enforced by the function signature: the caller
is required to supply `selected_point_ids` explicitly. The function does not
derive which points are ambiguous — the docstring documents this directly:
"RTDL does not infer which points need boundary-event reconciliation." The
metadata key `"selected_point_filter_mode": "caller_supplied_ambiguity_set"` is
embedded in every return value to make this contract machine-readable.

The function's internal logic is:
1. Partition candidates into `selected_mask` and `passthrough_mask` using
   `cp.isin`.
2. For selected candidates, keep only those whose `(point_id, shape_id)` pair
   appears in the boundary events with `|crossing_t| <= crossing_tolerance`.
3. Passthrough rows are returned as-is with `membership=1` and
   `owner_face_id=-1` (sentinel: no owner-face assignment performed here).
4. The full output is sorted by `(point_id, shape_id)` for deterministic
   ordering.

No ownership or priority is inferred at any step. The `owner_face_id=-1`
sentinel on passthrough rows correctly signals "this continuation did not
perform owner-face selection" rather than "ambiguous" — downstream callers
reading only the passthrough rows do not need to perform further reconciliation
unless their own contract requires it.

**One structural observation (not a defect):** The function exposes
`crossing_tolerance` as a caller-controlled parameter defaulting to `0.0`.
This is the right design: strict zero is safe for the current probe, and
exposing the knob avoids a future source change when a deterministic tolerance
policy is established. The output metadata records the actual value used, which
is necessary for reproducibility.

The pair-key encoding for the boundary-event lookup (lines 1167–1191) includes
the same overflow guard used elsewhere in the module (`int64_max` arithmetic
check, offset normalization for negative IDs). This is correct.

---

## Q2: Does Goal3386 correctly keep live exact output out of the signal inputs and use it only for evaluation?

**Pass.**

The oracle separation is genuine at both the code level and the test level.

In `run_probe()` (lines 119–232 of the script), the three signal sources and
the oracle are obtained from distinct call sites:

```python
exact_pairs = _pair_set(tuple(prepared.run(points)))          # oracle only
candidate_columns = prepared.candidate_device_columns(points)  # signal input 1
boundary_columns = prepared.first_boundary_crossing_device_columns(...)  # signal input 2
# topology_rows, incident_rows derived from CDB                # signal input 3/4
```

`_derive_selected_points()` (lines 60–116) receives `county`, `topology_rows`,
`candidate_pairs`, and `zero_boundary_pairs`. It does not receive or reference
`exact_pairs`. Every computed field — `candidate_count`,
`zero_boundary_candidate_count`, `incident_row_count`, `candidate_face_count`,
`candidate_shape_ids`, `zero_boundary_candidate_shape_ids` — is derived
exclusively from the four signal sources. The oracle contributes nothing to the
selection predicate.

`exact_pairs` is used only post-filter (lines 172–173):
```python
true_extra_points = sorted({point_id for point_id, shape_id in candidate_pairs - exact_pairs})
```
This defines the ground-truth label set for evaluation and is never fed back
into the signal.

The test `test_probe_uses_live_candidate_and_boundary_device_columns` checks
both `"signal_inputs_exclude_exact_oracle": true` and
`"exact_oracle_used_only_for_signal_evaluation": true` programmatically, and
additionally searches the script text for `"candidate_device_columns(points)"`,
`"first_boundary_crossing_device_columns"`, and `"prepared.run(points)"` as
distinct call sites. A future merge that collapsed the oracle and candidate
calls would fail this test.

The `try/finally` block (lines 133–169) guarantees that `boundary_columns.close()`,
`candidate_columns.close()`, and `prepared.close()` execute regardless of
pipeline exceptions — resource management is correct.

---

## Q3: Does the bounded signal honestly derive the same seven true candidate-extra points without the fixed Goal3328 point list?

**Pass.**

`_derive_selected_points()` (lines 60–116) contains no hardcoded point IDs.
The selection predicate (lines 108–113) is purely structural:

```python
is_selected = (
    row["candidate_count"] > row["zero_boundary_candidate_count"]
    and row["zero_boundary_candidate_count"] == 2
    and row["incident_row_count"] == 3
    and row["candidate_face_count"] == 4
)
```

All four input measures are derived from live device columns and CDB topology:
- `candidate_count` — from OptiX candidate device columns
- `zero_boundary_candidate_count` — from OptiX boundary-event device columns,
  filtered to `crossing_t == 0.0`, intersected with candidate pairs
- `incident_row_count` — from `chains_to_incident_face_candidate_rows(county)`
- `candidate_face_count` — from CDB topology rows, non-zero face IDs only

The JSON artifact confirms `"selected_points_match_true_extra_points": true`.
The selected set `[522, 523, 538, 539, 540, 564, 565]` is computed rather than
looked up. This represents a genuine constructive advance over Goal3381, which
required the caller to supply the seven point IDs directly.

**Observation on signal tightness:** The predicate `zero_boundary_candidate_count == 2`
is a hard equality constraint rather than a threshold. This is appropriate as a
first validated formula, but it is specific to the structural pattern present in
this slice: the seven selected points each have exactly 2 zero-boundary candidate
shapes. Points with a different number of zero-boundary candidates (including
points 651 and 652 from Goal3383, which have no zero-boundary events among their
candidates) are correctly excluded. Whether different CDB slices produce points
with, say, 3 or 4 zero-boundary candidates that are also true extras is an open
question that requires evidence at larger scale.

---

## Q4: Does the Goal3385 helper drop exactly 12 selected candidate extras and match the 1417-row live exact output on the 512-chain slice?

**Pass.**

The JSON artifact records the following counts, which must be verified for
internal consistency:

| Measure | Value |
| --- | ---: |
| OptiX candidate rows | 1429 |
| Passthrough candidate rows | 1403 |
| Selected candidate rows | 26 |
| Selected kept rows | 14 |
| Selected dropped rows | 12 |
| Filtered rows | 1417 |
| Live exact rows | 1417 |
| Missing exact rows | 0 |
| Extra rows | 0 |

The arithmetic is fully consistent:
- 1403 + 26 = 1429 (passthrough + selected = total candidates) ✓
- 14 + 12 = 26 (kept + dropped = selected) ✓
- 1403 + 14 = 1417 (passthrough + selected-kept = filtered) ✓
- 1417 = 1417 (filtered = exact) ✓
- Candidate extras before filter = 1429 − 1417 = 12 ✓

The last check confirms that all 12 extra candidate rows belong exclusively to
the 7 selected points. None of the 1403 passthrough rows were extras — the
signal captured the entire over-candidated set without false coverage of exact
rows.

The test `test_selective_boundary_event_filter_matches_live_exact` pins every
one of these values programmatically. `matches_exact: true`,
`missing_exact_row_count: 0`, and `extra_row_count: 0` are verified as
Boolean/integer assertions rather than string checks.

The 7 × 4 = 28 candidate rows for the selected points minus the 2 rows that
happen to be in exact_pairs = 26 selected candidates. Wait — reviewing the JSON
feature rows: point 522 has 3 candidates, point 523 has 3, points 538/539/540
each have 4, and points 564/565 each have 4, giving 3+3+4+4+4+4+4 = 26 total.
Of those 26, 14 are kept (have zero-boundary events among the exact matches)
and 12 are dropped (the extras). This is structurally correct.

---

## Q5: Are the boundaries correct?

**Pass, fully.**

**Goal3385** (`closed_shape_topology.py` lines 1095–1219 and the report):
- The function does not infer ambiguous points or app ownership
- The report states: "does not authorize a native default route" and
  "does not authorize release"
- The `validate_owner_face_priority_pipeline_contract()` function (lines
  1432–1435) checks that all `claim_boundary` values are false, and now also
  checks that `run_selective_closed_shape_boundary_event_membership_pipeline_cupy`
  appears in `optional_columnar_pipeline_helpers`

**Goal3386** (JSON artifact and report):
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

The report carries the correct framing: "This is not yet a default route."
and "This is still a bounded signal probe, not a default route or public
claim." The test `test_claim_boundaries_stay_blocked_and_report_is_bounded`
iterates all seven flags, asserts each is `False`, and checks for "not yet a
default route," "one bounded," and "claim-boundary flags remain false" in the
report text.

No speedup numbers, latency claims, or paper-reproduction wording appear in
any of the inspected files.

The `__init__.py` export of
`run_selective_closed_shape_boundary_event_membership_pipeline_cupy` (line 610)
is correct — the function is listed under `optional_columnar_pipeline_helpers`
in the contract, not as a promoted default.

---

## Q6: What remains before this can be proposed as a default route candidate?

The evidence established so far is solid within its scope. The following gaps
must be closed before the signal can graduate from a bounded probe to a default
front door candidate:

**1. Larger CDB slices (critical).**
The current evidence covers 512 chains from `br_county`, producing 512 probe
points. The signal predicate `zero_boundary_candidate_count == 2` is a hard
equality constraint derived from the structural patterns in this slice alone.
At a minimum, the full `br_county` dataset and other county-level RayJoin CDBs
should be tested to establish whether the `== 2` threshold holds, whether it
needs to become `>= 2` or `in {2, N}`, and whether the false-positive rate
remains zero.

**2. Other RayJoin dataset families (critical).**
The probe is validated on a single Brazilian county CDB. RayJoin public assets
include state-level and national-level datasets with qualitatively different
chain densities and topological patterns. The 651/652 false-positive failure
mode from Goal3383 was specific to a four-shape corner junction; analogous
patterns in different administrative geometries may produce false positives that
this signal cannot resolve.

**3. Deterministic tolerance policy (medium priority).**
`crossing_tolerance` defaults to `0.0` (strict exact zero), which is sufficient
for the current evidence but raises the question of what happens with
near-zero crossings in datasets with different floating-point characteristics
or different OptiX build flags. A documented, formally adopted tolerance policy
(or a proof that strict zero is robust across tested platforms) should precede
any default-route proposal.

**4. Signal simplification and generalization analysis (medium priority).**
The current selection predicate has four conjuncts. It would be valuable to know
whether all four are load-bearing on larger datasets: specifically, whether
`zero_boundary_candidate_count == 2` alone (without the incident row and face
count conjuncts) already achieves zero false positives. If so, the signal could
be simplified, reducing the number of CDB-derived features required for the
helper. If not, the predicate logic needs explicit documentation of which
conjunct excludes which failure mode.

**5. Native lowering (blocked).**
The existing contract explicitly states:
`"native_lowering_status": "blocked_until_contract_stable_and_validated"`.
This is correct. No native lowering should be attempted before the signal is
validated at scale and the tolerance policy is fixed.

**6. Candidate leakage check on passthrough rows (low, precautionary).**
The passthrough rows are assigned `owner_face_id=-1` (no owner-face
assignment). A future composition that joins the output of this helper into a
pipeline that requires a non-negative `owner_face_id` for all rows would
silently fail to process passthrough rows correctly. A downstream guard — or
an explicit contract note that passthrough rows require a separate owner-face
assignment step — would prevent this failure mode before it manifests.

---

## Additional Observations

**Commit traceability.** The JSON artifact records
`rtdl_commit: 8f2660556ac28b37f8b9114bac930962f27720b2`. The source commit for
Goal3386 is `8f266055` (abbreviated in the git log); these match. The pod run
at commit `49d2ea1b` (the record-artifact commit) passes all 17 tests and the
48-test full owner-face chain. Traceability is intact.

**Arithmetic between "selected" and "true extras".** The 26 selected candidate
rows are exactly the union of candidates for the 7 selected points. Of those
26, 14 are true memberships (confirmed by zero-boundary events) and 12 are
false extras (no zero-boundary event). The coincidence that "12 dropped" equals
"12 candidate extras before filter" is not a coincidence: it is proof that all
extra candidates belong to and are fully covered by the selected set. The signal
achieves perfect recall and perfect precision on this slice for point selection
(zero false negatives, zero false positives on point identification), and the
filter achieves perfect recall and precision on row selection from those points.

**Test suite alignment.** The two test files cover complementary concerns. The
Goal3385 tests are unit-level (mock data, exercise CuPy path directly, and
verify contract registration). The Goal3386 tests are integration-level (read
the real artifact, verify every count, verify claim-boundary flags, check report
text). Together they pin the contract, the arithmetic, and the boundary text
independently — a single change that breaks one would fail the appropriate test.

**No overlap with Goal3381 route.** Goal3381 required the caller to supply the
seven point IDs directly (fixed list). Goal3386 derives them constructively.
The two approaches could in principle produce divergent results on new data.
The test `test_signal_selects_exactly_true_candidate_extra_points` pins the
point IDs to `[522, 523, 538, 539, 540, 564, 565]`, which is a record-and-pin
test against the current artifact. If a future run on the same slice produces
different selected points (e.g., due to an OptiX driver update), this test
would correctly fail, triggering a re-review.

---

## Verdict

**`accept-with-boundary`**

Goal3385 is a well-designed, genuinely app-agnostic CuPy continuation primitive.
It enforces the caller-supplied ambiguity set contract, exposes the tolerance
parameter correctly, and is registered as an optional helper rather than a
default. The implementation is internally consistent, the pair-key overflow guard
is correct, and the passthrough semantic is sound.

Goal3386 is an honest constructive probe. The oracle separation is genuine and
test-verified at the call-site level. The seven true extra points are derived
without a hardcoded list. The arithmetic is fully self-consistent. All
claim-boundary flags are correctly blocked, and the report framing accurately
describes what was and was not established.

**What remains blocked:** native default route, public speedup, RayJoin paper
reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, and release.

**The primary next gate** is evidence on larger CDB slices and additional dataset
families. The `zero_boundary_candidate_count == 2` hard threshold needs to be
stress-tested before the signal can be trusted to generalize, and a deterministic
tolerance policy for `crossing_tolerance` should be established alongside that
scale-up work.
