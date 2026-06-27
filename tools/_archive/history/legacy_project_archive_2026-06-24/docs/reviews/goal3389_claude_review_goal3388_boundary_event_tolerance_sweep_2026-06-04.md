# Claude Review: Goal3388 Boundary-Event Tolerance Signal Slice Sweep

**Date:** 2026-06-04

**Reviewer:** Claude (Sonnet 4.6)

**Verdict: `accept-with-boundary`**

---

## Scope

Read-only external review of Goal3388. Source files inspected:

- `scripts/goal3388_boundary_event_tolerance_signal_slice_sweep.py`
- `tests/goal3388_boundary_event_tolerance_signal_slice_sweep_test.py`
- `docs/reports/goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.json`
- `docs/reports/goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.md`
- `docs/reviews/goal3387_claude_review_boundary_event_signal_route_2026-06-04.md` (prior gate)

---

## Q1: Does Goal3388 genuinely address the larger-slice and tolerance-policy gap raised in Goal3387, within its stated scope?

**Pass, with a structural note.**

Goal3387 raised two explicit next gates:

1. Test larger CDB slices to stress the `zero_boundary_candidate_count == 2` hard equality.
2. Replace that equality rule with an explicit, deterministic tolerance policy.

Goal3388 addresses both. Slices of 512, 1024, and 2048 chains are run, providing 4× scale evidence relative to Goal3386. All three match the exact oracle with zero missing and zero extra rows.

The tolerance policy is upgraded from strict-zero-equality with a 4-conjunct selection predicate to a 2-conjunct predicate with an explicit `crossing_tolerance = 1e-5`:

**Goal3386 selection predicate (4 conjuncts):**
```python
is_selected = (
    candidate_count > zero_boundary_candidate_count
    and zero_boundary_candidate_count == 2
    and incident_row_count == 3
    and candidate_face_count == 4
)
```

**Goal3388 selection predicate (2 conjuncts):**
```python
candidate_count > zero_count and zero_count <= 2
```

**Structural note on the simplification:** The two CDB-topology-derived conjuncts
(`incident_row_count == 3`, `candidate_face_count == 4`) have been dropped entirely.
The hard equality `== 2` has been relaxed to `<= 2`. This is a deliberate
generalization: the signal now requires only the two OptiX device column sources and
no CDB topology features. The consequence — a stable over-selection of points
633/634/635 at the point level — is addressed by Q4 below. The simplification is the
right direction but is a structural change from Goal3386 that should be documented
explicitly as a signal design choice, not merely as a side effect of the tolerance work.

**One gap within scope:** All three slices share the same start offset (`start=256`),
producing nested slices [256, 768), [256, 1280), [256, 2304). The 2048-chain slice
subsumes the other two. This is a valid incremental design for verifying monotonic
behavior, but it means that chains 0–255 of `br_county` are not covered by any of
the three runs. The "larger slice" evidence is real but not a coverage sweep of
the full dataset.

---

## Q2: Is the tolerance policy (`abs(crossing_t) <= 1e-5`) documented and bounded enough for this internal characterization, without overclaiming route readiness?

**Pass for characterization scope; one gap for future promotion.**

The `1e-5` value is:
- Encoded as the `--crossing-tolerance` default in `parse_args()`.
- Recorded in the artifact as `"crossing_tolerance": 1e-05`.
- Described in the report as a deliberate choice that "keeps legitimate near-zero rows."
- Test-pinned: `self.assertAlmostEqual(payload["crossing_tolerance"], 1e-5)`.

The report correctly frames this as a bounded characterization, not a route policy.
The tolerance value is not presented as formally adopted.

**Gap:** The report does not state the rationale for `1e-5` specifically (as opposed to
`1e-4` or `1e-6`). The artifact records the GPU and driver
(`NVIDIA RTX A5000, 580.126.09`) but does not state that the tolerance was
platform-calibrated or validated across OptiX build configurations. For a future
route-promotion proposal, a documented derivation of the tolerance bound — or a proof
that strict zero is sufficient and `1e-5` is a conservative envelope — should
accompany the evidence. This is not a defect for the current characterization goal.

---

## Q3: Does the selected-point signal stay independent from the exact oracle?

**Pass.**

The call structure in `_run_one()` is:

```python
exact_pairs = _pair_set(tuple(prepared.run(points)))          # oracle: evaluation only
candidate_columns = prepared.candidate_device_columns(points)  # signal input 1
boundary_columns = prepared.first_boundary_crossing_device_columns(...)  # signal input 2
```

