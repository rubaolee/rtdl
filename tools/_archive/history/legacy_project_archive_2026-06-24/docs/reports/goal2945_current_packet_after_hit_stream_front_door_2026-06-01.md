# Goal2945: Current Packet After Generic Hit-Stream Front Door

Date: 2026-06-01
Status: pod packet passed

## Purpose

Goal2945 reruns the full seven-app v2.5 canonical packet after Goal2943 added
the public generic event-ordered RT hit-stream front door:

`rt.run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(...)`

The front door is intentionally narrow and app-agnostic:

- RTDL/OptiX produces generic `(ray_id, primitive_id)` hit-stream columns.
- A bounded CuPy consumer waits on the producer CUDA event and performs grouped
  reductions without host row materialization before the consumer.
- The exposed operation is still a generic primitive-id reduction, not a
  RayJoin, geometry-overlay, or database-specific continuation.
- The path does not authorize release, public speedup, broad RT-core, whole-app
  speedup, true-zero-copy, or automatic partner-selection wording.

Artifact directory:

`docs/reports/goal2945_current_packet_after_hit_stream_front_door_pod/`

## Packet Result

- source commit: `5b6741fa7bf08a4934b283bd755a67af2b04ed7b`
- status: `pass`
- all_pass: `true`
- artifact count: `7 / 7`
- dirty artifacts: `{}`
- claim-boundary violations: `{}`
- elapsed: `497.126s`

The packet records Goal2916 toolchain provenance:

- GPU: `NVIDIA RTX A5000, 570.211.01`
- metadata version: `rtdl.goal2916.toolchain_provenance.v1`
- CUDA home: `/usr/local/cuda-12`
- NVCC: CUDA `12.8`
- PTX arch/compiler: `compute_86`, `nvcc`
- Torch/CuPy/Triton/Numba: `2.8.0+cu128`, `14.1.0`, `3.4.0`, `0.65.1`
- RTDL OptiX library exists: `true`
- OptiX header exists: `true`

## Current Triage

`goal2945_triage.json`:

- status: `pass`
- performance targets: `[]`
- top priority: `null`

Key rows:

| App | Status | Key value |
| --- | --- | --- |
| RTNN | `current_path_acceptable` | CuPy/RTDL ratios: min `1.159x`, max `7.451x` |
| Hausdorff/X-HD | `current_path_acceptable` | target `4096`, RTDL/CuPy ratio `0.934x`; exact and RTDL/OptiX-backed, but not a speedup claim |
| RT-DBSCAN | `current_path_acceptable` | grouped stream speedup vs prepared CuPy grid `3.730x` to `5.088x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | CuPy selected for vector-sum continuation; max OptiX membership speedup vs Embree `143.497x` |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity path only in canonical packet; richer row/overlay continuation remains a v2.5-v3.0 runtime target |

Barnes-Hut vector continuation:

| Partner | Median seconds | Ratio vs Torch | Selected |
| --- | ---: | ---: | --- |
| Torch scatter-add | `0.000954` | `1.000x` | no |
| Triton offsets | `0.003887` | `4.072x` slower | no |
| CuPy by-key | `0.000772` | `0.809x` | yes |

## Result

Goal2945 confirms that adding the generic event-ordered hit-stream front door did
not regress the seven-app v2.5 packet. It also sharpens the next engineering
target: users can now call a generic RT hit-stream grouped-reduction front door,
but the richer user-language step is payload-mapped continuation, where generic
primitive payload columns can be reduced on the partner side after RT traversal.

That next step should still stay generic: group IDs, primitive payload values,
bounded output columns, explicit partner choice, event-ordered handoff, and
fail-closed overflow/status handling. App terms and app-specific logic should
remain in examples or user code, not in the native engine.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic Triton-selection
claim, automatic CuPy-selection claim, package-install claim, paper-reproduction
claim, or app-specific native engine logic claim.

Release still requires a user-requested release packet and fresh 3-AI release
consensus.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 scripts\goal2902_v2_5_current_packet_perf_triage.py --packet-dir docs\reports\goal2945_current_packet_after_hit_stream_front_door_pod --raydb-gate docs\reports\goal2896_raydb_same_contract_perf_gate_pod\goal2896_summary.json --output docs\reports\goal2945_current_packet_after_hit_stream_front_door_pod\goal2945_triage.json

[goal2902] status=pass apps=10 targets=0 output=docs\reports\goal2945_current_packet_after_hit_stream_front_door_pod\goal2945_triage.json
```
