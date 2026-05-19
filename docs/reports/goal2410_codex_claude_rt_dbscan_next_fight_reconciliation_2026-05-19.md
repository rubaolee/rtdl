# Goal2410 Codex/Claude RT-DBSCAN Next-Fight Reconciliation

Date: 2026-05-19

Status: planning round closed; next implementation target selected

Inputs:

- Codex plan: `docs/reports/goal2408_codex_rt_dbscan_next_fight_plan_2026-05-19.md`
- Claude review: `docs/reviews/goal2409_claude_review_goal2408_rt_dbscan_next_fight_plan_2026-05-19.md`

## Decision

Proceed with Candidate B as the next implementation fight:

```text
generic fixed-radius cell-graph component continuation for all-core 3-D point
sets, with fallback to the existing CuPy grid continuation when non-core points
exist
```

The target remains app-agnostic. No DBSCAN-native ABI, no hard-coded cluster
expansion inside OptiX, and no broad RT-core or release claim is authorized.

## Where Codex And Claude Agree

Both reviewers agree that Goal2405 is the current positive path:

- true OptiX RT fixed-radius count-threshold device columns exist;
- the primitive is generic;
- dense `clustered3d` at 131k points improved over the pure CuPy baseline in
  pod measurements;
- the remaining cost is the radius-graph component continuation.

Both reviewers agree that Goal2407 is a negative result:

- the raw OptiX any-hit core-graph union prototype compiled and matched
  signatures;
- it did not beat Goal2405;
- no runtime API should be promoted from that prototype;
- raw in-traversal atomic union should not be revisited without a different
  scheduling/aggregation design.

Both reviewers agree that Candidate B is the best next fight:

- it attacks the measured continuation bottleneck;
- it reduces dense all-core component work from point-level union pressure to
  cell-level graph pressure;
- it can be expressed as a generic fixed-radius graph continuation;
- it can start as a CuPy partner continuation without touching the native OptiX
  ABI.

## Claude Corrections Accepted By Codex

Claude tightened the acceptance gate. Codex accepts these corrections.

1. The cell-graph fast path must not union neighboring cells by adjacency alone.
   A cell-pair kernel must prove at least one actual point pair has
   `dist^2 <= radius^2` before unioning those cells.

2. The all-core gate must be exact and reported in metadata. The implementation
   should expose generic metadata such as `cell_graph_fast_path_active`, not a
   DBSCAN-shaped public concept.

3. Fast path and fallback path must be mutually exclusive. Mixed-core datasets
   must take the fallback and match the CPU reference.

4. The 26-neighbor cell scan is sound only when `cell_size == radius`. This
   invariant must be explicit in code and tests.

5. Pod evidence must include more than a dense timing win. It must also include
   fallback evidence and fast-path activation evidence.

## Goal2409 Implementation Contract

The next implementation should add a partner-side adapter named:

```python
radius_graph_components_3d_cupy_cell_graph_partner_columns(...)
```

The RT-DBSCAN benchmark may add a mode named:

```text
optix_rt_core_flags_cupy_cell_graph_components_3d
```

Required behavior:

- If all `core_flags` are one, use the cell-graph fast path.
- If any `core_flags` entry is zero, fall back to
  `radius_graph_components_3d_cupy_grid_partner_columns`.
- The fast path must only union cells after confirming an actual in-radius
  cross-cell point pair.
- The output schema must match the existing component-column schema:
  `point_ids`, `component_labels`, `is_core`, and `neighbor_counts`.
- Metadata must include:
  - `adapter`;
  - `partner`;
  - `cell_graph_fast_path_active`;
  - `fallback_adapter` when fallback occurs;
  - `component_label_policy`;
  - claim-boundary flags set conservatively.

## Required Static Tests Before Performance Work

Goal2409 must add tests that verify:

- generic adapter and mode names;
- no `dbscan` native ABI or native source change is introduced;
- mixed-core input triggers fallback;
- all-core input can activate the fast path;
- both paths preserve the existing component-column schema.

## Required Pod Evidence

Goal2409 pod evidence must compare:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_cell_graph_components_3d
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
- fallback status for mixed-core rows;
- clear claim boundary flags.

## Pass/Fail Policy

Pass if:

- every correctness signature matches;
- mixed-core fallback is observed and correct;
- the fast path activates on dense clustered data;
- dense 131k improves over Goal2405 by at least 5% in warm-tail median, or the
  new artifacts identify a concrete next smaller fix without regressing the
  supported path.

Fail or abort if:

- any signature mismatches;
- fallback is missing for mixed-core data;
- the dense all-core fast path never activates;
- cell-pair existence scanning degenerates into the same point-pair workload as
  the current grid continuation and does not improve timing.

## Boundary

This reconciliation does not authorize release closure, broad RT-DBSCAN
speedup claims, paper reproduction claims, or v2.x closure. It only selects the
next benchmark-driven implementation target and records the correctness gates
that must be met before performance claims are discussed.
