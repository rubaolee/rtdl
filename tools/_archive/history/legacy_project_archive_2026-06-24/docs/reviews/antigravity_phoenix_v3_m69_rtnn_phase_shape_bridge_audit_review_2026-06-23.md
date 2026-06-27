# Antigravity Review: Phoenix V3 M69 RTNN Phase/Shape Bridge Audit

**Date:** 2026-06-23  
**Reviewer:** Antigravity AI (independent external review)  
**Call for Review:** [call_for_review_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md)  
**Candidate Report:** [phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reports/phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md)  
**Machine-Readable Packet:** [phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.json)  
**Frozen Set-A/B Scorecard:** [phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json)  
**Repeat50 Evidence:** [summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/summary.json)  

---

## Verdict

```text
accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release
```

This review accepts the M69 local RTNN phase/shape bridge audit. The shape configurations of all 14 frozen Set-A RTNN rows map to the generic runner surface, and the phase attribution mathematically and honestly isolates the input-packing and session-setup effects from the steady-state execution phase. However, because the frozen scorecard shows a persistent app-win gap and the performance is entirely due to amortization rather than hot-query speedup, **no release, runbook execution, or POD spend is authorized by this verdict.**

---

## P0 Findings

**None.**  
The data, timings, and classifications reported in the candidate packet reconcile perfectly with the repeat50 execution logs and frozen Set-A/B scorecard. No correctness regressions or overclaims were detected in the audit documents.

---

## P1 Findings

### P1-A: Real App-Win Gap Remains on Frozen Scorecard
The frozen all-app scorecard indicates that 13 out of 14 RTNN rows and 6 out of 7 shape groups remain below the target threshold of `1.05x`. The overall geomean speedup for the RTNN family is `1.003327x`. RTNN is approved as a *shape bridge candidate* only, meaning its data formats are compatible with the generic runner surface. It does not exit the performance gate, and no public or release promotion is allowed on this basis.

### P1-B: Lack of Hot-Query Speedup
Phase attribution confirms that the steady-state hot-query speedup vs legacy is `0.988781x` (a minor performance regression). The entire speedup observed in the repeat50 run is due to data packing consolidation and execution-prepare amortization. Any future milestone protocol must keep hot-query, runner-wall, prepare, and input-packing metrics strictly separated.

---

## P2 Findings

### P2-A: Full-Batch Self-Query Constraint
The productized runner mode `prepared_execution_ranked_summary` currently requires full-batch self-queries (`query_batch_size == point_count`). This constraint separates it from general runtime front doors that allow arbitrary query batching.

### P2-B: Amortization Dependency
The positive performance signal is only present under `repeat50` conditions, relying on session reuse to amortize compile and setup overhead.

---

## Evidence Notes

### Arithmetic Reconciliations
All timing and speedup values match the raw data in the [repeat50 summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/summary.json):

*   **Total Runner-Wall Delta:** `3.208734s` (legacy) - `2.341841s` (runner) = `0.866893s`
*   **Input Load/Pack Delta:** `1.995450s` (legacy) - `1.715503s` (runner) = `0.279946s`
    *   *Share of Delta:* `0.279946s / 0.866893s = 0.32293` (~`32.3%`)
*   **Runner-After-Pack Delta:** `1.213284s` (legacy) - `0.626317s` (runner) = `0.586967s`
    *   *Share of Delta:* `0.586967s / 0.866893s = 0.67709` (~`67.7%`)
*   **Execution Prepare Delta:** `0.409430s` (legacy) - `0.052025s` (runner) = `0.357405s`
*   **Hot-Query Speedup:** `0.010689s` (legacy median) / `0.010810s` (runner median) = `0.988781x` (no speedup)

These values verify that data handling and session setup are the sole sources of the runner-wall delta.

---

## Answers to Review Questions

### 1. Is M69 correct that RTNN is bridgeable to the generic fixed_radius_ranked_summary_3d_prepared_session runner surface?
Yes. The 14 frozen Set-A RTNN rows map to the generic [run_fixed_radius_ranked_summary_3d_prepared_session](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/prepared_execution.py#L855) runner in [prepared_execution.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/prepared_execution.py). The benchmark application [rtdl_rtnn_benchmark_app.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py) successfully targets this productized session runner.

### 2. Is the phase attribution correct and sufficiently honest: input load/pack is about 32.3% of the runner-wall delta, runner-after-pack is about 67.7%, and hot-query speedup is not the material source?
Yes. The phase attribution is correct and honest. It accurately separates data packing and structure build overheads, demonstrating that the steady-state query itself shows no performance improvement (`0.988781x`).

### 3. Does M69 correctly identify that the current front door uses prepared_optix_ranked_summary, while the productized runner mode exists separately as prepared_execution_ranked_summary?
Yes. The benchmark application exposes two separate paths:
*   Legacy front door: [rtnn_prepared_optix_ranked_summary_payload](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py#L285)
*   Productized runner mode: [rtnn_prepared_execution_ranked_summary_payload](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py#L437)

### 4. Is the next recommendation right: M70 may draft a reviewed focused protocol with no execution, but M69 itself authorizes no runbook, no POD, no all-app, and no public claims?
Yes. Limiting the M70 recommendation to drafting a focused protocol (without execution or spend authorization) is the correct path. It prevents unreviewed performance claims while keeping development within local-only boundaries.

### 5. Are the stop conditions sufficient to prevent RTNN app-specific tuning, repeat50 overclaiming, and mixing exact aggregate / productized runner / graph partner bridge contracts into one public claim?
Yes. The stop conditions in the report and JSON prevent:
1. App-specific native logic tuning.
2. Amortization overclaiming without a shape bridge.
3. Mixing differing query contracts into one public speedup claim.

### 6. Are the non-authorization boundaries complete?
Yes. The non-authorization boundaries are complete and prevent any release or public-facing claims.

---

## Non-Authorization Boundaries

> [!IMPORTANT]
> This review does NOT authorize:
> *   No V3 release
> *   No all-app benchmark runs
> *   No POD spend
> *   No paid/focused POD spend
> *   No runbook execution
> *   No public speedup wording
> *   No broad V3-over-V2 claims
> *   No whole-app or paper reproduction claims
> *   No RT-core speedup claims
> *   No automatic partner selection
> *   No route-specific RTNN app tuning
> *   No watch-row closure

---

## Recommendation

1.  **Proceed to M70 protocol drafting only.** The next milestone (M70) may draft a focused execution protocol detailing the same-contract incumbents and exact shapes, but must contain no runbook execution.
2.  **Maintain strict phase separation.** Any future test protocol must keep loading, packing, session-prepare, and hot-query execution times isolated.
3.  **Do not close the RTNN watch-row.** RTNN remains below the `1.05x` performance exit criteria on the frozen scorecard.
