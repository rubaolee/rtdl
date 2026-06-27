# Claude Review: Phoenix V3 Grouped-Reduction Prepared-Query Contract

Date: 2026-06-20

Reviewer: Claude (claude-sonnet-4-6)

## Verdict

```text
verdict: approve-with-required-fixes
P0 issues: 0
P1 issues: 4
2ai_consensus_authorized: true after listed fixes
recommended_next_action: apply 4 P1 fixes, re-seek external review of the corrected
  contract, then promote sum-only rows to M7 candidate wording review; do not promote
  count rows; do not require another pod run
```

## Review Scope

Artifacts reviewed:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json
scripts/v3_phoenix_grouped_reduction_prepared_query_contract.py
tests/v3_phoenix_grouped_reduction_prepared_query_contract_test.py
```

Evidence lineage verified:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.json
docs/reviews/codex_phoenix_v3_grouped_reduction_m7_pod_evidence_2ai_consensus_2026-06-20.md
```

## Math Verification

All figures in the contract artifact were independently verified against the raw
intake JSON using the stated formula:

```
total(n) = cold_prepare_total_sec + n * elapsed_median_sec
speedup(n) = embree_total(n) / optix_total(n)
break_even = (optix_cold - embree_cold) / (embree_hot - optix_hot)
```

Results (computed independently, rounded to displayed precision):

| Scale | Mode | Hot speedup | Break-even | Break-even ceil | Repeat-1 e2e | Repeat-100 e2e |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 262,144 | count | 9.538x | 13.632844 | 14 | 0.736139x | 2.452213x |
| 262,144 | sum   | 224.269x | 1.003339 | 2 | 0.998768x | 32.394864x |
| 524,288 | count | 8.819x | 13.734133 | 14 | 0.682897x | 2.633207x |
| 524,288 | sum   | 180.509x | 0.960568 | 1 | 1.015863x | 33.608424x |

All values match the contract and intake JSON to full floating-point precision.
No math defects found.

## Lineage Verification

- `source_intake` in the contract JSON correctly points to the fresh pod evidence
  artifact under `phoenix_v3_grouped_reduction_m7_20260620`.
- `source_intake_status: grouped_reduction_m7_post_run_intake_not_promoted` matches
  the intake JSON's `status` field exactly.
- The Codex 2-AI consensus (2026-06-20) accepted the intake as
  `grouped_reduction_m7_post_run_intake_not_promoted` with all authorization flags
  false, which is consistent with the contract's own flags.
- Both source warmup files carry `warmup=3`, satisfying `minimum_warmup_for_m7: 3`.
- `both_match_cpu_reference: true` for all four pairs in the intake JSON.
- Lineage is clean and fully traceable. No lineage defects found.

## Authorization Flag Check

All required flags are correctly false in both MD and JSON:

```text
status: prepared_query_contract_draft_not_release        ✓
release_authorized: false                                 ✓
public_speedup_claim_authorized: false                    ✓
whole_app_speedup_claim_authorized: false                 ✓
m7_promotion_authorized: false                            ✓
m7_qualified_release_rows: 0                              ✓
```

## Test Coverage Assessment

The five tests cover the contract correctly:
- `test_contract_is_draft_not_release`: asserts all authorization flags false. ✓
- `test_contract_terms_are_user_reproducible`: checks required timing fields and
  contract terms. ✓
- `test_candidate_rows_keep_m7_false_but_preserve_repeat100_signal`: asserts m7_promoted
  false and checks repeat-100 thresholds. ✓
- `test_forbidden_claims_block_hot_query_overread`: verifies key forbidden strings. ✓
- `test_markdown_contains_contract_boundaries`: spot-checks the rendered MD. ✓
- `test_generator_reproduces_checked_payload_shape`: runs `build_payload()` and
  compares to the saved JSON. ✓

No test defects found.

## Review Question Responses

### Q1: Does the contract correctly define a user-understandable prepared-query model?

Partially. The structure is correct: the contract names the prepare-once/run-many
pattern, identifies what is fixed before prepare, and forbids hot-query speedup without
cold cost and repeat count. However, several terms in the normative sections are
project-internal and would not be understandable to an external user without reading
internal documentation. See P1-1 below.

### Q2: Does it correctly distinguish hot prepared-query speedup, repeat-aware
end-to-end timing, and whole-app timing?

Yes, with one disclosure gap. The three-way distinction is structurally present:
the candidate table has three separate columns (hot speedup, repeat-1 e2e, repeat-100
e2e), the forbidden claims block end-to-end conflation, and `whole_app_speedup_claim_authorized`
is false with a promotion gate enforcing this. The gap is that the repeat-100
end-to-end column is a modeled projection from the formula, not a directly measured
100-iteration run — and the draft wording does not say so. See P1-2 below.

### Q3: Are the repeat-100 grouped_sum rows reasonable M7 candidates?

