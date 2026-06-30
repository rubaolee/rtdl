# Claude Review: Goal3383 Owner-Face Ambiguity Signal Negative Probe

**Date:** 2026-06-04

**Reviewer:** Claude (Sonnet 4.6)

**Verdict: `accept-with-boundary`**

---

## Scope

Read-only external review of Goal3383. Source files inspected:

- `scripts/goal3383_owner_face_ambiguity_signal_negative_probe.py`
- `docs/reports/goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.json`
- `docs/reports/goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.md`
- `tests/goal3383_owner_face_ambiguity_signal_negative_probe_test.py`
- `docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.md`
- `docs/reviews/goal3382_claude_review_selective_live_owner_face_route_probe_2026-06-04.md`

---

## Q1: Does Goal3383 correctly keep exact OptiX output out of the signal inputs and use it only as an evaluation oracle?

**Pass.**

The separation is genuine at two levels: code structure and test verification.

In `run_probe()` the live exact run and the live candidate columns are distinct calls:

```python
exact_pairs = _pair_set(tuple(prepared.run(points)))          # oracle only
candidate_columns = prepared.candidate_device_columns(points)  # signal input
```

`_build_feature_rows()` constructs every signal-relevant field — `candidate_count`,
`incident_row_count`, `incident_chain_count_max`, `incident_max_face_count`,
`candidate_face_count` — from the candidate pairs and CDB-derived topology/incident
rows only. The exact oracle contributes nothing to any of those fields.

The `extra_count` field IS computed from `candidate_pairs - exact_pairs` and stored
in each feature row. However, none of the five signal predicates in `_signal_specs()`
reference `extra_count`. The oracle-derived value is present in the data structure
but is never read by any predicate. `extra_count` is used exclusively in
`_evaluate_signals()` to define `true_extra_points` — the ground-truth label set
against which signal recall and precision are measured.

The JSON artifact records:

```json
"signal_inputs_exclude_exact_oracle": true,
"exact_oracle_used_only_for_signal_evaluation": true
```

The test `test_probe_uses_live_optix_candidates_and_exact_only_for_evaluation`
verifies both flags programmatically and also checks the script text for
`"candidate_device_columns(points)"` and `"prepared.run(points)"` as distinct
call sites, so a future merge that collapsed those two calls would fail the test.

The `try/finally` block mirrors Goal3381's resource management: `candidate_columns.close()`
and `prepared.close()` are guaranteed to execute even if the pipeline raises.

**Minor observation (not a defect):** `extra_count` being present in `feature_rows`
while never used by any predicate is slightly confusing at a code-reading level.
A future refactor could separate the "ground truth" annotation from the feature
engineering; the current structure is unambiguous in its behavior but requires the
reader to inspect all five lambdas to confirm the oracle is never leaked.

---

## Q2: Are the tested simple signals represented fairly?

**Pass, with a scoping note.**

The five signals span a progression from coarse to precise:

| Signal | Strategy |
| --- | --- |
| `candidate_count_ge_3` | Broad recall baseline — any over-candidated point |
| `candidate_count_gt_incident_max_face_count` | Imbalance between candidates and peak incident faces |
| `incident_row_eq_3_candidate_ge_4` | Junction topology conjunction with candidate cardinality |
| `incident_row_eq_3_candidate_face_count_eq_4` | Same junction conjunction, using distinct candidate face count |
| `incident_chain_count_eq_3_candidate_face_count_eq_4` | Chain-level count instead of row-level count |

The design is fair. Signal 1 establishes the recall upper bound. Signals 2–5 tighten
specificity by conjoining two independent topology/candidate measures. Signals 4 and 5
test whether the `incident_row_count` vs. `incident_chain_count_max` distinction changes
precision — it does not (both give 2 false positives). This negative tie is itself
informative.

