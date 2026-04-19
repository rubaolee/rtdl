# Goal 540: HIPRT Probe Backend Bring-Up

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal540_hiprt_probe`

HIPRT SDK: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

## Goal

Bring HIPRT into RTDL as a bounded backend probe surface before attempting workload execution. This goal answers whether RTDL can build and load a HIPRT native library, report HIPRT version information, and create/destroy a HIPRT context on the Linux NVIDIA CUDA path.

This is not a full HIPRT workload backend yet.

## Code Changes

- Added native HIPRT probe library source: `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- Added Python HIPRT runtime loader: `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- Exported public probe functions from RTDL: `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- Added skip-safe probe tests: `/Users/rl2025/rtdl_python_only/tests/goal540_hiprt_probe_test.py`
- Added `make build-hiprt` support: `/Users/rl2025/rtdl_python_only/Makefile`

## Public Probe Surface

```python
import rtdsl as rt

version = rt.hiprt_version()
probe = rt.hiprt_context_probe()
```

Expected result shape:

```python
{
    "version": (2, 2, 15109972),
    "api_version": 2002,
    "device_type": 1,
    "device_name": "NVIDIA GeForce GTX 1070",
}
```

## Linux Host Facts

- Host: `lx1`
- Kernel: `Linux lx1 6.17.0-20-generic #20~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Mar 19 01:28:37 UTC 2 x86_64`
- GPU: `NVIDIA GeForce GTX 1070`
- NVIDIA driver: `580.126.09`
- Driver-reported CUDA version: `13.0`
- HIPRT runtime library: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64/libhiprt0200264.so`

## Build Command

```bash
cd /tmp/rtdl_goal540_hiprt_probe
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Build result: `PASS`

The only compiler diagnostic was a warning inside vendor Orochi source about an ignored `fread` return value in `OrochiUtils.cpp`. RTDL code compiled successfully.

## Probe Command

```bash
cd /tmp/rtdl_goal540_hiprt_probe
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 - <<'PY'
import json
import rtdsl as rt
print(json.dumps({"version": rt.hiprt_version(), "probe": rt.hiprt_context_probe()}, indent=2))
PY
```

Observed output:

```json
{
  "version": [
    2,
    2,
    15109972
  ],
  "probe": {
    "version": [
      2,
      2,
      15109972
    ],
    "api_version": 2002,
    "device_type": 1,
    "device_name": "NVIDIA GeForce GTX 1070"
  }
}
```

Probe result: `PASS`

## Test Commands

Local macOS import/skip check:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal540_hiprt_probe_test
```

Result:

```text
Ran 2 tests in 0.000s
OK (skipped=2)
```

Linux real HIPRT probe test:

```bash
cd /tmp/rtdl_goal540_hiprt_probe
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest tests.goal540_hiprt_probe_test
```

Result:

```text
Ran 2 tests in 0.087s
OK
```

## Correctness Meaning

This validates:

- RTDL can compile a HIPRT native shim against the official HIPRT SDK 2.2.0 package.
- RTDL can load the resulting library from Python with `ctypes`.
- RTDL can report the HIPRT SDK version.
- RTDL can initialize Orochi on the CUDA path, discover the NVIDIA device, create a HIPRT context, and destroy it cleanly.
- The Python API degrades cleanly on machines without the HIPRT native library by raising a loader error; the unit test skips in that case.

## Explicit Non-Claims

- This does not validate AMD GPU hardware acceleration.
- This does not validate HIPRT on CPU. HIPRT did not provide a CPU RT fallback path for this goal.
- This does not validate RTDL workload execution through HIPRT.
- This does not claim HIPRT performance.
- This does not change the released OptiX, Vulkan, Embree, or CPU workload semantics.

## Verdict

Goal 540 implementation status: `PASS`, bounded to HIPRT backend probing and context creation.

Next HIPRT step, if approved: implement the first minimal HIPRT workload kernel with oracle parity, likely ray-triangle hit count or fixed-radius candidate filtering, before attempting broader ITRE lowering integration.
