# Minimal ITRE Extension Demo Kernels

Date: 2026-04-18
Status: design sketch, not implemented

This page shows what the proposed post-`v0.8.0` minimal ITRE extensions could
look like before implementation.

These snippets are **not runnable RTDL code today**. They are API sketches for
review. The goal is to preserve RTDL's current boundary:

- RTDL owns typed inputs, traversal, bounded refinement, and emitted rows.
- Python owns app orchestration, reductions, visualization, and domain policy.
- No shader callbacks are exposed to users.
- No mutable ray payloads are exposed to users.
- No device-side recursive ray spawning is exposed to users.
- No renderer, material system, BRDF, skybox, path tracing, or global
  illumination APIs are proposed here.

## 1. Any-Hit / Early-Exit Traversal

### Purpose

Use this when the app only needs to know whether a probe is blocked or collides,
not how many total hits exist.

Useful for:

- robot collision yes/no
- line-of-sight blockage
- sensor coverage
- RF/acoustic direct-path blockage
- broad-phase culling

### Proposed Kernel Shape

```python
import rtdsl as rt


@rt.kernel
def robot_link_blocked_any_hit():
    link_rays = rt.input("link_rays", rt.Rays3D, role="probe")
    obstacles = rt.input("obstacles", rt.Triangles3D, role="build")

    candidates = rt.traverse(link_rays, obstacles, accel="bvh")

    # Proposed: bounded early-exit predicate.
    # Semantics: emit at most one row per ray with blocked=True/False.
    blocked = rt.refine(
        candidates,
        predicate=rt.ray_triangle_any_hit(
            t_min=0.0,
            t_max=1.0,
            include_endpoints=True,
        ),
    )

    return rt.emit(
        blocked,
        fields=[
            "ray_id",
            "blocked",
            "hit_count_limited",  # 0 or 1, not full hit count
        ],
    )
```

### What Data Becomes What Data?

```text
robot link rays + obstacle triangles
  -> one bounded any-hit row per link ray
  -> Python groups rows into colliding pose IDs
```

### Why This Is Minimal

This is a new predicate/traversal option, not a shader hook. Backends may use
native early termination internally, but users still see normal RTDL rows.

### First Correctness Contract

- `blocked=False` if no valid blocker intersects the ray segment.
- `blocked=True` if one or more blockers intersect the ray segment.
- `hit_count_limited` is only `0` or `1`.
- deterministic first-blocker ID is not required in the first release.

## 2. Line-Of-Sight / Visibility Rows

### Purpose

Use this when an app needs visibility between observer-target pairs.

Useful for:

- robot perception
- waypoint visibility
- transmitter-receiver direct-path screening
- camera coverage planning
- terrain/viewshed-lite workloads

### Proposed Standard-Library Shape

This should be a standard-library helper built on any-hit, not a new language
core feature.

```python
import rtdsl as rt


def visibility_rows_app(observers, targets, blockers, *, backend="auto"):
    # Proposed helper: Python builds probe rays as typed RTDL rows.
    los_rays = rt.make_los_rays(
        observers=observers,
        targets=targets,
        max_distance_field="target_distance",
    )

    rows = rt.run(
        los_visibility_kernel,
        backend=backend,
        los_rays=los_rays,
        blockers=blockers,
    )

    # Python owns policy: convert rows into app-level visibility tables.
    return {
        (row["observer_id"], row["target_id"]): row["visible"]
        for row in rows
    }


@rt.kernel
def los_visibility_kernel():
    los_rays = rt.input("los_rays", rt.Rays3D, role="probe")
    blockers = rt.input("blockers", rt.Triangles3D, role="build")

    candidates = rt.traverse(los_rays, blockers, accel="bvh")
    blocked = rt.refine(
        candidates,
        predicate=rt.ray_triangle_any_hit(
            t_min=0.0,
            t_max="ray.max_distance",
            self_hit_epsilon=1e-6,
        ),
    )

    return rt.emit(
        blocked,
        fields=[
            "observer_id",
            "target_id",
            "visible",  # derived as not blocked
            "blocked",
        ],
    )
```

### What Data Becomes What Data?

```text
observer points + target points + blocker triangles
  -> observer-target rays
  -> visibility rows
  -> Python builds coverage/visibility decisions
```

