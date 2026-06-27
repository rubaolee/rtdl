---

## External Technical Review: Phoenix V3 M59 LibRTS Yellow/Open Decision
**Reviewer:** External AI reviewer
**Date:** 2026-06-23
**Packet status at intake:** `m59_librts_set_b_yellow_open_limit_not_step2_gap_pending_external_review`

---

## Verdict

```
accept_m59_librts_set_b_yellow_open_limit_continue_set_a_step2
```

No blocking findings. Two P2 concerns to carry forward in the evidence ledger. Details below.

---

## Question-by-Question Audit

### Q1. Is it correct to classify M58 LibRTS/AABB as Set-B controls rather than Set-A architecture-bearing probes?

**Yes. The classification is technically sound.**

Set-A is defined as multi-phase, residency-rich, continuation-heavy workloads where the prepared runner can produce a material runtime-sourced gain. LibRTS/AABB is a prepared AABB index count/query-set route. The evidence confirms this directly:

- `optix_cold_single_shot`: `repeat=1, warmup=0` — single-shot by design, no multi-phase structure.
- `embree_32768_stress`: `repeat=20, warmup=5` — a stress repetition of a single backend count operation, not a multi-phase residency pipeline.
- Source-signature preflight (required=true, returncode=0) verified all eight markers: `set_b_control_candidate=True` and `set_a_probe_candidate=False` confirmed in live source.

Classifying this family as Set-A would be incorrect. Set-B (parity target) is the only honest classification. The freeze-before-run rule is satisfied: classification is in source code and preflight-verified, not decided after seeing results.

---

### Q2. Is the OptiX cold single-shot row correctly kept yellow/open?

**Yes. Yellow/open is the only defensible label.**

Raw numbers from `summary.json`:

| Metric | Value | Set-B floor |
|---|---|---|
| Full geomean | 0.979485x | 0.98x (**MISS** — marginal but real) |
| Median | 0.938x | — |
| Pass count ≥0.95x | 3/8 | — |
| First-sample-stripped geomean | 1.002x | — |
| **First-sample-stripped median** | **0.939x** | — |

The M59 packet invokes first-sample stripping to explain the cold-start effect. This is a valid framing for the geomean (cold first shot inflates V3's apparent cost), but the stripped median is still 0.939x — meaning 5 of the 7 post-cold-shot samples also fail to clear 0.95x. The cold-start explanation covers the arithmetic of the geomean; it does not cover the rest of the distribution. Green or closed is not supportable. Yellow/open is correct.

---

### Q3. Is it technically acceptable to avoid another immediate LibRTS POD run from M59?

**Yes.**

The M57 one-shot authorization token was consumed by M58. No authorization exists for a second run. More importantly, even if authorized, another LibRTS run would not advance the project: the rows are failing because of single-shot characteristics and cold-start overhead that more samples will not eliminate without runtime changes — and LibRTS is not the place to make those runtime changes, because it is a Set-B control, not a Set-A trunk family. Engineering cycles spent on another LibRTS stability loop would displace the Step 2 work that can actually compound.

---

### Q4. Does M59 preserve the Set-B release risk instead of hiding it?

**Yes, with one deficiency to carry forward.**

The packet explicitly keeps both rows `yellow_stability_boundary_watch_row_open`, refuses closure, enumerates the OptiX weakness numerically, and states clearly that "LibRTS can remain a Set-B control only if the final evidence packet carries the yellow/open explanation honestly." The conditional form is correct — it does not pre-approve the row.

**The deficiency (see P2-1 below):** the required user-language explanation for the OptiX row is committed to but not supplied in this packet. M59 defers it as an obligation. That is acceptable for a decision packet but must not be forgotten.

---

### Q5. Is the proposed next action correct: return Step 2 to a Set-A runtime family?

**Yes. This is the only action consistent with the redesign.**

The redesign (`proposed_v3_redesign_build_the_runtime_trunk_first_2026-06-22.md`) is explicit: Step 2 must prove the runner is general by routing a second and third Set-A family through the same productized execution path. LibRTS cannot contribute to that proof because it is a Set-B control. Suitable candidates are named in M59: Spatial/RayJoin, RTNN/ranked summary, RT-DBSCAN/component continuation, Barnes-Hut/frontier accumulation, Triangle, or Hausdorff. The selection must be frozen and rationale committed before any run.

---

### Q6. Does the packet preserve all non-authorization boundaries?

**Yes. All twelve boundaries are present and explicit in both the decision report and the intake report:**

- no V3 release ✓
- no all-app benchmark run ✓
- no broad paid POD campaign ✓
- no second M57 run ✓
- no additional LibRTS POD run ✓
- no public speedup wording ✓
- no broad V3-over-V2 claim ✓
- no V4 work ✓
- no embedding ✓
- no C ABI ✓
- no true-zero-copy claim ✓
- no watch-row closure ✓

---

### Q7. If rejecting, what concrete runtime-engine work should supersede this decision?

Not applicable. This review accepts the decision. See P2 findings below.

---

## Findings

### P0 (Blocking) — None

### P1 (High priority, non-blocking this decision) — None

### P2 (Non-blocking; must be discharged before release review)

**P2-1: First-sample-stripped median (0.939x) undercuts the cold-start explanation**

The M59 packet correctly notes that stripping the first sample brings the OptiX geomean to 1.002x. However, the stripped median (samples 2–8) is 0.939x, and 5 of those 7 samples are below 0.95x. The cold-start framing explains one sample; it does not explain the post-cold distribution. The required user-language explanation must address this explicitly — it cannot only point to the stripped geomean without also accounting for the weak stripped median. If the explanation cannot address both, the row represents a genuine systematic V3 execution overhead on single-shot OptiX, not just cold start noise.

**Obligation:** before any release decision, the user-language explanation for `optix_cold_single_shot` must cover: (a) why V3 has higher cold-start cost than V2.14, (b) why the median of non-cold-start samples is still 0.939x, and (c) whether this is noise at n=7 or a systematic overhead that would require a fast-path bypass for single-shot routes.

**P2-2: OptiX Set-B floor miss (0.979x < 0.98x) should be called out explicitly**

The M59 decision says the geomean is "just under the Set-B 0.98x parity line." This is accurate but understated. The `set_b_geomean_v3_vs_v2 >= 0.98x` gate from the bar proposal is technically failed by 0.000515x. Yellow/open is the correct label (no dispute), but the final release evidence packet must explicitly register this as a below-floor row with accepted explanation rather than treating it as borderline-acceptable on the basis of proximity. The precedent matters: a pattern of "just under floor but close enough" claims is the failure mode the scorecard is designed to prevent.

---

## Summary

The M59 classification decision is technically sound. LibRTS/AABB is a Set-B control by workload structure and by source-verified metadata, not by post-hoc result interpretation. The yellow/open labels are correctly preserved. The authorization boundaries are intact. The next action — returning Step 2 to a Set-A runtime family — is the correct move under the redesign.

The two P2 findings are obligations to be discharged at the release review stage, not at this decision stage. Neither constitutes a reason to modify M59 or request another LibRTS run.
