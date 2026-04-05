# RTDL v0.1 Work Report

Date: 2026-04-05
Status: complete

## Purpose

This report summarizes the work that produced the RTDL v0.1 release package.

It is not a full chronological diary of every goal. It compresses the work
into the major technical and packaging areas that matter for understanding the
release.

## 1. Language and runtime surface

The v0.1 package now includes:

- a Python-hosted DSL for writing non-graphical ray-tracing kernels
- runtime lowering and backend dispatch
- prepared-execution and runtime-cache machinery
- user-facing examples and a quick tutorial

This moved the project from backend experiments toward a usable language/runtime
surface.

## 2. Backend closure

### OptiX

The OptiX path progressed from raw backend viability to a mature backend story:

- runtime-owned prepared execution cache
- identity-based fast path for canonical geometry
- packed-geometry reuse
- parity repair for positive-hit candidate generation
- cold prepared run-1 win on the accepted long row

Published closure points include Goals 98, 99, and 100.

### Embree

The Embree path progressed from correctness failure on the long exact-source
row to a parity-clean and competitive backend:

- repaired positive-hit candidate generation/finalization logic
- restored exact parity on the accepted long exact-source row
- demonstrated faster-than-PostGIS prepared and repeated raw-input runs there

Published closure point:

- Goal 83

### Vulkan

The Vulkan path was reworked into a correct and supported backend:

- sparse positive-hit redesign
- hardware validation on Linux
- long exact-source prepared and raw-input execution unblocked
- parity-clean on the accepted flagship row

Vulkan is released as a supported backend, not a flagship performance backend.

Published closure points include Goals 78, 85, 87, 88, and 103.

## 3. Trust and correctness work

The release package does not rely only on backend agreement.

It also includes:

- deterministic Python mini-envelope oracle trust
- deterministic native small-envelope oracle trust
- PostGIS external checking on accepted workload packages

This is the main correctness scaffold behind the release.

Published anchor:

- Goal 75

## 4. Reproduction and performance work

The release package includes two complementary reproduction stories:

- Goal 102:
  - full honest bounded RayJoin reproduction package for Embree and OptiX
- Goal 103:
  - full honest bounded RayJoin reproduction package for Vulkan

And one performance-focused synthesis:

- Goal 104:
  - detailed performance report covering boundaries, datasets, environments,
    and results

The strongest current performance result is the accepted long exact-source
`county_zipcode` positive-hit `pip` surface.

## 5. Validation, audit, and front-door cleanup

The release package also required substantial packaging work:

- release validation rerun:
  - Goal 100
- final release review and audit:
  - Goal 105
- front-door cleanup:
  - README cleanup
  - tutorial and example cleanup
  - canonical user-facing sorting example renamed to user-facing names
  - future-direction bibliography cleanup

## 6. Net result

The work behind RTDL v0.1 achieved:

- a bounded but real research release
- one language/runtime surface
- three serious backends with distinct roles
- a reviewed trust story
- a reviewed reproduction/performance story
- a cleaner release-facing documentation surface

## Canonical references

- `/Users/rl2025/rtdl_python_only/docs/v0_1_release_notes.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal100_release_validation_rerun_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal103_full_honest_rayjoin_reproduction_vulkan_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal105_final_release_review_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal105_final_release_audit_2026-04-05.md`
