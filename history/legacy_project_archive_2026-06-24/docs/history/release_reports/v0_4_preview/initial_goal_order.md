# RTDL v0.4 Preview: Initial Goal Order

## Goal order

1. Define the public `fixed_radius_neighbors` workload contract.
2. Add the Python/DSL surface for that workload.
3. Add the Python reference implementation, deterministic fixtures, and first dataset-ingestion helpers.
4. Add native CPU/oracle support and closure tests.
5. Close Embree for the new workload.
6. Add the external baseline harness (`scipy.spatial.cKDTree` and bounded PostGIS cases).
7. Add `knn_rows` as the second workload in the same family.
8. Close OptiX and Vulkan under explicit bounded contracts.
9. Add the public example chain, tutorial extension, bounded benchmark report, and final `v0.4` audit.

## Why this order

This order forces:

- public semantics before backend breadth
- truth-path closure before performance claims
- baseline evidence before expansion to the second workload
- release-facing docs after the actual feature family is stable

That is the main lesson from the `v0.3.0` line.
