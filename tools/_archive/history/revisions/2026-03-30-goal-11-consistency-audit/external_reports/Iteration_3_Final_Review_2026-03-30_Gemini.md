Following the Goal 11 consistency audit, I have reviewed the revised implementation and documentation. The project successfully synchronizes the language documentation, plan schema, and test suite with the current six-workload surface.

### Findings

- **Makefile**: The `build` target is now compiler-only, removing the hard dependency on Embree for initial setup, and has been updated to include all six canonical workloads (`lsi`, `pip`, `overlay`, `ray_tri_hitcount`, `segment_polygon_hitcount`, `point_nearest_segment`).
- **README.md**: Now accurately reflects the fresh-checkout experience and explicitly lists the expanded workload coverage.
- **Documentation (`docs/rtdl/`)**: The DSL reference, programming guide, and LLM authoring guide have been fully updated to describe the Goal 10 workload extensions, including correct predicates and emit fields.
- **Schema (`schemas/rayjoin_plan.schema.json`)**: The `workload_kind` and `predicate` enums are now synchronized with the implementation, allowing validation of plans for all six supported workloads.
- **Tests (`tests/rtdsl_language_test.py`)**: Regression tests have been expanded to validate that all six workloads compile, lower, and match the documentation.

### Residual Risk Note

- The project maintains a deliberate scope split between the "frozen" Embree baseline (4 workloads) and the "current" RTDL surface (6 workloads). This distinction is explicitly labeled in the `README.md` and programming guides, minimizing the risk of user confusion regarding which workloads are part of the comparative baseline.

No blockers
