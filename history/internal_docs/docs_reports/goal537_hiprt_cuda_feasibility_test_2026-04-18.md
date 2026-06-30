# Goal 537: HIP RT CUDA-Path Feasibility Test

Date: 2026-04-18
Status: HIP RT CUDA-path feasibility proven on Linux NVIDIA via two bounded paths

## Question

Can RTDL create a new experimental backend path for AMD HIP RT, and can the
current Linux NVIDIA host run a HIP RT CUDA-path smoke test before we have AMD
GPU hardware?

## Current Answer

The Linux NVIDIA host is reachable and has CUDA/NVIDIA capability. A first
probe found no system HIP RT install. After that, HIP RT source repositories
and official HIP RT SDK packages were installed under the Linux user's home
directory.

The initial current-source attempt was not sufficient:

- a build without an explicit CUDA SDK path produced `libhiprt0300164.so`, but
  the HIPRT `hiprtTest.CudaEnabled` smoke test reported zero CUDA devices
- a build with `CUDA_PATH=/usr` enabled CUEW, but failed to compile because the
  installed CUDA 12.0 headers are older than the CUDA 12.2-era symbols expected
  by the current HIPRT/Orochi source snapshot

The follow-up environment work found two working CUDA-path configurations:

- the official HIP RT SDK `v2.2.0e68f54` builds and runs a CUDA-only
  `00_context_creation` tutorial on the `NVIDIA GeForce GTX 1070`
- the same SDK builds and runs the `01_geom_intersection` ray/geometry tutorial
  when executed from the expected tutorial directory
- a local toolkit-only CUDA `12.2.2` install under
  `/home/lestat/vendor/cuda-12.2.2` allows the current HIPRT source tree to
  build with CUEW enabled, and `hiprtTest.CudaEnabled` passes

Therefore the answer is: **yes, the Linux NVIDIA host can run a native HIP RT
CUDA-path smoke test without AMD GPU hardware.** This is still not AMD hardware
validation and not an RTDL backend implementation.

The current test goal is therefore scoped to:

- detect HIP RT headers/libraries
- detect CUDA/NVIDIA host capability
- determine whether a HIP RT CUDA-path smoke test can be attempted
- attempt a bounded user-space HIP RT source install/build when artifacts are
  missing
- attempt official HIP RT SDK binaries and an older compatible SDK release
- attempt a non-system CUDA 12.2+ toolkit path for the current HIPRT source
- explicitly avoid claiming AMD GPU correctness or performance

## Source Boundary

AMD HIP RT documentation describes HIP RT as GPU-oriented and as supporting AMD
and NVIDIA GPUs. It also states that hardware-accelerated ray tracing works only
on AMD RDNA2-or-newer GPUs. Therefore this goal treats HIP RT as GPU-only for
RTDL planning and treats the GTX 1070 result as a CUDA compatibility smoke, not
as AMD RT-core acceleration evidence.

## Probe Artifact

Added reusable probe script:

- `scripts/goal537_hiprt_host_probe.py`

The script records:

- `nvidia-smi` availability and GPU identity
- CUDA compiler availability
- HIP compiler/config availability
- HIP RT header/library artifacts
- whether a HIP RT CUDA-path smoke test can be attempted
- explicit `can_validate_amd_gpu_backend=false`

## Local Mac Probe

Ran:

```text
PYTHONPATH=src:. python3 scripts/goal537_hiprt_host_probe.py \
  --machine macos-local-hiprt-probe \
  --output docs/reports/goal537_macos_hiprt_host_probe_2026-04-18.json
```

Result summary:

```json
{
  "can_attempt_hiprt_cuda_smoke_test": false,
  "can_validate_amd_gpu_backend": false,
  "has_cuda_gpu": false,
  "has_cuda_toolchain": false,
  "has_hip_toolchain": false,
  "has_hiprt_artifacts": false
}
```

This is expected on local macOS and does not answer the Linux NVIDIA
HIP RT CUDA-path question.

## Linux Probe

First attempt while the host was unreachable:

```text
ssh -o ConnectTimeout=8 -o BatchMode=yes lestat-lx1 'hostname; date -Is'
```

Result:

```text
ssh: connect to host 192.168.1.20 port 22: Operation timed out
```

Ping check:

```text
2 packets transmitted, 0 packets received, 100.0% packet loss
```

Therefore the Linux HIP RT CUDA-path probe could not run yet.

Retry after the host became reachable, before user-space HIPRT install:

