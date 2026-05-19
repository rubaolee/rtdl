# Goal2413 RT-DBSCAN Corrected Microcell Next-Fight Contract

Date: 2026-05-19

Status: corrected implementation contract after Codex/Claude review exchange

Inputs:

- Codex plan: `docs/reports/goal2408_codex_rt_dbscan_next_fight_plan_2026-05-19.md`
- Claude review: `docs/reviews/goal2409_claude_review_goal2408_rt_dbscan_next_fight_plan_2026-05-19.md`
- Codex counter-review:
  `docs/reports/goal2411_codex_counter_review_goal2409_cell_graph_safety_2026-05-19.md`
- Claude counter-review:
  `docs/reviews/goal2412_claude_review_goal2411_microcell_counter_review_2026-05-19.md`

## Final Decision

Goal2409 should implement the corrected Candidate B' path:

```text
generic fixed-radius microcell component continuation
```

The earlier radius-cell component graph must not be implemented. A radius-sized
3-D cell is not internally clique-safe: two same-cell points can be farther than
the radius and therefore belong to separate radius-graph components.

## Public Adapter Target

Use the explicit name:

```python
radius_graph_components_3d_cupy_microcell_graph_partner_columns(...)
```

Use this benchmark mode:

```text
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

## Required Algorithmic Contract

The microcell path must:

1. Require or compute `core_flags` and `neighbor_counts`.
2. Check whether all points are core before any fast-path work.
3. Fall back to `radius_graph_components_3d_cupy_grid_partner_columns` when any
   point is non-core.
4. Use:

   ```text
   microcell_size = radius / sqrt(3)
   neighbor_cell_range = ceil(radius / microcell_size)
   ```

5. Treat each occupied microcell as an internally connected clique.
6. Union two microcells only after finding at least one actual cross-microcell
   point pair with `dist^2 <= radius^2`.
7. Label each point by its microcell component.
8. Preserve the existing output schema:

   ```text
   point_ids, component_labels, is_core, neighbor_counts
   ```

## Required Metadata

Every result must include:

- `adapter`;
- `partner`;
- `cell_graph_fast_path_active`;
- `cell_graph_granularity = "clique_safe_microcell"`;
- `microcell_size_policy`;
- `neighbor_cell_range`;
- `fallback_adapter` when fallback occurs;
- `component_label_policy`;
- conservative claim-boundary flags.

## Required Local Tests

Before pod timing, tests must cover:

- static export/import wiring;
- no native source changes and no `dbscan` native ABI;
- same-radius-cell disconnected points do not merge;
- mixed-core input triggers fallback and preserves schema;
- all-core input can activate the microcell fast path.

The same-radius-cell disconnected test must be able to run without CuPy by using
a small CPU reference helper or static logic, because it is the key correctness
reason the first cell-graph plan was rejected.

## Required Pod Evidence

Compare these modes:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

Datasets:

```text
clustered3d
road3d
```

Sizes:

```text
32768, 65536, 131072
```

Each artifact must include:

- `signatures_match == true`;
- warm-tail median timing;
- `cell_graph_fast_path_active`;
- `cell_graph_granularity`;
- `neighbor_cell_range`;
- fallback status for mixed-core rows.

## Abort Policy

Abort or downgrade Candidate B' if:

- any correctness signature mismatches;
- same-cell disconnected cases merge incorrectly;
- mixed-core fallback does not trigger;
- the fast path never activates on dense clustered rows;
- the microcell cross-pair scan is effectively the same cost as the current
  point-level CuPy grid continuation and does not improve timing.

If Candidate B' is correct but does not win, pivot to Candidate A:

```text
prepared CuPy grid continuation hardening
```

## Boundary

This contract authorizes only a benchmark-driven implementation experiment. It
does not authorize a release claim, broad RT-core speedup claim, RT-DBSCAN paper
reproduction claim, or v2.x closure. The RTDL native engine must remain
app-agnostic.
