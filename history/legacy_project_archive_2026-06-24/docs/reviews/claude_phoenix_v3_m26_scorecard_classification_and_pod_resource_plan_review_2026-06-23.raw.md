---

## Second AI Review — Phoenix V3 M26 Scorecard Classification and POD Resource Plan

**Reviewer:** Claude (second AI reviewer)
**Date:** 2026-06-23
**Verdict:** `approve_with_amendments`

---

### Review Question 1 — Is the Set-B/control classification for LibRTS AABB single-shot correct, or should it be amended?

**Answer: Correct in architecture, but requires a timing-integrity caveat.**

The rationale is sound on its own terms: `aabb_index_all_count_only` is a lone primitive route with no cross-phase residency or continuation behavior. The V3 release mandate requires Set-A proof to come from multi-phase runtime gains, not from a single primitive invocation. Classifying this row as Set B/control is defensible architectural reasoning.

However, there is a classification-timing problem the packet does not resolve. This is the *first formal classification* of the row, and it lands immediately after the row returned `0.922x`. The packet never states whether the row was previously treated as Set A, or was always unclassified. That gap creates legitimate concern that D1 is post-result rationalization dressed as architecture, even if it isn't.

**Required amendment:** D1 must include an explicit statement of prior status — specifically, that the row was never previously designated Set A and was carried as a watch/control row from M22. If any prior document shows it was counted as Set A, the classification must be revisited under the freeze rule. Without that attestation, D1 is defensible in principle but vulnerable to challenge.

---

### Review Question 2 — Is it correct to reject counting prepared/repeated AABB as primary Set-A proof?

**Answer: Yes, rejection is correct. No amendment needed.**

The prepared/repeated OptiX numbers (`0.995x`, `0.999x` current/V2.14) demonstrate *parity*, not V3 material gain. The large `105.249x` and `63.596x` figures are OptiX-vs-Embree comparisons — hardware acceleration versus software ray-casting — not V3-versus-V2.14 runtime architecture wins. They prove the runner plumbing is wired and the hot OptiX path is healthy. That is exactly what supporting runner evidence means.

Using these as primary Set-A proof would conflate GPU-vs-CPU speedup with V3-vs-V2.14 speedup, which is a category error that would not survive scrutiny at release. D2 holds.

---

### Review Question 3 — Are the POD time/cost estimates reasonable enough for planning?

**Answer: Adequate as planning order-of-magnitude, but two items are fragile.**

The $0.25/hour rate is user-stated and appropriate to carry forward. The milestone chain from M27 to M35 is granular and internally consistent. The near-term 1-3 POD hour expectation is realistic.

Two items are potentially optimistic:

- **M27 cold OptiX repair (0.5–1.5 POD hours):** If the `0.922x` cold single-shot overhead is architectural — for example, if it comes from session initialization cost that is inherent to the prepared-runner model — it may not be tunable without a redesign that costs multiples of this estimate. The stop condition ("if cold row cannot clear without app-specific bypass, stop") is correct, but the wall-time budget before hitting that stop should be stated explicitly (e.g., "if not at ≥0.950x after 1 focused POD run, declare the repair blocked and proceed to Set-A trunk").

- **M29 Set-A trunk first execution (4–8 wall hours, 1–2 POD hours):** M25 required significant effort to establish runner routing evidence on a single family. The M29 estimate assumes that evidence transfers. If the chosen Set-A family requires its own routing investigation, this could expand to M25-scale effort. Acceptable for planning, but should be noted as a known risk.

The stop-early condition ("if Step-1/Step-2 trunk gains fail, stop after 2–4 POD hours") is the right circuit-breaker and I endorse it.

---

### Review Question 4 — Should M27 prioritize cold OptiX Set-B repair, Embree 32768 regression, or jump directly to the Set-A runtime trunk?

**Answer: The Embree 32768 regression must be triaged before M27 cold OptiX repair begins. The ordering in the plan is otherwise correct.**

