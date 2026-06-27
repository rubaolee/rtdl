I have read all eight required files. Here is my formal external review.

---

## External Review: V4 Section 8 Prepared Hot-Path Validation

**Date:** 2026-06-24
**Branch:** codex/v4-tier2-section8
**Verdict:** `accept_prepared_hot_path_credit_no_release`

---

### 1. Was the protocol revision legitimate?

**Yes — it was explicitly authorized by the prior Claude backfill review.**

The prior review (Q3 finding): *"The whole-call fail is controlling for this experiment. A protocol revision is the required next step before any summary route credit."* It then enumerated in Q5 exactly what the revised protocol must include. The revised protocol satisfies every stated requirement:

| Requirement (from prior Q5) | Revised Protocol | Harness | Status |
|---|---|---|---|
| Session boundary: prepare once, ≥7 measured calls within same session | "prepared scene creation excluded from timed windows" | `with rt.prepare_generic_...` opened once; `_measure()` runs 7 calls inside | ✓ |
| Baseline: rows emit+reduce, excluding case/oracle construction | "rows: OptiX emit + Python reduce_rows" | `_measure(lambda: _run_rows_hot(case))` — case/oracle built before timing | ✓ |
| Sizes: 8192, 32768, 131072 | Stated | `copies = (8192, 32768, 131072)` | ✓ |
| Repeats: ≥7 measured, 1 warmup | `repeat: 7, warmup: 1` | `--repeat 7 --warmup 1` | ✓ |
| Gate: ≥1.5x on ≥2 serious sizes | `SUMMARY_SPEEDUP_GATE = 1.5`, `MIN_PASSING_SERIOUS_SIZES = 2` | `_evaluate_gate()` implements both conditions | ✓ |
| Route D hand-written OptiX reference | Not sought here; wording remains unauthorized | `near_handwritten_optix_claim_authorized: false` | ✓ (not required for this credit) |
| External review required | "external_review_then_consider_summary_hot_path_credit" | `authorized_next_step` field | ✓ |

The prior review said "PreparedOutlierDetectionSession (or equivalent)." The harness uses `rt.prepare_generic_fixed_radius_count_threshold_2d` directly as the context manager — the same underlying API that `PreparedOutlierDetectionSession.__init__` wraps. This is the stated equivalent. **The revision is legitimate.**

---

### 2. Is the timing boundary valid and matched?

**Yes — with one material observation about summary-route variance.**

**Boundary implementation in the harness:**

```python
def _measure_size(copies, ...):
    case = app.make_outlier_case(copies=copies)           # excluded ✓
    oracle_rows = app.expected_tiled_density_rows(...)    # excluded ✓

    rows_result = _measure(lambda: _run_rows_hot(case))   # baseline timed ✓

    prepare_start = time.perf_counter()
    with rt.prepare_generic_fixed_radius_count_threshold_2d(...) as prepared:
        prepare_sec = time.perf_counter() - prepare_start # prepare excluded ✓
        summary_result = _measure(lambda: _run_summary_hot(prepared, ...))  # candidate timed ✓
```

**Baseline timed scope** (`_run_rows_hot`): `app._run_rows("optix", case)` (OptiX neighbor-row emit) + `app.density_rows_from_neighbor_rows(...)` (Python `reduce_rows(count)` conversion). Neither case construction nor oracle comparison is included. Correct.

**Candidate timed scope** (`_run_summary_hot`): `prepared.run(points, radius=..., threshold=...)` (prepared native fixed-radius count-threshold query) + `app._density_rows_from_count_rows(points, result["rows"])` (Python compact-to-density conversion). Prepare is outside the timed window. Correct.

**Symmetry:** Both routes receive 1 warmup call before 7 measured calls, using identical `_measure()`. The warmup is sufficient to saturate the rows OptiX pipeline — rows timing variance confirms this (1–4% spread). Summary route variance is higher (up to ~20% at 32768), which I flag below.

**Variance concern at 32768:** Summary timings at 32768: min=1.091s, max=1.305s, median=1.194s — a 19% peak-to-median ratio. This is noisier than the other sizes. The adversarial floor still holds: worst summary time (1.305s) vs. best rows time (2.103s) = 1.61x, well above the 1.5x gate. The variance does not invalidate the median statistic but should be noted as evidence of thermal or memory-pressure variance at this size.

**Overall boundary verdict: valid and matched across both routes.**

---

### 3. Is the result valid enough to grant prepared-session summary hot-path credit?

**Yes.**

| copies | points | correctness | rows baseline median | summary prepared median | speedup | gate (≥1.5x) |
|---:|---:|:---:|---:|---:|---:|:---:|
| 8192 | 65,536 | pass | 0.4709s | 0.2845s | 1.655x | pass |
| 32768 | 262,144 | pass | 2.1155s | 1.1935s | 1.772x | pass |
| 131072 | 1,048,576 | pass | 10.4256s | 5.2909s | 1.970x | pass |

**Correctness:** All three sizes pass. `rows_matches_oracle: true`, `summary_matches_oracle: true`. Oracle outlier counts match point-for-point at all sizes.

