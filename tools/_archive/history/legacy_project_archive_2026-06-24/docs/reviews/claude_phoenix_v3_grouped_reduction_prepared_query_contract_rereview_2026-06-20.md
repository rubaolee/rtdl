# Claude Re-Review: Phoenix V3 Grouped-Reduction Prepared-Query Contract

Date: 2026-06-20

Reviewer: Claude (claude-sonnet-4-6)

Prior review: `docs/reviews/claude_phoenix_v3_grouped_reduction_prepared_query_contract_review_2026-06-20.md`

## Verdict

```text
verdict: approved
P0 issues: 0
P1 issues: 0
2ai_consensus_authorized: true
recommended_next_action: advance sum rows (262144/sum and 524288/sum) to M7 candidate
  wording review; keep count rows as internal evidence only; no additional pod run required
```

## Re-Review Scope

Artifacts re-reviewed after four P1 fixes applied:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json
scripts/v3_phoenix_grouped_reduction_prepared_query_contract.py
tests/v3_phoenix_grouped_reduction_prepared_query_contract_test.py
```

---

## P1 Fix Verification

### P1-1: Internal terms in normative user-facing sections — FIXED

**Required:** Replace "RT-shaped table", "RayDB-specific native engine", "revenue/value
encoding", "predicate encoding", "compact grouped rows", and "the measured fixture" with
user-level language in `user_problem` and `public_contract` sections.

**Verified in script (`build_payload`, lines 31–49):**

- `user_problem`: "Run repeated grouped count/sum queries over a fixed-schema table with
  known row and group-key counts, without writing custom native code for that application."
  No internal terms present. ✓
- `public_contract.fixed_before_prepare`: "row count, group-key column, number of distinct
  groups, integer value column for sum, query/filter shape, backend, operation, and group
  capacity." No "revenue/value encoding" or "predicate encoding". ✓
- `public_contract.output_contract`: "one output row per group key must match the CPU
  reference exactly for count and integer sum on the stated table dimensions." No "compact
  grouped rows" or "the measured fixture". ✓

**Verified in JSON (line 217, 170, 172):** All three fields carry the corrected text. ✓

**Verified in test (`test_contract_terms_are_user_reproducible`, lines 37–38):** Asserts
that "RT-shaped table", "RayDB-specific native engine", and "revenue/value encoding" are
absent from the serialized JSON. ✓

---

### P1-2: Repeat-100 end-to-end speedup is a formula projection — FIXED

**Required:** (a) Add `repeat_scenario_values_are_formula_projections: true` to
`timing_contract`; (b) add `repeat_end_to_end_formula_note` explaining values are not
independently measured; (c) add projection disclosure to draft candidate wording.

**Verified in script (`build_payload`, lines 63–69):**

```python
"repeat_scenario_values_are_formula_projections": True,
"repeat_end_to_end_formula_note": (
    "Repeat-scenario values are computed from measured cold prepare and "
    "the measured hot-query median. They are not independent multi-query "
    "end-to-end runs."
),
```
✓

**Verified in JSON (lines 196–197):** Both fields present with correct values. ✓

**Verified in draft wording (`_draft_candidate_wording`, script lines 183–187):** Each sum
row wording string now contains:
> "(modeled from measured cold prepare plus 100 times the measured hot-query median, not
> from an independently measured 100-query loop)"
✓

**Verified in MD artifact:** Candidate table header reads "Modeled repeat 100 end-to-end"
(not "Repeat 100 end-to-end"). Repeat Profile section opens with: "These values are
formula projections from measured cold prepare and measured hot-query median. They are not
independently measured multi-query loops." ✓

**Verified in tests:**
- `test_contract_terms_are_user_reproducible` (line 42–43): asserts
  `repeat_scenario_values_are_formula_projections` is `True` and that
  `repeat_end_to_end_formula_note` contains "not independent multi-query end-to-end
  runs". ✓
- `test_forbidden_claims_block_hot_query_overread` (lines 80–82): asserts wording
  contains "modeled repeat 100 end-to-end" and "not from an independently measured
  100-query loop". ✓

---

### P1-3: Contract artifact omits intermediate repeat counts — FIXED

**Required:** `_candidate_rows` should extract and store speedups at all required repeat
counts (1, 2, 5, 10, 25, 50, 100) in a `repeat_profile` field on each row, with a
`repeat_profile_basis` disclosure. Tests should assert at least one intermediate count.

**Verified in script (`_candidate_rows`, lines 133–136):**

```python
repeat_profile = {
    str(repeat_count): pair["repeat_scenarios"][str(repeat_count)]["end_to_end_speedup"]
    for repeat_count in (1, 2, 5, 10, 25, 50, 100)
}
```
All seven required counts extracted. ✓

`repeat_profile_basis` field set to
`"formula_projection_from_measured_cold_prepare_and_hot_query_median"` (script line 164). ✓

**Verified in JSON:** All four candidate rows carry `repeat_profile` with keys
`"1"`, `"2"`, `"5"`, `"10"`, `"25"`, `"50"`, `"100"` and corresponding
speedup values. ✓

**Verified in MD artifact:** "Repeat Profile" section renders a full 7-column table for
all four rows with the projection disclosure. ✓

**Verified in tests:**
- `test_candidate_rows_keep_m7_false_but_preserve_repeat100_signal` (line 55): asserts
  `rows[(262144, "sum")]["repeat_profile"]["25"] > 9.0` — intermediate count present and
  correct (actual 9.517x). ✓
- Line 67: asserts `sorted(row["repeat_profile"].keys()) == ["1", "10", "100", "2", "25", "5", "50"]`
  for every row. ✓
- Line 68–71: asserts `repeat_profile_basis ==
  "formula_projection_from_measured_cold_prepare_and_hot_query_median"` for every row. ✓

---

### P1-4: `recommended_public_repeat_count_if_promoted: 100` for count rows — FIXED

**Required:** Count rows must receive `recommended_public_repeat_count_if_promoted: None`
and must carry the `count_mode_high_breakeven_blocks_public_claim` blocker. The
recommendation logic must gate on break-even before assigning a public repeat count.

**Verified in script (`_candidate_rows`, lines 148–151):**

```python
if mode == "count":
    blockers.append("count_mode_requires_double_digit_repeat_amortization")
    blockers.append("count_mode_high_breakeven_blocks_public_claim")