**Scoping note:** The five signals are all threshold-conjunction predicates over
at most two features. More expressive signal classes — ratios, per-face geometry,
winding-number derived fields, or learned classifiers — are not tested. The probe
makes no claim to have exhausted the signal family space; it tests the "simplest
plausible" signals and finds them insufficient. This is a legitimate scoping
decision for an early discovery probe, and the report does not overclaim
exhaustiveness.

---

## Q3: Is the negative conclusion justified?

**Yes, and the justification is tightly supported.**

The best compact signal (`incident_row_eq_3_candidate_face_count_eq_4`) achieves:

- Zero missed extra points (recall = 7/7)
- Two false positives: points 651 and 652

The `interesting_feature_rows` for those two points are decisive:

| Field | Point 651 | Point 652 |
| --- | ---: | ---: |
| `candidate_count` | 4 | 4 |
| `exact_count` | 4 | 4 |
| `extra_count` | 0 | 0 |
| `incident_row_count` | 3 | 3 |
| `candidate_face_count` | 4 | 4 |

Points 651 and 652 have the same topological signature as the seven true-ambiguity
points — three incident face rows, four distinct non-zero candidate faces — but
their four candidates are all correct exact rows. Applying owner-face repair to
them as if they were erroneous would discard valid memberships, introducing new
false negatives.

This makes the negative conclusion structurally sound rather than incidental. The
two false positives share the topological fingerprint that defines the best signal
without having any underlying geometry that the signal can distinguish. Short of
introducing geometric or face-level evidence beyond what topology and candidate
count expose, this signal class cannot achieve zero false positives while
maintaining zero missed extras on this slice.

The test `test_false_positive_points_are_already_exact_and_must_not_be_filtered_blindly`
pins the artifact values for both points and verifies the report contains the
explanatory phrases "already match exact" and "risk removing valid rows". This
is exactly the right level of test specificity for a negative result.

---

## Q4: Does the report correctly avoid overclaiming?

**Pass, fully.**

The report carries the artifact-internal verdict `reject-for-default-route` (the
internal probe label) and the report-level verdict `reject-for-default-route`. Note
that this is a probe-domain classification, distinct from the review verdicts;
the probe is itself accepted (with boundary) by this review for what it claims to
establish.

The JSON `claim_boundary` block carries all seven flags false:

```json
"native_default_route_authorized": false,
"public_speedup_claim_authorized": false,
"rayjoin_paper_reproduction_claim_authorized": false,
"release_authorized": false,
"rt_core_speedup_claim_authorized": false,
"rtdl_beats_rayjoin_claim_authorized": false,
"true_zero_copy_claim_authorized": false
```

The test `test_claim_boundaries_stay_blocked` iterates all seven and asserts each
is False, then checks the report for "does not authorize a native default route"
and "claim-boundary flags remain false".

The report's framing is accurate: "This is a useful negative result. It prevents
us from shipping a tempting but wrong default route." That framing correctly
positions the result as a precautionary contribution rather than a capability
regression, without implying that a working discovery policy is imminent.

No overclaim language was found in any inspected file.

---

## Q5: What should the next engineering target be?

The false-positive evidence from points 651 and 652 sharpens the problem
considerably. Both points have the same topological signature as the true-ambiguity
points, but their candidates are all correct. The topology census alone — incident
row count, incident chain count, candidate face count — cannot distinguish
"boundary junction where RT-core produces over-candidates" from "legitimate
four-shape corner where all candidates are exact."

Of the four options listed in the handoff, the recommendation is:

**Richer generic boundary-event primitive, first.**

The core issue is not that the signal thresholds are wrong; it is that the signal
feature space has reached its ceiling. All features currently available to
`_signal_specs()` — candidate counts, incident row counts, incident chain counts,
candidate face adjacency — are aggregate structural summaries. They lose the
geometric detail (proximity to a face boundary, winding contribution per face,
signed distance to the boundary edge) that would let the primitive distinguish
points 651/652 from the ambiguous cluster.

