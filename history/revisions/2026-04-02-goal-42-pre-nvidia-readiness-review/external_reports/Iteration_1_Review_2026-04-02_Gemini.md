I will begin by exploring the codebase to locate OptiX-related files and understand the current state of the backend integration.
I will now examine `src/rtdsl/optix_runtime.py`, `docs/goal_39_optix_backend_audit.md`, and the `src/native/` directory to understand the current status and implementation of the OptiX backend.
I will now read the `docs/goal_39_optix_backend_audit.md` and `src/rtdsl/optix_runtime.py` files.
I will now read the contents of `src/rtdsl/optix_runtime.py` to confirm the status of the OptiX backend integration.
I have confirmed that `optix_runtime.py` is structurally complete and mirrors `embree_runtime.py`. I will now examine the `Makefile` to understand the build process for `librtdl_optix.so`.
The `Makefile` contains a `build-optix` target that requires `OPTIX_PREFIX` and `CUDA_PREFIX`. Since the current machine is macOS, this will likely fail. I'll now examine `tests/optix_embree_interop_test.py` to understand the OptiX testing procedures.
`optix_embree_interop_test.py` verifies structural interop but skips OptiX execution. I'll search for other OptiX-related tests now.
I found only one test file with "optix" in its name. I'll now search for "optix" across all files in the `tests/` directory.
`rt.generate_optix_project` is verified in several tests, and golden files include OptiX-specific code. I haven't found a test for `run_optix` or `prepare_optix` execution, likely due to macOS limitations. I'll check `run_full_verification.py` for any such tests.
`run_full_verification.py` lacks OptiX smoke tests. I'll examine `src/rtdsl/runtime.py` for backend selection logic and check if `rtdsl.baseline_runner` supports an `optix` backend.
`src/rtdsl/runtime.py` lacks a backend-selecting `run` function, only defining `run_cpu` and `run_cpu_python_reference`. I'll re-examine `src/rtdsl/__init__.py` for top-level exports.
`__init__.py` exports various `run_*` functions. I'll now examine `src/rtdsl/baseline_runner.py` to understand how `run_baseline_case` operates.
`baseline_runner.py` lacks OptiX support. I've found that the OptiX backend is present but untested on current hardware due to build dependencies. API parity looks promising, but C++ implementation completeness in `rtdl_optix.cpp` remains to be verified. I'll now examine that file for workload implementation and placeholders.
I have completed a thorough investigation of the OptiX backend and its integration within the RTDL project. The backend is logically mature, mirroring the Embree API and supporting all six core workloads. However, it remains unverified on NVIDIA hardware. I will now synthesize these findings into a comprehensive pre-NVIDIA readiness review, covering summary, severity-ordered findings, current readiness, remaining tasks, and a final verdict.
Roadmap Milestone D, "real OptiX/CUDA execution path wired to generated artifacts," is currently represented by the unverified `src/native/rtdl_optix.cpp`. I've gathered all necessary information.
# Pre-NVIDIA Readiness Review: RTDL OptiX Backend

**Project:** RTDL (Python-only)  
**Date:** Thursday, April 2, 2026  
**Repository Head:** `ef9db4a`  
**Environment:** macOS (Darwin) — No NVIDIA hardware present.

---

## 1. Summary
The RTDL project possesses a mature-looking OptiX backend that mirrors the Embree (CPU) implementation in both Python API and functional scope. It supports all six core workloads (LSI, PIP, Overlay, RayHitCount, SegmentPolygonHitcount, PointNearestSegment). The integration utilizes a C++ native library (`src/native/rtdl_optix.cpp`) that employs NVRTC for runtime CUDA compilation, eliminating the need for pre-compiled PTX files. However, as this environment lacks NVIDIA hardware, the backend has never been built or executed in this repository.

## 2. Findings (Ordered by Severity)

### [CRITICAL] No Build/Execution Baseline
The code has never been compiled or run on the target platform (NVIDIA/Linux). There is a significant risk of build-time failures due to missing or mismatched dependencies (CUDA Toolkit, OptiX SDK) and potential runtime issues in the complex C++/CUDA interop layer.

### [HIGH] Lack of Execution-Level Test Coverage
Current tests (`tests/optix_embree_interop_test.py`) only verify structural interop (data layout parity). There are no automated tests that invoke `run_optix` or `prepare_optix`. The first execution on an NVIDIA machine will be a "cold start" for the entire GPU stack.

### [MEDIUM] Hardcoded Environment Assumptions
The `Makefile` relies on `OPTIX_PREFIX` and `CUDA_PREFIX` environment variables. If the NVIDIA machine uses non-standard paths (e.g., specific versions in `/usr/local/cuda-12.x`), the build will fail immediately without clear diagnostic hints.

### [LOW] NVRTC JIT Overhead
The decision to use NVRTC means the first call to any workload will incur a compilation delay. While `rtdl_optix.cpp` includes a static caching mechanism, the first launch on a large dataset might hit a timeout if the environment is not pre-warmed.

---

## 3. What is Ready Now
- **Python API Parity:** `src/rtdsl/optix_runtime.py` is complete and interchangeable with the Embree backend.
- **Native Implementation:** `src/native/rtdl_optix.cpp` contains the full implementation for all six workloads, including device kernels and OptiX 7 pipeline management.
- **Codegen Support:** `src/rtdsl/codegen.py` successfully generates OptiX project skeletons for custom DSL kernels.
- **Data Interop:** Structural parity between CPU and GPU layouts is verified by existing unit tests.

## 4. Pre-Connection Checklist (Required Actions)
- [ ] **Verify Dependencies:** Confirm the NVIDIA machine has **CUDA Toolkit ≥ 11.0** and **OptiX SDK 7.x** installed.
- [ ] **Build Hardening:** Test the `Makefile` with `make build-optix` immediately upon login.
- [ ] **Create Smoke Test:** Implement a minimal execution test (e.g., `tests/optix_smoke_test.py`) that runs a small LSI case on the GPU.
- [ ] **Baseline Sync:** Ensure `tests/fixtures/rayjoin/` is populated on the target machine to enable parity checking against the CPU oracle.

---

## 5. Final Verdict: READY-WITH-GAPS

The backend is architecturally sound and logically complete. The "gaps" are purely physical verification and build-environment hardening.

**Recommendation:** Proceed with NVIDIA machine connection, but prioritize a "Hello World" build and a single-workload GPU smoke test before attempting full scale-up or performance benchmarking.
