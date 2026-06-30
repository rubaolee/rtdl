# Goal1875 - Fixed-Radius OptiX Partner Device Columns

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1875 adds the first native OptiX fixed-radius partner bridge:

- `rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns`
- `prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(...)`
- `fixed_radius_count_threshold_2d_optix_partner_device_columns(...)`

The bridge accepts caller-owned PyTorch/CuPy CUDA point columns, builds the
OptiX search acceleration structure from device-side AABBs, and writes
partner-owned output columns:

- `query_ids`
- `neighbor_counts`
- `threshold_flags`

The native row contract is:

`generic_fixed_radius_count_threshold_2d_device_columns`

## Boundary

This goal authorizes true zero-copy wording only for this exact fixed-radius
subpath: caller-owned query/search point columns and caller-owned output columns.
The OptiX GAS is still native acceleration state and is still required.

This goal does not authorize:

- v2.0 release readiness;
- broad RT-core speedup wording;
- whole-app speedup wording;
- arbitrary PyTorch/CuPy acceleration wording;
- package-install wording.

## Pod Evidence

Pod:

- SSH target: `root@213.192.2.116 -p 40189`
- key used by Codex: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- checkout: `/root/rtdl`
- base commit before patch: `6fadd554`

Validation:

- `PYTHONPATH=src:. python3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_adapters.py src/rtdsl/__init__.py`
- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda`
- Torch CUDA smoke through `fixed_radius_count_threshold_2d_optix_partner_device_columns(...)`
- CuPy CUDA smoke through `fixed_radius_count_threshold_2d_optix_partner_device_columns(...)`

Smoke fixture:

- query IDs: `[10, 11, 12]`
- query points: `(0,0)`, `(2,0)`, `(5,0)`
- search points: `(0,0)`, `(1,0)`, `(6,0)`
- radius: `1.1`
- threshold: `2`

Expected and observed:

- output query IDs: `[10, 11, 12]`
- neighbor counts: `[2, 1, 1]`
- threshold flags: `[1, 0, 0]`

Both Torch and CuPy produced the expected output on the pod.

## v2.0 Impact

Goal1873 created the partner reference/conformance path for fixed-radius apps.
Goal1875 adds the native OptiX device-column bridge needed by
`service_coverage_gaps` and `event_hotspot_screening`.

Those apps still need app-level adapters, pod timing artifacts, and external
review before they can become accepted v2.0 performance rows.
