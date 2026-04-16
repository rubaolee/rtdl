# RTDL v0.7 Branch Support Matrix

Date: 2026-04-15
Status: bounded branch line

## Workload Surface

Current bounded DB kernels:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Backend Matrix

| Backend | `conjunctive_scan` | `grouped_count` | `grouped_sum` | Notes |
|---|---|---|---|---|
| `cpu_python_reference` | yes | yes | yes | canonical truth path |
| `cpu` | yes | yes | yes | native/oracle correctness path |
| `embree` | yes | yes | yes | bounded first-wave RT backend |
| `optix` | yes | yes | yes | bounded first-wave RT backend; Linux GPU validation story |
| `vulkan` | yes | yes | yes | bounded first-wave RT backend; Linux GPU validation story |
| `postgresql` | baseline | baseline | baseline | external correctness/perf anchor, not an RTDL backend |

## Query-Shape Boundary

Current bounded DB family supports:

- conjunctive predicates
- up to 3 primary RT clauses per RT job
- one group key
- integer-compatible `grouped_sum`

Current bounded DB family does not support:

- arbitrary SQL
- transactions
- joins as a first-class RTDL DB feature
- multi-group-key grouped RT kernels

## Platform Boundary

- `Linux`
  - primary validation platform
  - carries PostgreSQL correctness/performance anchoring
  - carries OptiX and Vulkan validation story
- `Windows`
  - bounded local/runtime surface for non-PostgreSQL work
- `local macOS`
  - bounded local/runtime surface for non-PostgreSQL work

## Public Example Surface

Current public DB examples expose:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`

PostgreSQL is not a public example backend flag.
