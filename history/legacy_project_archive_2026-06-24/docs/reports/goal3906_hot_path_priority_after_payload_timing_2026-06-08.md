# Goal3906 Hot-Path Priority After Payload Timing Visibility

## Purpose

Goal3906 turns the Goal3905 timing-visible scale packet into an engineering
priority map. The goal is to avoid spending pod time on rows that only look slow
because they include Python process startup, imports, CUDA/OptiX context setup,
or cold scene preparation.

Source artifact:
`docs/reports/goal3905_current_scale_after_robot_timing_aliases_a5000/summary.json`

## Current Timing Map

| App | Process sec | Hot signal sec | Process / hot | Hot signal used |
| --- | ---: | ---: | ---: | --- |
| `hausdorff_xhd` | `1.751664` | `0.047288` | `37.0x` | measured query total |
| `spatial_rayjoin` | `10.256468` | n/a | n/a | per-contract medians; wrapper is not a single hot metric |
| `rt_dbscan` | `3.503113` | `0.080629` | `43.4x` | app payload elapsed |
| `robot_collision` | `1.752192` | `0.000071` | `24552.4x` | prepared tail total run |
| `contact_manifold` | `0.751673` | `0.000495` | `1518.0x` | native collect |
| `raydb_style` | `1.751910` | `0.000928` | `1887.1x` | app payload elapsed |
| `barnes_hut` | `1.752067` | `0.008744` | `200.4x` | Numba force kernel median |
| `librts_spatial_index` | `2.002213` | `0.032499` | `61.6x` | prepared query median |
| `rtnn` | `3.002902` | `0.000181` | `16567.2x` | prepared runner median |
| `triangle_counting` | `1.251976` | `0.000178` | `7046.9x` | prepared query median |

## Engineering Interpretation

### Rows Not Worth Process-Time Tuning

These rows already have tiny hot-path metrics in the current promoted scale
shape: `robot_collision`, `contact_manifold`, `raydb_style`, `rtnn`, and
`triangle_counting`. Their process times are mostly wrapper/setup evidence.

The next useful work for these rows is either larger steady-state scale probes
or cold/hot documentation, not micro-tuning the current process wrapper.

### RT-DBSCAN

The Goal3898 segmented-count signature path fixed the former signature
bottleneck. In Goal3905, payload elapsed is about `0.080629` seconds. The
remaining meaningful hot cost is the grouped native/adapter run, not the
cluster-signature materialization.

Next target: reduce the generic grouped-union/stream adapter cost while keeping
the Numba signature path and no DBSCAN-specific native engine logic.

### LibRTS

The LibRTS row is a prepare-once/query-many workload. Goal3905 shows:

- scene prepare: about `0.610099` seconds in the payload
- query prepare: about `0.107379` seconds across point/box prepared queries
- prepared query median: about `0.032499` seconds

The current app already uses the generic prepared AABB index, prepared query
buffers, and the fused multi-operation native count. The remaining work is not
another app trick; it is either cold-build optimization or a stronger prepared
session interface for repeated query sets.

Next target: prepared-session cache/reuse evidence for AABB index scenes and
query buffers, or native build-path profiling if cold-build time becomes the
performance target.

### RayJoin

RayJoin must stay contract-by-contract. Goal3896/Goal3902/Goal3905 show:

- one-shot PIP favors Numba at this slice;
- repeated PIP favors RTDL/OptiX prepared batching;
- LSI and overlay active-count strongly favor RTDL/OptiX prepared scalar counts;
- the wrapper elapsed is not a single hot-path performance metric.

Next target: input staging and reusable dataset/session setup for the RayJoin
representative script, while preserving the explicit mixed-route decision table.

## Boundary

Goal3906 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is an internal engineering-priority packet, not a public performance comparison and not a release packet.
