# Goal2948: Payload Grouped-Sum Scale Probe

Date: 2026-06-01
Status: scale runner added; pod evidence pending

## Purpose

Goal2947 proved the generic event-ordered primitive-payload grouped-sum front
door on a tiny fixture. Goal2948 adds the scale probe that decides whether the
current CuPy consumer is already useful at larger hit-stream sizes, or whether
the next performance problem is a multi-block/partial-reduction consumer.

The probe is intentionally generic:

- rays: generic 3-D rays
- primitives: generic 3-D triangles
- payload: `primitive_group_ids` and `primitive_values`
- operation: `hit_stream_primitive_payload_grouped_sum_f64`
- partner: explicit `cupy`

It does not encode RayJoin, database, geometry-overlay, or other app-specific
native engine logic.

## Runner

`scripts/goal2948_payload_grouped_sum_scale_probe.py`

Default pod command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=build/librtdl_optix.so \
python3 scripts/goal2948_payload_grouped_sum_scale_probe.py \
  --ray-count 4096 \
  --triangle-count 64 \
  --group-count 8 \
  --warmups 1 \
  --repeats 3 \
  --output /tmp/goal2948_payload_grouped_sum_scale_probe.json
```

Expected hit rows: `4096 * 64 = 262144`.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic partner
selection claim, package-install claim, paper-reproduction claim, or app-specific
native engine logic claim.

The result is a diagnostic for the next optimization target.