recommended_repeat = 100 if mode == "sum" and repeat_100 >= 2.0 and break_even_ceiling <= 5 else None
```

Count rows: `mode == "count"` → `recommended_repeat = None`. ✓
Both count blockers appended. ✓

Sum rows: 262,144/sum (break_even=2) and 524,288/sum (break_even=1) both satisfy
`mode == "sum" and repeat_100 >= 2.0 and break_even_ceiling <= 5` → `recommended_repeat = 100`. ✓

**Verified in JSON:**
- `grouped_reduction_count_repeat100_262144`: `recommended_public_repeat_count_if_promoted: null`,
  `count_mode_high_breakeven_blocks_public_claim` in blockers. ✓
- `grouped_reduction_count_repeat100_524288`: same. ✓
- `grouped_reduction_sum_repeat100_262144` and `grouped_reduction_sum_repeat100_524288`:
  `recommended_public_repeat_count_if_promoted: 100`. ✓

**Verified in tests:**
- Line 60: `assertIsNone(rows[(262144, "count")]["recommended_public_repeat_count_if_promoted"])` ✓
- Line 61: `assertIsNone(rows[(524288, "count")]["recommended_public_repeat_count_if_promoted"])` ✓
- Line 56: `assertEqual(rows[(262144, "sum")]["recommended_public_repeat_count_if_promoted"], 100)` ✓
- Line 59: `assertEqual(rows[(524288, "sum")]["recommended_public_repeat_count_if_promoted"], 100)` ✓
- Line 62: `assertIn("count_mode_high_breakeven_blocks_public_claim", rows[(262144, "count")]["blockers"])` ✓

---

## Authorization Flag Recheck

All required authorization flags remain correctly false in both MD and JSON after fixes:

```text
status: prepared_query_contract_draft_not_release        ✓
release_authorized: false                                 ✓
public_speedup_claim_authorized: false                    ✓
whole_app_speedup_claim_authorized: false                 ✓
m7_promotion_authorized: false                            ✓
m7_qualified_release_rows: 0                              ✓
```

No authorization flag was altered by any of the four fixes. ✓

---

## Math Recheck (No Change Expected)

Math was verified correct in the prior review. No numeric fields were altered by the P1
fixes. Spot-check of `repeat_profile` values in the JSON against the formula
`cold_prepare_total_sec + n * elapsed_median_sec` for the intermediate counts confirms
they are consistent with the intake data carried through from the prior review. No new
math defects introduced.

---

## Test Coverage Recheck

Six tests now cover the corrected contract:

| Test | Coverage |
| --- | --- |
| `test_contract_is_draft_not_release` | All authorization flags false. ✓ |
| `test_contract_terms_are_user_reproducible` | No internal terms; projection flags; formula note. ✓ |
| `test_candidate_rows_keep_m7_false_but_preserve_repeat100_signal` | Profile keys, intermediate counts, count-row `None`, blockers. ✓ |
| `test_forbidden_claims_block_hot_query_overread` | Forbidden strings; wording disclosure. ✓ |
| `test_markdown_contains_contract_boundaries` | "Modeled repeat 100 end-to-end", "Repeat Profile", "formula projections". ✓ |
| `test_generator_reproduces_checked_payload_shape` | `build_payload()` round-trips to saved JSON. ✓ |

One minor gap identified but not blocking: `count_mode_high_breakeven_blocks_public_claim`
is asserted only for the 262,144/count row (test line 62), not the 524,288/count row.
Both rows receive the blocker via the same code path; the omitted assertion is a coverage
gap, not a correctness defect. No new blocker required.

---

## Residual Items Confirmed Clean

- Lineage: no change to `source_intake` or `source_intake_status` fields. Still correctly
  points to `phoenix_v3_grouped_reduction_m7_20260620` evidence. ✓
- `same_contract_embree_and_optix_rows` promotion gate remains in the list. ✓
- `whole_app_speedup_claim_authorized_false` promotion gate remains in the list. ✓
- Draft wording is still gated with "not publishable" on both sum rows. ✓
- `break_even_repeat_count_ceiling` values unchanged: 14 (count), 2 (262K/sum), 1 (524K/sum). ✓
- 524,288/sum blocker correctly reads `repeat_1_end_to_end_margin_too_small_for_public_claim`
  (1.016x), not `repeat_1_end_to_end_not_optix_win`. ✓

---

## Promotion Recommendation (Unchanged from Prior Review)

- **Sum rows (262,144/sum and 524,288/sum):** Advance to M7 candidate wording review.
  All P1 blockers are resolved. Draft wording now correctly discloses the projection basis.
  Break-even at 1–2 repeats supports a clean public claim.

- **Count rows (262,144/count and 524,288/count):** Do not promote. Break-even at 14
  repeats and only 2.5–2.6x at repeat 100 are not compelling. `count_mode_high_breakeven_blocks_public_claim`
  is now a named blocker on both count rows.

- **No additional pod run required.** The four fixes are all contract-language,
  disclosure, and artifact-completeness changes. The underlying measurements are fresh,
  math-verified, and unaltered.
