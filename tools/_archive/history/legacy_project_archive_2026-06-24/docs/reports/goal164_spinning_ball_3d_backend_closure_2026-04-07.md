# Goal 164 Report: Spinning-Ball 3D Backend Closure

## Decision

The first true 3D spinning-ball demo slice is now closed on Linux with
deterministic row-level parity across:

- `cpu_python_reference`
- `embree`
- `optix`
- `vulkan`

for the bounded `ray_triangle_hit_count` 3D workload line.

## What Landed

Main demo and test:

- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_spinning_ball_3d_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal164_spinning_ball_3d_demo_test.py`

Public/runtime-side 3D additions:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/types.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`

Native backend 3D entry points:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`

## 3D Demo Shape

The demo is a true 3D pinhole-camera scene:

- triangulated sphere mesh
- two orbiting light sources with trails
- RTDL handles dense ray-vs-triangle hit queries
- Python handles:
  - camera setup
  - analytic shading
  - animation timing
  - frame writing

This preserves the intended v0.3 split:

- RTDL = heavy geometric-query engine
- Python = surrounding application logic

## Local Validation

Commands:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m compileall \
  src/rtdsl/optix_runtime.py \
  tests/goal164_spinning_ball_3d_demo_test.py \
  examples/visual_demo/rtdl_spinning_ball_3d_demo.py
PYTHONPATH=src:. python3 -m unittest tests.goal164_spinning_ball_3d_demo_test
```

Observed result:

- `Ran 7 tests`
- `OK`
- local backend-dependent cases skipped where the native backend is unavailable

## Linux Row-Level Parity

Environment:

- host: `lestat@192.168.1.20`
- working directory:
  - `/home/lestat/work/rtdl_v03_3d_backend_try`

Preparation:

- synced current working tree to the Linux host
- rebuilt native backends:
  - `make build-optix`
  - `make build-vulkan`

Deterministic parity command:

```bash
cd /home/lestat/work/rtdl_v03_3d_backend_try
PYTHONPATH=src:. python3 -m unittest tests.goal164_spinning_ball_3d_demo_test
```

Observed result:

- `Ran 7 tests`
- `OK`

The test module checks raw RTDL rows, not image-level output only, for:

- one-ray/one-triangle sanity
- medium sphere-mesh scene
- actual spinning-ball demo ray/triangle pack

## Linux Demo Smoke Results

Same-scene Linux smoke reruns used:

- `64 x 64`
- `12` latitude bands
- `24` longitude bands
- `2` frames
- comparison backend:
  - `cpu_python_reference`

Observed result:

- `embree`
  - frame parity: `[true, true]`
  - query share: `0.2910365123873938`
- `optix`
  - frame parity: `[true, true]`
  - query share: `0.42824791422914515`
- `vulkan`
  - frame parity: `[true, true]`
  - query share: `0.4172197171810654`

## Important Fixes

Two real fixes were needed during closure.

### 1. Python/runtime 3D packing and dispatch

The runtime side needed explicit 3D dimension handling so that:

- empty 3D payloads do not silently fall back to 2D
- pre-packed inputs fail fast on dimension mismatch
- all three native backends select their `*_3d` symbols on the 3D path

### 2. OptiX 3D parity bug

The remaining OptiX divergence was inside the native 3D path.

Accepted fix:

- remove the extra local unpack/copy detour
- operate directly on the packed `RtdlRay3D` and `RtdlTriangle3D` ABI structs
- use the exact 3D hit test directly in the final ray/triangle loop

After that fix, the deterministic Linux parity matrix passed.

## Honest Boundary

This goal closes a bounded 3D ray/triangle workload line.

Accepted meaning:

- the spinning-ball 3D demo is real
- Linux row-level parity is clean across Embree, OptiX, and Vulkan
- RTDL can now support a true 3D visual-demo query core in this narrow line

This does not mean:

- RTDL is now a general rendering engine
- the whole backend stack is broadly optimized for arbitrary 3D rendering
- Vulkan 3D performance is already a mature optimized story

The current Vulkan 3D path is accepted as correctness-first, not as a mature
performance flagship.

## Conclusion

Goal 164 closes the first true 3D visual-demo backend line for RTDL:

- real 3D scene
- real Linux backend coverage
- raw-row parity, not just image smoke
- OptiX correctness issue found and fixed during closure

That is enough to treat the spinning-ball 3D demo as a real `v0.3` foundation
instead of only a CPU/reference prototype.
