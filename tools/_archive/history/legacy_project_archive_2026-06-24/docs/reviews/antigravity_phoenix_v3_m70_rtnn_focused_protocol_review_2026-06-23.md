# Antigravity Review: Phoenix V3 M70 RTNN Focused Protocol Draft

**Date:** 2026-06-23  
**Reviewer:** Antigravity AI (independent external review)  
**Call for Review:** [call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md)  
**Candidate Protocol Draft:** [phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md)  
**Candidate Protocol JSON:** [phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json)  
**Candidate Protocol Report:** [phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reports/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md)  
**Gate Test Suite:** [v3_phoenix_m70_rtnn_focused_protocol_gate_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py)  

---

## Verdict

```text
accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod
```

This review accepts the Phoenix V3 M70 RTNN focused protocol draft. The draft correctly carries forward all constraints from the M69 consensus, provides explicit shape lists and same-contract incumbents, enforces proper phase metric separations, and defines robust stop conditions. Acceptance is for the protocol draft only, authorizing no benchmark execution, release action, or POD spend.

---

## P0 / P1 / P2 Findings

### P0 Findings
**None.**  
All documents reconcile perfectly. The machine-readable JSON aligns exactly with the Markdown specification and report. Gate tests in [v3_phoenix_m70_rtnn_focused_protocol_gate_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py) run and pass successfully, confirming that the schema checks and non-authorization boundaries are fully locked down.

### P1 Findings
*   **P1-A: Real App-Win Gap is Still Active:** The frozen all-app scorecard indicates that 13 out of 14 RTNN rows and 6 out of 7 shape groups sit below the performance exit criterion of `1.05x` (with an overall geomean of `1.003327x` for the RTNN family). The RTNN is bridged as a data-compatible candidate but has not exited the performance gate.
*   **P1-B: Steady-State Hot-Query Regressions:** The steady-state query itself shows a minor regression of `0.988781x` vs legacy. Any runner-wall improvement is entirely due to data packing consolidation and execution-prepare amortization. This boundary must remain visible, preventing any whole-app or steady-state speedup claims.

