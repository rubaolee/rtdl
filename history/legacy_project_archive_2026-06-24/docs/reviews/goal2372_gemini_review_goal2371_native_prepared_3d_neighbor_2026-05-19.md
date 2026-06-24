# Gemini Review for Goal2371: Native Prepared 3D Bounded-Neighbor

Date: 2026-05-19

## Review Summary

The independent review of Goal2371 confirms that the new native prepared 3D bounded-neighbor path successfully addresses the identified technical debt from Goal2369 by reusing a native search-side uniform-cell structure/device buffers across query runs. The implementation adheres to app-agnostic naming conventions and correctly removes the per-run overhead of building and uploading the search grid. Performance improvements are observed, especially at smaller scales, with larger scales showing reduced but still notable gains. The limitations of the current implementation, particularly the dominance of row download and host exact refinement, are clearly stated and bounded in the report. All specified claim boundaries are respected.

## Verdict

accept-with-boundary

## Findings

1.  **ABI/API Naming:** The new ABI (`rtdl_optix_prepare_fixed_radius_neighbors_3d`, `rtdl_optix_run_prepared_fixed_radius_neighbors_3d`, `rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d`) and Python API (`PreparedOptixFixedRadiusNeighbors3D`, `prepare_optix_fixed_radius_neighbors_3d`) are generic and do not introduce `rtnn` specific engine names. This aligns with the app-agnostic design boundary.
2.  **Reuse of Native Search Structure:** The implementation effectively reuses the native search-side uniform-cell structure and device buffers across query runs. This is evidenced by the `prepare` time being zero for subsequent runs in the pod data and the explicit statements in the report and test assertions.
3.  **Pod Evidence Consistency:** The pod evidence consistently supports the report's claims. Row counts match Goal2369 results, the native prepared mode is correctly identified as `prepared_uniform_cell_compact`, per-run native `prepare` times are 0.0, and upload times are significantly lower compared to the packed `run-optix` mode from Goal2369.
4.  **Interpretation Bounding:** The interpretation of results is appropriately bounded. It acknowledges that while the improvement is real, the performance for larger datasets (e.g., 262k points) is now dominated by the overhead of row download and host-side exact refinement, rather than native search-grid preparation.
5.  **Claim Boundaries:** All specified claim boundaries are respected. The report explicitly states that the evidence does not authorize RTNN paper equivalence, RT-core acceleration, broad speedup claims, or release readiness. The `claim_boundary` flags in the JSON artifacts corroborate these statements.

## Required Follow-up Work

- None explicitly required as part of this review, but the report clearly identifies the next performance bottleneck as the need for device-resident exact filtering or row summarization to further reduce host-side overhead.