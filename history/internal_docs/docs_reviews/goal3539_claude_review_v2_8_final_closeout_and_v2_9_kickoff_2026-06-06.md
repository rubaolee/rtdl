# Goal3539: Claude Review — v2.8 Final Closeout and v2.9 Kickoff Plan

Date: 2026-06-06

Reviewer: Claude (independent read-only review)

Verdict: `accept-with-boundary`

## Reviewed Artifacts

| Artifact | Role |
| --- | --- |
| `docs/reports/goal3536_v2_8_vs_v2_3_10s_steady_state_a5000_2026-06-06.md` | 10s steady-state measurement baseline |
| `docs/reports/goal3522_v2_8_internal_closeout_3ai_consensus_2026-06-05.md` | Prior 3-AI internal closeout consensus |
| `docs/reports/goal3537_v2_8_final_internal_closeout_after_10s_evidence_2026-06-06.md` | v2.8 final closeout supplement |
| `docs/reports/goal3538_v2_9_performance_first_kickoff_plan_2026-06-06.md` | v2.9 kickoff plan |

---

## Q1: Does Goal3537 Correctly Close v2.8 After the Stricter Goal3536 Evidence?

**Yes, with one gap to track.**

Goal3537 is a correct supplement to Goal3522. It:

- Cites the full evidence chain (Goal3522, Goal3527, Goal3533, Goal3536) in order.
- Accurately transcribes the six target-compliant Goal3536 rows (median 1.016x, geomean 1.039x).
- Accurately transcribes the five partial rows, including their stated reasons for partial status.
- Explicitly corrects the RayDB grouped-sum overclaim (previous 7.2x → actual 0.998x under long-run measurement).
- Carries forward the five concrete weak-row debts as numbered items.
- Preserves the Goal3522 public boundary without weakening any of its prohibitions.

**Gap:** Goal3536 reports an all-row diagnostic reading of 11 rows (median 1.006x, geomean 0.946x) that is distinct from the target-compliant-subset reading. Goal3537 cites only the target-compliant subset numbers in its summary. A reader who reads only Goal3537 and not Goal3536 may miss that the all-row geomean is below 1.0x. Goal3537 does not need to lead with the all-row diagnostic, but it should mention it once with an explicit note that it is diagnostic-only due to the five partial rows. This prevents future readers from cherry-picking the 1.039x figure in isolation.

---

## Q2: Does Goal3537 Avoid Overclaiming v2.8 as a Broad Performance Leap?

**Yes, clearly and without ambiguity.**

The document explicitly states "v2.8 is not positioned as a broad performance leap over v2.3" and lists eight numbered items in the Final v2.8 Position section that collectively rule out every major overclaim vector: public release, public speedup, broad RT-core speedup, true-zero-copy, arbitrary partner-composition. The RayDB Correction section is particularly important — it names the specific prior artifact that carried the false 7.2x reading and states the correct long-run result.

No overclaim language was found in the closeout statement.

---

## Q3: Is Goal3538 the Right v2.9 Performance-First Plan?

**Yes, substantially.**

The plan is correctly scoped. Its central discipline — measure first, repair before new features, no architecture labels — is the right response to the Goal3536 evidence. The eight Engineering Rules are stronger than equivalent rules in prior versions: Rule 5 (sub-millisecond rows cannot be headline evidence without resident-loop stretch) and Rule 6 (no fake same-contract ratios for evolved contracts) directly close the two measurement pathologies that corrupted v2.8 evidence.

Workstream ordering is logically sound: harness coverage (WS1) precedes weak-row repair (WS2) because measurement quality is a prerequisite for determining whether a regression is real or an artifact.

One scoping concern: Workstream 3 (Resident Execution and Batching) introduces new runtime mechanics — CUDA graph replay, persistent stream/executor pools, device-resident grouped reductions. These are new features, not measurement fixes. The plan correctly gates each with "only if correctness is fail-closed" and "only where they preserve determinism," which is appropriate discipline. But Workstream 3 should not be started in parallel with Workstream 1 and 2; it should begin only after V2.9-G2 (full 10s table with no silent partial rows) is closed. The current plan does not explicitly enforce this ordering, and parallel work would create the same measurement-quality problem that Goal3536 was built to solve.

---

## Q4: Are the P0 Priorities Correct (Barnes-Hut, Spatial RayJoin, Full 10s Coverage)?

**Yes, the P0 selection is correct. One P1 needs a clarifying note.**

**Barnes-Hut P0:** At 0.464x, Barnes-Hut is a genuine regression, not measurement noise. It is the only row in Goal3536 that falls below 0.5x. P0 is warranted and non-negotiable.

**Spatial RayJoin P0:** Correct. The current spatial RayJoin evidence is a single sub-millisecond row (0.000526s v2.3 vs 0.000503s v2.8), which Goal3536 flags as partial because the wrapper reached only milliseconds of total time. This is the lowest-quality row in the entire table. Multiple promoted contracts depend on RayJoin; if that single noisy row turns out to be a regression at scale, it would invalidate a significant portion of the v2.8 capability story. P0 is the right designation.

