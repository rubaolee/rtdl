# Claude Review: Phoenix V3 Spatial RayJoin M7 Feasibility Packet

Reviewer: Claude Sonnet 4.6  
Date: 2026-06-21  
Scope: V3 only. Artifacts reviewed from date 2026-06-20.

```text
VERDICT: APPROVE_WITH_REQUIRED_FIXES

P0 findings: 0
P1 findings: 1
P2 findings: 3
```

---

## Artifacts Reviewed

| File | Role |
| --- | --- |
| `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` | Primary feasibility packet |
| `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.json` | Machine-readable packet |
| `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md` | Underlying M5 evidence |
| `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md` | Row classification context |
| `docs/reviews/call_for_review_phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` | Call for review |
| `docs/reviews/external_review_blocked_phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` | External review blockage record |

---

## Question-by-Question Answers

### Q1. Is `spatial_rayjoin_m7_feasibility_not_promoted` correct?

**Yes. The classification is correct.**

Three independent gates each require non-promotion:

1. **Author-code gap.** RayJoin author RT is faster than RTDL OptiX on the M5 PIP row (5.728x wall, 3.861x native traversal). The packet discloses this prominently in the M5 Point-Location table (feasibility `.md` lines 93–95; JSON `rayjoin_rt_speedup_vs_rtdl_optix: 5.72759...`). Non-promotion is the only honest response to that gap.

2. **External review blocked.** Both the Claude and Gemini external review attempts failed for infrastructure reasons. The blockage document (`external_review_blocked_...`) records the precise error strings and correctly concludes that neither stdout file constitutes a review verdict. The JSON field `current_packet_external_review_status: blocked_current_packet` and `current_packet_2ai_consensus_status: not_recorded_for_this_packet` reflect this accurately.

3. **Row classification.** The M7 row classification packet independently marks all three `spatial_rayjoin` rows `not_m7_qualified` with `rayjoin_author_rt_faster_than_rtdl_optix` as the leading blocker. The feasibility packet is consistent with that independent record.

---

### Q2. Does the packet separate the four evidence categories?

**Yes, with one clarity gap (see P2-C below).**

| Category | How separated |
| --- | --- |
| Tiny route-health row | Named separately in "Tiny Negative Row" section; explicit `warmup=0, repeat=1`, `row_count=0` (overlay), labeled `non-claim`; forbidden from public use |
| Same-contract topology evidence | M5 PIP (1.920x wall, 2.834x native; 100k parity-filtered points, 1000 repeats) and overlay active-count (499x, 25 repeats) are each labeled "same-contract internal" and scoped to their output contracts |
| Authored hot-route evidence | Three tiled rows (30489x, 516x, 10.703x) explicitly labeled `internal_hot_route_not_m7` in both `.md` and JSON `classification` field |
| Author-code comparison | RayJoin `query_exec` timing (0.470 ms, C++ internal timer) is placed in the same table as RTDL OptiX timing and correctly noted as faster; the timing-basis caveat (C++ timer vs. Python `time.perf_counter`) is documented in the M5 evidence |

The separation is substantively complete. The one gap (P2-C) is that the authored hot-route rows are not pinned to a specific artifact or run path; they are attributed only to "the all-app calibrated route map" without a file path.

---

### Q3. Are any statements too strong for current evidence?

**No P0 or P1 overclaims found. One P2 wording note.**

The Verdict section (feasibility `.md` line 17) opens with:

> "Spatial RayJoin is one of the strongest Phoenix V3 internal topology-stream evidence families."

This is a relative internal ranking judgment, not a public performance claim, and all release/speedup flags are false. However, "strongest" is asserted without a comparative ranking across evidence families. It is defensible given the authored hot-route magnitudes, but a qualified phrase ("among the stronger") would be more precise. This is P2-A.

No other statements are too strong. The overlay 499x speedup is bounded to `overlay_active_pair_dependency_count` and the forbidden wording explicitly disallows whole-overlay and paper-section claims. The 30489x authored row is kept in the authored hot-route section and forbidden from public use without exact contract context.

---

### Q4. Are M7 blockers complete enough before any future public row promotion?

**Substantively complete. One required addition (P1).**

The eight blockers cover:

| Blocker | Adequacy |
| --- | --- |
| `rayjoin_author_rt_faster_than_rtdl_optix` | Correct; this is the leading content gate |
| `not_full_rayjoin_paper_reproduction` | Correct; overlay active-count ≠ Section 5.7 full reproduction |
| `not_full_polygon_overlay_or_materialization` | Correct; row materialization is excluded from timed path |
| `mixed_timing_basis_requires_public_methodology_review` | Correct; C++ timer vs. Python perf_counter is a real apples-to-apples gap |
| `m3_phase_table_gap_for_pip_before_public_row` | Correct; no build/traversal/continuation/host breakdown exists yet |
| `tiny_standard_row_is_negative_and_must_stay_explained` | Correct; prevents a future agent from citing 0.034x without context |
| `broad_v3_faster_than_v2_claim_authorized_false` | Correct |
| `no_public_row_level_release_review` | Correct but partial — see P1 below |

