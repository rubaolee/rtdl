# Gemini Review: Goal2962 Large-Scale v2.5 Stress Probe

- **Review Date:** 2026-06-01
- **Reviewer:** Gemini CLI
- **Subject Goal:** Goal2962 (Large-Scale v2.5 Stress Probe)
- **Source Commit:** `28bcf380` (Review), `8deb21be` (Artifacts)
- **Verdict:** `accept`

## Summary

This independent review confirms that Goal2962 successfully provides large-scale stress evidence for the v2.5 RT-core paths. The evidence demonstrates that RTNN, Exact Hausdorff, and RT-DBSCAN maintain correctness, acceleration, and stability at scales significantly larger than the standard canonical packet (up to 262,144 points). The report and associated source changes strictly adhere to claim boundaries, explicitly disclaiming release authorization or public speedup wording.

## Findings

### 1. Artifact Integrity and Source Provenance
The three primary artifacts were verified against the review criteria:
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rtnn_262k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_hausdorff_16k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rt_dbscan_262k.json`

All three artifacts correctly report:
- `status: pass`
- `source_commit: 8deb21bea3930830ad03d3d7410356c786af5479`
- `source_dirty: []` (clean source)
- GPU: `NVIDIA RTX A5000`

### 2. RTNN Stress (262K Points)
RTNN evidence at 262,144 points across uniform, clustered, and shell distributions is sound:
- **Chunking:** The implementation correctly utilizes four 65,536-query graph chunks, staying within graph-safe limits while processing the 262K total queries.
- **Correctness:** `ranked_aggregate_matches_cupy_grid` is `true` for all distributions.
- **Performance:** RTDL maintains a significant lead over the CuPy grid opponent (ratios from `2.07x` to `4.61x`).
- **Native Phase:** `upload_sec` is recorded as `0.0`, confirming efficient native-phase execution.

### 3. Exact Hausdorff Stress (16K x 16K)
The Hausdorff artifact at 16,384 x 16,384 points provides strong evidence for the RT-core path:
- **Path:** Uses `rtdl_rt_grouped_reduced_nearest_witness` with OptiX backend.
- **Precision:** Reports `distance_error: 0.0` and `matches_exact_baseline: true` against the `cupy_grouped_grid_rawkernel` opponent.
- **Efficiency:** The RT-core path remains competitive at `0.937x` ratio, supporting the continued use of the target-8192 reduced witness strategy.

### 4. RT-DBSCAN Stress (262K Points)
The RT-DBSCAN evidence confirms that grouped-stream continuation handles scale effectively:
- **Acceleration:** `grouped_stream_rt_core_accelerated` is `true`.
- **Compactness:** `grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream` is `true`, proving the path remains memory-efficient at scale.
- **Correctness:** `signatures_match` is `true` for the 262K point dataset.
- **Speedup:** Maintains a `4.58x` speedup versus the prepared CuPy grid.

### 5. Boundary Preservation
The review specifically analyzed the report and `src/rtdsl/v2_5_internal_readiness.py` for overclaiming:
- **Report:** `docs/reports/goal2962_large_scale_v2_5_stress_probe_2026-06-01.md` contains a clear "Boundary" section explicitly blocking release, public speedup, and broad RT-core claims.
- **Source:** `v2_5_internal_readiness.py` correctly incorporates the Goal2962 report as a requirement and adds a corresponding allowed next action, while maintaining all `claim_authorization` flags at `False`.
- **Verification:** `tests/goal2962_large_scale_v2_5_stress_probe_test.py` successfully verifies these boundaries and artifact states.

## Recommendation

The stress evidence layered on top of the Goal2959 zero-target packet is appropriately framed. It provides the necessary engineering confidence that the v2.5 optimizations are robust across scales. The verdict is **accept** as the work is complete, verified, and correctly bounded.
