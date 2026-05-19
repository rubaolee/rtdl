# Independent Gemini Review: Goal2435 RT-DBSCAN Single-Pass Chunked Adjacency

**Date:** 2026-05-19

**Reviewer:** Gemini

## Overview

This review covers Goal2435, which refactors the chunked adjacency continuation introduced in Goal2433. Specifically, Goal2435 aims to remove the redundant second Ray Tracing (RT) adjacency fill by capturing core-neighbor candidates for border points during the initial union pass. The goal is to improve the efficiency of the memory-bounded chunked path while preserving the generic nature of the component labeling.

## Review Questions

### 1. Is the single-pass border-candidate algorithm correct for generic fixed-radius component labels?

**Finding:** Yes, the single-pass border-candidate algorithm appears correct for generic fixed-radius component labels.

*   The `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_2026-05-19.md` report explicitly states, "The single-pass chunked continuation is correct."
*   Pod evidence from `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_pod/tiny_app.json` shows `matches_reference: true` and correct edge counts, confirming exact correctness for a small fixture.
*   Larger `clustered4096_repeat.json`, `clustered8192_repeat.json`, and `clustered32768_chunked.json` artifacts all report `signatures_match: true`, indicating consistent results with established signatures.
*   The algorithm is described as "still generic radius-graph component labeling," indicating no deviation from the generic contract.

### 2. Does it preserve the app-agnostic boundary and avoid DBSCAN-native engine logic?

**Finding:** Yes, Goal2435 successfully preserves the app-agnostic boundary and avoids introducing DBSCAN-native engine logic.

*   The report clearly states, "This is still generic radius-graph component labeling. No DBSCAN-native engine ABI was added."
*   The changes in `src/rtdsl/partner_adapters.py` introduce two new CuPy kernels (`radius_graph_3d_chunk_adjacency_union_border_candidate_kernel` and `radius_graph_3d_border_candidate_label_kernel`) that are generic in their function, not specific to DBSCAN.
*   The `examples/v2_0/research_benchmarks/rt_dbscan/README.md` and `docs/research/future_version_to_do_list.md` consistently reinforce the project's claim boundaries, explicitly stating that no DBSCAN-specific native ABI is added.

### 3. Do the report and README honestly state that this is a memory/continuation improvement, not a broad speedup claim?

**Finding:** Yes, the report and README honestly and consistently state the nature of this improvement.

*   The `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_2026-05-19.md` explicitly notes: "Its value is bounded memory, not raw speed." and "It does not authorize a broad RT-core speedup claim, a DBSCAN paper-reproduction claim, or a release claim."
*   The performance snapshot in the report accurately shows improvements over the Goal2433 chunked path but also clarifies that it "remains slower than full adjacency when full adjacency fits."
*   The `examples/v2_0/research_benchmarks/rt_dbscan/README.md` also includes a "Claim Boundary" section that disclaims broad speedup or paper reproduction claims.
*   The `docs/research/future_version_to_do_list.md` also aligns with this, discussing that Goal2435 improved the chunked path but it remains slower than full adjacency.

### 4. Are the tests and artifacts enough for an `accept-with-boundary` verdict, or is more pod evidence needed?

**Finding:** Yes, the tests and artifacts provided are sufficient for an `accept-with-boundary` verdict.

*   The `tests/goal2435_rt_dbscan_single_pass_chunked_adjacency_test.py` thoroughly verifies the integration of the new kernels, the `adjacency_write_pass_count: 1` metadata, the presence of boundary-bounding statements in the report and README, and crucially, the correctness via `tiny_app.json` and performance improvement over Goal2433 via median `outer_elapsed_sec` comparisons for clustered repeat probes.
*   The `clustered32768_chunked.json` artifact provides evidence for larger, chunked datasets.
*   The report itself concludes with an `accept-with-boundary` verdict, which is well-supported by the evidence presented.

## Conclusion

Goal2435 successfully refines the memory-bounded chunked adjacency continuation by eliminating a redundant RT adjacency fill. This change improves the efficiency of the chunked path while strictly maintaining the app-agnostic native-engine boundary. The documentation is transparent about the scope and limitations of the improvement, clearly stating its primary value lies in bounded memory rather than raw speed comparable to full adjacency when memory is not a constraint. The provided tests and artifacts adequately demonstrate correctness and performance gains over the previous iteration.

## Verdict

`accept-with-boundary`
