# Goal 523: Claude External Review

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6

## Verdict: ACCEPT

The Linux public command validation honestly proves that the v0.8 six-app public command surface runs across available RTDL backends without making unsupported performance claims.

## Reasoning

**Test counts match.** The JSON artifact reports 88 passed, 0 failed, 0 skipped. Spot-checks of individual records confirm `"returncode": 0` and non-empty stdout throughout; no stderr is present. The summary in the report accurately reflects the artifact.

**Backend availability is genuine.** All six backends (`cpu_python_reference`, `oracle`, `cpu`, `embree`, `optix`, `vulkan`) are marked `true` in the artifact, consistent with the probe log showing Embree 4.3.0, OptiX 9.0.0, and Vulkan 0.1.0 built from the checkout.

**All six v0.8 apps are present.** The artifact contains entries for:
- `rtdl_hausdorff_distance_app.py` — 5 backends (cpu_python_reference, cpu, embree, optix, vulkan)
- `rtdl_ann_candidate_app.py` — 5 backends
- `rtdl_outlier_detection_app.py` — 5 backends
- `rtdl_dbscan_clustering_app.py` — 5 backends
- `rtdl_robot_collision_screening_app.py` — 4 backends (cpu_python_reference, cpu, embree, optix; **no vulkan variant**)
- `rtdl_barnes_hut_force_app.py` — 5 backends

**One coverage gap noted.** `robot_collision_screening_app` is absent from vulkan in the artifact. The report does not claim vulkan coverage for this app specifically — it only asserts 5-backend coverage for the three new Stage-1 proximity apps (ANN, outlier, DBSCAN). The gap is therefore not a dishonest claim, but it is a real limitation of the harness for that app. Future reviewers should confirm whether vulkan support for `robot_collision_screening_app` is intentionally deferred.

**Correctness signals are present.** Multiple app entries include `"matches_oracle": true`, providing a correctness anchor beyond mere exit-code checking.

**No performance claims.** The report's Honesty Boundary section explicitly states this is command validation only, that it does not claim the new Stage-1 apps outperform mature non-RT libraries, and that performance comparison is a separate future gate. The artifact contains no throughput, latency, or comparative benchmarking data.

## Summary

The validation is honest within its stated scope. The one gap (no vulkan variant for `robot_collision_screening_app`) is real but not misrepresented. No Linux public-command blocker is present.
