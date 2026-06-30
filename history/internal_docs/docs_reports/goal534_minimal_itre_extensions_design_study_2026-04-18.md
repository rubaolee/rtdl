# Goal 534: Minimal ITRE Extensions Design Study

Date: 2026-04-18
Status: draft pending external review
Context: follow-up to Goal533 brainstorm review

## Decision Frame

The rejected brainstorm correctly identified a real gap: ITRE is currently a
single-pass row-emission model, while low-level RT APIs expose richer ray
lifecycle control.

The wrong part was the direction: rendering shader hooks, mutable radiance
payloads, recursive ray spawning, BRDFs, skyboxes, path tracing, and global
illumination are outside RTDL's current product boundary.

The right next question is narrower:

> What minimal non-rendering ITRE extensions would make RTDL more useful for
> spatial/query workloads while preserving the row-emission model?

This report studies four concrete pressure areas:

- bounded any-hit / early-exit traversal
- line-of-sight and visibility rows
- multi-hop graph traversal as Python-orchestrated multi-stage ITRE
- hierarchical candidate filtering

It also names two supporting surfaces that may be standard-library helpers
rather than language features:

- bounded emitted-row reductions
- non-rendering probe/ray generation helpers

## Summary Recommendation

Do **not** implement shader hooks or mutable payloads.

Implement in this order:

1. **Bounded any-hit / early-exit traversal** as the first real feature.
2. **LOS / visibility rows** as a standard-library workload built on any-hit.
3. **Python-orchestrated multi-stage ITRE helpers** for graph and iterative
   apps, without device recursion.
4. **Hierarchical candidate filtering** only after Barnes-Hut and similar apps
   prove a reusable typed node-row contract.
5. **Bounded reductions** only where they are backend-neutral and row-based,
   not mutable shader payloads.

## Candidate 1: Bounded Any-Hit / Early-Exit Traversal

### What It Is

A traversal policy that returns as soon as the first valid hit is found for a
probe, instead of enumerating all hits.

Conceptual user-facing shape:

```python
hits = rt.refine(
    candidates,
    predicate=rt.ray_triangle_any_hit(max_t=1.0),
)
```

or:

```python
hits = rt.refine(
    candidates,
    predicate=rt.ray_triangle_hit_count(exact=False, stop_after_first=True),
)
```

The exact API should be decided later. The important semantics are:

- input is still typed probes/build data
- traversal is still one ITRE pass
- refinement is still bounded and exact for the documented predicate
- output is still rows, e.g. `{ray_id, any_hit, first_t?}`
- Python still owns app-level decisions

### Apps And Scenarios

- robot collision screening: answer "does this pose collide?" without counting
  every obstacle hit
- line-of-sight: answer "is target visible from source?"
- sensor coverage: determine which sample points are blocked by walls or
  terrain
- wireless/acoustic occlusion: determine whether a direct path is blocked
- spatial security/surveillance: camera-to-target visibility checks
- broad-phase simulation culling: skip expensive work when any blocker exists

### Existing Workload Impact

| Existing RTDL area | Impact |
| --- | --- |
| robot collision app | high value; current `ray_triangle_hit_count` can over-compute when only collision yes/no is needed |
| visual demos | possible internal acceleration, but docs must keep demo boundary: RTDL query core only, Python owns rendering/output |
| segment/polygon any-hit history | aligns with existing any-hit row concept; can reuse old semantics as design precedent |
| DB workloads | no direct impact |
| graph BFS / triangle count | no direct impact |
| nearest-neighbor apps | no direct impact |

### Usefulness

High. This is the smallest feature with clear app value and clear RT hardware
fit. It can reduce unnecessary hit enumeration and matches RT backends' natural
early-termination capability.

### Challenge

Medium.

CPU/oracle is straightforward: scan candidates and stop after the first valid
hit per probe.

Native backend challenge:

- Embree: map to occlusion-style traversal or terminate after first accepted hit
- OptiX: use any-hit/termination internally, but do not expose shader hooks to
  users
- Vulkan: implement equivalent early-exit semantics and prove parity

The hard part is not the user API. The hard part is guaranteeing identical row
semantics across CPU/oracle, Embree, OptiX, and Vulkan.

### Correctness Tests

- zero blockers: returns visible / no hit
- one blocker: returns blocked / hit
- multiple blockers: still returns one bounded result, not all hits
- blocker outside ray segment: no hit
- blocker exactly at endpoint: define and test inclusive/exclusive boundary
- degenerate triangle / segment: explicit error or documented behavior
- parity across CPU/oracle first; native parity later

### Performance Tests

Use two shapes:

- sparse-hit: mostly no blockers, measures overhead versus full hit-count
- dense-hit: early blockers common, should show benefit over full hit-count

Report:

