# Goal1850 - Segment/Polygon Partner Adapter Over Generic OptiX Witness Rows

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1850 adds the first app-level Python+partner+RTDL adapter on top of the
Goal1848 bounded all-hit witness contract:

`rtdsl.segment_polygon_anyhit_rows_optix_partner(...)`

The adapter accepts Python segment and polygon records, builds partner-owned
CUDA columns for rays and triangle fans, prepares the OptiX triangle scene from
partner-owned device columns, writes bounded all-hit witness rows into
partner-owned output tensors, and converts the resulting generic
ray/primitive witness pairs into app rows in Python.

The native engine still sees only:

- ray columns,
- triangle primitive columns,
- output witness columns,
- generic ray IDs,
- generic primitive IDs.

It does not see `segment_id`, `polygon_id`, row names, GIS logic, or duplicate
policy. Polygon fan triangulation, polygon-ID assignment, duplicate removal,
and app row naming live in Python.

## Validation

Local focused validation:

```text
PYTHONPATH=src;. py -3 -m py_compile src\rtdsl\partner_adapters.py src\rtdsl\__init__.py
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1850_segment_polygon_partner_adapter_test \
  tests.goal1848_optix_partner_bounded_all_witness_output_contract_test \
  tests.goal1847_optix_witness_pod_validation_packet_test
```

Result: 10 tests passed.

Pod smoke validation was run on the available RTX A4500 pod
(`root@213.173.108.219 -p 17793`) after resetting `/root/rtdl` to clean
`origin/main` commit `de2534ebd6aadd9ced42e81af5a7eaf6c31731ad`, using the
already-built OptiX backend. Both CuPy and Torch produced:

```text
[{"segment_id": 101, "polygon_id": 11},
 {"segment_id": 101, "polygon_id": 12}]
```

The captured artifact is:

`docs/reports/goal1850_segment_polygon_partner_adapter_pod_smoke.json`

For both partners, the artifact records:

- `direct_device_pointer_observed: true`
- `partner_tensor_handoff_authorized: true`
- `ray_columns_true_zero_copy_authorized: true`
- `triangle_scene_true_zero_copy_authorized: true`
- `witness_outputs_true_zero_copy_authorized: true`
- `true_zero_copy_authorized: true`
- `exact_row_semantics_authorized: true`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

## Boundary

This is not a v2.0 release gate pass. It is a narrow app-adapter proof that the
generic OptiX all-witness output can preserve app row identity when the Python
layer owns the app semantics.

The adapter currently starts from Python app records and creates partner-owned
CUDA tensors internally. That proves the engine-facing contract and the
partner-owned output path, but it is not yet an end-to-end benchmark over a
user-supplied PyTorch/CuPy dataset already resident on the GPU.

No broad RT-core speedup claim, whole-app acceleration claim, package-install
claim, or v2.0 release claim is authorized by this goal.