### P2 Findings
*   **P2-A: Self-Query Batching Limit:** The productized runner mode [prepared_execution_ranked_summary](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py#L437) restricts queries to full-batch self-queries (`query_batch_size == point_count`). Alternate configurations are unsupported under this protocol.
*   **P2-B: Single-Distribution Phase Split:** The M69 repeat50 phase attribution (`32.3%` input packing, `67.7%` runner-after-pack) is validated for the uniform distribution only. Clustered and shell distributions must establish independent phase measurements before their performance can be verified.

---

## Direct Answers to Review Questions

### 1. Does M70 name all exact frozen RTNN shapes and same-contract incumbents?
**Yes.**  
Section "Frozen Shapes" of [phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md) names all 7 frozen shape groups and all 14 rows across the `uniform`, `clustered`, and `shell` distributions. Section "Same-Contract Incumbents" explicitly pairs each row with its exact counterpart (either `frozen_v2_14_embree_ranked_summary_row` for Embree or `legacy_app_front_door_prepared_optix_ranked_summary` for OptiX) and defines identical contract parameters (`point_count`, `distribution`, radius, k, and query batch size constraints) in both Markdown and JSON representation.

### 2. Does it correctly carry the M69 boundary that repeat50 phase evidence is uniform-distribution only?
**Yes.**  
Section "M69 Carry-Forward" explicitly lists `repeat50 phase attribution is uniform-distribution evidence only`. This is further reinforced in the "Phase Metric Contract" section (which designates the M69 reference as uniform-distribution only) and in the stop conditions, which abort the protocol if non-uniform distributions attempt to reuse this phase split without distinct measurements.

### 3. Does it require per-distribution phase bounds before clustered or shell shapes are used?
**Yes.**  
The protocol MD tables and JSON fields tag clustered and shell shapes with `per_distribution_phase_bound_required: true` (while uniform shapes are `false`). The stop conditions explicitly halt execution if clustered or shell shapes are evaluated using extrapolated uniform metrics.

### 4. Does it preserve the full-batch self-query constraint?
**Yes.**  
The protocol details that the productized runner mode `prepared_execution_ranked_summary` requires full-batch self-queries. In the JSON packet, all shape objects specify `"query_role": "full_batch_self_query"`, and a stop condition explicitly triggers if non-self-query batches are proposed without a separate code-path review.

### 5. Are hot-query, runner-wall, prepare, and input-loading/packing metrics separated strongly enough?
**Yes.**  
The "Phase Metric Contract" section defines 10 individual metrics (such as `input_load_sec`, `input_pack_sec`, `execution_prepare_sec`, `runner_after_input_load_pack_sec`, `hot_query_median_sec`, and `runner_wall_sec`) that must remain separate. A dedicated stop condition halts execution if any of these metrics are merged, and the gate test validates this separation constraint.

### 6. Are the stop conditions enough to prevent RTNN app tuning, repeat50 overclaiming, and contract mixing?
**Yes.**  
The 9 stop conditions defined in M70 are highly comprehensive and fail-closed:
*   **App Tuning Prevention:** Aborts if any route-specific app tuning appears, or if productized metadata does not show `runtime_trunk_executes_end_to_end=true` with `prepared_execution_session_runner`.
*   **Repeat50 Overclaiming Prevention:** Aborts if runner-wall gains are purely due to input pack consolidation or repeat50 amortization with zero steady-state runner-after-pack contribution.
*   **Contract Mixing Prevention:** Aborts if different contracts (e.g. aggregate vs raw vs partner bridge) are merged into a single speedup claim, or if a shape lacks its exact same-contract incumbent row.

### 7. Is M71 local harness design/dry-run gate the right next step, with no POD and no runbook execution?
**Yes.**  
Continuing to M71 for local harness design and a dry-run gate (verifying execution paths and checking telemetry formats locally) is the correct incremental path. It allows validation of the harness code while maintaining the sandbox boundaries by explicitly forbidding runbook execution, all-app benchmarks, and paid/focused POD spend.

### 8. Are any non-authorization boundaries weakened?
**No.**  
All 14 non-authorization items listed in the M69 consensus are fully preserved, word-for-word, in the M70 protocol draft, report, and gate tests. The non-authorization block is carried forward in its entirety with no modifications or weakening.

---

## Carry-Forward Requirements for M71

Any local harness designed or dry-run gate built in M71 must enforce the following requirements:

1.  **Dry-Run Validation Only:** The harness must restrict its operations to schema validation, telemetry layout verification, and configuration dry-runs. It must execute no actual benchmark runs on live clusters or hardware.
2.  **Telemetry Phase Isolation:** The harness must output separate fields for all 10 defined metrics (`input_load_sec`, `input_pack_sec`, `input_load_pack_sec`, `execution_prepare_sec`, `runner_after_input_load_pack_sec`, `hot_query_median_sec`, `runner_wall_sec`, `measured_total_sec`, `measured_median_sec`, and `signature_match_status`) and must fail-closed if any metrics are merged or missing.
3.  **Strict Productized Path Check:** The harness must verify that the target executable uses [run_fixed_radius_ranked_summary_3d_prepared_session](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/prepared_execution.py#L855) through the productized [prepared_execution_ranked_summary](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py#L437) runner, ensuring `runtime_trunk_executes_end_to_end=true` and that no route-specific tuning or mock pathways are active.
4.  **Batch Constraint Enforcement:** The harness must raise an error and halt if the input query batch size deviates from the point count (`query_batch_size != point_count`), maintaining the full-batch self-query constraint.
5.  **Per-Distribution Setup:** The harness must support individual phase boundaries for the `uniform`, `clustered`, and `shell` distributions, preventing clustered/shell execution logic from reusing uniform-distribution timing profiles.

---

## Explicit Non-Authorization Block

> [!IMPORTANT]
> This review carries an explicit non-authorization block:
> No V3 release, no all-app benchmark run, no POD spend, no paid POD spend, no focused POD spend, no runbook execution, no public speedup wording, no broad V3-over-V2 claim, no whole-app speedup claim, no paper reproduction claim, no RT-core speedup claim, no automatic partner selection, no route-specific RTNN app tuning, and no watch-row closure.
