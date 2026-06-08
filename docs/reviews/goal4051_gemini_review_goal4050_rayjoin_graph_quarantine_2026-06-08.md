# Independent Gemini Review for Goal4050 RayJoin Graph Quarantine

**Date:** 2026-06-08

**Reviewer:** Gemini CLI Agent

## Overall Verdict: `accept-with-boundary`

The artifacts for Goal4050 clearly document a critical issue with the prepared-points CUDA graph replay lane in RayJoin-style PIP paths, exhibiting `OptiX error: CUDA error` during graph preparation. The accompanying report and code updates appropriately quarantine this problematic lane, while reaffirming the functionality and recommendation of the working single prepared point/closed-shape count and prepared batch-count executor lanes.

The "boundary" aspect is precisely the quarantining of the CUDA graph replay, which is effectively removed from recommended performance pathways until a fundamental fix for the OptiX/CUDA capture error is implemented.

## Required Checks Summary

1.  **Verify that Goal4050 does not overclaim:** **PASS**. The report (`docs/reports/goal4050_rayjoin_pip_graph_replay_quarantine_2026-06-08.md`), artifact (`docs/reports/goal4050_rayjoin_pip_graph_current_negative_probe_pod.json`), and code (`src/rtdsl/current_benchmark_route_decisions.py`, `src/rtdsl/v2_9_benchmark_adequacy.py`) consistently and explicitly state that Goal4050 does not authorize any release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core, true-zero-copy, or automatic partner/backend-selection claims. All claim-boundary flags within the JSON artifact are set to `false`, and programmatic checks exist to enforce this.

2.  **Verify the route decision is technically sensible:** **PASS**. The decision to quarantine the prepared-points CUDA graph replay is well-supported by evidence of consistent `OptiX error: CUDA error` failures, both with and without validation. The report explicitly states that this path is unusable. Conversely, the continued recommendation of the working batch executor and scalar-count executor lanes is sensible, as these are consistently shown to return correct counts. The `current_benchmark_route_decisions.py` and `v2_9_benchmark_adequacy.py` files reflect this quarantine in their `rejected_or_unpromoted_candidates` and `next_runtime_action` fields for `spatial_rayjoin`.

3.  **Verify the artifact is internally consistent:** **PASS**. The `goal4050_rayjoin_pip_graph_current_negative_probe_pod.json` artifact accurately records the expected counts for the single (`6`), batch (`[6, 6, 6, 6, 6]`), and batch executor (`[6, 6, 6, 6, 6]`) lanes. It also correctly reflects the `failed_closed` status and `OptiX error: CUDA error` for both `graph_validated` and `graph_raw` entries. All `claim_boundary` flags are `false`, consistent with the report.

4.  **Verify the tests cover the regression boundary without requiring hidden app semantics or app-specific native engine logic:** **PASS**. The `tests/goal4050_rayjoin_pip_graph_replay_quarantine_test.py` validates the numerical consistency of the artifact, the correct integration of the quarantine decision into the `rtdsl` route guidance modules, and the proper documentation of the quarantine in the Markdown report. These tests focus on verifiable outputs and published guidance, avoiding reliance on obscure internal application details.

5.  **State whether the verdict is `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`, and list any required fixes before this route guidance can be used:** **`accept-with-boundary`**.
    *   **Verdict:** `accept-with-boundary`
    *   **Required fixes:** None. The route guidance itself is to quarantine and explicitly not use the failing graph replay path. The documentation, code, and tests are aligned with this decision. The goal has successfully identified and isolated a non-viable path.

## Conclusion

Goal4050 effectively addresses the identified issue with the RayJoin prepared-points CUDA graph replay. The documentation and code changes clearly reflect the quarantine of this path and reinforce the use of stable, working alternatives. No further fixes are required for this route guidance to be considered valid and actionable.