The sum rows are reasonable internal M7 candidates. The case for 262,144/sum:
break-even at just 2 repeats, 32.4x speedup at repeat 100, hot speedup of 224.3x
shows the mechanism is real. The case for 524,288/sum: break-even below 1 repeat
(the Embree cold cost is itself higher, so OptiX wins on the very first query),
33.6x at repeat 100. Both rows demonstrate compelling speedup for repeated-query
workloads and deserve further wording review.

The count rows are not recommended for M7 promotion. Break-even at 14 repeats means
the large majority of realistic query workloads would not see a speedup, yet
`recommended_public_repeat_count_if_promoted: 100` would be set (because repeat-100
speedup exceeds the 2.0 threshold). A user who runs 10 queries would lose 8% on
262,144/count and 10% on 524,288/count compared to Embree. See P1-4 below.

### Q4: P0/P1 wording, math, lineage, or test defects?

No P0 defects. Four P1 defects described below. No math or lineage defects.

### Q5: What exact next action should Phoenix take?

Apply the four P1 fixes, re-seek external review of the corrected contract, then
promote sum-only rows to M7 candidate wording review. No additional pod run is
required — the evidence is fresh and math-verified. Do not promote count rows.

---

## P1 Issues

### P1-1: Internal terms in normative user-facing sections

**Location:** `user_problem` string and `public_contract.fixed_before_prepare` in
both the MD and JSON.

**Issue:** The following terms appear in sections that are intended to be
user-understandable but are project-internal:

- `user_problem`: "RT-shaped table" and "RayDB-specific native engine" — an external
  user does not know what an RT-shaped table is, nor what it means to write a
  RayDB-specific native engine. The user cannot tell whether their data fits this
  contract.
- `public_contract.fixed_before_prepare`: "revenue/value encoding" and "predicate
  encoding" — these name internal schema concepts. A user cannot determine from this
  string alone whether their aggregation column and filter structure are compatible.
- `public_contract.output_contract`: "compact grouped rows" and "the measured fixture"
  — both are internal terms.

**Required fix:** Before any final public-row review, replace internal terms in the
`user_problem` and `public_contract` sections with user-level descriptions. For
example: "RT-shaped table" → "a fixed-schema column-per-field table with a known
row count and group-key cardinality"; "compact grouped rows" → "one output row per
group key containing the aggregate result"; "the measured fixture" → "the data table
with the dimensions stated above." The `fixed_before_prepare` field should name the
user-visible parameter (e.g., "the column encoding of the aggregation field") not the
internal implementation concept.

This does not block the contract from proceeding as a draft, but must be resolved
before any final public-row wording review.

---

### P1-2: Repeat-100 end-to-end speedup is a formula projection, not a direct
measurement — draft wording does not disclose this

**Location:** `timing_contract.repeat_end_to_end_formula`, the candidate table "Repeat
100 end-to-end" column, and the draft candidate wording strings.

**Issue:** Independent verification confirms that every entry in the intake JSON's
`repeat_scenarios` (at counts 1, 2, 5, 10, 25, 50, 100, 500, 1000) matches the
formula `cold_prepare_total_sec + n * elapsed_median_sec` to full floating-point
precision. This means the repeat-100 end-to-end speedup of 32.4x and 33.6x are
modeled projections computed from the single measured hot-query median, not the
result of running 100 consecutive prepared queries on the pod.

The projection assumes that the hot-query time is constant across 100 iterations.
This may not hold under thermal pressure, OS scheduling jitter, or memory bandwidth
saturation at larger scales. The 262,144/sum pair has an OptiX cold prepare of ~2.99s
and a hot-query time of ~4.9ms; at 100 repeats the hot-query contribution is ~0.49s
out of a ~3.48s total. Even modest jitter in the hot-query time changes the speedup
materially.

