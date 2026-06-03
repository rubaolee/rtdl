# Goal3180: Ray/Triangle Hit-Stream Typed Producer Metadata

Date: 2026-06-03

## Purpose

Goal3180 closes a narrow v2.8 substrate gap shared by Spatial RayJoin and
triangle counting: the generic ray/triangle native hit-stream path already had
v2.5 device-column handoff metadata, but it did not yet present itself through
the newer v2.8 typed-result-stream producer contract.

This goal adds typed producer metadata for the generic
`ray_triangle_hit_stream_3d` producer. The stream columns remain generic:

| Column | Role | Meaning |
| --- | --- | --- |
| `ray_ids` | `group_key` | caller-owned query/ray group id |
| `primitive_ids` | `item_id` | hit primitive id |

No RayJoin, triangle-counting, database, GIS, graph, or app-specific terms are
introduced into the native engine contract.

## Code Changes

- Added `V2_8_RAY_TRIANGLE_HIT_STREAM_TYPED_PRODUCER_VERSION` and
  `V2_8_RAY_TRIANGLE_HIT_STREAM_TYPED_PRODUCER_PRIMITIVE`.
- Added
  `make_v2_8_ray_triangle_hit_stream_typed_stream_contract(...)`.
- Attached `typed_result_stream` and `v2_8_typed_producer_metadata` to
  `RtdlHitStreamColumnHandoff.to_metadata()`, including native device-column
  residency and device-status-pointer facts when present.
- Exported the new helper and constants from `rtdsl`.
- Refreshed the v2.8 runtime-gap rows for Spatial RayJoin and triangle counting:
  generic hit-stream typed producer metadata now exists, while benchmark-app
  adoption and resident grouped continuation remain open.

## What This Does Not Claim

This is a metadata/contract hardening step over an existing generic native
device-column path. It does not finish Spatial RayJoin or triangle counting.
The remaining work is still real:

- Spatial RayJoin needs benchmark-app adoption of resident hit streams,
  parity/count grouping over resident rows, and boundary-witness ownership at
  serious scale.
- Triangle counting needs segmented/streamed graph lowering, benchmark-app
  adoption of resident candidate streams, and resident continuation at serious
  scale.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3180_ray_triangle_hit_stream_typed_producer_metadata_test tests.goal2706_native_optix_hit_stream_device_columns_test tests.goal2710_raydb_native_device_hit_stream_path_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test tests.goal3172_v2_8_runtime_gap_compact_mask_refresh_test
```

Local result:

```text
Ran 20 tests in 0.117s
OK
```

Pod validation command shape:

```powershell
ssh -i .\id_ed25519_rtdl_codex -p 22063 -o StrictHostKeyChecking=no root@69.30.85.131 "..."
```

Pod environment:

- Host: `root@69.30.85.131 -p 22063`
- Commit: `2757c7da`
- Repo: `/root/rtdl_goal3151`
- Python: `/root/venvs/rtdl_goal3154/bin/python`
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`

Pod focused-suite result:

```text
Ran 20 tests in 0.045s
OK
```

Additional pod live OptiX smoke, executed from `/tmp/goal3180_smoke.py` with
`PYTHONPATH=src:.` and
`RTDL_OPTIX_LIBRARY=/root/rtdl_goal3151/build/librtdl_optix.so`:

```json
{
  "row_count": 1,
  "overflow": false,
  "native_proven": true,
  "stream_kind": "hit_stream",
  "producer": "ray_triangle_hit_stream_3d",
  "device_resident": true,
  "zero_copy": false
}
```

This proves that the live OptiX device-column handoff carries the new v2.8
typed producer metadata on NVIDIA hardware. It still does not authorize
true-zero-copy wording, public speedup wording, release, or paper-reproduction
claims.