- setup time
- query time
- total time
- hits per ray distribution
- backend
- host

No broad speedup claim until compared with full hit-count and an external
baseline where appropriate.

## Candidate 2: Line-Of-Sight / Visibility Rows

### What It Is

A standard-library workload built on bounded any-hit.

Conceptual user-facing shape:

```python
rows = rt.visibility_rows(
    observers=observer_points,
    targets=target_points,
    blockers=triangles,
    backend="auto",
)
```

Output rows:

```text
observer_id, target_id, visible, blocker_id?, hit_t?
```

This should likely be a standard-library helper first, not a new core language
construct. It composes:

- Python builds observer-target rays
- RTDL runs bounded any-hit against blocker geometry
- Python consumes visibility rows

### Apps And Scenarios

- robot perception: can a robot sensor see a target point?
- autonomous navigation: is a waypoint visible from current pose?
- wireless/RF direct-path screening: is transmitter-receiver line blocked?
- acoustic direct-path screening: is source-listener line blocked?
- security/camera planning: which cameras see which zones?
- game/simulation AI: line-of-sight checks without becoming a game engine
- GIS/terrain viewshed lite: bounded visibility over simplified geometry

### Existing Workload Impact

| Existing RTDL app | Impact |
| --- | --- |
| robot collision screening | high; same ray/triangle foundation, but answers visibility/blocked rather than collision counts |
| Barnes-Hut | low direct impact |
| Hausdorff | none |
| ANN/outlier/DBSCAN | none |
| graph workloads | possible use as edge construction pre-pass, but not core |
| visual demos | could replace shadow checks internally, but must not become a renderer feature |

### Usefulness

High. LOS/visibility is a clean public app story because it is non-rendering,
common, and maps directly to RT traversal.

### Challenge

Low-to-medium if built on any-hit.

Potential pitfalls:

- ray segment parameter convention
- self-intersection epsilon
- blocker metadata mapping
- whether first blocker ID is deterministic across backends

Recommendation: first release only `visible` and maybe `hit_count_limited=0/1`.
Defer deterministic first-blocker ID unless all backends can guarantee it.

### Correctness Tests

- one observer, one target, no blocker
- one blocker between observer and target
- blocker behind target
- blocker behind observer
- multiple targets per observer
- multiple observers per target
- self-blocking epsilon case
- 2D segment/polygon LOS and 3D ray/triangle LOS should be separate contracts

### Performance Tests

Compare:

- RTDL any-hit visibility
- RTDL full hit-count used as a visibility proxy
- simple CPU brute force
- external geometry library if available for the specific 2D/3D case

Expected outcome:

- useful speedup should appear when many rays have early blockers or blocker
  geometry is large enough to benefit from acceleration structures
- no claim if the Python ray-construction step dominates small cases

## Candidate 3: Multi-Hop Graph As Python-Orchestrated Multi-Stage ITRE

### What It Is

Not device-side recursive rays.

A standard orchestration pattern for repeated ITRE kernels:

```text
frontier rows -> RTDL traversal/refine -> next frontier rows -> Python loop
```

Conceptual helper:

```python
state = rt.iterative_rows(
    initial=frontier,
    step=bfs_step_kernel,
    max_steps=depth,
    stop_when_empty=True,
)
```

The helper can live in Python first. It records and standardizes the pattern,
but each heavy step remains an RTDL kernel.

### Apps And Scenarios

- BFS beyond one bounded expansion
- multi-hop reachability
- shortest-path-like bounded frontier expansion, if weights are simple and
  reductions stay in Python
- graph influence propagation where each hop is candidate generation
- graph triangle/wedge exploration with iterative filtering
- spatial graph construction followed by bounded graph traversal

### Existing Workload Impact

| Existing RTDL area | Impact |
| --- | --- |
| graph BFS | high; current BFS can be made more app-usable as repeated frontier expansion |
| triangle count | medium; may help multi-stage motif exploration later |
| DB workloads | possible future semi-join style repeated filters, but not first target |
| Barnes-Hut | conceptually related to level-by-level traversal, but not graph-specific |
| nearest-neighbor apps | low |

### Usefulness

Medium-to-high for graph apps. It makes RTDL more useful without changing
backend execution first.

### Challenge

Medium if kept as Python orchestration.

High if attempted as device recursion or persistent GPU queues. That should be
avoided for now.

Key design issue:

- what state is allowed between iterations?

Recommended answer:

- Python owns state tables, visited sets, stopping conditions, and reductions
- RTDL owns each per-step traversal/refine kernel

This stays aligned with v0.8's app-building contract.

### Correctness Tests

- one-hop BFS equals current BFS
- two-hop BFS over small graph equals Python oracle
- cycle graph with visited set prevents infinite expansion
- disconnected graph returns empty frontier
- depth limit is honored exactly
- deterministic row ordering or documented sorted output