`_derive_selected_points_from_strict_zero_counts()` receives only
`candidate_pairs` and `strict_zero_boundary_pairs`. It has no reference to
`exact_pairs`. The oracle is used only post-filter:

```python
true_extra_points = sorted({point_id for point_id, shape_id in candidate_pairs - exact_pairs})
```

This line computes the ground-truth label set for evaluation and is never fed back
into the selection logic.

The test enforces oracle isolation at three levels:
- `payload["signal_inputs_exclude_exact_oracle"]` is asserted `True`.
- `payload["exact_oracle_used_only_for_signal_evaluation"]` is asserted `True`.
- Script text is searched for the three distinct call sites as separate string literals,
  so a future collapse of the oracle and candidate calls would break the test.

The `try/finally` resource management in `_run_one()` is correct: `boundary_columns.close()`,
`candidate_columns.close()`, and `prepared.close()` execute on both normal and exception paths.

---

## Q4: Is the over-selection of points 633, 634, 635 correctly framed as bounded and safe because the final filtered row set still matches exact?

**Pass, with a precision note on the framing.**

The critical safety invariant holds across all three slices:

```
selected_dropped_row_count == candidate_extra_row_count_before_filter
```

Verified from the artifact:

| Chains | Extras before filter | Dropped | Invariant |
| ---: | ---: | ---: | --- |
| 512 | 12 | 12 | true |
| 1024 | 17 | 17 | true |
| 2048 | 53 | 53 | true |

This proves that every extra candidate row belonged to a selected point, and the
filter dropped exactly the extras with no collateral loss of exact rows
(`missing_exact_row_count = 0` in all three runs).

The framing in the report is mostly correct: points 633/634/635 are selected by the
signal because they satisfy `candidate_count > strict_zero_count AND strict_zero_count <= 2`,
but they are NOT true-extra points. All their candidate pairs are legitimate exact
membership rows. The 1e-5 tolerance filter keeps all those rows because their boundary
crossings are near-zero (`|crossing_t| <= 1e-5`), so no rows are dropped for these
points. The filter is harmless for them.

**Precision note:** The report says these points are selected "because those points
contain legitimate near-zero boundary events that strict zero alone would misclassify."
This is slightly backwards: the points are selected because the strict-zero signal
predicate fires on them (their `strict_zero_count <= 2` and there are non-zero-crossing
candidates). But all their non-zero-crossing candidates turn out to be exact memberships
with near-zero crossings, not extras. The tolerance filter correctly keeps them. The
stability of the false-positive set across all three slice sizes (always exactly
633/634/635, not growing with scale) is the key evidence of boundedness.

The test `test_signal_is_bounded_over_selection_not_oracle_selection` pins
`selected_false_positive_point_ids == [633, 634, 635]` for every row, and also asserts
`selected_missed_extra_point_ids == []`. Together these confirm full recall at the
point level and a stable, bounded false-positive set.

---

## Q5: Are the claim boundaries correct?

**Pass, fully.**

The JSON artifact records all seven claim-boundary flags as `false`:

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

The test `test_claim_boundaries_and_report_remain_bounded` iterates all seven flags
and asserts each is `False`. It also checks for the three required report phrases:
"does not authorize a native default route", "does not authorize release", and
"not only `br_county`". All pass.

The script embeds the interpretation string at construction time:
```python
"interpretation": (
    "Bounded multi-slice sweep: strict-zero boundary-event count selects likely ambiguous points, "
    "and a small explicit crossing tolerance keeps legitimate near-zero rows while the generic "
    "boundary-event CuPy filter removes candidate extras. This is not a default route; it is a "
    "scale characterization of a candidate signal over county slices."
)
```

No speedup numbers, latency figures, paper-reproduction wording, or route-promotion
language appear in any inspected file.

The report's "Boundary" section also correctly lists the remaining next gates, which
aligns with the evidence gaps identified in this review.

---

## Q6: What should be the next gate?

Based on the evidence in Goal3388 and the remaining gaps, the following priority ordering is recommended:

**1. Full `br_county` sweep (critical).**
The three nested sub-slices cover chains 256–2304. Chains 0–255 are untested. A
single full-dataset run would close this gap and also reveal whether the false-positive
set {633, 634, 635} remains stable or grows with additional chains.

