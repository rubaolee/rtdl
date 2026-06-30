# Gemini Goal 201 Review

## Verdict

Pass. Goal 201 successfully adds the first external baseline harness for the `fixed_radius_neighbors` workload, satisfying the acceptance criteria without compromising the public contract or default dependencies.

## Findings

- **Correctness:** Both the SciPy and PostGIS baseline implementations enforce the exact RTDL semantics (`distance <= radius`, sorted by ascending `distance` then `neighbor_id`, grouped by `query_id`, and truncated to `k_max`). The implementations correctly handle RTDL's explicit deterministic tie-breaking.
- **Contract Honesty:** The baselines correctly act as comparison tools rather than defining the truth path. The RTDL public contract remains exactly as defined by the Python reference and native CPU paths. SciPy and PostGIS results are explicitly reshaped to match RTDL guarantees.
- **Optional-Dependency Honesty:** Both SciPy and psycopg2 (PostGIS) are properly guarded by `scipy_available()` and `postgis_available()` checks, remaining completely optional. They are not required for the default RTDL first-run environment, and raise descriptive `RuntimeError` exceptions only when their specific baselines are requested.
- **Clean Scoping for v0.4:** The goal accurately bounds its scope to just the SciPy and PostGIS CPU baselines for `fixed_radius_neighbors` without bleeding into performance claims, OptiX, or Vulkan implementations.

## Summary

The external baseline implementations in `src/rtdsl/external_baselines.py` and the wiring in `src/rtdsl/baseline_runner.py` meet all the stated non-goals and acceptance criteria for Goal 201. The tests provide solid coverage across the authored, runner, and SQL-shape paths. The documentation correctly sets expectations about the optional dependencies. Goal 201 is cleanly scoped and ready for `v0.4`.
