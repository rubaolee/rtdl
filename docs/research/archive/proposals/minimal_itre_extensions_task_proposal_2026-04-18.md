# Proposal: Minimal ITRE Extensions For Post-v0.8 RTDL

Date: 2026-04-18
Status: proposal, not implementation
Related:

- `docs/reports/goal533_codex_rtdl_api_brainstorm_review_2026-04-18.md`
- `docs/reports/goal533_claude_rtdl_api_brainstorm_review_2026-04-18.md`
- `docs/reports/goal534_minimal_itre_extensions_design_study_2026-04-18.md`
- `docs/rtdl/minimal_itre_extension_demo_kernels.md`

## Executive Summary

RTDL `v0.8.0` proved that the current ITRE model can support useful
RTDL-plus-Python applications without changing language internals. The next
task is to grow ITRE carefully where real app pressure exists.

This proposal defines the next bounded work package:

> Add minimal non-rendering ITRE extensions for any-hit / early-exit traversal,
> visibility rows, post-emit row reductions, Python-orchestrated multi-hop
> graph workflows, and hierarchy candidate rows.

The first implementable feature is:

> bounded any-hit / early-exit traversal, CPU/oracle first.

Everything else should be layered on top only after the contract is correct.

## Non-Goals

This task must not implement or expose:

- shader-stage callbacks such as `on_closest_hit`, `on_any_hit`, or `on_miss`
- mutable user ray payloads
- recursive device-side ray spawning
- path tracing
- ambient occlusion as a rendering feature
- global illumination
- BRDF, material, skybox, or renderer APIs
- a full simulation framework

Native backends may internally use low-level RT mechanisms, but the public RTDL
surface must remain typed inputs, bounded traversal/refinement, and emitted
rows.

## Product Goal

Make RTDL more useful for real spatial/query applications while preserving the
v0.8 boundary:

```text
Python prepares domain data
  -> RTDL emits bounded query rows
  -> Python reduces rows into app answers
```

The new surfaces should reduce user burden for:

- collision yes/no queries
- line-of-sight and visibility
- repeated graph expansion
- hierarchy candidate discovery
- common post-emit reductions
- probe/ray input construction

## Proposed Surface Areas

### 1. Bounded Any-Hit / Early-Exit Traversal

#### Purpose

Answer whether a probe has at least one valid hit without enumerating every
hit.

#### Proposed API Direction

Preferred first API:

```python
rt.ray_triangle_any_hit(
    t_min=0.0,
    t_max=1.0,
    include_endpoints=True,
)
```

Possible compatibility option:

```python
rt.ray_triangle_hit_count(
    exact=False,
    stop_after_first=True,
)
```

Recommendation: create a separate predicate name, `ray_triangle_any_hit`, to
avoid overloading hit-count semantics.

#### Proposed Kernel Sketch

```python
@rt.kernel
def robot_link_blocked_any_hit():
    link_rays = rt.input("link_rays", rt.Rays3D, role="probe")
    obstacles = rt.input("obstacles", rt.Triangles3D, role="build")

    candidates = rt.traverse(link_rays, obstacles, accel="bvh")
    blocked = rt.refine(
        candidates,
        predicate=rt.ray_triangle_any_hit(t_min=0.0, t_max=1.0),
    )

    return rt.emit(blocked, fields=["ray_id", "blocked", "hit_count_limited"])
```

#### Output Contract

Minimum row fields:

- `ray_id`
- `blocked` or `any_hit`
- `hit_count_limited`

Rules:

- `hit_count_limited` is `0` if no valid hit exists.
- `hit_count_limited` is `1` if one or more valid hits exist.
- first blocker ID is not part of the first release contract.
- exact hit distance is optional and should be deferred unless all backends can
  reproduce it reliably.

#### Apps And Scenarios

- robot collision yes/no
- line-of-sight blockage
- visibility/camera coverage
- sensor coverage
- RF or acoustic direct-path blockage
- broad-phase culling

#### Existing-App Value

- high value for robot collision screening
- possible internal acceleration for visual demos, but no renderer claim
- no direct impact on DB, graph, or nearest-neighbor apps
- reuses design precedent from segment/polygon any-hit rows

#### Difficulty

Medium.

CPU/oracle is straightforward. Cross-backend semantic parity is the main risk.

### 2. Line-Of-Sight / Visibility Rows

#### Purpose

Offer a standard-library workload that builds on any-hit.

#### Proposed API Direction

```python
rows = rt.visibility_rows(
    observers=observer_points,
    targets=target_points,
    blockers=triangles,
    backend="auto",
)
```

This should be standard library first, not language core.

#### Output Contract

Minimum row fields:

- `observer_id`
- `target_id`
- `visible`
- `blocked`

Deferred fields:

- `blocker_id`
- `hit_t`

These require deterministic first-hit semantics and should not be in the first
release unless parity is proven.

#### Apps And Scenarios

- robot perception
- navigation waypoint visibility
- transmitter/receiver direct-path screening
- acoustic source/listener direct-path screening
- camera-zone coverage
- terrain/viewshed-lite queries

#### Existing-App Value

- high for robot/sensor applications
- useful for future app demos
- must not be described as rendering shadows or AO

#### Difficulty

Low-to-medium after any-hit exists.

### 3. Bounded Emitted-Row Reductions

#### Purpose

Reduce repeated Python boilerplate after RTDL emits rows.

#### Proposed API Direction

```python
rt.reduce_rows(
    rows,
    group_by=("pose_id",),
    op="any",
    value="blocked",
    output_field="pose_collides",
)
```

Supported first operations:

- `any`
- `count`
- `sum`
- `max`
- `min`

Recommendation: Python helper first. Native acceleration only after evidence
shows reductions dominate runtime.

#### Apps And Scenarios

- Hausdorff max-distance reduction
- outlier neighbor counts
- DBSCAN core-point counts
- robot pose collision flags
- Barnes-Hut vector sums later

#### Existing-App Value

High ergonomics across v0.8 apps.

#### Difficulty

Low as Python helper. Medium-to-high as native feature due to grouping,
ordering, and floating-point determinism.

### 4. Multi-Hop Graph As Python-Orchestrated ITRE

#### Purpose

Support repeated graph expansion while keeping Python in control of state.

#### Proposed API Direction

No device recursion.

Possible helper:

```python
rt.iterative_rows(
    initial=frontier,
    step=bfs_step_kernel,
    max_steps=depth,
    stop_when_empty=True,
)
```

This should start as a Python orchestration helper or tutorial pattern.

#### Apps And Scenarios

- multi-hop BFS
- bounded reachability
- graph influence propagation
- motif/wedge exploration

#### Existing-App Value

High for the graph BFS line. It makes the graph workload more app-usable
without changing backend execution semantics.

#### Difficulty

Medium as Python orchestration. High and not recommended as device recursion.

### 5. Hierarchical Candidate Filtering

#### Purpose

Represent hierarchy levels as typed rows and emit candidate node rows.

#### Proposed API Direction

Future typed inputs:

- `NodeAABB2D`
- `NodeAABB3D`
- `TreeNode2D`
- `TreeNode3D`

Future predicate:

```python
rt.node_candidate_rows(
    max_level="params.max_level",
    max_distance="params.discovery_radius",
)
```

#### Apps And Scenarios

- Barnes-Hut candidate levels
- broad-phase collision culling
- adaptive spatial search
- level-of-detail proximity queries

#### Existing-App Value

Very high for Barnes-Hut. Medium for robot collision and proximity apps.

#### Difficulty

High. This needs a separate contract before implementation.

### 6. Non-Rendering Probe Generation Helpers

#### Purpose

Reduce boilerplate when apps construct common probe rows.

#### Proposed API Direction

```python
rt.make_los_rays(observers, targets)
rt.make_link_edge_rays(links, poses)
rt.make_sensor_fan_rays(origin, angles, max_distance)
```

These helpers produce typed RTDL input rows. They do not change backend
semantics.

#### Apps And Scenarios

- LOS and visibility
- robot link collision
- sensor coverage
- terrain visibility
- RF/acoustic direct-path screening

#### Difficulty

Low-to-medium. The main risk is API clutter; keep helpers general.

## Implementation Plan

### Goal A: Formal Any-Hit Contract

Deliverables:

- new contract doc for `ray_triangle_any_hit`
- exact row schema
- exact ray interval semantics
- endpoint inclusion rule
- self-hit epsilon rule
- degenerate input behavior
- CPU/oracle expected behavior
- native backend parity requirements

Acceptance:

- 2+ AI consensus
- at least one Claude/Gemini review
- no implementation yet

### Goal B: CPU/Python Reference And CPU/Oracle Any-Hit

Deliverables:

- Python reference implementation
- CPU/oracle implementation if applicable to current backend architecture
- unit tests for edge cases
- no Embree/OptiX/Vulkan claim yet

Acceptance:

- full local test pass
- targeted any-hit correctness suite
- correctness report
- Claude/Gemini review

### Goal C: Visibility Rows Standard-Library App

Deliverables:

- `make_los_rays` helper or local app-level equivalent
- `visibility_rows` helper or example
- runnable example using CPU/Python reference and CPU/oracle
- docs explaining non-rendering boundary

