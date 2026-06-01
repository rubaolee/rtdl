# Goal2934: Current Packet After CuPy Vector-Sum Selection

Date: 2026-06-01
Status: pod packet passed

## Purpose

Goal2934 reruns the full seven-app v2.5 canonical packet after Goal2932 added
the CuPy grouped vector-sum preview and Goal2933 taught the Barnes-Hut harness
to select the fastest measured same-contract vector partner instead of falling
back to Torch when Triton loses.

This is a current-source engineering packet for the v2.5 direction:

- RTDL/OptiX provides generic RT traversal, membership, and grouped stream work.
- Partner libraries provide generic continuation work when they win timing.
- The user-facing Python layer chooses partners explicitly and records the
  selected path.
- The native engine remains app-agnostic.

Artifact directory:

`docs/reports/goal2934_current_packet_after_cupy_vector_pod/`

## Packet Result

- source commit: `34b4f241e9bc235a4ffcd65a04067cc63211eea1`
- status: `pass`
- all_pass: `true`
- artifact count: `7 / 7`
- dirty artifacts: `{}`
- claim-boundary violations: `{}`
- elapsed: `462.464s`

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

`goal2934_triage.json`:

- status: `pass`
- performance targets: `[]`
- top priority: `null`

Key rows:

| App | Status | Key value |
| --- | --- | --- |
| RTNN | `current_path_acceptable` | CuPy/RTDL ratios: uniform `1.074x`, clustered `2.511x`, shell `7.576x` |
| Hausdorff/X-HD | `current_path_acceptable_near_parity` | target `4096`, RTDL/CuPy ratio `1.012x`; exact and RTDL/OptiX-backed, but not a speedup claim |
| RT-DBSCAN | `current_path_acceptable` | grouped stream speedup vs prepared CuPy grid `4.435x` to `5.152x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | CuPy selected for vector-sum continuation; max OptiX membership speedup vs Embree `137.303x` |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity path only |

Barnes-Hut vector continuation:

| Partner | Median seconds | Ratio vs Torch | Selected |
| --- | ---: | ---: | --- |
| Torch scatter-add | `0.001482439` | `1.000x` | no |
| Triton offsets | `0.004093980` | `2.762x` slower | no |
| CuPy by-key | `0.000714710` | `0.482x` | yes |

## Result

Goal2934 confirms the current v2.5 packet stays green after the CuPy vector
selection work. The important design effect is not that CuPy is globally
"better" than Torch or Triton. The effect is that RTDL's Python partner layer
can measure and select a partner per generic continuation contract while the RT
part remains in the app-agnostic OptiX engine.

For the Barnes-Hut benchmark, the RT membership phase remains RTDL/OptiX and
the force-vector continuation now selects CuPy for the measured dense
presegmented grouped vector-sum shape. Triton remains visible as a preview path
but is not promoted because it loses same-contract timing here.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic Triton-selection
claim, automatic CuPy-selection claim, package-install claim, paper-reproduction
claim, or app-specific native engine logic claim.

The packet supports the engineering conclusion that the current Python +
partner + RTDL v2.5 substrate is coherent after CuPy vector-sum selection.
Release still requires a user-requested release packet and fresh 3-AI release consensus.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2934_current_packet_after_cupy_vector_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 11 tests
OK
```
