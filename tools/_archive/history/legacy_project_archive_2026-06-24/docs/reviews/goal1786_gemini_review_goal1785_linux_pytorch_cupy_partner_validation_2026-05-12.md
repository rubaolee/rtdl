# Gemini Review: Goal1785 Linux PyTorch and CuPy Partner Validation

**Verdict:** `accept-with-boundary`

**Date:** 2026-05-12
**Reviewer:** Gemini (Autonomous CLI Agent)

## Overview

This review evaluates the validation of PyTorch CUDA, CuPy CUDA, and NumPy CPU partner adapters on a Linux host (GTX 1070) for the RTDL v2.0 track. The validation follows the "Protocol first. PyTorch reference first." consensus established in Goal1777 and the roadmap in `v1_8_v2_0_python_partner_rtdl_gate.md`.

## Independent AI Reviewer Statement

Gemini is a distinct AI reviewer. I operate independently of the primary implementation and previous review cycles. I explicitly note that **"Codex+Codex" is invalid consensus**; this review provides the necessary cross-model validation required for the v2.0 release gate.

## Evidence Evaluation

### 1. Environment Isolation and PEP 668 Adherence
The validation host environment correctly avoided mutating the system Python (managed by PEP 668) by using a checkout-local `.partner_site` directory via `pip install --target`. This demonstrates high standards for environment stability and reproducibility.
- **Evidence:** `docs/reports/goal1785_linux_pytorch_cupy_partner_validation_2026-05-12.md` lines 38-43.

### 2. Framework-Specific Validation (22-pass / 0-skip)
The test suite executed (spanning goals 1781, 1783, 1777, and 1675) provides meaningful evidence of protocol compliance across the three core frameworks:
- **PyTorch:** Verified CUDA descriptor export, CPU allocation, and the critical rejection of grad-enabled tensors (`tests/goal1781_real_framework_partner_availability_test.py` line 34).
- **CuPy:** Verified CUDA export/allocation and rejection of CPU allocation (`tests/goal1781_real_framework_partner_availability_test.py` line 74).
- **NumPy:** Verified host stride preservation and CPU-only allocation constraints (`tests/goal1783_numpy_cpu_partner_adapter_test.py` line 36).
- **Implementation Alignment:** `src/rtdsl/partner.py` correctly implements these adapters with strict boundary checks (e.g., `PyTorchAdapter.export_tensor` detach check at line 144).

### 3. Hardware Bounding
The report correctly identifies the NVIDIA GeForce GTX 1070 as a "smoke validation host." This appropriately bounds the evidence as functional verification of CUDA interop rather than final RT-core performance evidence for the v2.0 release.
- **Evidence:** Report section "Boundary", lines 76-77.

### 4. Claim Boundary and Release Readiness
The validation maintains the v2.0 claim boundary by explicitly stating what is *not* claimed:
- No true zero-copy claim (pending measured evidence).
- No OptiX execution path wired (engine remains app-agnostic).
- No RT-core acceleration claim from this specific functional test.
- No v2.0 release readiness claim.
This aligns with the roadmap constraints in `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`.

## Next Step Validation

The proposed next step—wiring a narrow app-agnostic OptiX primitive path (`ANY_HIT` or `COUNT_HITS`) through partner descriptors—is the correct progression. It preserves the engine/adapter separation while moving toward hardware-accelerated evidence.

## Conclusion

Goal1785 provides robust, isolated evidence that the RTDL partner protocol works with real framework binaries on Linux. The "accept-with-boundary" verdict is appropriate because while the functional interop is proven, the v2.0 release remains blocked by the absence of OptiX timing and hardware-acceleration artifacts.
