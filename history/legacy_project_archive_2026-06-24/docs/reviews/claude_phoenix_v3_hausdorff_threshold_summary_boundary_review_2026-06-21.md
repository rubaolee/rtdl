# Claude Review: Phoenix V3 Hausdorff Threshold-Summary Boundary Packet

Reviewer: Claude Sonnet 4.6
Date: 2026-06-21
Scope: RTDL Phoenix V3 only. V4 not discussed.

Artifacts inspected:
- `docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.json`
- `tutorials/current/13_hausdorff_threshold_summary.md`
- `docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json` (targeted grep; file is 2.3 MB)
- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`
- `docs/reviews/external_review_blocked_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md`

---

## Verdict

**APPROVE_WITH_REQUIRED_FIXES**

One P1 fix is required before this packet can be considered a clean audit artifact. Two P2 findings are recommended. No P0 issues were found.

---

## Fact Verification

| Claimed fact | Verified? | Notes |
| --- | --- | --- |
| Status is `hausdorff_threshold_summary_boundary_not_m7` | YES | Present in both .md and .json |
| 262144-copy row: query OptiX/Embree = 1.864x | YES | .json: `1.8644032673876425`; summary.json grep confirms `optix_speedup_vs_embree: 1.8644032673876425` |
| 262144-copy row: wall OptiX/Embree = 1.258x | PARTIAL | .json: `1.2576431649500308`; consistent with stated Embree wall 21.594s / OptiX wall 17.170s; but wall field provenance in summary.json is not cited (see P1) |
| warmup=0, repeat=1 | YES | .json `best_current_row` and summary.json top-level `case_repeat: 1` both confirm single-run-only |
| All oracle fields true | YES | `matches_oracle`, `oracle_decision_matches`, `oracle_identity_matches`, `oracle_within_threshold` all `true` in .json |
| Claim is threshold decision only, not full Hausdorff witness | YES | `full_hausdorff_witness_claim_authorized: false` in .json; `threshold_decision_only_not_full_exact_hausdorff_witness` listed as blocker |
| RTX rerun not available; GTX 1070 cannot be RT-core M7 evidence | YES | `no_current_rtx_pod_rerun` blocker present; external review blocked file confirms |
| `m7_promotion_authorized: false` | YES | Present in all artifacts |
| `release_authorized: false` | YES | Present in all artifacts |

---

## Question-by-Question Assessment

### Q1: Is `hausdorff_threshold_summary_boundary_not_m7` still the correct classification?

**Yes. The classification is honest and accurate.**

The following blockers are real and none are resolved:

- `case_repeat: 1` at the top level of summary.json confirms that every benchmark in the calibrated run, including all three hausdorff_xhd threshold rows, was executed exactly once. There is no multi-run variance evidence for any scale.
- The 16384-copy and 65536-copy rows both show wall losses (0.657x and 0.965x respectively). Wall timing is genuinely mixed across scales. The 262144 row wins on wall but the capability as a whole cannot be characterized as delivering wall speedups.
- The threshold contract is a subproblem. Summary.json confirms the metric source is `run_phases.query_fixed_radius_threshold_reached_count_sec` and states `"public_boundary": "Decision subproblem only; not full exact Hausdorff witness materialization."` for all three rows.
- No external review was completed. The blocked-review file confirms that both the Claude and Gemini attempts failed at the tooling level and no verdict was obtained.
- The M7 classification packet dated 2026-06-20 listed all three hausdorff threshold rows as `not_m7_qualified` with blocker `no_focused_m7_packet`. The new packet replaces that placeholder with specific technical blockers, which is an improvement in precision, not a loosening.

No promotion is warranted. The classification stands.

### Q2: Are the new blockers `repeat1_no_multi_run_variance_evidence` and `no_current_rtx_pod_rerun` necessary and sufficient?

**Both are necessary. Together with the existing four blockers they are sufficient.**

`repeat1_no_multi_run_variance_evidence` directly closes the prior gap where `no_focused_m7_packet` was listed as the only blocker. Single-shot measurement creates real risk: a one-run result could reflect a scheduler artifact, thermal state, or initialization effect. This blocker is correctly named and correctly applied.

`no_current_rtx_pod_rerun` is necessary because the local machine is a GTX 1070, which lacks RT cores. A measurement run there would test BVH traversal on shader cores only and cannot serve as RT-core evidence for M7 promotion. This blocker prevents a future reviewer from assuming the calibrated run already constitutes an RTX validation.

One gap: neither the .md nor the .json explicitly states why the RTX pod matters in concrete terms (i.e., that the local machine lacks RT cores and that RT-core execution is a precondition for an M7 release row). The blocker name implies this but does not state it. This is a P2 issue, not a P1; the name is unambiguous enough for anyone reading the broader V3 context.

### Q3: Does the tutorial prevent users from reading the 262144 row as public speedup?

**Yes, effectively.**

The tutorial (`tutorials/current/13_hausdorff_threshold_summary.md`) does the following correctly:

1. Opens with "Status: V3 rebuild tutorial, not a release claim."
2. Shows both the query column and the wall column side by side. A reader cannot see 2.000x or 1.864x without also seeing 0.657x and 0.965x directly adjacent.
3. Explicitly states in prose: "The 262,144-copy row matches the deterministic threshold oracle, but it was measured with warmup=0 and repeat=1, so it remains a promising rebuild boundary row rather than an M7-qualified public result."
4. Has a Claim Boundary section with explicit forbidden wording, including "Do not claim Hausdorff V3 is 2x faster end to end."

One minor gap: the tutorial does not explain why `wall_timing_mixed_across_scales` is a systemic concern rather than a row-specific one. A reader who only sees the 262144 row in isolation might not understand that the smaller-scale wall regressions (0.657x) make a general `threshold_summary` wall claim impossible. This is P2; the tutorial is still effective at blocking misuse.

### Q4: Is any wording too weak or too strong?

**No wording is too strong. One wording gap is too weak (P2).**

The phrase "promising" applied to the 262144 row is accurate and not inflated. The row has query win + wall win at scale and oracle correctness across all four oracle fields. "Promising rebuild boundary row" is honest.

The `wall_timing_mixed_across_scales` blocker is listed alongside the 262144 row's individual data without any contextual sentence explaining why a scale-specific wall win does not resolve it. Since the 262144 row wins on wall (1.258x), a reader could reasonably ask how this blocker applies to that specific row. The answer is that you cannot claim `threshold_summary` generally delivers wall speedups when two of three tested scales show wall losses — but the packet does not say this. One sentence would close the gap.

The V2/V3 paired context (geomean 1.062x) is correctly framed as "modest V3-over-V2 context" and not broad speedup evidence. The framing is accurate; 6.2% over V2.14 as an app-level geomean does not support any release wording.

### Q5: Any hidden broad V3-over-V2, full-Hausdorff, or release claim leakage?

**None found.**

Checked each potential leak vector:

- `whole_app_speedup_claim_authorized: false` and `full_hausdorff_witness_claim_authorized: false` appear explicitly in the JSON.
- The exact-witness rows (`hausdorff_exact_witness_points_131072` and `hausdorff_exact_witness_points_32768`) are OptiX-only with no Embree comparison and are not included in the boundary packet table. They are correctly excluded from any ratio claim.
- The `forbidden_public_wording` array in the JSON matches the forbidden section in the .md and the tutorial. All three artifacts are aligned.
- The M7 packet (2026-06-20) lists `threshold_summary` as a "Next M7 Promotion Candidate" but the Must Fix conditions listed there (dedicated packet, row-level correctness proof, wall/hot methodology, external review) remain unmet. The new boundary packet does not accidentally satisfy them or claim they are met.
- The `public_speedup_claim_authorized: false` field appears on every individual hausdorff row in summary.json.

No leakage detected.

---

## Findings

### P1 — Wall Timing Field Provenance Not Cited

**File:** `docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md` and `.json`

The boundary packet states:

```
Embree wall: 21.594328731 s
OptiX wall:  17.170473576 s
Wall OptiX / Embree: 1.258x
```

These numbers are internally consistent (21.594 / 17.170 = 1.2576...) and the claim appears correct. However, summary.json's `cases` section only records `query_fixed_radius_threshold_reached_count_sec` (query phase times). The wall times must come from `wall_median_sec` fields in the `rows` section of summary.json, but the packet does not cite this source field.

The query:wall discrepancy for the 262144 row (query 1.864x, wall 1.258x) is a significant and important distinction — the smaller wall ratio reflects OptiX having higher setup cost. This distinction is a central part of the boundary analysis. The field provenance must be traceable.

**Required fix:** In the `best_current_row` section of the .json and the matching table in the .md, add the field source for wall times, e.g.:
```
embree_wall_sec source: rows[].wall_median_sec (full app wall, includes scene prepare + query)
optix_wall_sec source:  rows[].wall_median_sec (full app wall, includes scene prepare + query)
```
This closes the audit gap without changing any claimed numbers.

### P2 — `wall_timing_mixed_across_scales` Applicability Not Explained for 262144 Row

**File:** `docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md` (blockers section)

The blocker `wall_timing_mixed_across_scales` applies to the capability as a whole but the 262144 row wins on wall (1.258x). A reader seeing this blocker next to the 262144 row data could conclude the blocker is stale or inapplicable.

**Recommended fix:** Add one sentence under the blockers list:
```
Scale-specific wall win at 262,144 copies does not authorize a general
threshold_summary wall speedup claim; the 16,384-copy and 65,536-copy rows
show wall losses of 0.657x and 0.965x respectively.
```

### P2 — Dangling References in External Review Blocked File

**File:** `docs/reviews/external_review_blocked_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md`

This file references:
- `docs/reviews/call_for_review_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md`
- `docs/reviews/claude_attempt_blocked_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md`
- `docs/reviews/claude_attempt_blocked_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.stderr.txt`
- `docs/reviews/gemini_attempt_blocked_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md`
- `docs/reviews/gemini_attempt_blocked_phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.stderr.txt`

None of these files appear in the repository. The blocked-review file is correctly cautious in its verdict (no approval, no consensus) but the referenced artifacts do not exist. An auditor following the reference chain hits dead ends.

**Recommended fix:** Either create the referenced stub files with their known content (the tooling failure messages) or remove the specific file references and replace with a plain-text description of the failure mode.

---

## Promotion Decision for the 262144 Row

The question "can this row be promoted?" is answered by the blockers:

| Blocker | Resolved? |
| --- | --- |
| `threshold_decision_only_not_full_exact_hausdorff_witness` | No |
| `wall_timing_mixed_across_scales` | No — scale-local wall win is not global win |
| `repeat1_no_multi_run_variance_evidence` | No — `case_repeat: 1` confirmed in summary.json |
| `no_current_rtx_pod_rerun` | No |
| `no_focused_public_row_external_review` | No — review was blocked, not completed |
| `must_keep_threshold_scope` | No |

**The 262144 row cannot be promoted.** The row is promising and the query-phase speedup is real, but single-run measurement and no RTX rerun are absolute gates. Promoting a repeat=1 row to M7 would directly violate the methodology that produced the three existing M7-qualified rows.

---

## Bottom Line

The no-M7 classification is honest. The packet correctly captures the strongest available Hausdorff threshold signal, clearly separates query-phase and wall-phase results, and does not leak any release, broad V3-over-V2, or full-Hausdorff-witness claim. All seven authorization flags are `false` and internally consistent across the .md, .json, and tutorial.

One required fix (P1): Add the `wall_median_sec` field citation so the wall timing numbers in the best-current-row table are auditable without reading the full 2.3 MB source file.

Two recommended fixes (P2): Clarify `wall_timing_mixed_across_scales` applicability at the 262144 scale; resolve dangling references in the blocked-review file.

The packet may be used as a rebuild boundary lesson after the P1 fix. It must not be used as release evidence or M7 evidence regardless of fix status.
