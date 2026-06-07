# Goal3763 HIPRT Context-Probe Tail Repair And CUDA-Path Smoke

Date: 2026-06-07

## Purpose

After closing the current Numba-reference lane, the next project direction is
AMD/HIPRT parity. The available pod is an NVIDIA RTX A5000, not AMD hardware,
but it can still validate part of the HIPRT stack through HIPRT's CUDA/Orochi
path.

Goal3763 does three things:

1. Installs the expected HIPRT SDK on the pod.
2. Repairs a truncated native HIPRT API source tail that prevented
   `make build-hiprt`.
3. Runs focused HIPRT functional smoke tests on the A5000.

This is useful HIPRT readiness evidence, but it is not AMD hardware evidence.

## SDK Setup

The repository Makefile expects HIPRT v2.2 at:

```text
/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

The pod did not have that SDK installed. The SDK was downloaded from the
official GPUOpen download URL:

```text
https://gpuopen.com/download/hiprtSdk-2.2.0e68f54.zip
```

Observed SHA-256:

```text
72172d20b44f6e4dc72ea760b56cb73bfcab857aa5c475168cbabbc771dff66b
```

The zip extracted `hiprt/`, `contrib/`, `tools/`, and `tutorials/` directly
under the vendor directory, so those directories were normalized into the
Makefile's expected SDK root.

## Source Repair

`src/native/hiprt/rtdl_hiprt_api.cpp` ended in the middle of
`rtdl_hiprt_context_probe` at:

```cpp
oroDeviceProp props{};
```

The missing tail was restored from older complete release commits. The restored
probe now:

- reads device properties with `oroGetDeviceProperties`;
- records the device name;
- creates a HIPRT context through `hiprtCreateContext`;
- destroys the HIPRT context;
- destroys the Orochi context;
- returns `0` on success.

`tests/goal3763_hiprt_context_probe_tail_repair_test.py` guards this exact
tail so the source cannot silently truncate there again.

## A5000 Evidence

Artifact:
`docs/reports/goal3763_hiprt_context_probe_tail_repair_and_cuda_path_smoke_a5000.json`

Clean source evidence:

- source commit: `db62dc81`
- GPU: NVIDIA RTX A5000, driver 580.126.09
- git status: clean
- build command: `make build-hiprt -j2`
- build result: pass, `build/librtdl_hiprt.so`
- focused test result: 26 focused HIPRT tests pass

Focused tests:

- `tests.goal540_hiprt_probe_test`
- `tests.goal541_hiprt_ray_hitcount_test`
- `tests.goal551_hiprt_ray_triangle_2d_test`
- `tests.goal639_hiprt_native_any_hit_test`
- `tests.goal674_hiprt_prepared_anyhit_2d_test`
- `tests.goal3755_robot_collision_hiprt_route_readiness_test`
- `tests.goal3756_robot_collision_amd_parity_contract_correction_test`

## Interpretation

This closes an important setup/source blocker for the AMD lane: the HIPRT SDK
can be installed on the pod, the HIPRT backend can build, and the CUDA/Orochi
path can execute focused functional tests on NVIDIA.

It does not prove AMD GPU performance. The v2.10 AMD/HIPRT parity ledger
therefore stays in planning-gate mode:

- robot collision remains `ready_for_amd_functional_pod`;
- the other benchmark apps still need generic HIPRT extensions or promotion
  beyond compatibility fallback;
- AMD performance claims still require an AMD GPU pod.

## Claim Boundary

This goal does not authorize release action, AMD hardware performance wording,
whole-app acceleration wording, broad RT-core wording, paper reproduction
wording, or app-specific native-engine logic.
