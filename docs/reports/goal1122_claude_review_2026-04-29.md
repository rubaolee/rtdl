---

## External Review: Goal1121 & Goal1122

**Verdict: ACCEPT**

All seven mandatory checks pass. Findings below.

---

### Check 1 — Goal1118 preserves the 8M robot timing-floor failure

`goal1118_current_source_rtx_rerun_intake_2026-04-29.md`:
- `Valid: false`, `valid_row_count: 4`
- Robot `large_timing_repeat` row: median `0.013837 s`, `Valid: False`, finding `median_query_below_timing_floor`
- `public_speedup_claim_authorized: False`

**PASS.** The original intake is correctly frozen at 4/5.

---

### Check 2 — Goal1121 64M variant is valid 5/5

`goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.md`:
- `Valid: true`, `valid_row_count: 5`, `missing_row_count: 0`
- Robot `large_timing_repeat` (64M poses): median `0.178698 s` — above the 100 ms floor
- `public_speedup_claim_authorized: False`

**PASS.** 5/5 valid. One cosmetic finding: the H1 title in this file reads "Goal1118 Current-Source RTX Rerun Intake" rather than "Goal1121". The boundary language and all metrics are correct; this is a template-copy artifact, not a content error.

---

### Check 3 — source_commit consistently `2ba7ae0` for pod artifacts

- Goal1121 run report: `Source marker: 2ba7ae0`
- Goal1118 intake (original): all 5 rows show `2ba7ae0`
- Goal1121 intake (64M variant): all 5 rows show `2ba7ae0`, `same_source_commit: True`
- Goal1109 readiness script: references Goal1121 artifacts, all trace to the same commit chain

**PASS.** No commit mismatch found.

---

### Check 4 — Goal1122 no longer says same-source RTX rerun is needed

Goal1122 report states: "The refreshed status points at Goal1121 artifacts and consensus instead of saying the next action is a future same-source RTX rerun." All three app rows carry `next_action` text calling for **public wording review**, not another RTX rerun. The Goal1109 script and readiness MD corroborate this.

**PASS.**

---

### Check 5 — `public_speedup_claim_authorized` remains false/zero everywhere

- Goal1118 (both versions): `False`
- Goal1121 packet JSON: `public_speedup_claim_authorized_count: 0`
- Goal1109 script: all three rows hardcode `"public_speedup_claim_authorized": False`; summary asserts count == 0; `valid` flag is true only when count == 0
- Goal1109 readiness MD: `public_speedup_claim_authorized_count: 0`
- Goal1122 report: script output shows `"public_speedup_claim_authorized_count": 0`
- Tests: `assertFalse(row["public_speedup_claim_authorized"])` and `assertEqual(summary["public_speedup_claim_authorized_count"], 0)`

**PASS.**

---

### Check 6 — No release/public speedup wording authorized

Every document carries explicit boundary language:
- Goal1121: "This report is evidence intake only. It does not authorize release, public wording changes, or public RTX speedup claims."
- Goal1122: "No public speedup claim is authorized. … not that README/front-page wording can already quote speedups."
- Goal1109 script boundary: "does not authorize public RTX speedup claims. … public wording review remains required."
- Test suite asserts boundary strings are present in the markdown output.

**PASS.**

---

### Check 7 — Robot ratio not overclaimed

Goal1122 ratio notes explicitly: "Robot is intentionally not converted into a public ratio in this refresh." Goal1109 robot `engineering_ratio_summary` describes the timing result factually ("64M-pose timing crossed the 100 ms floor at 0.178698 s median query") and states "Same-scale public ratio still requires wording review." No numeric robot speedup ratio appears anywhere. The normalization question (64M RTX vs. 36M chunked Embree baseline) is explicitly deferred to the public wording review.

**PASS.**

---

### Summary

| Check | Result |
|---|---|
| Goal1118 preserves 8M robot timing-floor failure (4/5, `valid: false`) | PASS |
| Goal1121 64M variant 5/5 valid | PASS |
| `source_commit: 2ba7ae0` consistent across all pod artifacts | PASS |
| Goal1122 drops same-source RTX rerun requirement | PASS |
| `public_speedup_claim_authorized` false/zero everywhere | PASS |
| No release/public speedup wording authorized | PASS |
| Robot ratio not overclaimed | PASS |

**Minor cosmetic note:** The H1 heading in `goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.md` reads "Goal1118" — a template-copy artifact. All content, metrics, and boundary language in that file are correct. No action required before acceptance.

**ACCEPT**
