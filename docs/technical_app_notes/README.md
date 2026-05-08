# RTDL Technical App Notes

These notes are for engineers who want to understand how the RTDL application
examples are implemented. They are not tutorials, benchmark recipes, or release
claim pages.

The purpose is to explain, app by app, how the public examples map application
data into RTDL primitives, how v1.0 implemented the app-facing native paths, and
how the current main/v1.5.x line is moving those paths toward generic reduction,
bounded collection, and reduced-copy mechanisms.

## Scope

- Primary sources: `docs/application_catalog.md`,
  `docs/app_engine_support_matrix.md`, `docs/v1_0_app_acceleration_inventory.md`,
  and the Goal1408 v1.0-vs-current comparison reports.
- Active engine focus: Embree and OptiX.
- Frozen proof surfaces before v2.1: Apple RT, HIPRT, and Vulkan.
- Claim boundary: this directory is explanatory. It does not authorize public
  speedup claims, whole-app acceleration claims, broad RTX claims, or true
  zero-copy claims.

## Reading Order

1. Read `app_implementation_matrix.md` for the per-app architecture and
   v1.0-to-current transition.
2. Read `app_primitive_classification.md` for reduction, split-contract,
   candidate-refinement, and bounded-collection planning groups.
3. Read `docs/application_catalog.md` for public-facing app names, commands,
   and supported summary modes.
4. Read `docs/app_engine_support_matrix.md` for backend support status.
5. Read the relevant performance reports only as measured evidence for their
   exact command scope.

## Shared Architecture Terms

- Python orchestration means fixture generation, CLI parsing, app policy,
  postprocessing, formatting, and any app-specific logic outside the native
  traversal/reduction path.
- RTDL traversal means the backend-owned ray/geometry or proximity query phase.
- Native continuation means native code continues after traversal to produce a
  compact summary rather than returning large intermediate row lists to Python.
- Reduction means RTDL/backend-side summary operators such as count, min, max,
  sum, any-hit, or threshold-count.
- Bounded collection means a fixed-capacity row/result path. In the current
  roadmap, `COLLECT_K_BOUNDED` remains experimental until promotion evidence is
  complete.
- Reduced-copy means avoiding unnecessary intermediate materialization or
  reusing staging buffers. It is not the same claim as true zero-copy.
