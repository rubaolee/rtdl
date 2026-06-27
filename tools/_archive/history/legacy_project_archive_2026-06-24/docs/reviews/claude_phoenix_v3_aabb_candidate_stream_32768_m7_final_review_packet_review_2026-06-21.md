All arithmetic is verified. I now have everything I need for the formal review.

---

## Phoenix V3 AABB Candidate-Stream 32768 M7 Final Review

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-06-20  
**Verdict:** **CONDITIONAL APPROVE** — one P0 wording change required before promotion. The row is internally consistent and the evidence is release-grade. See the P0 fix below.

---

### Arithmetic Verification

All three published ratios are arithmetically correct to three decimal places, derived directly from the raw evidence files:

| Metric | Computed from evidence | Packet claims | Result |
|---|---|---|---|
| Query OptiX / Embree | 814.338822x | 814.339x | **PASS** (rounds correctly) |
| Wall OptiX / Embree | 132.753177x | 132.753x | **PASS** |
| Elapsed OptiX / Embree | 73.826475x | 73.826x | **PASS** |

Embree query median: 36.09376s (warmup=2, repeat=5)  
OptiX query median: 0.04432s (warmup=2, repeat=5)

---

### Count Verification

All three count fields match between Embree, OptiX, and the independent float32 oracle:

| Count | RTDL Embree | RTDL OptiX | float32 oracle | Match |
|---|---|---|---|---|
| point\_contains | 46,343,760 | 46,343,760 | 46,343,760 | **PASS** |
| range\_contains | 32,302,908 | 32,302,908 | 32,302,908 | **PASS** |
| range\_intersects | 70,429,254 | 70,429,254 | 70,429,254 | **PASS** |

float64 oracle deltas (backend minus float64): +10, +8, +19 — exactly as documented. The relative magnitudes are ~2–3×10⁻⁷ (sub-ppm). These are consistent with float32 boundary semantics, not a correctness bug. Correctly disclosed.

---

### Question 1: Is the float32-inclusive numeric contract acceptable for M7 wording if explicitly named?

**Yes.** The float32 oracle closes the prior `cpu_reference_skipped_and_matches_reference_null` blocker. All three count fields agree. The contract is named explicitly in the row ID, the packet metadata, the draft wording, the JSON, and the tutorial. The forbidden wording list explicitly prohibits claiming float64 accuracy. This is sufficient for row-scoped M7 wording.

---

### Question 2: Does the float64 mismatch require blocking the row?

**No.** The mismatch is adequately disclosed and correctly attributed. The deltas (+10/+8/+19 out of 46M/32M/70M) are a known float32 boundary artifact, not a sign of implementation error. The draft wording does not claim float64 accuracy anywhere. The float64 oracle status is correctly marked `complete_with_expected_mismatch` rather than `pass`. The disclosure is complete.

---

### Question 3: Is the 814.339x query ratio safe to publish with the proposed wording?

**Yes, subject to the P0 fix below.** The comparison pair is unambiguous: current RTDL OptiX vs current RTDL Embree, same workload, same protocol, same hardware. The phrase "RTDL's OptiX route vs RTDL Embree route" correctly prevents misreading as LibRTS paper, authors-code, or V2 comparison. The final boundary sentence covers all four forbidden interpretations explicitly.

**However:** the quantitative sentence currently reads:

> "RTDL's OptiX route was 814.339x faster than the RTDL Embree route **for the measured query median**"

The float32-inclusive qualification appears in the preceding setup sentence, not in the sentence containing the 814.339x number. A reader who extracts the number in isolation — which will happen — will not see the numeric contract next to it. This is the one structural gap.

**P0 fix (required before promotion):** embed the numeric contract directly in the speedup sentence:

> "RTDL's OptiX route was 814.339x faster than the RTDL Embree route **for the measured float32-inclusive query median**"

This is a four-word insertion that closes the extraction risk without changing the meaning.

---

### Question 4: Are the non-paper, non-authors-code, count-only, and non-V2 boundaries strong enough?

**Yes.** Each boundary is held by multiple independent mechanisms:

- **Non-paper:** both Embree and OptiX evidence files have `"paper_reproduction": false`, `"paper_equivalent_dataset": false`. The packet JSON has `"paper_reproduction_claim_authorized": false`. The draft wording says "not a LibRTS paper reproduction."
- **Non-authors-code:** both evidence files have `"authors_code_comparison": false`. The packet JSON has `"librts_authors_code_claim_authorized": false`. The draft wording says "not LibRTS authors-code timing."
- **Count-only:** the row ID itself contains `count_only`. The workload description says "AABB count-only". The draft wording says "not full spatial-index acceleration."
- **Non-V2:** arithmetic confirms V3 is 3.44% **slower** than V2.14 on OptiX (V3: 0.04432s vs V2.14: 0.04285s), so no V3-over-V2 claim is arithmetically supportable. The packet JSON has `"broad_v3_faster_than_v2_claim_authorized": false`. The draft wording says "not a V3-over-V2 speedup claim." The no same-row V2.14 Embree time correctly blocks any paired V2 wall/elapsed comparison.

All four boundaries are structurally enforced, not just asserted.

---

### Question 5: If approved, should only this exact row become M7-qualified?

**Yes, strictly.** The V2.14 paired data confirms this is OptiX-vs-Embree on the current build, not a V2 comparison. No other AABB row, no V2 comparison row, and no broader spatial-index row is authorized by this evidence. The promotion scope is exactly:

```
aabb_candidate_stream_all_count_only_float32_32768
```

---

### P0 Wording Change (Required Before Promotion)

In both `.md` and `.json` draft public wording, change the speedup sentence from:

```
RTDL's OptiX route was 814.339x faster than the RTDL Embree route for the measured query median
```

to:

```
RTDL's OptiX route was 814.339x faster than the RTDL Embree route for the measured float32-inclusive query median
```

This is the only required change.

---

### P1 Note (Non-Blocking, Recommended)

The tutorial (`12_aabb_candidate_stream.md`) lists `operation: all` (the raw artifact label) while the packet row ID uses `all_count_only` (the descriptive label). Both are accurate but they will confuse anyone trying to match the tutorial table to the evidence JSON. A one-line parenthetical — "(the raw artifact uses `operation: all`; `all_count_only` names what is returned)" — would prevent this confusion.

---

### Summary Verdict

| Item | Result |
|---|---|
| Arithmetic correct | PASS |
| Counts verified against float32 oracle | PASS |
| float64 mismatch disclosed | PASS |
| float32 contract named in row and wording | PASS (P0 fix required in speedup sentence) |
| Non-paper boundary | PASS |
| Non-authors-code boundary | PASS |
| Non-V2 boundary | PASS (V3 is actually 3.44% slower on OptiX) |
| Count-only boundary | PASS |
| Scope limited to exact row | PASS |

**Decision: APPROVE with P0 fix applied.** After the "float32-inclusive" insertion into the speedup sentence, `aabb_candidate_stream_all_count_only_float32_32768` is M7-qualified for row-scoped public wording. All other promotion conditions (2-AI consensus, explicit `m7_promotion_authorized: true` gate) remain.