**P1 finding — missing explicit blocker for 2-AI consensus gap:**

The packet records `2ai_consensus_status: not_recorded_for_this_packet` in the status fields, but the M7 blockers list does not contain a named blocker for the absent 2-AI consensus. The existing `no_public_row_level_release_review` captures the row-promotion gate but could be read as applying only to the eventual public-row packet, not to the closure of this feasibility packet itself. Without a named blocker here, a future agent could mark all eight listed blockers resolved and treat the packet as closed while still lacking 2-AI consensus on the feasibility document. A ninth blocker should be added explicitly.

---

### Q5. Hidden release claim, broad V3-over-V2 claim, V4/ABI/embedding leakage, or paper-reproduction leakage?

**None found.**

| Check | Result |
| --- | --- |
| Hidden release claim | All five release/claim flags are false in both `.md` header and JSON root. The forbidden-public-reading field in JSON explicitly enumerates prohibited claims. No ambiguous affirmative language found. |
| Broad V3-over-V2 claim | `broad_v3_faster_than_v2_claim_authorized_false` is listed as both a M7 blocker and in the JSON `forbidden_public_reading`. No V2 comparison appears anywhere in the packet body. |
| V4 / C ABI / embedding leakage | None found. The packet is fully V3-scoped; no V4 symbols, ABI, or embedding language appear. |
| RayJoin paper-reproduction leakage | `paper_reproduction_claim_authorized: false` in both documents. The overlay active-count section explicitly states `rayjoin_section57_full_reproduction_claim_authorized: false` in the JSON. The `.md` Interpretation block (line 122–124) explicitly reads "not full polygon overlay and not RayJoin Section 5.7 reproduction." No paper claim is made anywhere. |
| Author-faster fact hidden | Disclosed. The PIP evidence table shows `RayJoin author RT: 5.728x faster than RTDL OptiX wall` and `3.861x faster than RTDL OptiX native traversal`. The goal-level audit (line 205–206) names hiding this fact as the canonical foolish action. No hiding detected. |

---

## Findings

### P1

**P1-A — Missing named blocker for 2-AI consensus gap**

Location: `phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` §M7 Blockers (lines 144–151); `phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.json` `m7_blockers` array.

The `2ai_consensus_status: not_recorded_for_this_packet` status field is present and correct, but the M7 blockers list does not contain a named item for this gap. A future reviewer checking only the blockers list could miss that 2-AI consensus has not been achieved for this feasibility document.

**Required fix:** Add `no_2ai_consensus_for_this_feasibility_packet` (or equivalent) as a ninth entry in the `m7_blockers` list in both the `.md` and `.json` files.

---

### P2

**P2-A — "Strongest" internal ranking is unqualified**

Location: `phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` line 17.

> "Spatial RayJoin is one of the strongest Phoenix V3 internal topology-stream evidence families"

The claim is defensible but the ranking across evidence families is not shown in this packet. Replacing "strongest" with "stronger" or adding "see M7 row classification packet for relative ranking" would be more precise.

**Suggested fix:** Qualify or remove the superlative, or cite the M7 classification packet as the source of the relative ranking.

---

**P2-B — Authored hot-route rows lack a pinned artifact path**

Location: `phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` §Strong Authored Hot-Route Rows (lines 130–138).

The three tiled rows (30489x, 516x, 10.703x) are attributed to "the all-app calibrated route map" but no file path or artifact label is given. If a future reviewer wants to verify these numbers or understand their provenance, they have no pointer.

**Suggested fix:** Add a table row or footnote with the route-map file path or artifact label from which these readings were taken.

---

**P2-C — Overlay active-count warmup/repeat count not stated in feasibility packet**

Location: `phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md` §Overlay Active-Count Evidence (lines 109–126).

The M5 evidence document records `warmup=2, repeat=25` for the overlay workload, versus `repeat=1000` for PIP. The feasibility packet does not state the overlay repeat count inline; a reader of the feasibility packet alone does not know the overlay timing is from 25 repeats rather than 1000. The `mixed_timing_basis_requires_public_methodology_review` blocker covers this at the blocker level but not at the table level.

**Suggested fix:** Add a row to the overlay evidence table listing `OptiX repeats: 25 / Embree repeats: 25` (or equivalent), mirroring the PIP section format.

---

## Required Fixes Before Closure

1. **(P1, required)** Add `no_2ai_consensus_for_this_feasibility_packet` to the M7 blockers list in both the `.md` and `.json` files.

---

## Bottom Line

The packet is honest and correctly classified. It prominently discloses the most critical fact — RayJoin author RT is faster than RTDL OptiX — keeps all release and public-claim flags false, properly documents the external review blockage rather than pretending consensus, and correctly separates the four evidence categories. The P1 finding is a named-blocker gap: the absent 2-AI consensus for this specific feasibility packet should appear as an explicit blocker rather than only in the status fields, so no future agent can declare the packet closed without satisfying that gate. The three P2 findings are precision improvements, not honesty failures. The packet may be closed after the P1 fix is applied and after 2-AI consensus is recorded for this packet.
