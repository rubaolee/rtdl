# V4 Goal4672 Prerequisite: V2.14 Per-App Primitive Audit

Date: 2026-06-25

Status: `goal4672_prerequisite_v2_14_per_app_primitive_audit_complete_not_target_selection`

Decision label:

```text
v2_14_primitives_preexisting__existing_app_target_selection_requires_new_runtime_lever
```

Machine evidence:

```text
future/v4/evidence/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json
```

## Why This Audit Exists

Goal4672 cannot honestly select the next V4 performance target until the V2.14
denominator is explicit. V2.14 was not a primitive-free baseline. Many benchmark
apps already had primitive-first RTDL/OptiX routes or explicit partner routes.

Therefore V4 cannot count these as new speed wins:

- moving an existing V2.14 primitive behind a cleaner V4 front door;
- certifying a partner route that V2.14 already used;
- comparing against a weak baseline while ignoring V2.14's stronger app route;
- reporting operator-only evidence as whole-app evidence.

## Main Finding

V2.14 already had a primitive or explicit mixed partner route for every promoted
benchmark app in the current V4 app set.

That does not mean V4 has no value. It means the current V4 value is mostly:

- bounded public operator surface;
- cleaner front door and claim boundaries;
- route/productization cleanup;
- selected focused app-route progress, such as Hausdorff.

It does mean V4 cannot claim formal high-performance app-level superiority until
it proves either:

1. a generic runtime/primitive lever absent from V2.14; or
2. a material same-primitive improvement over the V2.14 app route under frozen
   same-hardware app protocol.

## V2.14 App Primitive Ledger

| App | V2.14 decision | V2.14 primitive/route | V4 implication |
| --- | --- | --- | --- |
| `hausdorff_xhd` | `primitive_first` | RTDL/OptiX active-frontier nearest-witness plus generic grouped max continuation. | V4 Hausdorff must be framed as official route/productized continuation and measured app-route improvement, not first invention of nearest-witness. |
| `spatial_rayjoin` | `mixed_explicit` | Numba bounded PIP one-shot; RTDL/OptiX prepared point/shape and segment/count primitives for repeated routes. | Current V4 has no app route; a V4 win needs a new generic relation-topology route. |
| `rt_dbscan` | `mixed_explicit` | fixed-radius count-threshold device columns plus grouped stream component labels. | Goal4670/4671 modest gains are expected because V2.14 already had the main RT pipeline. |
| `robot_collision` | `no_partner_needed` | prepared RTDL/OptiX any-hit collision flag primitive and scalar count. | Not a clean second true V4 win target by default; V2.14 already had this primitive family. |
| `contact_manifold` | `no_partner_needed` | prepared bounded contact-witness collect primitive. | Needs a new full generic contact route or a material bounded-collect improvement. |
| `raydb_style` | `primitive_first` | RTDL/OptiX grouped count/sum/min/max/avg reductions. | V4 grouped-i64 catalog work mostly productizes an existing primitive-first route. |
| `barnes_hut` | `fastest_partner_with_numba_reference` | RTDL/OptiX aggregate-frontier membership plus explicit CuPy/Numba force-vector continuation. | A true V4 opportunity remains only if a generic fused aggregate-tree weighted-vector primitive beats this route. |
| `librts_spatial_index` | `no_partner_needed` | prepared RTDL/OptiX AABB spatial-index query primitive. | V4 AABB catalog value is real, but LibRTS app parity is expected. |
| `rtnn` | `primitive_first` | prepared RTDL/OptiX fixed-radius ranked-summary aggregate. | Goal4660/4661 parity is expected; wrappers are not a speed claim. |
| `triangle_counting` | `primitive_first` | generic RT graph relationship-count composition; measured V2.14 row used weighted any-hit sum. | V4 weighted-sum is not a clean new app win against V2.14; the V4/V3 regression remains a blocker. |

## Raw Evidence Cross-Checks

The serious V2.14 raw rows confirm the route-table warning:

- `raydb_style`: measured with
  `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` through
  `paper_rt_optix_prepared_grouped_reduction`.
- `triangle_counting`: measured with
  `ray_triangle_weighted_any_hit_sum_3d` /
  `PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_DEVICE_COLUMNS_V1`.
- `librts_spatial_index`: measured with `aabb_index_query_2d`.
- `rt_dbscan`: measured with OptiX fixed-radius count-threshold and grouped
  union, plus `partner="cupy"` for the component signature.
- `hausdorff_xhd`: Goal4669 used an Embree directed-summary denominator, but
  the V2.14 route table already records an OptiX nearest-witness primitive-first
  path.

## Immediate Correction To Goal4672

I should not finalize `robot_collision` as the next clean V4 win target merely
because the any-hit flags operator has strong operator-level evidence. V2.14
already had prepared OptiX any-hit collision flags, including device-buffer
modes.

`robot_collision` may still be used only as a same-primitive improvement
experiment with V2.14 as the explicit denominator. It cannot be counted as a
"new V4 capability" win unless the frozen app-level result proves V4 materially
improves that V2.14 route.

The better Goal4672 rule is:

```text
Select an existing app only if V4 has a real new generic runtime lever absent in
V2.14, or if the experiment is explicitly framed as same-primitive improvement
over V2.14. Otherwise declare that a new generic primitive is required.
```

## Goal-Level Decision Audit

1. Was I being stupid?
   - Yes.
2. If yes, what action made it stupid?
   - I was about to select `robot_collision` mainly from current V4 operator
     evidence and prior Embree-vs-OptiX evidence without first proving whether
     V2.14 already had the same primitive route.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes. Audit V2.14 per-app primitives first, then select only targets where
     V4 has a real new runtime lever or a frozen same-primitive improvement over
     V2.14.
4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4672 must use this audit as a prerequisite and must not count
     front-door/productization migration as V4 speed.

## Non-Authorization

This audit does not authorize V4 release, public speedup wording, whole-app
high-performance wording, partner-migration speed claims, same-primitive
productization speed claims, C ABI, embedding, non-Python hosts, true zero-copy,
arbitrary callbacks, or app-specific native kernels.
