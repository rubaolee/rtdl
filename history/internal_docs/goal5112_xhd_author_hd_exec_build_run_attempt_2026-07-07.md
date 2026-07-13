# Goal5112 - X-HD Author `hd_exec` POD Build/Run Result

Date: 2026-07-07

## Status

```text
completed_tiny_same_input_author_json_gate_matched__author_build_patch
```

Goal5112 built the pinned X-HD author `hd_exec` on POD, ran it on the
Goal5111 tiny same-input WKT fixture, and compared author `HDResult` against
the deterministic RTDL exact Hausdorff reference.

Result:

```text
author_hd_result = 1.0
rtdl_reference.hausdorff = 1.0
abs_diff = 0.0
tolerance = 1e-9
matched = true
```

This closes the first bounded X-HD same-input author JSON gate. It does **not**
claim full paper reproduction, exact paper dataset reproduction, or performance.

## Inputs

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny2d_a.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny2d_b.wkt
Paper-reproduction-apps/x-hd-paper/data/fixtures/tiny2d_expected.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
```

Expected exact reference:

```text
directed_a_to_b = 1.0
directed_b_to_a = 1.0
hausdorff       = 1.0
tolerance       = 1e-9
```

## Author Source Provenance

Pinned repository:

```text
https://github.com/pwrliang/X-HD.git
```

Pinned commit:

```text
7bf41c8442d059c94f4178355c6d5a10571d9658
```

Observed on POD:

```text
HEAD: 7bf41c8442d059c94f4178355c6d5a10571d9658
submodules:
  0e174fe3f2662b2ee7530c73aedcb85114ef6a3b thirdparty/cudaKDTree
  4296cc91b5c8c26d4e7d7aac0cee2b194ffc5800 thirdparty/rply
```

This independently closes the Goal5110 non-blocking provenance note about the
pinned author commit and submodules.

## POD Environment

```text
host: 45c502cfccb5
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
CUDA runtime reported by nvidia-smi: 12.4
nvcc: 12.0.140
cmake used: 3.30.4
compiler: gcc/g++ 11
```

The bare SSH command initially failed because the agent used the wrong key.
The successful POD route used the project key explicitly:

```text
ssh -i ~/.ssh/id_ed25519_rtdl_codex_current_pod root@213.173.108.24 -p 13502
```

## Author Build Patch

The author source did not build/run as raw source on the POD toolchain. A
minimal build-compatibility patch was required and is recorded here:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_author_build_patch_goal5112.diff
```

Patch summary:

1. `NVIDIA/optix-dev` was pinned from `v9.0.0` to `v7.7.0`.
   - Raw `v9.0.0` and `v8.1.0` builds linked, but `optixInit()` failed at
     runtime with `OPTIX_ERROR_UNSUPPORTED_ABI_VERSION` on this POD driver.
   - `v7.7.0` matched the runtime driver ABI and executed successfully.
2. Three Thrust `transform_reduce` device lambdas were wrapped with
   `cuda::proclaim_return_type`.
   - This fixes the CCCL/libcudacxx error:
     `Attempt to use an extended __device__ lambda in a context that requires
     querying its return type in host code`.
   - The wrapped lambdas are in:
     `src/geoms/mbr_helper.h` and
     `src/hd_impl/hausdorff_distance_nearest_neighbor_search.h`.

The patch is classified as `Author+BuildPatch`: it changes build/toolchain
compatibility, not Hausdorff algorithm semantics.

## Build Evidence

Configure/build logs:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5112_pod_configure_optix77.log
Paper-reproduction-apps/x-hd-paper/results/goal5112_pod_build_optix77.log
```

Build result:

```text
[100%] Built target hd_exec
```

The older local configure log remains as a local-machine blocker record only:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5112_local_cmake_configure.log
critical local error: No CUDA toolset found
```

It is no longer the active Goal5112 outcome.

## Author JSON Gate Evidence

Primary POD summary:

```text
Paper-reproduction-apps/x-hd-paper/results/tiny2d_author_gate_summary_pod.json
```

Author raw JSON:

```text
Paper-reproduction-apps/x-hd-paper/results/tiny2d_author_hd_exec_output_pod.json
```

POD command executed by the runner:

```text
hd_exec
  -input1 tiny2d_a.wkt
  -input2 tiny2d_b.wkt
  -n_dims 2
  -input_type wkt
  -variant rt
  -execution gpu
  -json xhd_author_tiny2d_optix77_v2.json
  -overwrite=true
  -check=false
```

Observed author stderr includes:

```text
Points A: 3 Points B: 3
Avg Running Time 3.901 ms
HausdorffDistance: distance is 1
```

The timing field is retained as author phase metadata only. No performance
claim is authorized from this tiny fixture.

## Runner Hardening

During POD execution, the runner exposed a real fail-closed bug: if the author
subprocess failed before writing JSON, the runner wrote a diagnostic summary
but returned success because `matched` was `null`. This has been fixed.

Current behavior:

```text
author subprocess returncode != 0 -> author_run_failed=true, matched=false, runner exit code 2
```

Regression coverage was added in:

```text
tests/goal5111_xhd_author_json_gate_test.py
```

## Verification

Local tests:

```text
py -m unittest tests.goal5110_xhd_paper_app_scaffold_test tests.goal5111_xhd_author_json_gate_test
```

Result:

```text
Ran 8 tests in 0.174s
OK
```

## What This Proves

- The pinned author source can be built on POD as `Author+BuildPatch`.
- The author `variant=rt` path executes on the tiny WKT fixture.
- The author `HDResult` matches the deterministic RTDL exact Hausdorff
  reference for that same tiny input.
- The app-owned runner now fails closed on author subprocess failure.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not prove author performance parity or RTDL speedup.
- It does not prove raw unpatched author source execution on this POD.
- It does not prove that the existing RTDL Hausdorff benchmark assets already
  reproduce paper figures.

## Recommended Next Goal

Move to a slightly larger bounded same-input workload and compare:

```text
author HDResult
RTDL exact/reference HDResult
input point counts and dimensionality
author JSON phase fields as metadata only
```

Keep `Author+BuildPatch` provenance explicit until a raw-author build is shown
on a compatible driver/toolchain.
