# Goal 400 Review: v0.6 PostgreSQL-Backed All-Engine Correctness Gate

Date: 2026-04-14
Reviewer: Antigravity

## Overview

This review evaluates the Goal 400 implementation, which establishes a PostgreSQL-backed correctness anchor for the RT-kernel graph line (specifically for `bfs` and `triangle_count` operations). This gate ensures that all RT backends (Embree, OptiX, Vulkan) agree with both the Python/oracle truth paths and a relational SQL baseline.

## Review Findings

### 1. Semantics Match
- **BFS Expansion**: The PostgreSQL implementation in `graph_postgresql.py` correctly implements the one-step frontier expansion semantics. The use of `DISTINCT ON (dst_vertex)` in the SQL expansion path matches the `dedupe=True` requirement of the RT-kernel `bfs_discover` predicate. The JOIN logic with the visited vertex set correctly filters already-visited nodes.
- **Triangle Counting**: The implementation uses a relational join between the edge table and seed edges to find common neighbors ($w$ such that $(u, w)$ and $(v, w)$ exist). The enforcement of the canonical order $u < v < w$ ensures results are consistent with the RT-kernel `triangle_match` operation.

### 2. PostgreSQL Implementation (Indexes & Temp Tables)
- **Table Strategy**: The use of `CREATE TEMP TABLE ... ON COMMIT DROP` is appropriate for a bounded correctness gate, ensuring isolation and clean teardown.
- **Optimization**: The implementation includes all necessary indexes for performant relational joins:
    - Primary edge indexes on `(src)`, `(dst)`, and `(src, dst)`.
    - Join indexes on `frontier(vertex_id)`, `visited(vertex_id)`, and `seeds(u, v)`.
- **Reliability**: The forced `ANALYZE` after data insertion ensures the PostgreSQL query planner makes correct decisions even on small test datasets.

### 3. Parity Evidence
- **Testing**: The test suite `goal400_v0_6_postgresql_graph_correctness_test.py` provides comprehensive coverage by checking parity across:
    - Python Reference
    - Native Oracle
    - Embree
    - OptiX
    - Vulkan
- **Platform Closure**: The implementation report successfully documents parity closure on both macOS and Linux (with live GPU backends), satisfying the gate's verification requirement.

### 4. Recommendation: Acceptance
Goal 400 effectively upgrades the project's correctness story by introducing an external, independently verified baseline (PostgreSQL). The implementation is clean, well-tested, and adheres to the project's technical patterns.

**Status**: **APPROVED** for acceptance as a bounded correctness gate.

## Action Items
- [x] Verify semantics match across all engines.
- [x] Confirm SQL optimization paths (indexes/temp tables).
- [x] Audit parity results against the implementation report.
