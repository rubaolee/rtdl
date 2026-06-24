# External Review - Goals4148-4151 RT-DBSCAN Single-Pass Direct-Status Candidate

Date: 2026-06-09
Reviewer: Gemini CLI
Verdict: accept-with-boundary

## Summary

This review covers the introduction of the `single_pass_candidate` convergence mode for the RT-DBSCAN prepared direct-status component-signature path. The implementation allows for an explicit one-pass execution of the union-find logic, which provides a significant speedup (approx. 2x) in the hot replay path by skipping the second "no-change" iteration used for convergence proof.

## Research & Verification

1.  **Implementation Verification**:
    - Checked `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`.
    - Confirmed `convergence_mode` defaults to `"until_stable"`.
    - Confirmed `"single_pass_candidate"` limits the loop to 1 iteration and sets `convergence_proven` to `False`.
    - Metadata correctly captures `final_changed_flag` (which is `1` for the candidate).

2.  **Benchmark & Interpretation**:
    - Reviewed Goal4149 (1M points) and Goal4150 (scale sweep) reports.
    - Verified same-signature parity across `clustered3d`, `road3d`, and `ngsim_dense` profiles.
    - Confirmed replay speedups are consistently around 2.0x.
    - The interpretation correctly acknowledges that this is empirical parity, not a universal convergence theorem.

3.  **Advisor Metadata**:
    - Verified `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`.
    - The advisor correctly surfaces the single-pass option as an explicit user-selected candidate with attached evidence refs and speedup metrics.
    - `single_pass_promoted_default` remains `False`.
    - No hidden dispatch or automatic selection was introduced.

4.  **Testing**:
    - Executed `tests/goal4148_...` through `tests/goal4151_...`.
    - All 17 tests passed.

## Responses to handoff questions

1.  **Does the implementation preserve the stable default and keep `single_pass_candidate` explicitly user-selected?**
    - Yes. The default in both the runtime and the advisor is `until_stable`.

2.  **Are the pod results correctly interpreted?**
    - Yes. The reports emphasize same-signature parity on specific profiles and the lack of a universal convergence proof (`final_changed_flag == 1`).

3.  **Does Goal4151 expose useful advisor metadata without creating hidden dispatch?**
    - Yes. The metadata is informative and keeps the choice explicit.

4.  **Are there any correctness risks?**
    - The risk is limited to datasets not yet tested. The boundary is clear: this is a candidate for measured/verified packets, not a general-purpose replacement for the stable loop.

## Boundary & Claims

- **Accept-with-boundary**: The boundary is strictly defined by the lack of a universal convergence proof. The candidate is only verified for the measured scales and profiles.
- **Blocked Claims**: This review does NOT authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper reproduction, hidden dispatch, automatic partner selection, automatic partition-cell-factor selection, automatic convergence-mode selection, app-specific engine logic, native ABI additions, AMD claims, or true-zero-copy claims.