```text
scp scripts/goal537_hiprt_host_probe.py lestat-lx1:/tmp/goal537_hiprt_host_probe.py
ssh -o ConnectTimeout=8 -o BatchMode=yes lestat-lx1 \
  'python3 /tmp/goal537_hiprt_host_probe.py \
    --machine linux-hiprt-cuda-probe \
    --output /tmp/goal537_linux_hiprt_host_probe_2026-04-18.json'
```

Historical console summary before HIPRT source install:

```json
{
  "can_attempt_hiprt_cuda_smoke_test": false,
  "can_validate_amd_gpu_backend": false,
  "has_cuda_gpu": true,
  "has_cuda_toolchain": true,
  "has_hip_toolchain": false,
  "has_hiprt_artifacts": false
}
```

Detected Linux host facts from that pre-install run:

- GPU: `NVIDIA GeForce GTX 1070`
- NVIDIA driver: `580.126.09`
- compute capability: `6.1`
- CUDA compiler: `/usr/bin/nvcc`
- CUDA compiler version: `12.0`
- HIP compiler/config: not found
- HIP RT headers/libraries: not found
- `libamdhip64.so.5` exists, but that is HIP runtime, not HIP RT

After the user-space install below, the saved
`docs/reports/goal537_linux_hiprt_host_probe_2026-04-18.json` was refreshed and
now detects the `/home/lestat/vendor/HIPRT` source/build artifacts. The
pre-install "missing HIP RT artifacts" state is retained here as historical
console evidence, not as the current JSON file contents.

## User-Space HIPRT Install Attempt

After the initial probe showed no HIP RT artifacts, the following user-space
source trees were installed on `lestat-lx1`:

- `/home/lestat/vendor/HIPRT`
- `/home/lestat/vendor/hiprtsdk`

Recorded revisions:

```text
HIPRT:    e3c01fce5860f5d74b959ae71abbbab6a5462aed
hiprtsdk: 2442d0d5832f7ee3e06c3daa768fb89958241fd4
```

The `hiprtsdk` repository is tutorial/example material and expects HIP RT SDK
artifacts to be provided separately. The `HIPRT` repository contains the source
used for the build attempt.

### Build Attempt A: Source Build Without Explicit CUDA_PATH

Command shape:

```text
cd /home/lestat/vendor/HIPRT
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBITCODE=OFF
cmake --build build -j4
```

Evidence files copied into this repository:

- `docs/reports/goal537_hiprt_cmake_configure_2026-04-18.log`
- `docs/reports/goal537_hiprt_cmake_build_2026-04-18.log`
- `docs/reports/goal537_hiprt_cuda_enabled_test_2026-04-18.log`

Outcome:

- build succeeded
- produced `/home/lestat/vendor/HIPRT/dist/bin/Release/libhiprt0300164.so`
- produced `/home/lestat/vendor/HIPRT/dist/bin/Release/unittest64`
- configure warned that `HIP_PATH` was not defined
- configure warned that the required CUDA version for this Orochi snapshot is
  `12.2`
- configure disabled CUEW because `CUDA_PATH` was not found

Smoke test:

```text
LD_LIBRARY_PATH=/home/lestat/vendor/HIPRT/dist/bin/Release \
  /home/lestat/vendor/HIPRT/dist/bin/Release/unittest64 \
  --gtest_filter=hiprtTest.CudaEnabled --device=0
```

Result:

```text
number of HIP devices detected = 0
number of CUDA devices detected = 0
NO COMPATIBLE DEVICE FOUND. check your driver.
```

Interpretation: the library artifact exists, but the no-`CUDA_PATH` build did
not produce a usable CUDA-path HIP RT runtime on this host.

### Build Attempt B: Source Build With CUDA_PATH=/usr

Command shape:

```text
cd /home/lestat/vendor/HIPRT
CUDA_PATH=/usr cmake -S . -B build_cuda -DCMAKE_BUILD_TYPE=Release -DBITCODE=OFF -DCUDA_PATH=/usr
cmake --build build_cuda -j4
```

Evidence files copied into this repository:

- `docs/reports/goal537_hiprt_cmake_configure_cuda_path_2026-04-18.log`
- `docs/reports/goal537_hiprt_cmake_build_cuda_path_2026-04-18.log`

Outcome:

- configure found CUDA SDK folder `/usr`
- configure enabled CUEW
- configure again warned that this Orochi snapshot expects CUDA `12.2`
- compile failed inside Orochi/CUEW against the installed CUDA `12.0` headers

Representative compile failures include missing newer CUDA symbols/types such
as:

- `CUcoredumpSettings`
- `CUgraphNodeParams`
- `CUmulticastObjectProp`
- `cudaKernel_t`
- `tcudaGetKernel`

