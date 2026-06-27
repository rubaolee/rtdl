# Goal2241: RayJoin Same-Query PIP Uses Closed-Shape Membership

Status: local implementation ready for pod timing.

## Purpose

Goal2238 added a generic OptiX primitive:

```text
rtdl_optix_run_point_closed_shape_membership_2d
```

Goal2241 wires the RayJoin same-query PIP runner to use that primitive instead
of reaching PIP through the older compiled RTDL kernel path. This keeps the
native surface app-agnostic while preserving the same RayJoin-facing output row
contract.

## Code Path

For `workload == "pip"` and `backend == "optix"`,
`scripts/goal2192_rayjoin_same_query_stream_runner.py` now calls:

```text
rt.closed_shape_membership_2d_optix(points=..., shapes=..., result_mode="positive_hits")
```

The runner then maps the generic primitive rows back into the application-facing
contract used by the same-query evidence harness:

```text
point_id  <- point_id
polygon_id <- shape_id
contains <- membership
```

This mapping is deliberately in Python because `polygon_id` is RayJoin
application vocabulary. The engine still sees only points, closed shapes, and
membership rows.

The runner also packs the PIP points and shapes once per `run-stream`
invocation and reuses those packed buffers across warmups and repeats. This is
important for fair timing because the primitive accepts `PackedPoints` and
`PackedPolygons`; timing repeated Python packing would measure harness overhead,
not the closed-shape membership primitive.

## Output Metadata

The same-query artifact now records:

```json
{
  "implementation_path": "closed_shape_membership_2d_optix",
  "uses_generic_closed_shape_membership": true,
  "input_preparation_path": "prepacked_points_and_shapes_once_per_run_stream"
}
```

for the PIP/OptiX backend row.

## Validation

Local tests cover the route and schema-preserving row conversion:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2192_rayjoin_same_query_stream_adapter_test \
  tests.goal2241_rayjoin_same_query_pip_closed_shape_path_test
```

The pod timing still needs to be rerun from a pushed commit against the
RayJoin-exported same-query stream. The expected claim boundary remains narrow:
this can support a PIP same-query implementation-path improvement, not a full
RayJoin reproduction or broad paper-scale speedup claim.

In short: this is not a full RayJoin reproduction.