### Performance Tests

Measure separately:

- per-step RTDL query time
- Python frontier management time
- total loop time
- frontier sizes per depth

Do not hide Python orchestration cost. If Python dominates, report it honestly.

## Candidate 4: Hierarchical Candidate Filtering

### What It Is

A way to represent hierarchy levels as typed rows and run bounded candidate
filtering level by level.

This is not recursive traversal inside the backend. It is a row-emitting
contract for hierarchy nodes:

```text
body rows + node rows -> candidate node rows
candidate node rows + Python opening rule -> accepted nodes / expanded nodes
expanded nodes -> next RTDL pass
```

Potential future typed inputs:

- `Box2D` / `Box3D`
- `TreeNode2D` / `TreeNode3D`
- `SphereBound`
- `NodeAABB`

Potential output rows:

```text
probe_id, node_id, level, distance_bound, accepted_candidate
```

### Apps And Scenarios

- Barnes-Hut candidate filtering
- fast multipole style candidate staging, if kept bounded
- broad-phase collision culling with BVH or spatial tree levels
- level-of-detail proximity queries
- adaptive spatial search where Python controls expansion
- spatial indexing experiments without becoming a full index framework

### Existing Workload Impact

| Existing RTDL app | Impact |
| --- | --- |
| Barnes-Hut force app | very high; current app explicitly says RTDL lacks tree-node primitives and opening predicates |
| robot collision | medium; broad-phase hierarchy could cull obstacle groups before ray checks |
| Hausdorff / ANN | medium; hierarchy could become candidate-set construction later, but current apps already work |
| outlier / DBSCAN | medium; hierarchy can accelerate neighborhood candidates but requires careful exactness |
| graph workloads | low direct impact |
| DB workloads | low direct impact |

### Usefulness

High long-term, but not first.

This is the most important path if RTDL wants to support more simulation and
spatial-index workloads while staying non-rendering.

### Challenge

High.

Reasons:

- need stable typed hierarchy representation
- need exact correctness contract for approximate/bounded filtering
- need deterministic output across backends
- Python opening rules may still dominate runtime
- native backends need efficient node layouts
- the boundary between "RTDL kernel" and "full simulation/index framework" is
  easy to blur

### Correctness Tests

- fixed small quadtree/octree fixture
- known body-node candidate rows
- opening rule applied in Python matches oracle
- level limit honored
- empty tree / single-node tree
- overlapping node bounds
- degenerate zero-area node

### Performance Tests

Report separately:

- tree construction time in Python
- RTDL candidate-generation time
- Python opening/filter/reduction time
- total app time

This separation is mandatory. Otherwise the feature may look faster or slower
for the wrong reason.

## Supporting Surface A: Bounded Emitted-Row Reductions

### What It Is

Backend-neutral reductions over emitted rows, not mutable ray payloads.

Examples:

```python
rt.reduce_rows(rows, group_by="probe_id", op="any")
rt.reduce_rows(rows, group_by="probe_id", op="count")
rt.reduce_rows(rows, group_by="probe_id", op="max", value="distance")
rt.reduce_rows(rows, group_by="body_id", op="sum_vector", value=("fx", "fy"))
```

This could be:

- a Python standard-library helper first
- a native backend feature only after repeated evidence shows Python reduction
  dominates

### Apps And Scenarios

- Hausdorff: max nearest-neighbor distance
- outlier detection: neighbor count per point
- DBSCAN: count neighbors for core detection
- robot collision: any hit per pose/link
- Barnes-Hut: vector sum per body, eventually
- DB grouped count/sum: already related but under DB-specific contract

### Existing Workload Impact

Very high ergonomics. It reduces repeated app boilerplate.

Performance impact depends on whether reduction is moved into native backend.
As a Python helper, usefulness is high but speedup is not guaranteed.

### Challenge

Low as Python helper.

Medium-to-high as native backend primitive, especially for:

- stable grouping
- floating-point determinism
- vector reductions
- large group counts

### Recommendation

Start as standard library, not language core.

Do not call it payload state. It is row reduction after emit, preserving ITRE.

## Supporting Surface B: Non-Rendering Probe Generation Helpers

### What It Is

Helpers that build probe rays or query records for non-rendering workloads.

Examples:

```python
rt.make_los_rays(observers, targets)
rt.make_sensor_fan_rays(origin, angles, max_distance)
rt.make_link_edge_rays(robot_links)
```

These should produce typed RTDL input rows. They should not introduce
Monte-Carlo rendering distributions, BRDF sampling, hemisphere shading normals,
or depth-of-field.

### Apps And Scenarios

