# Goal2248: Prepared Closed-Shape Membership

Status: implemented; pod timing recorded by Goal2249.

## Purpose

Goal2245 showed that once Python packing was removed from the repeated timing
loop, the RayJoin same-query PIP/OptiX path reached `0.08343074284493923`
seconds median for 100,000 queries. The remaining overhead is still not the
ideal primitive shape: each native call rebuilds and uploads the closed-shape
scene before launching.

Goal2248 adds a prepared generic closed-shape membership surface:

```text
rtdl_optix_prepare_point_closed_shape_membership_2d
rtdl_optix_run_prepared_point_closed_shape_membership_2d
rtdl_optix_destroy_prepared_point_closed_shape_membership_2d
```

and the Python wrapper:

```text
prepare_point_closed_shape_membership_2d_optix(...)
PreparedOptixPointClosedShapeMembership2D.run(...)
```

## Boundary

The public vocabulary is still generic: point, closed shape, membership,
prepared scene. RayJoin/PIP/polygon naming remains in the Python application
harness only when mapping `shape_id` to the app-facing `polygon_id` field.

The prepared path currently supports `positive_hits` output. Full matrix output
remains on the non-prepared helper.

## Expected Measurement

The same-query runner now records:

```json
{
  "implementation_path": "prepared_closed_shape_membership_2d_optix",
  "input_preparation_path": "prepared_shape_scene_and_prepacked_points_once_per_run_stream"
}
```

Pushed-commit pod timing is recorded in Goal2249. Goal2248 by itself remains an
implementation report; the measured performance claim lives in the Goal2249
evidence report and its review chain.
