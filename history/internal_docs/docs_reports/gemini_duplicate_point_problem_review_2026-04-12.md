### Verdict
The duplicate-point problem is accurately isolated, and the mitigation strategy (a preflight guard and a duplicate-free selector) is both technically coherent and strictly honest. The current state establishes a clear, documented boundary for cuNSearch's behavior regarding exact duplicates rather than masking the issue. It is acceptable and safe for continuing v0.5 work without making misleading claims.

### Findings
- **Problem Description:** Goal 285 correctly diagnoses the cuNSearch correctness failure. It identifies that exact cross-package duplicate points are being dropped by cuNSearch (even when `k_max` is increased), whereas the RTDL CPU reference accurately includes them.
- **Guard Implementation:** The preflight guard introduced in `src/rtdsl/rtnn_duplicate_audit.py` and integrated into `src/rtdsl/rtnn_comparison.py` is transparent. It explicitly detects duplicate coordinates and returns an early blocked result with detailed notes, rather than silently ignoring or falsifying parity. The Goal 286 report correctly frames this as a "contract hardening step" rather than a backend fix.
- **Selector Continuation:** `find_duplicate_free_kitti_pair` in `src/rtdsl/rtnn_kitti_selector.py` is a pragmatic approach for a bounded continuation. By scanning for authentic KITTI frame pairs that naturally lack cross-package duplicates, the benchmark (Goal 288) can proceed to measure performance on real data without artificially scrubbing or modifying the dataset.
- **Honesty and Claims:** The reports consistently maintain an objective tone, explicitly noting that results are bounded and do not represent a "broad paper-level claim." The distinction between a generalized backend fix and a bounded contract exclusion is strictly maintained.

### Risks
- **Floating-Point Brittleness:** The current audit relies on exact floating-point equality (`key = (x, y, z)` in Python). If minor floating-point drift is introduced anywhere in the dataset loading or transformation pipelines, near-duplicates might bypass the guard and trigger strict parity failures.
- **Scaling Bottlenecks:** The `find_exact_cross_package_matches` method uses Python-level dictionary lookups for every coordinate. While this is entirely fine for bounded point packages (e.g., 1024 to 2048 points), it could become a significant performance bottleneck if applied to multi-million point clouds in later milestones.
- **Perception:** Users viewing the benchmark results might overlook the duplicate-free constraint and assume cuNSearch is universally robust for all point clouds, unless the boundary constraint is highly visible in top-level documentation.

### Recommendation
- **Proceed with v0.5:** The implementation is structurally sound and intellectually honest. You are cleared to proceed with v0.5 work.
- **Documentation Visibility:** Ensure the cuNSearch duplicate-point limitation and the resulting contract boundaries are prominently documented in the top-level v0.5 release notes or feature matrices, not just in offline goal reports.
- **Future Maturation (Post-v0.5):** Investigate if a small epsilon tolerance is needed for the duplicate point guard to catch near-duplicates. Furthermore, consider moving the duplicate audit down into a faster, native validation layer if large-scale point clouds are integrated in future testing.