**Gate:** All three sizes pass at 1.5x. The requirement is ≥2. Margin above gate: +0.155x, +0.272x, +0.470x. No size is borderline.

**Route integrity:**
- `native_continuation_active: true` on summary at all sizes ✓
- `native_continuation_backend: "optix_threshold_count"` ✓
- `generic_primitive: "FIXED_RADIUS_COUNT_THRESHOLD_2D"` — not an app-identity kernel ✓
- `neighbor_row_materialization: false` on summary ✓
- `tier: "tier2_fused_native_primitive_hot_path"` ✓

**Harness self-attestation:** `release_claim_authorized: false`, `near_handwritten_optix_claim_authorized: false`, `timing_boundary` string matches the protocol description. `authorized_next_step: "external_review_then_consider_summary_hot_path_credit"`. All consistent.

**This review grants prepared-session summary hot-path credit, subject to the claim wording in §4.**

---

### 4. What claim wording, if any, is authorized?

The protocol authorizes the following base text. This review narrows and confirms it:

> For a prepared fixed-radius count-threshold scene (fixture: `make_outlier_case`, copies=8192–131072, 65,536–1,048,576 points), the compact summary hot path (prepared native `FIXED_RADIUS_COUNT_THRESHOLD_2D` query + Python compact-to-density conversion) beats the separated neighbor-row emit+reduce path (OptiX neighbor-row emit + Python `reduce_rows(count)`) by 1.65x–1.97x median wall time in the prepared-session hot-path protocol.

**Mandatory accompanying scope statement** whenever this claim is cited:

- This is a prepared-session hot-path comparison. It excludes scene preparation time. The whole-call app-route gate (original Section 8) still **fails** and has not been withdrawn.
- This is not a broad V4 speedup claim.
- This does not generalize beyond the measured operator (`FIXED_RADIUS_COUNT_THRESHOLD_2D`) and fixture.
- Hardware must be stated if cited (not recorded in the evidence JSON; requirer must supply from pod run provenance).

---

### 5. What remains required before adding another Tier-2 primitive?

In priority order:

1. **This review's outcome must be recorded.** The `accept_prepared_hot_path_credit_no_release` verdict must be filed against this packet before any work on a new primitive begins.

2. **The whole-call Section 8 failure remains on record and is not superseded.** The original gate outcome (`performance_gate.status: "fail"`, `v4_tier2_thesis_locally_validated: false`) was not overturned by this protocol revision. It was answered on a different question. Any future work that revisits the whole-call route (e.g., amortized prepare from `PreparedOutlierDetectionSession` at the app level) must go through a new formal protocol and external review.

3. **Any new Tier-2 primitive requires its own formal protocol document, measurement, and external review.** The scalar fused primitive and the summary prepared hot path are the only two authorized Tier-2 credits. A third primitive cannot be promoted on the basis of either of these packets — it needs its own chain.

4. **Route D (hand-written OptiX reference) remains unacquired.** No near-handwritten OptiX wording may be used for any claim until an independent Route D result is externally reviewed. This requirement is carried forward.

5. **No additional pod spend or architecture promotion** is authorized by this packet beyond recording the current credit.

---

### 6. Unauthorized claim confirmation

| Claim | Status | Evidence |
|---|---|---|
| V4 release claim | **Not authorized** | `release_claim_authorized: false` in result JSON; protocol §Claim Boundary; report final line |
| Broad V4 speedup wording | **Not authorized** | Protocol §Claim Boundary: "does not authorize broad V4 speedup wording" |
| Near-handwritten OptiX wording | **Not authorized** | `near_handwritten_optix_claim_authorized: false` in result JSON; Route D not acquired |
| Tier-3 callback claim | **Not authorized** | No Tier-3 measurement in this packet; not within scope of any reviewed protocol |
| App-specific native engine claim | **Not authorized** | `app_specific_native_engine_logic_allowed: false` in app metadata; protocol §Claim Boundary |
| Broad V3-over-V2 wording | **Not authorized** | Protocol §Claim Boundary; not measured in this packet |
| Automatic partner selection claim | **Not authorized** | `automatic_partner_selection_authorized: false` in app metadata |
| True-zero-copy claim | **Not authorized** | `true_zero_copy_claim_authorized: false` in app metadata |
| Whole-call app-route summary credit | **Not authorized** | Original Section 8 whole-call gate failed and is not overturned by this packet |

All prohibitions from the protocol, the harness `plan` metadata, the app code metadata, and the prior backfill review are internally consistent and intact.

---

## Verdict

**`accept_prepared_hot_path_credit_no_release`**

The protocol revision was explicitly authorized by the prior external review and was executed faithfully. The timing boundary is correctly implemented and symmetric. All three measured sizes pass the 1.5x gate with margin. Correctness passes at all sizes. Route integrity flags confirm the generic primitive, not an app-identity kernel. No V4 release, no broad speedup claim, no near-handwritten OptiX wording, no Tier-3 callback claim, and no app-specific native engine claim is authorized. The whole-call Section 8 gate failure remains on record and is not superseded by this result.
