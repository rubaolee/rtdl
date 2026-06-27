# Goal4415 V3.0 M18 Device-Side Grouped Contract Evidence

Date: 2026-06-15

Status: complete for the internal M18 evidence gate.

## What Changed

M18 adds an app-agnostic device-side grouped input contract for prepared OptiX
3-D closest-hit grouped argmin:

- prepared rays may come from partner-owned device columns;
- grouped inputs may come from partner-owned device columns;
- the group mapping contract is `per_prepared_ray_ordinal`;
- the hot path can run OptiX traversal plus grouped argmin on device without
  materializing closest-hit rows or group outputs to host;
- group output materialization is an explicit finalize step after the measured
  hot window.

This closes the M17 fail-closed gap for device-column prepared ray batches. The
old host `ray_id -> group_id` path remains intact and still requires host ray-id
bookkeeping. The new path does not remove that guard; it adds a separate
device-side contract.

## Implementation

Native:

- Added per-prepared-ray kernels:
  - `closest_hit_grouped_argmin_min_key_per_ray_group`
  - `closest_hit_grouped_argmin_min_index_per_ray_group`
- Added app-agnostic C ABI:
  - `rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create_device_per_ray_groups`
  - `rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device`
  - `rtdl_optix_closest_hit_grouped_argmin_inputs_3d_finalize`

Python:

- Added `prepare_closest_hit_device_per_ray_grouped_argmin_inputs(...)`.
- Added `ray_closest_hit_prepared_grouped_argmin_device(...)`.
- Added `PreparedOptixClosestHitGroupedArgmin3D.materialize_grouped_results()`.
- Added M18 evidence module and runner.

## Pod Evidence

Artifact:

`docs/reports/goal4415_v3_0_m18_device_side_grouped_contract_evidence_8192_2026-06-15.json`

Hardware:

RTX 4000 Ada Generation, driver 550.127.08

Parameters:

- rays: 8,192
- groups: 128
- triangles: 2
- warmups: 2
- repeats: 5
- partners: CuPy and Numba

| Partner | Signature | Prepare median | Device hot median | Finalize median | Prepare max H2D | Hot max H2D | Hidden D2H/D2D/unknown |
|---|---:|---:|---:|---:|---:|---:|---|
| CuPy | `[128, 128, 1408, 128000000, 11, 11]` | 0.000403s | 0.0000735s | 0.0000590s | 0 B | 40 B | none |
| Numba | `[128, 128, 1408, 128000000, 11, 11]` | 0.000385s | 0.0000720s | 0.0000575s | 0 B | 40 B | none |

Interpretation:

- CuPy and Numba produce identical grouped-argmin results.
- Prepare and hot measured windows pass no-hidden-column-copy checks.
- The 40 hot-window H2D bytes are within launch-parameter scope, not named
  column movement.
- Per-group result arrays are downloaded only in the explicit finalize window.

## Claim Boundary

Allowed internal claim:

RTDL V3 now has a generic device-side grouped argmin contract for prepared
device-column ray batches, validated with CuPy and Numba partner-owned input
columns at 8,192 rays / 128 groups on the pod.

Not allowed:

- public speedup claim;
- RT-core speedup claim;
- author-code parity claim;
- automatic partner/backend selection claim;
- end-to-end zero-copy claim.

Preferred wording:

`measured-window no-hidden-copy`

Do not promote internal `true_zero_copy_ready` fields to public prose without
the measured-window qualifier.

## Methodology Limits

The CUDA transfer counter is an LD_PRELOAD shim over public CUDA runtime/driver
copy calls in the measured process. It does not prove absence of transfers that
could occur through unobserved internal library mechanisms, child processes, or
non-CUDA DMA paths. This is sufficient for the M18 named-column hot-path gate,
but not for public end-to-end zero-copy wording.

## Tests

Local:

`PYTHONPATH=src py -3 -m unittest tests.goal4415_v3_0_m18_device_side_grouped_contract_test`

Result: 6 tests OK.

Pod:

`make build-optix`

Result: OK.

`PYTHONPATH=src python -m unittest tests.goal4415_v3_0_m18_device_side_grouped_contract_test`

Result: 6 tests OK.

Pod evidence:

`PYTHONPATH=src RTDL_OPTIX_LIB=/workspace/rtdl_v3_main/build/librtdl_optix.so python scripts/v3_0_m18_device_side_grouped_contract_measure.py --ray-count 8192 --group-count 128 --warmups 2 --repeats 5 --output docs/reports/goal4415_v3_0_m18_device_side_grouped_contract_evidence_8192_2026-06-15.json`

Result: validation OK.

## Next Target

M19 should use this contract to revisit one benchmark-shaped grouped workload
that was previously blocked by host-indexed grouped inputs. The best next
candidate is RTNN/ranked nearest summary or a RayJoin point-location slice,
because both can generate `per_prepared_ray_ordinal` group columns in partner
code without adding app-specific native names.
