# Gemini Review: Goal1783 NumPy CPU Partner Adapter

**Verdict: `accept`**

**Reviewer: Gemini (Independent AI Reviewer)**

## Executive Summary

This review evaluates **Goal1783: NumPy CPU Partner Adapter** for RTDL v2.0. The implementation successfully adds NumPy as an explicit Python-only partner adapter for CPU/Embree workloads, fulfilling the requirements of the v2.0 partner protocol while maintaining strict architectural boundaries.

Gemini is a distinct AI reviewer. Per project mandates, any "Codex+Codex" consensus is considered invalid; this review represents an independent verification of the implementation against the provided goals and handoff requirements.

## Technical Analysis

### 1. NumPy Registration and Protocol Alignment
In `src/rtdsl/partner.py`, the `NumPyAdapter` is correctly implemented and registered. The `V2_0_PARTNER_PROTOCOL_VERSION` and `V2_0_PARTNER_CPU_REFERENCE_PARTNER` constants are pinned to `"rtdl.partner.v2.0"` and `"numpy"` respectively. 
- **Evidence:** `src/rtdsl/partner.py` lines 12 and 330.
- **Contract Validation:** `rt.validate_v2_0_partner_protocol_contract()` explicitly checks that the `cpu_reference_partner` is `"numpy"`.

### 2. Adapter Selection Logic
The `rt.partner.auto(obj)` function correctly prioritizes specific adapters over the generic DLPack fallback.
- **Evidence:** `src/rtdsl/partner.py` lines 249-257. The loop iterates through `_ADAPTERS` (which contains `numpy`) before falling back to `_GENERIC_DLPACK`.
- **Test Verification:** `tests/goal1783_numpy_cpu_partner_adapter_test.py` (`test_auto_prefers_numpy_adapter_over_generic_dlpack`) confirms that a NumPy array resolves to the `"numpy"` adapter name and source protocol.

### 3. Descriptor Fidelity and Strides
The implementation of `NumPyAdapter.export_tensor` accurately captures host memory metadata.
- **Contiguity:** The adapter handles non-contiguous views by extracting strides from the `__array_interface__` or the object directly.
- **Evidence:** `src/rtdsl/partner.py` line 195 (`strides=_strides_tuple(obj)`).
- **Test Verification:** `tests/goal1783_numpy_cpu_partner_adapter_test.py` (`test_numpy_descriptor_preserves_non_contiguous_host_strides`) verifies stride preservation for a non-contiguous slice `base[:, ::2]`.

### 4. Output Allocation and Device Isolation
Output allocation for the NumPy partner is correctly restricted to the CPU.
- **Evidence:** `src/rtdsl/partner.py` lines 204-205 raise `ValueError` if `device_type` is not `"cpu"`.
- **Test Verification:** `tests/goal1783_numpy_cpu_partner_adapter_test.py` (`test_numpy_output_allocation_is_cpu_only`) confirms rejection of `"cuda:0"` requests.

### 5. Boundary Preservation and Non-Claims
The implementation adheres to the app-agnostic native-engine gate:
- **No Native Mutation:** The changes are restricted to the `src/rtdsl` Python package. No C++/native engine code was modified.
- **No Overclaims:** The report `docs/reports/goal1783_numpy_cpu_partner_adapter_2026-05-12.md` explicitly disclaims zero-copy, native execution, and v2.0 release readiness, categorizing the work as a "local CPU partner slice."

## Conclusion

Goal1783 is a high-quality implementation of the NumPy partner adapter. It provides the necessary infrastructure for Embree-based CPU parity in v2.0 without introducing application-specific logic into the native engine or making premature claims about performance optimizations.

The implementation is verified as correct and safe for integration into the v2.0 partner track.