A boundary-event primitive that exposes per-candidate signed-distance-to-boundary
or face-winding information would give signals access to the geometric evidence
needed to break the tie. This would also open a path toward the independent
priority derivation that Goal3382 identified as the second primary blocker.

**Stronger topology policy** is a useful complementary target but is unlikely to
succeed without richer feature input. Goal3378 already showed that applying a
topology-only priority globally drops 410 true exact rows; the two false positives
here suggest that even gated topology policies will hit the same geometric
ambiguity ceiling unless face-level evidence is available.

**Larger-scale characterization** should follow the primitive work rather than
precede it. Establishing whether the false-positive population (points sharing the
same topological signature but without boundary ambiguity) grows linearly or
super-linearly with CDB size is a meaningful question, but the answer changes the
urgency of the primitive work only at the margins.

**A different route** (e.g., pre-filter or post-filter applied outside the
candidate pipeline) is worth keeping in reserve, but the selective continuation
architecture established through Goals 3380–3381 is the correct structural level
to extend before abandoning the continuation approach.

---

## Additional Observations

**Best-signal tie.** Two signals — `incident_row_eq_3_candidate_face_count_eq_4`
and `incident_chain_count_eq_3_candidate_face_count_eq_4` — have identical key
tuples `(0, 2, 9)` under the selection criterion. Python's `min()` returns the
first in insertion order, so the reported best signal is stable given the current
`_signal_specs()` ordering, but a list reordering would silently change the
`best_simple_signal_name` field. The test pins the name explicitly
(`assertEqual(..., "incident_row_eq_3_candidate_face_count_eq_4")`), which would
catch a reordering; this is correct behavior for a record-and-pin test. No action
required, but worth noting if `_signal_specs()` is expanded.

**Candidate topology completeness.** `_build_feature_rows()` skips topology for
any candidate shape whose `shape_id` is absent from `topology_by_shape`. A shape
with no topology entry silently contributes nothing to `candidate_face_count` or
the zero-face flag. In the current CDB, topology and shapes are co-derived, so
this should not cause divergence; but if a future probe uses a CDB where some
shapes lack topology rows, the face-based signals would under-count candidates
without raising an error. A future defensive check here would be inexpensive.

**Test-suite alignment.** All five tests are well-matched to the artifact: they
pin numeric thresholds (counts, point IDs), check structural flags, verify report
text content, and assert the false-positive-points data directly. The 10-test,
14-test, and 41-test pod runs reported in the handoff all pass, and the test file
is self-consistent with the artifact values confirmed in this review.

**Commit traceability.** The JSON records `rtdl_commit:
6779cdc9bee86745924593154371eef5816ce039`, consistent with the pod run commit
cited in the handoff (`6779cdc9`). Goal3383's record commit is `80292b5f`, one
commit later; the intervening commit is the record-artifact step, not a source
change.

---

## Verdict

**`accept-with-boundary`**

Goal3383 is a sound, honest negative probe. The oracle separation is genuine and
test-verified. The five simple topology signals are a fair first-family sweep.
The negative conclusion — no tested signal achieves both zero false positives
and zero missed extras — is directly supported by the evidence for points 651
and 652, which share the best signal's topological fingerprint without having
boundary ambiguity. All seven claim-boundary flags are correctly blocked.

The probe is accepted for what it claims: evidence that simple topology/candidate
signals cannot serve as a default discovery criterion for the owner-face
ambiguity set on this 512-chain slice. The structural insight it contributes is
that the blocking defect is geometric, not a threshold problem — the feature space
available to this signal family has reached its ceiling.

**What remains blocked:** native default route, ambiguity-set discovery, independent
priority derivation, all public-claim categories. The next milestone is a
boundary-event primitive that exposes per-candidate geometric evidence (winding,
signed distance, or face proximity), enabling signal predicates that can resolve
the 651/652 false-positive case.
