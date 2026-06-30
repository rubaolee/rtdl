# Gemini Review: Goal1777 v2.0 Partner Protocol Baseline

**Verdict:** `accept`

**Date:** 2026-05-12
**Reviewer:** Gemini (Autonomous CLI Agent)

## Overview

This is an independent review of Goal1777, the first implementation slice of the RTDL v2.0 "Python+partner+RTDL" roadmap. This review evaluates the protocol baseline against the established architectural mandates.

**Consensus Note:** Gemini is a distinct AI reviewer. Consensus is only valid when derived from independent AI entities; Codex implementation plus Codex review (Codex+Codex) is invalid for establishing architectural consensus.

## Evidence of Compliance

### 1. Protocol and Partner Hierarchy
The implementation in `src/rtdsl/partner.py` correctly implements the mandated hierarchy:
- **Selection Order:** `("protocol", "torch", "cupy")` is pinned in `V2_0_PARTNER_PROTOCOL_ORDER`.
- **Roles:** `V2_0_PARTNER_REFERENCE_PARTNER = "torch"` and `V2_0_PARTNER_CONFORMANCE_PARTNER = "cupy"` are explicitly defined.
- **Verification:** `tests/goal1777_v2_0_partner_protocol_baseline_test.py` validates these constants and ensures that drift (e.g., swapping reference/conformance roles) results in a contract rejection.

### 2. Engine and Application Agnosticism
The "Engine absolutely app-agnostic" rule is preserved through several layers:
- **Boundary Definition:** `V2_0_PARTNER_ENGINE_BOUNDARY` is set to `"python-adapter-only"`, ensuring partner logic does not leak into the native engine.
- **Generic Descriptors:** `RtdlTensorDescriptor` and `RtdlOutputSpec` use generic vocabulary (`data_ptr`, `device_type`, `dtype`, `shape`) without partner-specific or application-specific (e.g., database, graph) terminology.
- **Adapter Isolation:** Partner-specific logic (e.g., `torch.empty`, `cupy.cuda.Device`) is encapsulated within `PyTorchAdapter` and `CuPyAdapter` classes.

### 3. Claim Blocking (Streams and Zero-Copy)
The implementation rigorously blocks unproven claims as directed:
- **Streams:** `RtdlTensorDescriptor.__post_init__` raises `ValueError` if `stream_handle != 0`. The contract `stream_policy` is `stream_handle_reserved_zero`.
- **Zero-Copy:** The contract `zero_copy_claim` is explicitly set to `measured_evidence_required`.
- **Verification:** Tests confirm that non-zero stream handles are rejected, preserving the reservation for future v2.0 evidence.

### 4. Adapter Refinement
The baseline implementation demonstrates proactive tightening of framework-specific behaviors:
- **PyTorch:** `PyTorchAdapter` correctly handles the framework-specific device spelling (e.g., `"cpu"` vs `"cuda:1"`) and mandates detaching grad-enabled tensors.
- **CuPy:** `CuPyAdapter` correctly enforces `device_type='cuda'` and uses the `cupy.cuda.Device` context manager for multi-GPU allocation.

## Testing Adequacy

The test suite in `tests/goal1777_v2_0_partner_protocol_baseline_test.py` is sufficient for this "baseline slice":
- It uses mock-like objects (`_DLPackLike`, `_TorchLike`) to verify protocol logic without requiring full framework installations in the CI environment.
- It covers contract validation, descriptor/spec guards, and adapter-specific allocation logic.
- **Missing Tests (Planned):** As noted in the roadmap (`docs/reports/goal1770_v2_0_roadmap_boundary_after_v1_8_release_2026-05-12.md`), real framework integration tests and performance phase timing are deferred to the next slice. This is appropriate for a protocol baseline.

## Conclusion

Goal1777 successfully establishes the v2.0 interop substrate while protecting the native engine from application and framework creep. The "Non-Claims" section in the implementation report (`docs/reports/goal1777_v2_0_partner_protocol_baseline_2026-05-12.md`) correctly frames the current state as a protocol foundation rather than full release readiness.

The implementation is technically sound, follows all architectural directives, and is ready for the next phase of v2.0 development.
