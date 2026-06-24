ACCEPT

Findings:
The updates in `tests/goal825_tier1_profiler_contract_test.py`, `tests/goal858_segment_polygon_docs_optix_boundary_test.py`, and `tests/goal973_deferred_decision_baselines_test.py` are legitimate stale-expectation repairs.
- `goal825` update correctly reflects "scalar threshold-count" and "scalar core-count" claim scopes.
- `goal858` update correctly references "Goal969" in the documentation.
- `goal973` update correctly reflects the new baseline counts (`17 / 0 / 0`).
The reported full-suite result is "OK", indicating successful repair and verification. The "Boundary" section clearly outlines the scope and limitations, with no overclaims or missing release boundaries identified.
