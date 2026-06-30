# Goal2543 Barnes-Hut Authors-Code OptiX Build And Timing

Date: 2026-05-23

## Scope

This report updates the earlier authors-code gate after the user provided local
NVIDIA OptiX SDK installers. It records the first successful build and timing
run of the published OWL/RT-BarnesHut artifact on the RTX A5000 pod.

This is still a bounded engineering comparison. The authors' sample and the
RTDL benchmark prototype do not currently share an identical contract:

- authors' sample: OWL/OptiX RT-BarnesHut code from the published artifact,
  3-D body data path, hardcoded compile-time body count;
- RTDL prototype: app-independent generic 2-D aggregate-frontier weighted
  vector-sum contract, Torch/CUDA partner prototype, validated against the
  RTDL reference contract.

Therefore the timings below are useful for positioning and next-target
selection, but they do not authorize a public speedup claim.

## Pod And SDK Environment

Pod:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Observed hardware/software:

- host: `05cd7c946142`
- GPU: NVIDIA RTX A5000, 24 GB
- driver: `565.57.01`
- initial CUDA toolkit: `/usr/local/cuda-12.8`, `nvcc 12.8.93`
- side-by-side CUDA compiler installed for compatibility:
  `/usr/local/cuda-12.6`, `nvcc 12.6.85`
- OptiX SDK installed from user-provided official NVIDIA installer:
  `/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64`

The OptiX SDK was not available from the pod image. The user downloaded:

`NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64-35015278.sh`

The SDK was copied to the pod and installed with:

`/root/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64-35015278.sh --skip-license --prefix=/opt/optix --include-subdir`

## Authors' Artifact

Artifact:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `BarnesHutRT`
- commit observed earlier on this pod: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- sample target: `samples/cmdline/s01-rtbarneshut`
- CMake target: `rtbarneshut`

## Build Workarounds

The build is now possible, but required three environment/toolchain workarounds:

1. Missing pod packages:

`apt-get install -y libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev libxmu-dev libxi-dev libtbb-dev libxrandr-dev libxinerama-dev libxcursor-dev`

2. Missing complete standard header under the current CUDA/GCC toolchain:

`-DCMAKE_CUDA_FLAGS="-include array"`

Without this flag, `hostCode.cu` fails on `std::array<float, 5>`.

3. Pod exposes one CUDA device as ordinal `0`, while the sample hardcodes:

`int gpuDeviceID = 1;`

For this pod timing run, the pod checkout was patched to:

`int gpuDeviceID = 0;`

This is an environment portability patch, not an algorithmic change.

The sample also hardcodes:

`constexpr int NUM_POINTS = 100000000;`

For size-matched diagnostics, the pod checkout was rebuilt with
`NUM_POINTS = 8192` and `NUM_POINTS = 32768`.

## CUDA 12.8 Failure

The first successful build used CUDA 12.8, but runtime failed:

`Unsupported .version 8.7; current version is '8.6'`

The pod driver line is R565. CUDA 12.8 generated PTX newer than the driver's
OptiX path accepted. Installing CUDA 12.6 compiler/dev components and rebuilding
with `/usr/local/cuda-12.6/bin/nvcc` fixed this runtime issue.

Configure/build shape:

`cmake -S . -B build-rtdl-bh-optix81-cuda126 -DCMAKE_BUILD_TYPE=Release -DOptiX_ROOT_DIR=/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.6/bin/nvcc -DCUDAToolkit_ROOT=/usr/local/cuda-12.6 -DCMAKE_CUDA_ARCHITECTURES=86 -DCMAKE_CUDA_FLAGS="-include array" -DBUILD_TESTING=OFF`

`cmake --build build-rtdl-bh-optix81-cuda126 --target rtbarneshut -j$(nproc)`

## Authors-Code Timing

Command shape:

`build-rtdl-bh-optix81-cuda126/rtbarneshut new /root/rtbarneshut_<N>_input.txt`

The authors' executable reports three times:

- `Preprocessing Time`
- `RT Cores Force Calculations time`
- `Execution time`

Repeated warm runs:

| Bodies | Preprocessing time (ms) | RT Cores force time (ms) | Execution time (ms) |
|---:|---:|---:|---:|
| 8,192 | 19.648 | 5.462 | 27.247 |
| 8,192 | 18.759 | 5.530 | 27.408 |
| 8,192 | 18.894 | 5.346 | 27.496 |
| 32,768 | 19.354 | 6.616 | 29.294 |
| 32,768 | 19.638 | 6.634 | 29.592 |
| 32,768 | 20.609 | 6.677 | 29.489 |

Minimum observed authors-code force times:

| Bodies | Authors OWL/OptiX force min (ms) |
|---:|---:|
| 8,192 | 5.346 |
| 32,768 | 6.616 |

## RTDL Diagnostic Comparison

The closest RTDL GPU prototype evidence is Goal2542:

- backend: Torch/CUDA extension;
- contract: `generic_aggregate_frontier_weighted_vector_sum_2d_v1`;
- traversal: DFS resume-index rope;
- device: NVIDIA RTX A5000;
- correctness: exact traversal/contribution-count match vs RTDL reference,
  floating-point checksum deltas only.

| Bodies | RTDL rope resident kernel min (ms) | Authors OWL/OptiX force min (ms) | Boundary |
|---:|---:|---:|---|
| 8,192 | 7.035 | 5.346 | not same contract |
| 32,768 | 37.036 | 6.616 | not same contract |

Same-contract CPU baseline from Goal2539:

| Bodies | RTDL same-contract C++ 16-thread CPU (ms) | RTDL rope resident kernel min (ms) |
|---:|---:|---:|
| 8,192 | 6.01 | 7.035 |
| 32,768 | 58.29 | 37.036 |

## Engineering Interpretation

The authors' OWL/OptiX sample is now buildable and fast on the pod once the
environment is made compatible. That changes the Barnes-Hut benchmark status:
we no longer need to treat authors-code comparison as unavailable.

However, it also clarifies the real work left:

- RTDL's generic partner prototype is correct, app-independent, and already
  competitive with the same-contract CPU baseline at 32K bodies.
- The authors' optimized OWL/OptiX path is materially faster than the current
  RTDL Torch/CUDA prototype, especially at 32K.
- The gap is expected because RTDL currently uses one thread per source with
  generic arrays, source-dependent traversal divergence, exact-leaf loops, and
  a `contains_source` path that still carries avoidable per-node cost.
- The next RTDL optimization should target the generic runtime contract, not a
  Barnes-Hut-specific native kernel.

Recommended next target:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1` resident partner/native
optimization with source-containment acceleration, warp/block scheduling for
high-work sources, and repeated-timestep resident-state timing.

## Claim Boundary

Authorized internal statements:

- The authors' OWL/RT-BarnesHut sample can be built on the A5000 pod with
  OptiX SDK 8.1.0 and CUDA 12.6.
- On this pod, the authors' reported RT-core force phase measured about
  `5.35 ms` at 8,192 bodies and `6.62 ms` at 32,768 bodies after warmup.
- RTDL's current generic Torch/CUDA rope prototype measured `7.03 ms` at 8,192
  and `37.04 ms` at 32,768 for its own 2-D reference contract.

Not authorized:

- public RTDL-vs-paper speedup claims;
- paper reproduction claims;
- same-contract RTDL-vs-authors claims;
- claims that the RTDL native engine already matches the OWL/OptiX architecture.