The draft candidate wording ("32.395x repeat 100 end-to-end speedup after counting
cold prepare once") does not identify the speedup as modeled. A user reading this
wording could reasonably believe it was measured by running 100 queries end-to-end.

**Required fix:** The draft wording must include explicit modeled-projection
disclosure. Proposed addition:

```
(modeled: cold prepare measured once; hot-query median projected to 100 iterations
using the formula cold_prepare_total_sec + 100 * elapsed_median_sec; actual results
for long query sequences may differ due to thermal and scheduling variance)
```

The `timing_contract` object should add a field:
```json
"repeat_scenario_values_are_formula_projections": true
```

and the existing formula field should note:
```
"repeat_end_to_end_formula_note": "All repeat_scenario values in the intake are computed from this formula using the single measured elapsed_median_sec; they are not independently measured multi-iteration runs."
```

This is user-safety critical. Any public wording that quotes the repeat-100 speedup
without disclosing the projection basis misstates the nature of the measurement.

---

### P1-3: Contract artifact omits the intermediate repeat counts required by its
own timing contract

**Location:** `timing_contract.required_repeat_counts_for_reporting` vs. the candidate
row objects in the contract JSON.

**Issue:** The timing contract requires reporting at `[1, 2, 5, 10, 25, 50, 100]`.
However, each candidate row in the contract JSON stores only `repeat_1_end_to_end_speedup`
and `repeat_100_end_to_end_speedup`. The intermediate values (2, 5, 10, 25, 50) are
present in the intake JSON but are not carried into the contract artifact.

An external reviewer working only from the contract artifact cannot verify the shape
of the repeat-count curve, cannot spot anomalies at intermediate counts, and cannot
check whether the break-even ceiling is consistent with the intermediate speedup
profile. The full curve is important: for 262,144/count, the speedup at repeat=25
is 1.22x while break-even is stated at 14 — the curve should be visible to confirm
the claim.

**Required fix:** The script's `_candidate_rows` function should extract and store
speedups at all required repeat counts, or should reference the intake JSON with a
cross-check assertion. The generated contract JSON should contain something like:

```json
"repeat_profile": {
  "1": 0.999,
  "2": 1.367,
  "5": 2.465,
  "10": 4.271,
  "25": 9.517,
  "50": 17.726,
  "100": 32.395
}
```

for each candidate row. The test `test_candidate_rows_keep_m7_false_but_preserve_repeat100_signal`
should add assertions for at least one intermediate count.

---

### P1-4: `recommended_public_repeat_count_if_promoted: 100` is set for count rows,
where 14 repeats are needed to break even

**Location:** Script `_candidate_rows`, line:
`"recommended_public_repeat_count_if_promoted": 100 if repeat_100 >= 2.0 else None`

**Issue:** Count rows (break-even at 14 repeats) receive `recommended_public_repeat_count_if_promoted: 100`
because their repeat-100 speedup (2.45x and 2.63x) exceeds the 2.0 threshold.
However, a public claim at "repeat 100" for a row where any user running fewer than
14 queries would see a net regression is misleading. The 2.0x threshold was designed
for sum rows where break-even is 1–2 repeats; it is too low for count rows where
break-even is 14.

A user who reads "OptiX is faster for 100-repeat grouped_count" and runs a 10-repeat
workload would get 8–10% slower results than with Embree.

**Required fix:** Add a break-even check to the recommendation logic:

```python
be = pair["break_even_repeat_count_ceiling"]
if repeat_100 >= 2.0 and be <= 5:
    recommended = 100
elif repeat_100 >= 2.0 and be <= 14:
    recommended = None  # too high break-even for a clean public claim
else:
    recommended = None
```

Alternatively, add a flag `count_mode_high_breakeven_blocks_public_claim` to count
rows alongside the existing `count_mode_requires_double_digit_repeat_amortization`
blocker, and update the test to assert that count rows have `recommended_public_repeat_count_if_promoted: None`.

---

## Items Confirmed Correct

- All four hot-query speedup values verified independently. ✓
- All four break-even values verified independently (exact match). ✓
- All four repeat-1 and repeat-100 end-to-end speedup values verified. ✓
- `break_even_repeat_count_ceiling` (ceiling of raw float) is correct for all rows. ✓
- `cold_prepare_total_sec` is correctly the all-in cold cost (inclusive of
  `workload_build_sec`), not double-counted in the formula. ✓
- `workload_build_sec` is listed as a required field for transparency (breakdown
  visibility), not as a second addend — this is the right design. ✓
- The formula model is conservative in the correct direction: it counts the full
  cold prepare every time, which is the worst-case cost for the user. ✓
- Forbidden claims list covers the critical over-read paths (end-to-end conflation,
  whole-app claim, hiding cold cost). ✓
- Draft wording is correctly marked "not publishable." ✓
- `same_contract_embree_and_optix_rows` is a promotion gate — correct, since a
  user-facing row must show both backends. ✓
- The 524,288/sum row blocker uses `repeat_1_end_to_end_margin_too_small_for_public_claim`
  (1.016x), not `repeat_1_end_to_end_not_optix_win`, correctly distinguishing the
  small-win case from the sub-1.0 case. ✓

## Promotion Recommendation

If the P1 fixes are applied:

- **Sum rows (262,144/sum and 524,288/sum):** Advance to M7 candidate wording review.
  The sum rows demonstrate a real and well-bounded use case: prepare once, run many
  integer group-sum queries over a fixed schema. Break-even at 1–2 repeats makes the
  claim accessible to most repeated-query workloads. The repeat-100 projection (once
  disclosed as modeled) is a fair illustration of the benefit at scale.

- **Count rows (262,144/count and 524,288/count):** Do not promote. The 14-repeat
  break-even and only 2.5–2.6x speedup at repeat 100 do not support a compelling
  public claim. Keep as internal evidence.

- **No additional pod run required.** The math is verified and the evidence is fresh.
  The P1 issues are all contract-language and artifact-completeness concerns that can
  be resolved without a new measurement.

- **Final public row wording for sum rows** should state: the hardware, the fixed
  schema dimensions (rows, groups), the hot-query speedup, the break-even repeat count,
  and the modeled repeat-N end-to-end speedup with the projection disclosure. It must
  not claim whole-database or whole-app speedup, and must not quote the hot speedup
  as an end-to-end result.
