**Review of Goal 374: v0.6 cit-Patents Split-Bound Scale Plan**

This review is based on the following documents:
- `docs/goal_374_v0_6_cit_patents_split_bound_scale_plan.md`
- `docs/reports/goal374_v0_6_cit_patents_split_bound_scale_plan_2026-04-14.md`
- `docs/reports/goal369_v0_6_cit_patents_bfs_bounded_linux_eval_2026-04-13.md`
- `docs/reports/goal373_v0_6_cit_patents_triangle_count_bounded_linux_probe_2026-04-14.md`
- `docs/reports/goal365_v0_6_split_bound_scale_plus_one_eval_2026-04-13.md`

### 1. Justification of Proposed Next Split Bounds by Current `cit-Patents` Evidence

The proposed next split bounds are well-justified by the current `cit-Patents` evidence.

**For BFS:**
- Current bound: `500000` directed edges.
- Proposed next bound: `1000000` directed edges.
- Justification: Python, oracle, and PostgreSQL query time are still comfortable at the current bound, and PostgreSQL setup time dominates, so a larger bound is still informative.

**For Triangle Count:**
- Current bound: `50000` canonical undirected edges.
- Proposed next bound: `100000` canonical undirected edges.
- Justification: Python is still practical but already materially slower than BFS. A 2x step is a safer next measurement than a larger jump.

### 2. Honesty of the BFS/Triangle Split

The split is honest and evidence-driven.

- The `wiki-Talk` line already showed that BFS can advance faster while triangle count becomes truth-only earlier.
- The first `cit-Patents` results are consistent with the same pattern.
- The separate next caps reflect actual workload behavior rather than forcing a shared scale story.

### 3. Does the Report Overstate These as Accepted Production Bounds?

No.

The report explicitly says this is:
- a scale-decision slice only
- not a live larger result
- not a final accepted production bound
- not a benchmark claim
- not a paper-scale reproduction claim

**Conclusion:**
The proposed next split bounds are justified by the current `cit-Patents` evidence, the BFS/triangle split is honest, and the report does not overstate the proposed values as production bounds.