**2. Other RayJoin CDB families (critical).**
All evidence remains on a single CDB file (`br_county.cdb`). The `<= 2` threshold in
the new predicate is less overfitted than the old `== 2` equality, but it has not been
validated on state-level or national-level county geometries with different chain
densities or topological patterns. The 651/652 failure mode from Goal3383 was a
four-shape corner junction; analogous patterns in different families may produce
false positives the current signal cannot resolve.

**3. Signal behavior characterization for `zero_count = 0` (medium priority).**
The relaxation from `== 2` to `<= 2` permits `zero_count = 0` to qualify a point
for selection: any point with at least one candidate but no strict-zero boundary
events will now be selected. This case did not arise in Goal3386's tighter predicate.
A characterization of how often this fires in practice — and whether the 1e-5 filter
correctly handles such points without false drops — should precede route promotion.

**4. Tolerance derivation documentation (medium priority).**
For a future route-promotion proposal, the `1e-5` value should be accompanied by
either a derivation (e.g., based on observed near-zero `crossing_t` distributions)
or a demonstration that the result is stable across a range of tolerance values. Cross-
platform validation (different GPU, different OptiX driver) would further strengthen
the case.

**5. Boundary-event overflow stress testing (medium priority).**
No overflow was observed in any of the three slices
(`any_boundary_overflow: false`). The overflow path in the pipeline has not been
exercised. A constructed or found overflow scenario should confirm that the pipeline
fails safely or gracefully degrades rather than silently producing wrong results.

**6. Native lowering (blocked).**
Native lowering remains blocked until the signal is validated at scale on additional
dataset families and the tolerance policy is formally adopted.

---

## Additional Observations

**Arithmetic consistency (2048-chain slice):**

| Measure | Value |
| --- | ---: |
| OptiX candidate rows | 5672 |
| Passthrough candidate rows | 5542 |
| Selected candidate rows | 130 |
| Selected kept rows | 77 |
| Selected dropped rows | 53 |
| Filtered rows | 5619 |
| Exact rows | 5619 |

- 5542 + 130 = 5672 ✓
- 77 + 53 = 130 ✓
- 5542 + 77 = 5619 ✓
- Candidate extras = 5672 − 5619 = 53 ✓

The invariant `selected_dropped_row_count == candidate_extra_row_count_before_filter`
is confirmed.

**Commit traceability.** The artifact records
`rtdl_commit: 06945a9e054e9bebd8064eb7faa1aca8bd47ffc3`. The source commit for
Goal3388 in the git log is `06945a9e`, which matches. The pod run at commit
`ce87b13a` (the record-artifact commit) passes all 16 tests with 2 skips.
Traceability is intact.

**False-positive set stability across slice sizes.** The false-positive point IDs
{633, 634, 635} appear identically in all three slice results. These point IDs are
in the range covered by the 512-chain sub-slice [256, 768), so all three slices
include them by construction. Their presence is expected and stable. What this does
NOT yet tell us is whether other false-positive points would appear if the start
offset changed or if additional chains beyond 2304 were included.

**Test coverage.** The four tests cover complementary invariants:
- Oracle isolation (code-level call-site checks)
- Pinned counts across all three slices (arithmetic verification)
- Signal properties (false-positive IDs, recall completeness, dropped-equals-extras)
- Claim-boundary flags and report text

Together they are sufficient for the characterization scope. No test directly
verifies the `zero_count = 0` selection case or the tolerance sensitivity, which
aligns with the medium-priority gaps noted above.

---

## Verdict

**`accept-with-boundary`**

Goal3388 genuinely addresses both gates raised in Goal3387. The three-slice sweep
provides 4× scale evidence, and all three slices match the exact oracle with zero
missing and zero extra rows. The signal simplification (2 conjuncts, no CDB topology
features) and the explicit `1e-5` tolerance represent a real advance over Goal3386's
tighter but more fragile predicate. Oracle independence is maintained and test-verified.
Claim boundaries are fully intact.

**What remains blocked:** native default route, public speedup, RayJoin paper
reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, and release.

**The primary next gates** are: (1) full `br_county` to close the chain-offset gap, and
(2) additional RayJoin CDB families to validate the `<= 2` threshold beyond a single
dataset. A formal derivation or sensitivity analysis of the `1e-5` tolerance should
accompany any route-promotion proposal. Characterization of the new `zero_count = 0`
selection case is medium priority.
