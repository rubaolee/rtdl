# V4 Goal4679 Relation-Topology Target Selection

Date: 2026-06-25

Status:

```text
goal4679_select_relation_topology_same_primitive_target_no_pod_no_release
```

## Decision

Select the next V4 engineering target as:

```text
SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR
```

Proposed V4 surface name:

```text
v4_shape_pair_relation_active_count_2d_prepared_left_executor
```

The benchmark probe is `spatial_rayjoin.overlay_active_count`, but the engine
target is not RayJoin. The target is a generic shape-pair relation/topology
operator.

## Why This Target

The V4 design allows generic continuation/relation operators, not app-identity
native kernels. Shape-pair active count fits that rule if it is exposed as a
generic relation/topology operator.

The historical codebase already contains an app-agnostic native executor family
for this shape:

- `rtdl_optix_prepared_shape_pair_relation_active_device_prepared_left_executor_prepare`
- `rtdl_optix_prepared_shape_pair_relation_active_device_prepared_left_executor_run`
- `rtdl_optix_prepared_shape_pair_relation_active_device_prepared_left_executor_destroy`

Historical Goal3737 also checked that this executor family did not contain
RayJoin/GIS/county/soil/overlay app identity strings in the native engine.

## Integrity Lock

This is not a clean new V4 speed lever yet.

The V2.14 audit says V2.14 already had prepared shape-pair active-count routes
for the spatial/RayJoin family. Therefore:

- V4 speed credit requires a same-primitive comparison against the strongest
  V2.14 denominator.
- Front-door migration does not count as V4 speed.
- Partner migration does not count as V4 speed.
- Historical OptiX-vs-Numba speedups do not prove V4-over-V2.14 speed.

## Frozen Bars For The Next Measurement

Goal4680 must freeze the concrete local/static gate before any POD run. Any
later performance measurement must satisfy all of these before it can count as
V4 speed evidence:

| Gate | Required value |
| --- | ---: |
| correctness parity | required |
| V4/V2.14 same-primitive hot ratio | >= 1.20x |
| V4/V2.14 same-primitive wall ratio | >= 1.10x |
| V4/V3.0.2 hot parity floor | >= 0.98x |
| hot-path host row-stream materialization | forbidden |
| partner migration counted as speed | false |

If those bars are not met, the result may still be useful V4 productization or
coverage work, but it must not be used as a formal V4 speed win.

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No. The dangerous mistake would be to call spatial/RayJoin a clean second V4
win even though V2.14 already had same-family primitives.

2. If yes, what actions made it stupid?

Not applicable. The avoided stupid action was selecting an app identity and
then pretending a same-primitive migration was new V4 performance.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes. Select the generic relation/topology operator and force a V2.14
same-primitive denominator before any POD work.

4. Should I try a different path to solve the real problem?

Yes. Goal4680 must build the local/static V4 frontdoor and protocol gate. Only
after that gate passes should Goal4681 request a focused POD run.

## Non-Authorization

This goal does not authorize:

- V4 release.
- POD spending.
- public speedup wording.
- whole-app high-performance wording.
- broad V4-over-V2/V3 claims.
- raw RayJoin native kernels.
- app-identity native kernels.
- partner migration as speed evidence.
- Tier-3 callbacks, PTX module linking, C ABI, embedding, or non-Python hosts.

## Files

- Code:
  `src/rtdsl/v4_goal4679_relation_topology_target.py`
- Tests:
  `tests/v4_goal4679_relation_topology_target_test.py`
- Evidence:
  `future/v4/evidence/v4_goal4679_relation_topology_target_selection_2026-06-25.json`

## Next Work

Goal4680: create the local/static frontdoor and protocol gate for
`v4_shape_pair_relation_active_count_2d_prepared_left_executor`.

Goal4680 must not run POD. It must name the exact V2.14 denominator route,
confirm app-name-free V4 surface boundaries, and freeze correctness/performance
commands for a later focused POD run.
