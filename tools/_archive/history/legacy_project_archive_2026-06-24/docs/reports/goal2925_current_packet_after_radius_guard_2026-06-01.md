# Goal2925: Current Packet After Hausdorff Prepared-Radius Guard

Date: 2026-06-01
Status: pod packet passed

## Purpose

Goal2925 reruns the full seven-app v2.5 canonical packet after Goal2924 added
the app-level prepared-radius guard for the Hausdorff/X-HD grouped OptiX path.
This closes the Goal2924 follow-up requirement that the RTX packet be refreshed
from a source commit containing the fix.

Artifact directory:

`docs/reports/goal2925_current_packet_after_radius_guard_pod/`

## Packet Result

- source commit: `6ad6314192e9db0f659c76acc58a20767a194697`
- status: `pass`
- all_pass: `true`
- artifact count: `7 / 7`
- dirty artifacts: `{}`
- claim-boundary violations: `{}`
- elapsed: `458.803s`

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

`goal2925_triage.json`:

- status: `pass`
- performance targets: `[]`
- top priority: `null`

Key rows:

| App | Status | Key value |
| --- | --- | --- |
| RTNN | `current_path_acceptable` | CuPy/RTDL ratios: uniform `1.122x`, clustered `2.541x`, shell `7.696x` |
| Hausdorff/X-HD | `current_path_acceptable_near_parity` | target `4096`, RTDL/CuPy ratio `1.044x`; exact and RTDL/OptiX-backed, but not a speedup claim |
| RT-DBSCAN | `current_path_acceptable` | grouped stream speedup vs prepared CuPy grid `3.581x` to `4.927x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | Torch selected; max OptiX membership speedup vs Embree `133.477x` |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity path only |

## Result

Goal2924's guard does not break the canonical packet. The Hausdorff row remains
exact, uses RTDL/OptiX, reports RT-core use on the RTX pod, and stays within the
near-parity band against the optimized CuPy grid baseline. The result is not
promoted to a public speedup claim because this packet's Hausdorff median is
slightly slower than CuPy on this run.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic Triton-selection
claim, package-install claim, or paper-reproduction claim.

The packet supports the engineering conclusion that the current Python +
partner + RTDL v2.5 substrate is coherent after the radius-guard fix. Release
still requires a user-requested release packet and fresh 3-AI release consensus.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2925_current_packet_after_radius_guard_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 9 tests
OK
```