- robot link ray construction
- LOS observer-target rays
- sensor fan coverage
- terrain visibility samples
- RF/acoustic direct-path candidates

### Existing Workload Impact

High for usability. Current apps often do Python fixture construction manually.
Reusable probe builders can reduce burden without changing backend semantics.

### Challenge

Low-to-medium.

Most difficulty is API design and avoiding domain-specific one-off helpers.

### Recommendation

Standard-library helper only. Keep outputs inspectable as normal typed rows.

## Feature Ranking

| Candidate | Usefulness | Challenge | Existing-app benefit | First implementation type | Recommendation |
| --- | --- | --- | --- | --- | --- |
| any-hit / early-exit traversal | high | medium | high for robot/LOS | core predicate/traversal option | do first |
| LOS / visibility rows | high | low-medium | high for robot/sensor apps | standard-library workload | do after any-hit |
| emitted-row reductions | high | low as Python, medium-high native | high across v0.8 apps | standard-library helper first | do soon, no native claim yet |
| multi-hop graph orchestration | medium-high | medium | high for graph BFS apps | Python orchestration helper | do after API design |
| probe generation helpers | medium-high | low-medium | high ergonomics | standard-library helper | do opportunistically |
| hierarchical candidate filtering | high long-term | high | very high for Barnes-Hut | design first, then typed input | defer until contract is precise |

## Existing v0.8 App Impact Matrix

| Existing app | any-hit | LOS / visibility | row reductions | multi-hop graph | hierarchy |
| --- | --- | --- | --- | --- | --- |
| Hausdorff distance | no direct benefit | none | useful for max-distance reduction | none | possible future candidate indexing |
| ANN candidate search | no direct benefit | none | useful for recall/quality summaries | none | possible future candidate construction |
| Outlier detection | no direct benefit | none | useful for density counts | none | possible future neighborhood acceleration |
| DBSCAN clustering | no direct benefit | none | useful for core-point counts | none | possible future neighborhood acceleration |
| Robot collision screening | strong benefit | strong benefit | useful for pose/link collision flags | none | possible broad-phase obstacle culling |
| Barnes-Hut force approximation | low direct benefit | none | useful for vector force sums later | possible staged levels | strongest hierarchy pressure |

## Language Feature Or Standard Library?

| Surface | Category | Reason |
| --- | --- | --- |
| any-hit / early-exit traversal | language/runtime predicate or traversal option | changes backend execution semantics and must be parity-tested |
| LOS / visibility rows | standard-library workload | composition of ray generation plus any-hit rows |
| multi-hop graph orchestration | standard-library orchestration helper first | Python owns loop/state; RTDL owns each step |
| hierarchical candidate filtering | future language input/predicate surface | needs typed node records and backend lowering |
| emitted-row reductions | standard-library helper first | preserves emit-then-reduce model |
| probe generation helpers | standard-library helper | creates typed inputs, not backend semantics |

## Non-Goals

These remain out of scope:

- shader callbacks exposed to users
- mutable ray payloads
- device-side recursive ray spawning
- path tracing
- global illumination
- ambient occlusion as a rendering feature
- BRDF/material/skybox APIs
- a full simulation framework

## Proposed Goal Sequence

### Goal A: Any-Hit Contract

Write the formal contract for bounded any-hit / early-exit traversal:

- supported geometry
- ray segment boundary convention
- output row schema
- deterministic fields
- CPU/oracle truth path
- native backend requirements

### Goal B: CPU/Oracle Any-Hit Implementation

Implement the CPU/oracle path and tests only.

Acceptance:

- exact parity against brute force
- all edge cases documented
- no native backend claim

### Goal C: LOS / Visibility Standard-Library App

Build `visibility_rows` or equivalent using CPU/oracle any-hit.

Acceptance:

- runnable example
- correctness report
- clear non-rendering scenarios

### Goal D: Native Backend Bring-Up

Add Embree, then OptiX, then Vulkan any-hit support, one backend at a time.

Acceptance:

- parity against CPU/oracle
- dense/sparse performance report
- no unsupported deterministic first-hit claim

### Goal E: Multi-Stage ITRE Design

Design Python-orchestrated repeated-kernel helpers for BFS and hierarchy-like
apps. Do not implement device recursion.

### Goal F: Hierarchy Contract Study

Use Barnes-Hut and broad-phase collision as the pressure tests. Decide whether
typed tree-node inputs belong in RTDL.

## Final Recommendation

The next implementable feature should be:

> bounded any-hit / early-exit traversal for ray/triangle or segment/polygon
> visibility-style queries, CPU/oracle first.

The next design-only work should be:

> a non-rendering multi-stage ITRE design for graph and hierarchy apps.

This path keeps the useful part of the brainstorm while rejecting the parts
that would turn RTDL into a renderer or shader language.
