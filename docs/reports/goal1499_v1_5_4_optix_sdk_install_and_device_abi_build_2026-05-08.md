# Goal 1499: OptiX SDK Install And Device ABI Build

## Verdict

The current pod can be made OptiX-build-ready by installing NVIDIA's public
GitHub OptiX SDK `v8.0.0` checkout and linking it as `/opt/optix`.

After that setup, `make build-optix` succeeds, `build/librtdl_optix.so` exists,
Goal 1489 preflight is green, and the reserved
`rtdl_optix_collect_k_bounded_i64_device` symbol is exported.

## Pod Setup

- Pod: `root@213.173.108.6 -p 17339`
- RTDL checkout: `/root/rtdl_goal1498/rtdl`
- RTDL commit: `d4c1205837851226705e57b52404a395734a431b`
- OptiX SDK source: `https://github.com/NVIDIA/optix-sdk`
- OptiX SDK tag: `v8.0.0`
- OptiX SDK path: `/root/vendor/optix-sdk`
- Standard preflight link: `/opt/optix -> /root/vendor/optix-sdk`

## Evidence

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk` succeeded.
- `build/librtdl_optix.so` was produced.
- Exported symbols include:
  `rtdl_optix_collect_k_bounded_i64` and
  `rtdl_optix_collect_k_bounded_i64_device`.
- `optix_runtime.optix_version()` returned `[8, 0, 0]`.
- Goal 1489 preflight after the `/opt/optix` link returned:
  `valid_for_optix_device_buffer_execution_work=true`.

## Device ABI Boundary

The reserved device symbol is present, but it is still intentionally
fail-closed. A direct `ctypes` call returned status `1` with:

`rtdl_optix_collect_k_bounded_i64_device is ABI-reserved but not implemented; do not use as Goal1493 device-buffer execution evidence`

The call zeroed emitted count, overflow flag, and transfer counters.

## Artifact Paths

- `docs/reports/goal1499_make_build_optix_with_github_sdk.log`
- `docs/reports/goal1499_make_build_optix_with_github_sdk.exit`
- `docs/reports/goal1499_optix_collect_k_symbols_2026-05-08.txt`
- `docs/reports/goal1499_optix_collect_k_symbols_2026-05-08.exit`
- `docs/reports/goal1499_native_device_stub_ctypes_2026-05-08.json`
- `docs/reports/goal1499_native_device_stub_ctypes_2026-05-08.exit`
- `docs/reports/goal1499_optix_preflight_after_sdk_link_2026-05-08.json`
- `docs/reports/goal1499_optix_preflight_after_sdk_link_2026-05-08.md`
- `docs/reports/goal1499_optix_preflight_after_sdk_link_2026-05-08.exit`
- `docs/reports/goal1499_optix_version_2026-05-08.json`
- `docs/reports/goal1499_optix_version_2026-05-08.exit`

## Correction

The earlier Goal 1498 conclusion that the pod was blocked by missing OptiX
headers was true before SDK installation. It is no longer the current blocker
after installing the public OptiX SDK checkout and linking `/opt/optix`.

The current blocker is implementation: the device-pointer ABI exists and builds,
but the native device execution body is still a fail-closed stub.

## Claim Boundary

Goal 1499 records SDK setup, build, symbol, version, and fail-closed ABI
evidence only. It does not run a real OptiX device-buffer collect-k execution,
does not prove true zero-copy, and does not authorize public speedup wording,
whole-app claims, partner tensor handoff, stable primitive promotion, or release
action.
