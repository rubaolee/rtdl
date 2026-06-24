# Claude Review: Goal3523 v2.8 vs v2.3 Same-Contract Comparison Protocol

Date: 2026-06-05
Reviewer: Claude (Sonnet 4.6)
Verdict: **accept-with-boundary**

Goal3523 is ready for pod execution with one required correction (contact_manifold
promotion boundary) and one advisory fix (rt_dbscan phase-measurement disclosure).
The core protocol design — blocking all-app ratios until fresh same-contract pod
evidence exists — is sound and machine-enforced.

---

## Findings, Ordered by Severity

### [HIGH] contact_manifold promotion boundary is factually wrong

**File:** `src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py`, line 154–165

The row sets `v2_3_promoted=False` and records:

```
v2_3_source="v2.3 release report lists nine promoted benchmark apps;
contact manifold appears in later evidence, not the v2.3 released app table"
```

The v2.3 release report (`docs/release_reports/v2_3/README.md`) contradicts
this. Its header states "Ten promoted benchmark apps" and the promoted benchmark
table explicitly includes contact_manifold:

> Bounded contact witness / contact-manifold | Generic AABB broadphase plus
> bounded witness collection | Validates `COLLECT_K_BOUNDED`; no contact/collision
> native ABI

Contact_manifold is also present in the Goal2654 primary comparison table (26.29x
OptiX vs Embree) under the heading "Current promoted benchmark portfolio: 10
benchmark apps."

The practical effect is that the pod comparison protocol will incorrectly tell
future reviewers and pod operators that contact_manifold has no v2.3 baseline
for ratios, when in fact the v2.3 release report carries both its app-portfolio
entry and a Goal2654 evidence row. This is a documentation error, not a
measurement error, but it will corrupt the final pod comparison table if left
uncorrected.

**Required correction before pod execution:**

1. Change `v2_3_promoted=True` for contact_manifold.
2. Change `comparison_class` to `"fresh_same_contract_pod_required"` (the v2.8
   contract is evolved: prepared bounded witness collection vs the v2.3 generic
   AABB broadphase row, so a fresh same-contract run is still needed, but for
   the right reason).
3. Set `v2_3_optix_sec=0.0184764` from Goal2654 (the promoted OptiX timing).
4. Update `v2_3_source` to reference the v2.3 README promoted table and Goal2654
   row, not the incorrect "nine apps" count.
5. Update `required_next_action` to: run the same AABB broadphase collect-k
   contract in both lanes with identical grid/witness-capacity parameters,
   separating setup/warmup/steady-state.
6. Update `boundary` to reflect the contract evolution rather than a non-existent
   promotion gap.

**Cascading fix in `validate_v2_8_vs_v2_3_benchmark_comparison()`:** The
validator at line 286–287 guards `not any(row["comparison_class"] ==
"v2_3_not_promoted" ...)` and would fail after the correction since no row
would then carry that class. That check should be updated to verify that
contact_manifold records the contract-evolution boundary and is classified as
`fresh_same_contract_pod_required`.

**Cascading fix in test:** `test_contact_manifold_records_v2_3_promotion_boundary`
asserts `assertFalse(contact["v2_3_promoted"])` and `assertEqual(...,
"v2_3_not_promoted")`, both of which would need to flip to match the corrected
row.

---

### [MEDIUM] rt_dbscan artifact ratio compares mixed timing phases

**File:** `src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py`, line 125–137

The row sets `ratio_authorized_from_existing_artifacts=True` and computes:

```
v2_3_optix_sec = 1.62144     (Goal2654 / Goal2637 cluster-signature OptiX row)
v2_8_sec       = 0.302337887 (Goal3521 grouped-stream tail median at 131K points)
ratio          = 5.363x
```

The v2.3 timing of 1.62144 sec is a total-run OptiX value that includes scene
construction and any preparation. The v2.8 timing of 0.302337887 sec is the
"largest tail median" from the Goal3521 grouped-stream harness, which Goal3518
explicitly notes excludes "whole packet orchestration." These are different phases:
total-run vs steady-state tail.

The boundary field says "Only the grouped-stream path gets the roughly 4x-5x
continuation win" but does not state that the ratio mixes total-run (v2.3) against
tail-median (v2.8). A reader who takes the 5.36x figure at face value will
overestimate the wall-time improvement once setup and warmup are included in the
v2.8 timing during the final pod run.

**Recommended fix:** Append to the `boundary` field: "Note: v2.3 timing is a
total-run figure; v2.8 timing is the grouped-stream tail median excluding
preparation and warmup — the same-phase comparison will be established by the
required pod rerun." The `ratio_authorized_from_existing_artifacts=True`
classification can remain since the protocol already marks this as an internal
triage estimate that still requires a pod rerun.

---

### [LOW] rtnn apparent regression not surfaced as a pod preparation note

**File:** `src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py`, line 209–221

