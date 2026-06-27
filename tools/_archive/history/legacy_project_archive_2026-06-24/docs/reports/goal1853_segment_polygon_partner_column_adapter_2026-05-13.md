# Goal1853 - Caller-Supplied Partner Column Segment/Polygon Adapter

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1853 extends the Goal1850 adapter with:

`rtdsl.segment_polygon_anyhit_rows_optix_partner_columns(...)`

Unlike `segment_polygon_anyhit_rows_optix_partner(...)`, this entry point does
not start from Python segment and polygon records and does not create the input
GPU columns internally. The caller supplies partner-owned CUDA columns for:

- segment rays,
- polygon triangle primitives,
- polygon triangle AABBs.

The adapter allocates only the bounded witness output columns, invokes the
generic OptiX bounded all-witness native contract, synchronizes the selected
partner runtime, and converts generic witness IDs into app rows in Python.

## Engine Boundary

The native engine remains app-agnostic. It sees only generic ray columns,
triangle columns, AABBs, and output witness columns. It does not see `segment`,
`polygon`, GIS row names, duplicate-removal policy, or app-specific control
flow.

The app-specific mapping remains in Python:

- caller ray IDs are interpreted as segment IDs,
- caller triangle primitive IDs are interpreted as polygon IDs,
- generic witness pairs are deduplicated into app rows.

## Validation

Local focused validation:

```text
PYTHONPATH=src;. py -3 -m py_compile src\rtdsl\partner_adapters.py src\rtdsl\__init__.py
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1850_segment_polygon_partner_adapter_test \
  tests.goal1848_optix_partner_bounded_all_witness_output_contract_test \
  tests.goal1847_optix_witness_pod_validation_packet_test
```

Result: 12 tests passed.

Pod smoke validation was run on the available RTX A4500 pod
(`root@213.173.108.219 -p 17793`) after resetting `/root/rtdl` to clean
`origin/main` commit `dc825ce03d075cecb05ffc5b80b04652ff66882a`.
Both CuPy and Torch caller-supplied columns produced:

```text
[{"segment_id": 101, "polygon_id": 11},
 {"segment_id": 101, "polygon_id": 12}]
```

The captured artifact is:

`docs/reports/goal1853_segment_polygon_partner_column_adapter_pod_smoke.json`

For both partners, the artifact records:

- `input_contract: caller_supplied_partner_device_columns`
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

This is still not a v2.0 release gate pass. It is a narrow proof that an app
adapter can consume caller-supplied PyTorch/CuPy GPU columns directly while
preserving app row identity outside the native engine.

No broad RT-core speedup claim, whole-app acceleration claim, package-install
claim, or v2.0 release claim is authorized by this goal.
