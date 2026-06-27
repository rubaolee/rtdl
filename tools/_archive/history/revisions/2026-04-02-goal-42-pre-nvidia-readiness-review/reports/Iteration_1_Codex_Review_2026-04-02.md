# Goal 42 Codex Review

Repo reviewed: `/Users/rl2025/rtdl_python_only`
Head: `ef9db4a`

## Summary

The controlled repo now contains a real OptiX runtime slice and the earlier Goal 39 merge blockers appear closed. I did not find a new hard correctness blocker in the imported Python/ABI surface from static inspection plus the focused interop tests. The main remaining issues are pre-NVIDIA readiness gaps rather than obvious algorithmic defects.

## Findings

### 1. No hardware-independent build smoke exists for the imported OptiX native file

Files:
- `src/native/rtdl_optix.cpp`
- `Makefile`
- `tests/optix_embree_interop_test.py`

The new focused OptiX tests validate Python-side type interop only. They do not compile `src/native/rtdl_optix.cpp`, validate header discovery, or validate the `build-optix` target shape on a machine that actually has CUDA/OptiX headers installed. This is not a blocker for merge, but it is still a bring-up risk because the first NVIDIA session may be spent on basic toolchain breakage rather than runtime validation.

Severity: medium readiness gap.

### 2. `build-optix` has no preflight checks and will fail opaquely if defaults are wrong

Files:
- `Makefile`

`build-optix` assumes `OPTIX_PREFIX=/opt/optix` and `CUDA_PREFIX=/usr/local/cuda`, then directly invokes `$(CUDA_PREFIX)/bin/nvcc`. On a fresh GPU host with a different layout, this will fail immediately, but the failure mode is just the raw compiler/command error. The repo should ideally record a bring-up checklist or preflight helper before first GPU use.

Severity: medium readiness gap.

### 3. OptiX runtime docs still describe search path item 2 as `.so` only

Files:
- `src/rtdsl/optix_runtime.py`

The header comment still says search order item 2 is `build/librtdl_optix.so`, but `_find_optix_library()` is actually platform-aware and uses `.dylib` on Darwin. The implementation is correct; the comment is stale. This is minor, but since this file will be the first thing we read during bring-up, the comment should match the loader behavior.

Severity: low doc mismatch.

### 4. The first GPU session still lacks a checked-in bring-up procedure

Files:
- `docs/goal_39_optix_backend_audit.md`
- `docs/reports/goal39_optix_backend_audit_2026-04-02.md`
- repo root docs

The repo now has audit history and imported OptiX code, but it does not yet have one concise, operational bring-up doc for the first NVIDIA machine. We still need a single checklist covering environment variables, expected toolchain binaries, build command, loader verification, first smoke test, and what counts as success/failure.

Severity: medium readiness gap.

## Current Codex Verdict

- merge/import state: acceptable
- pre-NVIDIA readiness: not fully closed yet
- recommended next step: write the first-GPU bring-up checklist and add one build-oriented readiness pass before connecting hardware