The Embree regression (`stress_32768x1024_r20w5`, current/V2.14 = `0.891x`) is on a completely different code path from the OptiX watch row. If it is systemic rather than environmental, it would constitute an independent Phoenix V3 performance blocker that blocks release regardless of any OptiX outcome. Starting M27 cold OptiX repair without first determining whether the Embree regression is real would be optimizing against the wrong bottleneck.

The required triage is cheap: run 2–3 reproductions on the same POD to distinguish noise from regression. If it is reproducible, it must be logged as a separate open blocker before M27 repair starts. The plan currently says "separately log the Embree 32768 regression" as part of M27, which is too passive.

**Required amendment:** Triage of the Embree 32768 regression must be an explicit first step inside M27, not a background note. If triage confirms a reproducible regression (`< 0.950x`), it must be filed as an independent blocker alongside the cold OptiX row.

After triage, the M27 → M28/M29 ordering is correct. Set-B repair before Set-A trunk selection is the right sequencing — it keeps the classification clean before investing in new evidence.

---

### Review Question 5 — Does this plan preserve the performance mandate without wasting all-app POD time?

**Answer: Yes, structurally. Two stop conditions need numerical sharpening.**

D3 (all-app freeze) is maintained, the stop-early condition exists, and the exit condition for unlocking all-app is appropriately strict (≥2 Set-A probes with cross-phase residency confirmed, material gain, no hidden bypass). This is consistent with the project's source_tree_pod_gated_thirteen_row mandate.

The structural problem is that "material gain" in several stop conditions has no number. Without a threshold, an M30 focused probe could return `1.02x` and create an argument about whether it clears the bar. The Set-A probes in M30 and M31–M33 need a stated minimum (suggested: `≥1.050x` focused, same-POD V3/V2.14 on the primary Set-A family) before being counted as wins that unlock the next milestone.

**Required amendment:** State a minimum numerical threshold for "material gain" in the M30 and M31–M33 stop conditions. Without it, the freeze exit conditions are vulnerable to incremental creep.

---

### Review Question 6 — Does this packet authorize release, all-app, public speedup wording, or V4/external zero-copy/embedding scope?

**Answer: No. The non-authorization block is complete and correctly stated.**

The packet explicitly withholds authorization for:
- V3 release
- Full all-app rerun
- Public speedup wording
- Broad "V3 is faster than V2.x" wording
- Reclassifying rows after results
- Counting AABB single-shot as Set A
- V4/external zero-copy/embedding scope

No inadvertent authorization language was found in the body of the M26 document. The non-authorization block in both the call-for-review and the plan document are consistent with each other and with the M25 consensus. This is clean.

---

### Summary of Non-Authorizations (Confirmed)

This review does not authorize:
- V3 release
- Full all-app rerun
- Public speedup wording
- Broad "V3 is faster than V2.x" wording
- Counting AABB single-shot (Set B) as Set A
- Counting prepared/repeated AABB OptiX as primary Set-A release proof
- V4/external zero-copy/embedding claims
- Unlocking all-app before ≥2 true Set-A probes with material gains

---

### Amendments Required Before Execution

1. **D1 timing-integrity attestation:** Add explicit documentation that the AABB single-shot row was never previously designated Set A (carried from M22 as an unclassified watch/control row). If that cannot be attested, D1 must be treated as a potential freeze-rule conflict and escalated.

2. **Embree 32768 triage as M27 first step:** Triage of the Embree stress regression must be an explicit, sequenced first action inside M27 — not a background note. Reproducible result below `0.950x` = separate open blocker, logged before cold OptiX repair begins.

3. **Numerical threshold for "material gain":** M30 and M31–M33 stop conditions must state a minimum speedup (e.g., ≥1.050x focused same-POD V3/V2.14) for a probe to count as a Set-A win and unlock the next milestone.

---

**Verdict: `approve_with_amendments`**

The core classification decisions (D1, D2, D3) are architecturally sound and consistent with the M25 consensus. The resource plan is appropriately conservative. The three amendments above are required before engineering work proceeds — they close real exposure on classification integrity, an untracked blocker, and a vague stop condition that could permit creep. None of them require a new POD run or a new review cycle; they are documentation and scoping clarifications that should be resolved in writing before M27 begins.
