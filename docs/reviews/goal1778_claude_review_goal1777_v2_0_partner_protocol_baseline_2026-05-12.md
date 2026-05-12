# Goal1778: Claude Review of Goal1777 — v2.0 Partner Protocol Baseline

Reviewer: Claude (claude-sonnet-4-6), acting as a distinct AI reviewer independent of the Codex implementation agent.

Date: 2026-05-12

Verdict: `accept-with-boundary`

---

## Reviewer Independence Statement

This review is written by Claude, a distinct AI system from Anthropic. It is independent of the Codex agent that implemented Goal1777. A Codex implementation reviewed only by another Codex instance does not constitute independent consensus. This Claude review, together with the separate Gemini review, provides the required distinct-AI consensus for this architecture boundary.

---

## Review Scope

Files inspected:

- `src/rtdsl/partner.py`
- `src/rtdsl/__init__.py`
- `tests/goal1777_v2_0_partner_protocol_baseline_test.py`
- `docs/reports/goal1777_v2_0_partner_protocol_baseline_2026-05-12.md`
- `docs/reports/goal1770_v2_0_roadmap_boundary_after_v1_8_release_2026-05-12.md`
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`

---

## Verification Point 1: Contract API is Python-Only; No Partner or App Vocabulary Enters the Native Engine

**Pass.**

The entire Goal1777 implementation is confined to `src/rtdsl/partner.py`. All new symbols — `RtdlPartnerProtocolContract`, `RtdlTensorDescriptor`, `RtdlOutputSpec`, `PartnerAdapter`, `PyTorchAdapter`, `CuPyAdapter`, `PartnerContext`, and the supporting functions — are pure Python. No C extension, no shared library, and no native descriptor bridge is modified.

The `engine_boundary` field on `RtdlPartnerProtocolContract` is set to the constant `"python-adapter-only"` and is validated by `validate_v2_0_partner_protocol_contract()`. Any mutation of this value causes a `"reject"` result with the message "partner protocol must not enter app-agnostic native engine internals."

The public export surface in `__init__.py` adds the partner symbols cleanly alongside the existing API without introducing application-domain vocabulary (polygon, graph, KNN, BFS, trajectory, etc.) into any engine-facing path.

App-agnostic gate: **intact**.

---

## Verification Point 2: PyTorch as Reference Partner; CuPy as Conformance Partner

**Pass.**

The protocol constants are unambiguous:

```python
V2_0_PARTNER_PROTOCOL_VERSION   = "rtdl.partner.v2.0"
V2_0_PARTNER_REFERENCE_PARTNER  = "torch"
V2_0_PARTNER_CONFORMANCE_PARTNER = "cupy"
V2_0_PARTNER_PROTOCOL_ORDER     = ("protocol", "torch", "cupy")
```

The selection order is protocol-first, then PyTorch, then CuPy. The contract validator enforces all three: wrong order, wrong reference partner, or wrong conformance partner each produce a named error and a `"reject"` status.

The adapter hierarchy reflects the role split correctly: `PyTorchAdapter` handles both CPU and CUDA devices, while `CuPyAdapter.allocate_output()` explicitly rejects CPU and is CUDA-only. This correctly distinguishes the reference partner's broader surface from the lightweight conformance partner.

The `auto()` function iterates registered adapters and skips the `"dlpack"` name first, giving framework-specific adapters priority before falling back to the generic DLPack path. This preserves the selection-order rule at runtime.

---

## Verification Point 3: Stream and Zero-Copy Claims Blocked Until Measured Evidence

**Pass.**

Both blocking rules are enforced at multiple layers:

- `RtdlPartnerProtocolContract` carries `stream_policy = "stream_handle_reserved_zero"` and `zero_copy_claim = "measured_evidence_required"`, and the contract validator rejects deviation from either.
- `RtdlTensorDescriptor.__post_init__` raises `ValueError` if `stream_handle != 0`.
- `GenericDLPackAdapter.export_tensor()` raises if `stream not in (None, 0)`.
- `PyTorchAdapter.allocate_output()` raises if `stream not in (None, 0)`.
- `CuPyAdapter.allocate_output()` raises if `stream not in (None, 0)`.

The error message is consistent across all sites: `"v1.7 partner descriptors reserve stream_handle; expected 0"`. The non-claim is clear in the Goal1777 report and the gate document. Zero-copy and stream-order wording remain blocked at this slice.

---

## Verification Point 4: Allocation Behavior Changes Are Reasonable

**Pass with one minor observation.**

**PyTorchAdapter:** `allocate_output()` now spells the CPU device as `"cpu"` rather than `"cpu:0"`. PyTorch does not accept `"cpu:0"` as a valid device string, so this correction is necessary and correct. CUDA devices use `f"cuda:{spec.device_id}"` which is the canonical PyTorch form. The dtype is resolved via `getattr(torch, spec.dtype, spec.dtype)`, correctly converting a string like `"float32"` to `torch.float32` while falling back to the raw string if the attribute does not exist.

**CuPyAdapter:** `allocate_output()` rejects non-CUDA inputs explicitly. For `device_id == 0` it calls `cupy.empty(shape, dtype=spec.dtype)` directly; for `device_id > 0` it uses `cupy.cuda.Device(device_id)` as a context manager. This is the correct CuPy idiom for multi-GPU allocation.

**Minor observation:** The PyTorch path resolves dtype via `getattr(torch, spec.dtype, spec.dtype)` (producing a torch dtype object), while the CuPy path passes `spec.dtype` as a raw string directly to `cupy.empty`. For the current string-named dtypes this is harmless because CuPy accepts NumPy-style string dtypes. However, the asymmetry is worth documenting when adding real-framework conformance tests in the next slice, to confirm both paths under actual dtype round-trip scenarios.

Neither adapter's `import_output()` is implemented beyond `NotImplementedError` (inherited from `GenericDLPackAdapter`). This is declared intentional at this baseline and is consistent with the non-claims in the report.

---

## Verification Point 5: Report Does Not Overclaim v2.0 Release Readiness

**Pass.**

The Goal1777 report verdict is `accept-with-boundary` and states explicitly:

> "It is not v2.0 release readiness; release remains blocked until real PyTorch and CuPy evidence, partner path hardware validation, and final distinct-AI consensus exist."

The non-claims section correctly lists: no true zero-copy, no OptiX partner descriptor execution, no PyTorch allocator or stream-order proof, no CuPy device-resident output proof, no arbitrary acceleration claim, no v3.0 extension claim.

The gate document (`v1_8_v2_0_python_partner_rtdl_gate.md`) independently repeats the same blocked wording. The roadmap document (`goal1770`) marks v2.0 as active but not released. No document uses any of the forbidden phrases.

---

## Verification Point 6: Test Sufficiency for This Baseline Slice

**Adequate for the declared scope; four specific gaps noted for the next slice.**

The four tests in `goal1777_v2_0_partner_protocol_baseline_test.py` cover:

1. All contract field values and `validate_v2_0_partner_protocol_contract()` accepting the canonical contract.
2. Contract validation rejecting swapped partner roles and an invalid engine boundary.
3. PyTorchAdapter output allocation for CPU (device string `"cpu"`) and CUDA (device string `"cuda:1"`), verified against fake-torch call records.
4. CuPyAdapter CPU rejection and CUDA multi-device allocation, verified against fake-cupy call records.

These are the correct tests for a *contract and allocation-behavior baseline* that builds on prior Goal1675 substrate tests. They do not duplicate substrate coverage.

**Gaps that must be addressed before the next slice is accepted:**

1. **export_tensor paths not tested.** Neither `PyTorchAdapter.export_tensor()` nor `CuPyAdapter.export_tensor()` is exercised. Specifically, the grad-enabled rejection path in `PyTorchAdapter.export_tensor()` (`requires_grad=True`) has no test. This is the most important missing test because grad-rejection is a correctness boundary, not a style choice.

2. **Descriptor field validation not tested.** `RtdlTensorDescriptor.__post_init__` enforces negative shape, stride rank mismatch, negative byte_offset, and non-zero stream_handle. `RtdlOutputSpec.__post_init__` enforces invalid device_type, invalid fallback_policy, and non-positive alignment. None of these guards is tested.

3. **DLPack device integer normalization not tested.** `_normalize_dlpack_device()` maps integer type codes (1 → `"cpu"`, 2 → `"cuda"`) from the DLPack ABI. This path is not exercised, making it the most likely site for a silent regression.

4. **`auto()` priority ordering not tested.** The `auto()` function skips the `"dlpack"` adapter name and prefers framework adapters. A test with a DLPack-capable object whose module root is not `"torch"` or `"cupy"` (so it falls to the generic path) would confirm the fallback logic.

These gaps are appropriate to defer until real-framework tests in the next slice, as the report already acknowledges. They must not carry forward past the first real-framework test milestone.

---

## Summary

| Check | Result |
| --- | --- |
| Contract API Python-only; no native engine contamination | Pass |
| PyTorch as reference partner; CuPy as conformance partner | Pass |
| Stream and zero-copy blocked with evidence requirement | Pass |
| Allocation behavior changes correct for PyTorch CPU/CUDA and CuPy CUDA-only | Pass (minor dtype-resolution asymmetry noted) |
| Report does not overclaim v2.0 release readiness | Pass |
| Tests sufficient for this baseline slice | Adequate; four gaps documented for next slice |

**Verdict: `accept-with-boundary`**

The v2.0 partner protocol contract is correctly frozen, the engine boundary is intact, the stream and zero-copy gates hold, and the allocation fixes are sound. This baseline is accepted as the first v2.0 implementation slice.

The boundary: this review, together with the Gemini review, satisfies the distinct-AI consensus requirement for Goal1777. Neither this review nor the Gemini review constitutes v2.0 release readiness. Release remains blocked until real PyTorch and CuPy framework tests pass under hardware, the four test gaps above are closed, phase-timing artifacts are produced, and a final consensus report is written covering the complete v2.0 evidence set.
