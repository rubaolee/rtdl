# Gemini Review for Goal2375 Prepared 3D Neighbor Exact Count Summary

## Verdict: accept-with-boundary

## Review Questions & Answers:

1.  **Does Goal2375 keep the native/runtime surface app-agnostic?**

    *Answer:* Yes, Goal2375 keeps the native/runtime surface app-agnostic. The report explicitly states this, and the Python API for the new count functionality (e.g., `PreparedOptixFixedRadiusNeighbors3D.count`) is designed around generic geometric primitives (`search_points`, `query_points`, `radius`, `k_max`) without introducing application-specific terminology or logic. The intention to avoid `rtnn` ABI names further supports this.

2.  **Does the new count-summary path correctly avoid row materialization, row download, and host exact-refine for `result-mode=count`?**

    *Answer:* Yes, the new count-summary path correctly avoids row materialization, row download, and host exact-refinement for `result-mode=count`. The report and the tests explicitly confirm that `row_download` and `exact_refine` are 0.0, and `device_resident_summary` is true, indicating device-resident processing for counts.

3.  **Does the report honestly explain that count summary is not a byte-identical witness-row replacement, especially because the count and witness contracts can differ near boundaries or `k_max` saturation?**

    *Answer:* Yes, the report explicitly and honestly explains that the count summary is not a byte-identical witness-row replacement, highlighting potential differences near boundaries or `k_max` saturation. The test case confirms that this boundary claim is present in the report.

4.  **Does the report avoid RTNN paper-equivalence, RT-core speedup, broad runtime speedup, and release-readiness overclaims?**

    *Answer:* Yes, the report and the underlying claim boundaries in the runner explicitly avoid overclaiming. It states that it "does not authorize an RT-core speedup claim for general unbounded-neighbor traversals" and that "No native `rtnn` ABI names were added." The tests verify these disclaimers.

5.  **Are the tests and pod artifacts sufficient for accepting this as a v2.2 internal primitive improvement, with boundaries?**

    *Answer:* Yes, the tests and pod artifacts are sufficient. The tests thoroughly verify that the count summary surface is correctly wired, that the claim boundaries are preserved in the report and artifacts, and critically, that the device-resident summary avoids row materialization and host exact refinement. The pod artifacts themselves provide concrete evidence, and the performance comparison showing a >10x speedup for count summary over full row materialization is compelling for accepting this as a v2.2 internal primitive improvement, with the clearly defined boundaries.
