# RTDL v0.6 Support Matrix

Date: 2026-04-15
Status: released as `v0.6.1`

## Reading Guide

Status wording used below:

- `accepted`: part of the released `v0.6.1` claim surface
- `accepted, bounded`: supported under a narrower or explicitly limited
  contract
- `supporting baseline`: useful for validation/comparison, not the primary RTDL
  execution path
- `not in v0.6 scope`: intentionally outside the accepted `v0.6` package

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for the RT graph line | accepted |
| local macOS | development, focused regression, bounded checks | accepted, bounded |
| Windows | secondary portability/validation host; bounded graph validation | accepted, bounded |

## Backend Roles

| Backend | Role in `v0.6` | Current status |
| --- | --- | --- |
| Python reference | correctness / truth path | accepted |
| native CPU / oracle | compiled correctness baseline | accepted |
| PostgreSQL | external correctness baseline for graph workloads | supporting baseline |
| Embree | accelerated CPU graph backend | accepted |
| OptiX | accelerated GPU graph backend | accepted |
| Vulkan | accelerated GPU graph backend | accepted |
| Gunrock | external BFS comparison path | accepted, bounded |
| Neo4j GDS | external professional graph baseline | accepted, bounded |

## Workload Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `bfs` | released RT graph workload | accepted |
| `triangle_count` | released RT graph workload | accepted |

## Honest Summary

- `v0.6.1` is the released corrected RT graph line for the repo
- Linux is the platform for the main graph correctness/performance story
- Windows and local macOS are bounded supporting validation platforms
- PostgreSQL is the supporting external correctness baseline
- OptiX results on the Linux benchmark host are non-RT-core baselines because
  the host GPU was a GTX 1070
