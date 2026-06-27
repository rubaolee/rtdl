# Goal2948: Payload Grouped-Sum Scale Probe

Date: 2026-06-01
Status: pod scale probe passed

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

## Pod Results

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `0111488efb324b49d3258e0ac57254451b46a19e`

Artifacts:

- `docs/reports/goal2948_payload_grouped_sum_scale_probe_pod/goal2948_payload_grouped_sum_scale_probe.json`
- `docs/reports/goal2948_payload_grouped_sum_scale_probe_pod/goal2948_payload_grouped_sum_scale_probe_1m.json`

| Rows | Rays | Triangles | Median sec | Consumer sec | Native enqueue sec | Rows/sec | Consumer rows/sec |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `262144` | `4096` | `64` | `0.008242` | `0.001423` | `0.001450` | `31.805M` | `184.205M` |
| `1048576` | `16384` | `64` | `0.031053` | `0.003489` | `0.002249` | `33.767M` | `300.572M` |

Both runs preserved exact grouped counts and payload sums. The 1M-row consumer
time is still only `3.489 ms`, so the current single-kernel CuPy continuation is
not the immediate blocker for this primitive. The next likely performance target
is not "fix this consumer now"; it is to apply the same generic payload-mapped
front door to a benchmark app row path and measure whether traversal, row
production, or app-level payload preparation dominates at realistic workloads.