**Full 10s Coverage P0:** Correct. The 10s harness coverage is a prerequisite for every other performance claim. Without it, the weak-row repair results in V2.9-G3 through V2.9-G6 cannot produce final evidence either.

**LibRTS P2 (clarifying note):** LibRTS AABB index is at 0.894x with partial evidence — the wrapper reached only 6 seconds, not 10. The measured regression may be worse once full 10s evidence exists. P2 is defensible given that 0.894x is closer to parity than Barnes-Hut, but reviewers should note that the final LibRTS reading after proper repeat-hook support could cross the 0.95x remediation threshold in either direction. The plan's close rule ("recover to at least 0.95x, or prove the deficit is measurement/setup dominated") is the right gate; just do not assume P2 means low risk.

---

## Q5: Does the Plan Preserve the App-Agnostic Engine Boundary and Explicit Partner-Choice Rule?

**Yes, both are preserved without regression from Goal3522.**

Engineering Rule 2 ("App-specific native-engine code is forbidden") and Engineering Rule 3 ("Users choose partners explicitly; the runtime must not silently choose PyTorch, CuPy, Numba, or Triton") directly mirror the Goal3522 public boundary. Goal3537 item 6 in Carry-Forward Weak Rows adds the runtime-dispatch formulation explicitly.

Workstream 3 carries a potential boundary stress point: device-resident grouped reductions and CUDA graph replay are easy places to hide implicit partner selection if the implementation is not careful. The plan mitigates this with "must remain app-agnostic" and "generic contract" language, but these are aspirational rules. Before Workstream 3 code lands, a claim-boundary scan equivalent to Goal3520 should be run against any new resident-execution primitives. That scan is not listed in the V2.9 goal sequence and should be added, either as a sub-task of V2.9-G7 or as an explicit V2.9-G8.

---

## Q6: What Must Change Before v2.9 Implementation Starts?

Four items require resolution before the first implementation goal (V2.9-G1) begins:

**1. Add the all-row diagnostic reading to Goal3537.**
Goal3537 should cite the Goal3536 all-row diagnostic (median 1.006x, geomean 0.946x, diagnostic-only because five rows are partial) alongside the target-compliant subset. This is a documentation fix, not an implementation block, but it must exist before Goal3537 is treated as the canonical v2.8 performance record.

**2. Specify hardware continuity for the v2.9 measurement chain.**
Goal3536 used RTX A5000 (pod `root@69.30.85.203 -p 22057`, driver 580.126.09, 24564 MiB). V2.9-G2 through V2.9-G7 involve rerunning and extending the same table. The kickoff plan does not specify whether all v2.9 runs must use the same hardware class. If a different pod or GPU is used, ratios that cross the 0.95x threshold boundary could shift due to hardware differences alone, not code changes. Before V2.9-G1, write down the hardware continuity rule: either "same A5000 class required for all table-update runs" or an explicit statement that cross-hardware comparisons are permitted with named caveats.

**3. Add an acceptance gate for the honest-regression classification path.**
The Barnes-Hut close rule in Goal3538 states: "recover to at least 0.95x against v2.3 same-contract evidence, or write a bounded root-cause/honest-regression report." The plan does not specify who reviews the honest-regression report or what the review gate is. If Barnes-Hut cannot be repaired to 0.95x, a classification report alone should not close the row; it should require at minimum a single-AI review before V2.9-G7 can proceed. Add this gate to the V2.9-G3 acceptance criteria.

**4. Make Workstream 3 sequencing explicit.**
Workstream 3 (Resident Execution and Batching) must not start before V2.9-G2 is closed. Add an explicit dependency note: "Workstream 3 work begins only after V2.9-G2 final 10s table is accepted." This prevents the recurring problem of new-feature work contaminating a measurement baseline that is still being established.

**Advisory (not a blocker):** The RT-DBSCAN nuance established in Goal3522 — raw RT-count row is 0.937x at 32K while grouped-stream path reaches 4x+ — is not carried forward in Goal3537 or Goal3538. Goal3536 does not appear to have re-measured DBSCAN separately. V2.9-G7's final performance packet should ensure both RT-DBSCAN rows appear, not just the promoted grouped-stream headline.

---

## Summary

| Question | Finding |
| --- | --- |
| Q1: Goal3537 closes v2.8 correctly after Goal3536? | Yes; missing: all-row diagnostic citation. |
| Q2: Avoids broad performance overclaim? | Yes, clearly. |
| Q3: Goal3538 is the right v2.9 plan? | Yes; Workstream 3 sequencing needs to be made explicit. |
| Q4: P0 priorities correct? | Yes; LibRTS P2 carries hidden measurement risk worth flagging. |
| Q5: App-agnostic boundary and partner-choice preserved? | Yes; add claim-boundary scan to V2.9 goal sequence. |
| Q6: Changes before implementation starts? | Four items above (all-row diagnostic, hardware continuity, honest-regression gate, WS3 sequencing). |

**Verdict: `accept-with-boundary`**

The v2.8 closeout supplement and v2.9 kickoff plan are internally consistent, accurately grounded in Goal3536 evidence, and preserve the engineering discipline established in Goal3522. The four pre-implementation items above should be resolved — none requires new pod runs or code changes, only documentation and process clarity. After those are addressed, V2.9-G1 may begin.
