# Claude External Review: Phoenix V3 Phase A Performance-Source Verdict

Date: 2026-06-24
Reviewer: Antigravity (independent external review)
Candidate packet: [call_for_review_phoenix_v3_phase_a_performance_source_no_go_2026-06-24.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_phoenix_v3_phase_a_performance_source_no_go_2026-06-24.md)

---

## Verdict

**`accept_phase_a_no_go_enter_phase_h_capability_quality`**

Phase A has honestly failed to prove a V3 performance source under Claude's A-H roadmap and the Goal 0 anti-avoidance lock. The project must now bypass further Phase A candidate searches and enter Phase H capability/quality release planning.

---

## Analysis of Evidence

### 1. Barnes-Hut Goal 0 Result
- **Trunk Validation**: Successfully verified (`runtime_executed: true`, internal device residency holding, and correctness parity verified on focused evidence).
- **Performance**: The optimization path achieved a geomean improvement of only `~0.9526x`, which failed to cross the `0.98x` parity gate, the `1.00x` legacy V2.14 parity gate, and the `1.20x` Set-A performance bar.
- **Classification**: Reclassified as a backend-bound trunk proof/control row. Because the execution time is dominated by the shared RT traversal and force CUDA/OptiX kernels rather than trunk-removable overheads, further tuning is locked out to prevent tuning-spiral avoidance.

### 2. RTNN Reselected Candidate Result
- **Lock Conformance**: Conforms to the requirements of the reselection anti-avoidance lock.
- **Trunk Validation**: The productized session runner executes end-to-end with zero failed checks and verified correctness parity against the legacy same-contract OptiX path.
- **Performance**:
  - Hot query speedup: `0.9956x`
  - Runner-wall speedup: `1.0385x`
  - Projected frozen OptiX scorecard row speedup: `1.0362x`
- **Triage**: Although the cold+query submetric is strong (`1.58x`), using it to bypass the frozen scorecard-bound row targets constitutes metric shopping. The primary same-contract runner wall speedup misses the `>=1.20x` threshold by a wide margin.

### 3. Anti-Avoidance Lock and "No Third Search"
- Under both Claude's Goal 0 verdict and the RTNN candidate lock, any failure of the reselected family to cross the `1.20x` runtime-sourced performance bar with correctness parity is a decisive exit trigger.
- Searching for a third winner is explicitly forbidden. Continuing to search other families (such as Triangle or RayDB) would violate the anti-avoidance lock and constitute metric shopping.

---

## Answers to Reviewer Questions

1. **Do you agree that Phase A's performance-source exit gate is not met?**
   - **Yes.** Neither the primary Barnes-Hut workload nor the reselected RTNN candidate moved their respective scorecard blocker rows to the required `>=1.20x` runtime-sourced performance threshold.
2. **Do you agree that Barnes-Hut is closed as trunk proof/control and should not receive more tuning?**
   - **Yes.** Barnes-Hut is backend-bound (the runtime overhead elimination is fully applied, and the bottleneck lies in the shared kernels). No further tuning is allowed.
3. **Do you agree that the RTNN result proves execution/parity but misses the scorecard-bound `>=1.20x` performance-source bar?**
   - **Yes.** Parity holds and the runner executes correctly, but the same-contract scorecard row projection of `1.036x` misses the `1.20x` performance-source bar.
4. **Do you agree that searching for a third winner is forbidden by the anti-avoidance lock?**
   - **Yes.** resubmitting or selecting another family is locked out by the "no third search" kill condition.
5. **Should Phoenix V3 now enter Phase H capability/quality release planning, with no broad V3-over-V2 speedup claim?**
   - **Yes.** Reframing Phoenix V3 as a capability/quality release is the honest, evidence-supported path.
6. **Are there any concrete, non-metric-shopping grounds to keep Phase A open?**
   - **No.** The kill conditions have been met, and no further candidate search is authorized.

---

## Preservation of Non-Authorization

As mandated by this review, the following conditions remain strictly locked and unauthorized:
- **No V3 release** is authorized.
- **No all-app benchmark** run or POD spend is authorized.
- **No public speedup wording** or broad V3-over-V2 performance claims are authorized.
- **No V4**, embedding, C ABI, or external zero-copy claims are authorized.
- **No further Phase A candidate searches** are permitted.

The project enters Phase H capability/quality release planning.
