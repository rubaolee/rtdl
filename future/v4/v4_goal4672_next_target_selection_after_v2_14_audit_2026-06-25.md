# V4 Goal4672 Next Target Selection After V2.14 Audit

Date: 2026-06-25

Status: `goal4672_target_selection_complete_no_clean_existing_app_target`

Decision label:

```text
no_clean_existing_app_second_target_found__new_generic_runtime_lever_required
```

Machine evidence:

```text
future/v4/evidence/v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.json
```

## Decision

Goal4672 does not select an existing benchmark app as the next clean second V4
performance target.

That is not a retreat into wording. It is the direct result of the V2.14
primitive audit: V2.14 already had a primitive or explicit mixed partner route
for every promoted benchmark app. A clean V4 target now requires either:

1. a generic runtime/primitive lever absent in V2.14; or
2. a material same-primitive improvement over the V2.14 app route under a frozen
   same-hardware protocol.

Without one of those, the work is productization/parity, not V4 performance.

## Rejected Existing Targets

| App | Why rejected for clean second V4 win |
| --- | --- |
| `rt_dbscan` | Goal4670/4671 no-go; best true grouped-union probe remains below `1.20x`, and V2.14 already had count-threshold plus grouped-union routes. |
| `robot_collision` | V2.14 already had prepared RTDL/OptiX any-hit collision flags and scalar count. It can only be a same-primitive improvement experiment, not a clean new V4 win. |
| `raydb_style` | Goal4669 shows V4/V2.14 regression, and V2.14 already used `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`. |
| `triangle_counting` | Goal4669 shows V4/V3.0.2 regression, and V2.14 already used `ray_triangle_weighted_any_hit_sum_3d`. |
| `librts_spatial_index` | Goal4669 shows parity, and V2.14 already used prepared AABB index query. |
| `rtnn` | Goal4660/4661 serious rows are parity/slower, and V2.14 already had prepared ranked-summary aggregate. |
| `hausdorff_xhd` | Already the single true V4 app candidate win in Goal4669; it cannot serve as the second independent win. |
| `barnes_hut` | Existing aggregate-tree fused weighted-vector implementation was rejected for V4.0 as Barnes-Hut/N-body-specific and CUDA-only, not a generic RT-core Tier-2 operator. |
| `spatial_rayjoin` | Current V4 has no route; a target would first need a new generic relation-topology operator and protocol. |
| `contact_manifold` | V2.14 already had bounded witness collect and AABB broadphase primitives; a target needs a new full generic route or material bounded-collect improvement. |

## What Goal4673 Must Do

Goal4673 must not start with a POD run. It must first choose one target class
under this gate:

- name the generic operator or same-primitive improvement target;
- prove whether V2.14 already had the same primitive route;
- state whether the goal is a new runtime lever or a same-primitive improvement;
- freeze V2.14, V3.0.2, and V4 denominators;
- freeze correctness parity;
- freeze the numeric material-speed bar before running;
- prove the operator is not app-identity;
- record why partner migration cannot count.

Allowed target classes:

- new generic relation/topology operator for `spatial_rayjoin`-like workloads;
- new generic contact/witness pipeline beyond V2.14 bounded collect-k;
- material same-primitive improvement over V2.14 for an existing primitive;
- re-audited hierarchical aggregate operator only if algorithmic genericity and
  device-input gates pass. The existing aggregate-tree fused weighted-vector
  implementation does not pass as-is.

Forbidden target classes:

- `robot_collision` clean-new-win claim without the same-primitive V2.14
  denominator;
- RTDBSCAN direct-status special-contract rows;
- Barnes-Hut or DBSCAN app-identity kernels;
- partner certification or front-door cleanup counted as speed;
- fixing `0.98x` parity/regression rows as the whole V4 performance story.

## Goal-Level Decision Audit

1. Was I being stupid?
   - Yes.
2. If yes, what action made it stupid?
   - The stupid path was to keep searching for a convenient existing app target
     after the V2.14 audit showed the plausible candidates mostly reuse V2.14
     primitives.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes. Declare that no clean existing app target qualifies, then require
     Goal4673 to select a real new generic runtime lever or a material
     same-primitive improvement.
4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4673 starts with target design/selection, not POD measurement.

## Non-Authorization

This goal does not authorize V4 release, public speedup wording, whole-app
high-performance wording, a selected existing app target, POD spend, C ABI,
embedding, non-Python hosts, true zero-copy, arbitrary callbacks, or
app-specific native kernels.
