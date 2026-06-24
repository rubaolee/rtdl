Verdict: ACCEPT

## Findings:

The new public scalar output modes `density_count` (for outlier detection) and `core_count` (for DBSCAN clustering) have been implemented and documented as specified.

1.  **Accurate Description of Scalar OptiX Paths**:
    *   `README.md`, under "NVIDIA RT-Core Claim Boundary," explicitly lists both `outlier detection: --backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count` and `DBSCAN core count: --backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count`.
    *   `examples/README.md`, in the "Current v0.8 app example boundary" section, provides detailed explanations for `rtdl_outlier_detection_app.py` and `rtdl_dbscan_clustering_app.py`, clearly stating the flags and their scalar output.

2.  **No Overclaiming of Per-Point Labels or DBSCAN Clustering**:
    *   `README.md` explicitly states: "...full DBSCAN cluster expansion... remain outside the claim unless a later review explicitly authorizes them."
    *   `examples/README.md`, for `rtdl_outlier_detection_app.py` with `density_count`, notes it "emits only scalar threshold/outlier counts and avoids neighbor-row plus per-point summary-row materialization; use `density_summary` when point IDs are required."
    *   `examples/README.md`, for `rtdl_dbscan_clustering_app.py` with `core_count`, states it "emits only scalar core counts and avoids neighbor-row plus per-point core-flag materialization; use `core_flags` when point IDs are required. The full DBSCAN cluster expansion still needs neighbor connectivity and remains Python-owned."
    *   The `docs/reports/goal992_outlier_dbscan_scalar_public_paths_2026-04-26.md` itself included a clear "Honesty Boundaries" section reinforcing these limitations.

**Conclusion:** The documentation now accurately describes `outlier density_count` and `DBSCAN core_count` scalar OptiX paths and correctly avoids overclaiming per-point labels or DBSCAN clustering.
