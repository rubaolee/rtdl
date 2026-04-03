# Final Consensus: Vulkan KHR Ray-Tracing Backend Implementation

**Date:** 2026-04-02
**Project:** rtdl (Review of `claude-work/rtdl-latest`)
**Participants:** Claude (Author), Gemini CLI (Reviewer), Codex (Auditor)

## 1. Summary of Consensus
The participants reached consensus that the Vulkan KHR ray-tracing backend is structurally substantial and worth keeping in the repository, but its status should be treated as **provisional integration** rather than fully accepted release maturity. The implementation mirrors the existing OptiX and Embree backends and provides a credible cross-vendor GPU path, but it still requires stronger validation and tighter scaling guardrails.

## 2. Technical Agreement
- **Structural Parity:** The backend achieves full API and ABI parity with the OptiX and Embree paths.
- **Robustness:** Key Vulkan-specific hurdles (Anyhit/Opaque interaction, GLSL statement syntax, and JIT shader compilation via `shaderc`) have been successfully addressed.
- **Lazy Initialization:** The use of a thread-safe, singleton context for Vulkan and pipeline management is approved.

## 3. Identified Areas for Follow-up (Goal 45)
- **Precision:** The `float32` GPU path must be audited for parity with the double-precision CPU/Embree paths on high-precision datasets.
- **Verification:** Formal parity tests (e.g., `tests/rtdsl_vulkan_test.py`) must be added to the project's test suite.
- **Future-Proofing:** Python `ctypes` bindings should be updated with `_pack_ = 1` to ensure long-term memory layout consistency.
- **Cleanup:** An explicit shutdown mechanism for the Vulkan singleton should be considered for long-running environments.

## 4. Final Verdict
The Vulkan backend is approved to remain in the repository as a **provisional backend**. It should not be described as public-release-ready until the committed validation surface and output-capacity guardrails are strengthened.