### Why This Is Minimal

The only required core feature is any-hit. The LOS helper builds ordinary RTDL
input rows and consumes ordinary RTDL output rows.

## 3. Bounded Emitted-Row Reductions

### Purpose

Use this when many RTDL apps repeat the same safe row-reduction pattern after
emit.

Useful for:

- Hausdorff max distance
- outlier neighbor counts
- DBSCAN core-point counts
- robot link/pose collision flags
- Barnes-Hut force sums later

### Proposed Standard-Library Shape

This should start as a Python helper, not a native backend claim.

```python
import rtdsl as rt


def robot_pose_collision_app(link_hit_rows):
    # Proposed helper: post-emit row reduction.
    # This is not a mutable traversal payload.
    link_blocked = rt.reduce_rows(
        link_hit_rows,
        group_by=("pose_id", "link_id"),
        op="any",
        value="blocked",
        output_field="link_collides",
    )

    pose_blocked = rt.reduce_rows(
        link_blocked,
        group_by=("pose_id",),
        op="any",
        value="link_collides",
        output_field="pose_collides",
    )

    return tuple(pose_blocked)
```

### What Data Becomes What Data?

```text
per-link any-hit rows
  -> per-link collision rows
  -> per-pose collision rows
```

### Why This Is Minimal

The reduction happens after rows are emitted. It preserves ITRE instead of
adding mutable payload state inside traversal.

## 4. Multi-Hop Graph As Python-Orchestrated ITRE

### Purpose

Use this when an app needs repeated graph expansion, but each expansion step can
remain a normal RTDL kernel.

Useful for:

- multi-hop BFS
- bounded reachability
- influence propagation
- motif/wedge exploration

### Proposed Orchestration Shape

This is not device-side recursion. Python owns the loop and visited state.

```python
import rtdsl as rt


def bounded_reachability_app(edges, roots, *, max_depth, backend="auto"):
    visited = set(roots)
    frontier = tuple({"node_id": root} for root in roots)
    layers = []

    for depth in range(max_depth):
        rows = rt.run(
            bfs_frontier_step_kernel,
            backend=backend,
            frontier=frontier,
            edges=edges,
        )

        next_frontier = []
        for row in rows:
            dst = row["dst"]
            if dst not in visited:
                visited.add(dst)
                next_frontier.append({"node_id": dst})

        layers.append(tuple(next_frontier))
        if not next_frontier:
            break
        frontier = tuple(next_frontier)

    return {
        "visited": tuple(sorted(visited)),
        "layers": tuple(layers),
    }


@rt.kernel
def bfs_frontier_step_kernel():
    frontier = rt.input("frontier", rt.GraphFrontier, role="probe")
    edges = rt.input("edges", rt.GraphEdges, role="build")

    candidates = rt.traverse(frontier, edges, accel="bvh")
    next_edges = rt.refine(candidates, predicate=rt.bfs_frontier_edges())

    return rt.emit(next_edges, fields=["src", "dst", "edge_id"])
```

### What Data Becomes What Data?

```text
frontier nodes + graph edges
  -> next-edge rows
  -> Python updates visited/frontier state
  -> repeat until depth or empty frontier
```

### Why This Is Minimal

No recursive ray spawning. No persistent GPU queue. Each heavy step is a normal
ITRE kernel; Python owns iteration.

## 5. Hierarchical Candidate Filtering

### Purpose

Use this when an app needs hierarchy levels but can keep expansion policy in
Python.

Useful for:

- Barnes-Hut candidate levels
- broad-phase collision culling
- adaptive spatial search
- level-of-detail proximity queries

### Proposed Kernel Shape

```python
import rtdsl as rt


@rt.kernel
def body_to_tree_node_candidates():
    bodies = rt.input("bodies", rt.Points2D, role="probe")
    tree_nodes = rt.input("tree_nodes", rt.NodeAABB2D, role="build")

    candidates = rt.traverse(bodies, tree_nodes, accel="bvh")

    # Proposed bounded predicate: only emit nodes that might matter.
    # Python still applies the Barnes-Hut opening rule and force reduction.
    node_rows = rt.refine(
        candidates,
        predicate=rt.node_candidate_rows(
            max_level="params.max_level",
            max_distance="params.discovery_radius",
        ),
    )

    return rt.emit(
        node_rows,
        fields=[
            "body_id",
            "node_id",
            "node_level",
            "node_mass",
            "node_center_x",
            "node_center_y",
            "distance_bound",
        ],
    )
```

