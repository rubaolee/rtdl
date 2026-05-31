# Gemini Review for Goal2825 CUDA Graph Replay

Date: 2026-05-31

Verdict: `accept-with-boundary`

## Findings and Answers to Review Questions

### 1. Does Goal2825 keep the native engine app-agnostic, with no RTNN-specific native ABI or app-shaped continuation?

**Yes.** The native engine remains app-agnostic.
*   The new functions and structures introduced in `src/native/optix/rtdl_optix_workloads.cpp` and exposed through `src/native/optix/rtdl_optix_api.cpp` use generic terminology like "fixed-radius ranked summary aggregate batch graph 3d" rather than "RTNN".
*   The test `tests/goal2825_rtnn_cuda_graph_replay_prepared_batch_test.py` explicitly validates that no "rtnn" (case-insensitive) token is present in the native source files related to this feature.
*   The `docs/reports/goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md` report confirms this in its "Implementation Details".

### 2. Is CUDA graph replay exposed as an explicit opt-in handle rather than an invisible default behavior change?

**Yes.** CUDA graph replay is implemented as an explicit opt-in mechanism.
*   The `src/native/optix/rtdl_optix_api.cpp` file exposes distinct API functions: `rtdl_optix_prepare_fixed_radius_ranked_summary_aggregate_batch_graph_3d`, `rtdl_optix_replay_fixed_radius_ranked_summary_aggregate_batch_graph_3d`, and `rtdl_optix_destroy_fixed_radius_ranked_summary_aggregate_batch_graph_3d`. These must be called explicitly by the user.
*   The Python wrapper in `src/rtdsl/optix_runtime.py` defines `PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D` with clear `prepare` and `replay` methods, requiring explicit invocation.
*   The report `docs/reports/goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md` explicitly states this.

### 3. Does the report correctly bound the evidence to static prepared fixed-radius ranked-summary aggregate batches?

**Yes.** The evidence is appropriately bounded.
*   The title of the primary report, `docs/reports/goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md`, and its "Claim Boundary" section clearly define the scope.
*   The `docs/reports/goal2825_rtnn_cuda_graph_replay_pod/goal2825_summary.json` includes the flag `"prepared_static_cuda_graph_replay_probe": true`, reinforcing the static and prepared nature of the graph replay.
*   The `scripts/goal2348_rtnn_v2_2_external_runner.py` script specifically configures runs for this feature using `result_mode="ranked-summary-aggregate-prepared-query-batch-graph-float32"`.

### 4. Are the pod results correctly interpreted, including exact normalized aggregate parity and the modest 1.156x / 1.026x graph-vs-fused replay speedups?

**Yes.** The pod results are correctly interpreted and reported.
*   The `docs/reports/goal2825_rtnn_cuda_graph_replay_pod/goal2825_summary.json` shows `"same_ranked_aggregate_batch_summaries_normalized": true`, confirming parity.
*   The speedup values of 1.156x and 1.026x are directly from the `goal2825_summary.json` fields `speedup_graph_replay_vs_fused_normalized_min: 1.026` and `speedup_graph_replay_vs_fused_normalized_max: 1.156`, which are summarized as "modest 1.156x / 1.026x" in the main report. This accurately reflects the measured gains.

### 5. Does the claim boundary remain strict: no public RTDL-beats-CuPy, RTDL-beats-RTNN-paper, broad RT-core, whole-app speedup, or v2.5 release claim?

**Yes.** The claim boundary is strictly maintained.
*   The `docs/reports/goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md` report explicitly lists all these exclusions in its "Claim Boundary" section.
*   The `docs/reports/goal2825_rtnn_cuda_graph_replay_pod/goal2825_summary.json` contains corresponding `false` flags for all these claims (e.g., `"public_speedup_claim_authorized": false`, `"rtnn_paper_reproduction_claim_authorized": false`, `"whole_app_speedup_claim_authorized": false`, `"v2_5_release_authorized": false`).
*   The external runner `scripts/goal2348_rtnn_v2_2_external_runner.py` also sets relevant flags in its `claim_boundary` to `False` for RTDL runs to prevent overclaiming.

### 6. Is the next-step recommendation reasonable: event-ordered partner chaining or graph-node update support, rather than another single-kernel micro-reduction?

**Yes.** The next-step recommendation is reasonable and aligns with project goals.
*   The "Next Steps" section in `docs/reports/goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md` clearly outlines "event-ordered chaining from this prepared aggregate path into partner consumers, or graph-node update support" and explicitly states this "is in line with the policy against single-kernel micro-reductions". This demonstrates a strategic approach to further development beyond isolated optimizations.

## Conclusion

Goal2825 successfully integrates CUDA Graph Replay for fixed-radius ranked-summary aggregate batches while adhering to all specified boundaries and architectural principles. The implementation is app-agnostic, explicitly opt-in, and the performance gains are accurately measured and reported without overstating claims. The proposed next steps demonstrate a clear and reasonable path for future enhancements.