The v2.3 OptiX timing is 0.00153247 sec (single uniform ranked summary). The
v2.8 timing recorded in `v2_8_source` is 0.017263921 sec (worst-of-distribution
matrix row across three distributions). The implied naive ratio is 11.3x slower
in v2.8. The boundary correctly states "The v2.8 row is a worst-of-distribution
matrix row, not the same single uniform row." However, `v2_8_sec=None` (ratio
blocked) and the 0.017263921 figure only appears in the source string, not as a
machine-readable field.

This is unlikely to cause a comparison error but may confuse a pod operator
reading the protocol table who sees the v2.3 timing and the v2.8 source number
and infers a regression before reading the boundary text.

**Recommended fix (advisory):** Add a note to `required_next_action` that v2.8's
0.017263921 sec figure is worst-case distribution timing, and that the pod run
should lead with the uniform distribution row to produce the like-for-like
comparison against the v2.3 uniform number.

---

## Review Questions

### 1. Does the protocol correctly avoid a fake all-app v2.8/v2.3 ratio?

Yes. The design is sound:

- `ratio_authorized_from_existing_artifacts=False` is the default on 8 of 10 rows,
  enforced at construction time in `__post_init__`.
- `summarize_v2_8_vs_v2_3_benchmark_comparison()` always returns
  `pod_required_before_final_all_app_table=True`.
- The `validate_` function enforces that the majority of rows remain blocked
  pending fresh pod evidence.
- The claim boundary is machine-readable and the dataclass constructor raises
  `ValueError` for any row that tries to set `public_claim_authorized=True` or
  `release_authorized=True`.

The specific reasons for blocking each row are accurate (contract splits,
scale differences, phase mismatches, workload changes), subject to the contact
manifold correction above.

### 2. Are all 10 v2.8 benchmark apps represented? Is the contact_manifold v2.3 promotion boundary stated correctly?

All 10 apps are present. The contact_manifold promotion boundary is **wrong** —
see the HIGH finding above. The v2.3 README and Goal2654 both include contact
manifold as a promoted benchmark app.

### 3. Are rt_dbscan and triangle_counting bounded correctly?

`triangle_counting` is correctly bounded as `same_contract_existing_artifact`.
The v2.8 timing (0.000413392 sec) is slightly slower than v2.3 (0.000364401 sec),
ratio 0.881x, consistent with the test assertion `assertLess(ratio, 1.0)`. This
is a conservative, correctly-signed triage fact.

`rt_dbscan` has a phase-measurement concern described in the MEDIUM finding above.
The `same_output_evolved_runtime_existing_artifact` classification is acceptable
for internal triage provided the boundary field is updated to disclose the
total-run vs tail-median distinction. It should **not** be downgraded to
`fresh_same_contract_pod_required` because the same-output evidence from Goal3521
(confirmed signature match, 4.9x at 131K vs prepared CuPy grid) does support
an internal bounded estimate. The current handling is appropriate if the boundary
text is updated.

### 4. Are the fresh-pod-required next actions precise enough?

All seven blocked rows carry actionable instructions. The strongest ones are
`spatial_rayjoin` (specifies public-CDB fixture, two rows, two lanes) and
`robot_collision` (specifies matching pose/obstacle/link counts and phase split).
The weakest is `librts_spatial_index`, which says "run the same box count, query
count, operation mix, and timing phase" but does not name a specific dataset or
box/query count target; the pod operator will need to infer this from Goal2634 or
Goal2797. Acceptable for a protocol-prep document, but a pod runbook should pin
the fixture.

The pod packet spec in the report (two clean workspaces, full environment
variables, exact commands and artifact paths) is concrete and sufficient to begin
execution.

### 5. Does the protocol preserve claim boundaries?

Yes. The full claim boundary list is preserved:

- No public release wording.
- No public speedup wording.
- No whole-app speedup wording.
- No broad RT-core speedup wording.
- No package-install/PyPI wording.
- No true zero-copy wording.
- No paper reproduction claims.
- No hidden partner selection.
- No app-specific native-engine behavior.

All of these are blocked in the `CLAIM_BOUNDARY` constant, enforced by dataclass
`__post_init__` validation, checked by `validate_v2_8_vs_v2_3_benchmark_comparison()`,
and re-tested by `test_report_states_protocol_not_final_results` with explicit
forbidden-phrase detection. The forbidden-phrase list in the test is sufficient.

---

## Verdict

**accept-with-boundary**

Goal3523 is ready for pod execution after the contact_manifold correction
described under the HIGH finding. The pod operator should not proceed until
`v2_3_promoted` is corrected to `True` and the comparison class is updated from
`v2_3_not_promoted` to `fresh_same_contract_pod_required`, because the current
wording will cause the final comparison report to misstate the v2.3 promotion
history.

The rt_dbscan boundary text update is advisory: it does not block pod execution,
but should be applied before the final pod report is published.

The protocol is not yet the final all-app comparison report. The final report
requires fresh same-hardware evidence and an external review after artifacts exist.