### Python App Shape

```python
def barnes_hut_stage_app(bodies, quadtree, *, backend="auto"):
    node_rows = rt.run(
        body_to_tree_node_candidates,
        backend=backend,
        bodies=bodies,
        tree_nodes=quadtree.nodes,
    )

    # Python owns opening policy and force math.
    accepted = apply_opening_rule(node_rows, theta=0.7)
    forces = reduce_forces_in_python(accepted, bodies)
    return forces
```

### What Data Becomes What Data?

```text
bodies + Python-built tree nodes
  -> body-to-node candidate rows
  -> Python applies opening rule
  -> Python computes force vectors
```

### Why This Is Minimal

RTDL emits hierarchy candidate rows. It does not become a full Barnes-Hut or
N-body solver.

## 6. Non-Rendering Probe Generation Helpers

### Purpose

Use this to reduce app boilerplate when apps repeatedly need the same typed
probe rows.

Useful for:

- LOS observer-target rays
- robot link edge rays
- sensor fan rays
- terrain visibility samples
- RF/acoustic direct-path rays

### Proposed Helper Shapes

```python
import rtdsl as rt


def build_robot_collision_inputs(robot_links, poses, obstacles):
    link_rays = rt.make_link_edge_rays(
        links=robot_links,
        poses=poses,
        output_fields=("pose_id", "link_id", "ray_origin", "ray_dir"),
    )

    return {
        "link_rays": link_rays,
        "obstacles": obstacles,
    }


def build_sensor_visibility_inputs(sensor_origin, targets, blockers):
    sensor_rays = rt.make_los_rays(
        observers=[sensor_origin],
        targets=targets,
        observer_id="sensor_0",
    )

    return {
        "los_rays": sensor_rays,
        "blockers": blockers,
    }
```

### What Data Becomes What Data?

```text
domain objects
  -> typed RTDL probe rows
  -> normal RTDL kernels
```

### Why This Is Minimal

These helpers create typed inputs. They do not add backend semantics.

## Full Example: Visibility App With Any-Hit And Reduction

This combined sketch shows the intended app style.

```python
import rtdsl as rt


@rt.kernel
def visibility_any_hit_kernel():
    los_rays = rt.input("los_rays", rt.Rays3D, role="probe")
    blockers = rt.input("blockers", rt.Triangles3D, role="build")

    candidates = rt.traverse(los_rays, blockers, accel="bvh")
    blocked = rt.refine(
        candidates,
        predicate=rt.ray_triangle_any_hit(t_min=0.0, t_max="ray.max_distance"),
    )

    return rt.emit(
        blocked,
        fields=["observer_id", "zone_id", "ray_id", "visible", "blocked"],
    )


def camera_zone_coverage_app(cameras, zones, blockers, *, backend="auto"):
    los_rays = rt.make_los_rays(observers=cameras, targets=zones)

    rows = rt.run(
        visibility_any_hit_kernel,
        backend=backend,
        los_rays=los_rays,
        blockers=blockers,
    )

    coverage = rt.reduce_rows(
        rows,
        group_by=("zone_id",),
        op="any",
        value="visible",
        output_field="covered",
    )

    return tuple(coverage)
```

Data flow:

```text
cameras + zones + blockers
  -> observer-target rays
  -> visibility rows
  -> zone coverage rows
```

The heavy query is RTDL. The app policy remains Python.

## What These Sketches Intentionally Avoid

These sketches intentionally do not include:

- `@ctx.on_closest_hit`
- `@ctx.on_miss`
- user-defined any-hit shader callbacks
- mutable `rt.Payload`
- radiance / attenuation fields
- recursive `rt.enqueue_ray`
- material or BRDF APIs
- skybox sampling
- path tracing or ambient occlusion examples

Any backend may internally use low-level RT mechanisms, but the public RTDL
surface remains typed rows and bounded predicates.
