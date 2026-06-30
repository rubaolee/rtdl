# Goal1821: OptiX Partner Device-Descriptor Fail-Closed Path

Status: `accept-with-boundary`

Date: 2026-05-13

## Scope

Goal1821 adds the Python-side OptiX direct-device contract shape after
Goal1819's CUDA pointer descriptor. It validates a full partner-owned
ray/triangle any-hit column packet as CUDA device descriptors, records metadata,
and then fails closed unless a future native OptiX device-column ABI exists.

This is a safety and contract step. It is not native execution evidence.

## Added API

```python
packet = rt.pack_optix_ray_triangle_any_hit_2d_device_descriptor_inputs(
    ray_columns,
    triangle_columns,
)

rt.run_optix_partner_ray_triangle_any_hit_2d_device_descriptors(
    ray_columns,
    triangle_columns,
)
```

The packer requires every column to be a CUDA partner tensor with an observable
non-zero pointer. It returns metadata:

```text
transfer_mode = "device_descriptor_only"
direct_device_pointer_observed = True
direct_device_handoff_authorized = False
true_zero_copy_authorized = False
rt_core_speedup_claim_authorized = False
```

The runner requires the future native symbol:

```text
rtdl_optix_count_ray_primitive_anyhit_2d_device_columns
```

If that symbol is absent, the runner raises an error and does not silently fall
back to host staging.

## Boundary

Goal1821 still does not satisfy the v2.0 direct device-pointer blocker. The
remaining work is native OptiX execution from the device descriptors, stream and
lifetime rules, hidden-copy measurement, pod evidence, and 3-AI consensus.
