# RTDL v0.6 Support Matrix

Date: 2026-04-14
Status: released as `v0.6.0`

## Reading Guide

Status wording used below:

- `accepted`: part of the released `v0.6` claim surface
- `accepted, bounded`: supported under a narrower or explicitly limited contract
- `supporting baseline`: useful for validation/comparison, not the primary RTDL
  execution path
- `not in v0.6 scope`: intentionally outside the accepted `v0.6` package

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for the `v0.6` graph line | accepted |
| local macOS | local development and focused regression platform | accepted, bounded |
| Windows | not part of the current accepted graph-evaluation claim surface | not in v0.6 scope |

## Backend Roles

| Backend | Role in `v0.6` | Current status |
| --- | --- | --- |
| Python reference | correctness / truth path | accepted |
| native CPU / oracle | compiled correctness baseline | accepted |
| PostgreSQL | external correctness and SQL/timing baseline | supporting baseline |
| Embree | not part of the current graph line | not in v0.6 scope |
| OptiX | not part of the current graph line | not in v0.6 scope |
| Vulkan | not part of the current graph line | not in v0.6 scope |
| DuckDB | intentionally declined for this line | not in v0.6 scope |

## Workload Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `bfs` synthetic graphs | Python/oracle/PostgreSQL line closed on Linux | accepted |
| `triangle_count` synthetic graphs | Python/oracle/PostgreSQL line closed on Linux | accepted |
| `bfs` on `wiki-Talk` | bounded real-data Linux slice | accepted, bounded |
| `triangle_count` on `wiki-Talk` | bounded simple-undirected real-data Linux slice | accepted, bounded |
| `bfs` on `cit-Patents` | bounded real-data Linux slice | accepted, bounded |
| `triangle_count` on `cit-Patents` | bounded simple-undirected real-data Linux slice | accepted, bounded |

## Honest Summary

- `v0.6` is the graph-workload expansion line for the repo
- the accepted runtime stack is:
  - Python truth path
  - native CPU/oracle
  - PostgreSQL supporting baseline
- Linux is the platform for the real graph-evaluation story
- the line is intentionally bounded to:
  - `bfs`
  - `triangle_count`
- no accelerated graph backend is part of the current accepted `v0.6` package