Interpretation: making CUDA visible changes the failure mode from "no CUDA
device detected" to "current HIPRT/Orochi source is not compatible with this
host's CUDA 12.0 SDK headers."

## Linux Probe After User-Space HIPRT Build

Ran:

```text
HIPRT_ROOT=$HOME/vendor/HIPRT python3 /tmp/goal537_hiprt_host_probe.py \
  --machine linux-hiprt-source-build-probe \
  --output /tmp/goal537_linux_hiprt_source_build_probe_2026-04-18.json
```

Result artifact:

- `docs/reports/goal537_linux_hiprt_source_build_probe_2026-04-18.json`

Summary:

```json
{
  "can_attempt_hiprt_cuda_smoke_test": true,
  "can_validate_amd_gpu_backend": false,
  "has_cuda_gpu": true,
  "has_cuda_toolchain": true,
  "has_hip_toolchain": false,
  "has_hiprt_artifacts": true
}
```

Important distinction: the probe's `can_attempt_hiprt_cuda_smoke_test=true`
means required-looking files are discoverable after source build. It does not
mean the HIP RT CUDA runtime test passed. The actual smoke test did not pass.

## Official HIP RT SDK v3.0.9ba63f3 Attempt

Official GPUOpen endpoint:

```text
https://gpuopen.com/download/AMD-HIP-RT/
```

The endpoint redirected to:

```text
/download/hiprtSdk-3.0.9ba63f3.zip
```

Evidence files:

- `docs/reports/goal537_official_hiprt_head_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_sha256_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_files_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_context_run_2026-04-18.log`

Installed path:

```text
/home/lestat/vendor/hiprt-official/hiprtSdk-3.0.9ba63f3
```

SHA-256:

```text
dc1b8bd4842c74d580561449a3342911f7617e1f51ea6541fc3290e3f2e36e89  hiprtSdk-3.0.9ba63f3.zip
```

Useful installed artifacts include:

- `hiprt/linux64/libhiprt0300064.so`
- `hiprt/linux64/hiprt03000_nv.fatbin`
- `hiprt/linux64/hiprt03000_nv_lib.fatbin`

The stock `00_context_creation` tutorial built successfully, but its default
initialization path tried HIP and CUDA together. On this NVIDIA-only host, the
system `libamdhip64.so.5` exists but is incomplete for this SDK path, producing
an Orochi runtime failure before a clean CUDA-only context could be established.

When patched to compile a CUDA-only CUEW path, v3.0 still requires CUDA
12.2-era headers. With system CUDA 12.0 this reproduces the same CUEW compile
failure recorded earlier.

## Official HIP RT SDK v2.2.0e68f54 CUDA-Path Success

The official version-history endpoint also exposes older SDK packages. The
following package was installed:

```text
/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

SHA-256:

```text
72172d20b44f6e4dc72ea760b56cb73bfcab857aa5c475168cbabbc771dff66b  hiprtSdk-2.2.0e68f54.zip
```

Evidence files:

- `docs/reports/goal537_official_hiprt_2.2.0e68f54_sha256_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_2.2.0e68f54_cuda_only_make_context_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_2.2.0e68f54_cuda_only_run_context_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_2.2_cuda_only_make_geom_2026-04-18.log`
- `docs/reports/goal537_official_hiprt_2.2_cuda_only_run_geom_from_dir_2026-04-18.log`

Bounded local patches used only for this scratch smoke test:

- `ORO_API_HIP | ORO_API_CUDA` changed to `ORO_API_CUDA`
- `OROCHI_ENABLE_CUEW` added to the tutorial build
- `CPPFLAGS=-fpermissive` used for this older SDK's `make_uint2` declaration
  issue with GCC 13

Context smoke result:

```text
Executing on 'NVIDIA GeForce GTX 1070'
```

Ray/geometry tutorial result:

```text
hiprt ver.02002
Executing on 'NVIDIA GeForce GTX 1070'
image written at 01_geom_intersection.png
success
```

Interpretation: the Linux NVIDIA host can run a real HIP RT CUDA-path workload
with an older official SDK compatible with the current CUDA 12.0-era system
toolchain, after forcing the intended CUDA-only path.

## Local CUDA 12.2.2 Toolkit Path Success

Installed CUDA 12.2.2 toolkit-only under the user account:

```text
/home/lestat/vendor/cuda-12.2.2
```

This did not replace the system driver or `/usr/bin/nvcc`. The system still has
CUDA 12.0 under `/usr`; the test build explicitly used the local toolkit path.

Evidence files:

- `docs/reports/goal537_cuda_12_2_runfile_head_2026-04-18.log`
- `docs/reports/goal537_cuda_12_2_runfile_sha256_2026-04-18.log`
- `docs/reports/goal537_cuda_12_2_user_install_2026-04-18.log`
- `docs/reports/goal537_hiprt_cmake_configure_cuda122_2026-04-18.log`
- `docs/reports/goal537_hiprt_cmake_build_cuda122_2026-04-18.log`
- `docs/reports/goal537_hiprt_cuda122_enabled_test_2026-04-18.log`

CUDA runfile SHA-256:

```text
2b39aae3e7618d9f59a3c8fa1f1bc61f29c0b0e0df75fb05076badb352952ef2  cuda_12.2.2_535.104.05_linux.run
```

Installed toolkit check:

```text
nvcc: NVIDIA (R) Cuda compiler driver
Cuda compilation tools, release 12.2, V12.2.140
```

Current HIPRT source rebuild:

```text
CUDA_PATH=/home/lestat/vendor/cuda-12.2.2 \
  cmake -S . -B build_cuda122 -DCMAKE_BUILD_TYPE=Release -DBITCODE=OFF
