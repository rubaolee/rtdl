# Goal2917: Current Packet With Toolchain Provenance

Date: 2026-06-01
Status: pod packet passed

## Purpose

Goal2917 reruns the seven-app v2.5 canonical packet after Goal2916 added
toolchain provenance metadata to the packet runner. This directly reduces the
Goal2897/Goal2914 compiler flag alignment risk from "not visible in the packet"
to "visible and auditable in the packet summary."

## Pod Evidence

Artifact directory:

`docs/reports/goal2917_current_packet_with_toolchain_pod/`

Source commit executed on the pod:

`b21ff72dbfdb0653cace6cd9e353269ae75bcaf0`

Packet result:

- status: `pass`
- all_pass: `true`
- artifact count: `7 / 7`
- source dirty: `[]`
- claim-boundary violations: `{}`
- elapsed: `428.825s`

Toolchain provenance recorded in `goal2855_summary.json`:

- metadata version: `rtdl.goal2916.toolchain_provenance.v1`
- GPU/driver: `NVIDIA RTX A5000, 570.211.01`
- CUDA home: `/usr/local/cuda-12`
- NVCC: CUDA compilation tools `12.8`, build `cuda_12.8.r12.8/compiler.35583870_0`
- OptiX prefix: `/root/vendor/optix-sdk`
- OptiX header exists: `true`
- RTDL OptiX library: `/root/rtdl_goal2785_work/build/librtdl_optix.so`
- RTDL OptiX library exists: `true`
- PTX arch/compiler: `compute_86`, `nvcc`
- C++ compiler: `/usr/bin/g++`, GCC `13.3.0`
- partner versions: Triton `3.4.0`, Torch `2.8.0+cu128`, CuPy `14.1.0`, Numba `0.65.1`

## Current Performance Triage

`goal2917_triage.json` remains clean:

- performance targets: `[]`
- top priority: `null`

Notable rows:

| App | Current status | Key value |
| --- | --- | --- |
| RTNN | `current_path_acceptable` | minimum CuPy/RTDL ratio `1.118x` |
| Hausdorff/X-HD | `current_path_acceptable_near_parity` | RTDL/CuPy ratio `1.006x` |
| RT-DBSCAN | `current_path_acceptable` | minimum grouped-stream speedup vs prepared CuPy grid `3.787x` |
| Barnes-Hut | `current_path_acceptable_with_measured_partner_selection` | selected vector-sum partner `torch`; Triton remains unpromoted |
| Spatial RayJoin | `current_path_acceptable_but_rows_overlay_deferred` | count/parity only; row/overlay continuation still deferred |

## What This Solves

The current packet is now more reviewable:

- reviewers can see the exact CUDA/OptiX/PTX/compiler stack used for the timing run;
- reviewers can see which partner versions were present;
- future packet comparisons can detect toolchain drift without reading shell logs;
- the compiler flag alignment caution is tracked as provenance rather than hidden
  runbook state.

## Boundary

This is still not a compiler fairness proof. It records the toolchain used; it
does not prove that Triton, CuPy, Torch, CUDA C++, and RTDL native code used
identical optimization settings.

This is still not a second-architecture or multivendor result.

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, package-install claim,
automatic Triton-selection claim, or paper-reproduction claim.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2917_current_packet_toolchain_provenance_test

Ran 5 tests
OK
```
