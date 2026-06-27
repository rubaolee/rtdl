# V4 Goal4732 RayDB Device-Output Route Repair

Date: 2026-06-26

Status: `focused_pod_rerun_complete_pending_external_review_debt`

Decision:
`bind_raydb_style_v4_current_to_generic_v4_device_output_frontdoor_before_remeasuring`

## What Happened

The Goal4669 serious app-level RayDB row reported:

| comparison | hot speedup |
|---|---:|
| V4 / V2.14 | 0.974x |
| V4 / V3.0.2 | 1.005x |

That result was not a measurement of the V4 device-output frontdoor. The raw
payload shows that V4 current used the same legacy backend as V2.14/V3:

`paper_rt_optix_prepared_grouped_reduction`

with native symbol:

`rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction`

It returned compact grouped rows through the host bridge. Therefore the old row
is valid as a legacy-route measurement, but it is not the final V4 route result.

## Repair

I added a real app-level V4 RayDB route:

`paper_rt_v4_cupy_device_grouped_reduction`

The same code path also keeps a Torch entry point:

`paper_rt_v4_torch_device_grouped_reduction`

It uses the existing generic V4 surface:

`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

and generic primitive:

`RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`

This is not an app-specific native kernel. RayDB still only supplies generic
rays, triangles, primitive group ids, and primitive values.

## Driver Binding

The serious app-level runner now binds only `v4_current/raydb_style` to the new
CuPy device-output backend. V2.14 and V3.0.2 keep the old baseline backend
unchanged.

## Validation

Local protocol validation passed:

```powershell
py -m unittest tests.v4_goal4732_raydb_device_output_route_test tests.v4_goal4669_full_app_runner_test tests.v4_goal4730_complete_10_app_matrix_test tests.v4_goal4731_post_matrix_release_decision_test
```

Result: 21 tests passed.

## Focused POD Rerun

Evidence:

- `future/v4/evidence/v4_goal4732_raydb_focused_20260626/summary.json`
- `future/v4/evidence/v4_goal4732_raydb_focused_20260626/summary.md`

Focused serious result:

| comparison | hot speedup |
|---|---:|
| V4 / V2.14 | 0.985x |
| V4 / V3.0.2 | 0.954x |

The route metadata gate passed: V4 current used
`paper_rt_v4_cupy_device_grouped_reduction`, reported
`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`, passed CPU
correctness parity, used direct device output columns, bypassed the host row
bridge, and did not download grouped rows in the hot path.

Interpretation: Goal4732 repaired the benchmark binding and cleared the V2.14
no-regression floor, but it is not a high-performance win and still regresses
versus V3.0.2. This row may update the 10-app matrix only as a
`parity_not_v4_speed_win` / `v3_regression_open` row.

## Claim Boundary

No V4 release is authorized by this goal. No public speedup wording is
authorized. No whole-app high-performance claim is authorized. The previous
0.974x row is not erased; it remains the legacy-route measurement and is
superseded for V4-device-route purposes by the focused POD rerun above.

## Goal-Level Decision Audit

1. Was I being stupid?
   No for this decision. It would have been stupid to keep treating the
   legacy-route 0.974x row as the final V4 device-output result.

2. If yes, what action made the decision stupid?
   The earlier weak action was allowing the all-app driver to benchmark the old
   prepared grouped-reduction route while the V4 device-output surface existed
   separately.

3. Was there another path?
   Yes: only document RayDB as parity/regression. That would preserve a false
   benchmark binding and fail the user's demand for app-level V4 evidence.

4. Can I now try a different path that actually solves the problem?
   Yes. The app frontdoor and serious runner now bind V4 current to the generic
   device-output surface; the next truth test is a focused same-hardware POD
   rerun.

## Non-Authorization

Goal4732 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