CUDA_PATH=/home/lestat/vendor/cuda-12.2.2 \
  cmake --build build_cuda122 -j4
```

Result:

```text
BUILD:0
[100%] Built target unittest
```

CUDA smoke test:

```text
LD_LIBRARY_PATH=/home/lestat/vendor/HIPRT/dist/bin/Release \
  /home/lestat/vendor/HIPRT/dist/bin/Release/unittest64 \
  --gtest_filter=hiprtTest.CudaEnabled --device=0
```

Result:

```text
Executing on 'NVIDIA GeForce GTX 1070'
[  PASSED  ] 1 test.
```

Interpretation: the current HIPRT source tree is viable on this Linux NVIDIA
host when built against CUDA 12.2.2 headers/toolkit, even though the system
default CUDA is 12.0.

## Interpretation

The Linux host can support HIP RT CUDA-path experiments generally. There are now
two validated paths:

- official HIP RT SDK v2.2 with a CUDA-only tutorial build
- current HIPRT source with a user-space CUDA 12.2.2 toolkit

This means:

- HIP RT artifacts are no longer completely missing after user-space install.
- HIP RT CUDA-path runtime testing is not fundamentally blocked on this Linux
  NVIDIA host.
- The current HIPRT/Orochi source snapshot needs CUDA 12.2-compatible headers
  for the CUEW-enabled path; the local user-space CUDA 12.2.2 toolkit satisfies
  that requirement.
- The older official HIP RT SDK v2.2 can run a real tutorial workload with the
  system CUDA 12.0-era environment when forced to CUDA-only.
- This is not an AMD GPU validation.
- This is not evidence of HIP RT performance.
- This is not evidence of AMD RT hardware acceleration; GPUOpen documents that
  HIP RT hardware ray tracing acceleration applies to AMD RDNA2-or-newer GPUs.

## Next Required Engineering Action

RTDL may now open a bounded HIP RT experimental backend design goal, but it
should be scoped carefully:

- first target NVIDIA CUDA-path correctness only
- use either the current HIPRT source plus
  `/home/lestat/vendor/cuda-12.2.2`, or the official v2.2 SDK as a conservative
  tutorial-proven baseline
- keep AMD GPU correctness and AMD RT hardware acceleration out of scope until
  an AMD GPU host is available
- do not claim performance until RTDL owns a backend implementation and compares
  it against existing Embree/OptiX/Vulkan/CPU paths

Remaining environment options:

- use official v2.2 SDK for an initial minimal RTDL backend smoke
- use current HIPRT source with local CUDA 12.2.2 for a newer API path
- provide an AMD GPU host if the goal is actual AMD HIP RT correctness or
  performance validation

## Acceptance Boundary

This goal concludes:

- `hiprt_source_artifacts_installed`
- `hiprt_source_library_build_succeeded_without_cuda_path`
- `hiprt_cuew_enabled_build_failed_against_cuda_12_0`
- `official_hiprt_v3_sdk_installed`
- `official_hiprt_v2_2_cuda_context_smoke_passed`
- `official_hiprt_v2_2_cuda_geometry_tutorial_passed`
- `cuda_12_2_2_toolkit_installed_user_space`
- `current_hiprt_source_cuda122_cuew_build_passed`
- `current_hiprt_source_cuda122_cuda_smoke_passed`
- `hiprt_cuda_path_feasible_on_linux_nvidia`

It cannot conclude:

- AMD HIP RT backend correctness
- AMD GPU acceleration
- RTDL HIP RT support
- performance

Those require a later backend implementation and, for AMD-specific claims, a
supported AMD GPU validation host.