Acceptance:

- small fixtures with exact expected rows
- no first-blocker ID claim unless proven
- no rendering terminology except explicit non-goals

### Goal D: Row Reduction Helpers

Deliverables:

- Python `reduce_rows` helper
- examples for `any`, `count`, and `max`
- update v0.8 app examples where it reduces boilerplate

Acceptance:

- deterministic output ordering
- tests for empty rows, single group, multiple groups
- docs clarify this is post-emit reduction, not payload state

### Goal E: Native Any-Hit Backend Bring-Up

Order:

1. Embree
2. OptiX
3. Vulkan

Deliverables per backend:

- backend implementation
- parity suite against CPU/oracle
- sparse-hit and dense-hit performance tests
- backend-specific report

Acceptance:

- no backend is advertised until parity passes
- Linux is primary validation platform
- macOS/Windows boundaries documented separately

### Goal F: Multi-Hop Graph Orchestration Study

Deliverables:

- design doc for repeated ITRE loops
- BFS multi-hop app sketch
- cost model separating RTDL kernel time and Python state time

Acceptance:

- no device recursion
- no persistent GPU queue claim
- graph correctness oracle on small graphs

### Goal G: Hierarchy Contract Study

Deliverables:

- typed node-row proposal
- Barnes-Hut pressure analysis
- broad-phase collision pressure analysis
- exact boundaries for what RTDL owns versus Python

Acceptance:

- no N-body solver claim
- no physics framework claim
- clear row schema before implementation

## Correctness Strategy

### Any-Hit Fixtures

Minimum cases:

- no triangle
- one triangle hit
- one triangle miss
- multiple triangles hit
- blocker behind ray origin
- blocker beyond `t_max`
- blocker exactly at `t_min`
- blocker exactly at `t_max`
- ray parallel to triangle plane
- degenerate triangle
- duplicate triangles

### Visibility Fixtures

Minimum cases:

- one observer, one target, no blocker
- one observer, one target, one blocker
- blocker behind target
- blocker behind observer
- multiple observers
- multiple targets
- self-hit epsilon

### Reduction Fixtures

Minimum cases:

- empty rows
- one group
- many groups
- missing value field
- boolean `any`
- count
- max/min
- stable ordering

## Performance Strategy

Performance reports must separate:

- setup/preparation time
- query time
- Python orchestration time
- Python reduction time
- total app time

Any-hit performance should compare:

- full `ray_triangle_hit_count`
- `ray_triangle_any_hit`
- CPU brute force
- native backend versions only after parity

Datasets:

- sparse-hit: most rays unobstructed
- dense-hit: most rays blocked early
- mixed-hit: realistic distribution

Expected performance claim:

- any-hit may improve cases where many rays are blocked early
- any-hit may not help sparse-hit cases
- no broad speedup claim without evidence

## Documentation Plan

Docs to add or update:

- language contract for `ray_triangle_any_hit`
- standard-library docs for `visibility_rows`
- app tutorial for LOS/visibility
- feature home for any-hit / visibility
- capability boundary update
- release-facing examples only after runnable examples exist

Docs must state:

- not a renderer
- not shader callbacks
- not mutable payloads
- not recursive rays
- Python owns app policy

## Review And Consensus Gates

Every goal in this task requires:

- at least 2 AI consensus
- at least one Claude or Gemini review
- Codex consensus record
- local test evidence before closure

Native backend goals additionally require:

- Linux validation on `lestat-lx1`
- backend availability probe
- parity report against CPU/oracle

## Risks

### Scope Creep

Risk: any-hit turns into user-exposed shader hooks.

Mitigation: public API must be predicate/row based only.

### Determinism

Risk: first-hit identity or hit distance differs across backends.

Mitigation: first release only claims boolean any-hit and limited count.

### Performance Overclaim

Risk: early-exit is faster only on dense-hit cases.

Mitigation: always report sparse/dense/mixed cases separately.

### Backend Drift

Risk: CPU/oracle and native backends disagree on endpoint or epsilon behavior.

Mitigation: formal contract before native implementation.

### API Clutter

Risk: standard-library helpers become one-off app shortcuts.

Mitigation: only add helpers that serve multiple apps.

## Final Recommendation

Approve this task as the post-v0.8 minimal ITRE extension line.

Start with:

1. Goal A: formal `ray_triangle_any_hit` contract.
2. Goal B: CPU/Python reference and CPU/oracle correctness.
3. Goal C: LOS / visibility rows as the first user-facing app.

Defer:

- native backend any-hit until CPU/oracle is stable
- multi-hop graph helper until API placement is decided
- hierarchy support until a typed node-row contract is written
