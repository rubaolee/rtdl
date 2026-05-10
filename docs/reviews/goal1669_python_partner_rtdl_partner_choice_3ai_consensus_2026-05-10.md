# Goal1669 Python+Partner+RTDL Partner Choice 3-AI Consensus

Date: 2026-05-10

Participants:

- Codex
- Gemini
- Claude

Reviewed artifacts:

- `docs/reports/goal1669_python_partner_rtdl_partner_choice_architecture_2026-05-10.md`
- `docs/reviews/goal1669_gemini_python_partner_rtdl_partner_choice_review_2026-05-10.md`
- `docs/reviews/goal1669_claude_python_partner_rtdl_partner_choice_review_2026-05-10.md`
- `docs/reviews/goal1669_gemini_python_partner_rtdl_partner_choice_final_review_2026-05-10.md`
- `docs/reviews/goal1669_claude_python_partner_rtdl_partner_choice_final_review_2026-05-10.md`
- `tests/goal1669_python_partner_rtdl_partner_choice_architecture_test.py`

## Consensus Verdict

The Python+partner+RTDL architecture should be protocol-first and
partner-pluggable. RTDL should not hardwire PyTorch, CuPy, Numba, or any other
framework into the native engine.

The accepted first design is:

```text
DLPack-compatible handoff as the contract,
CuPy as the first blessed partner,
PyTorch as the first follow-up partner.
```

This preserves the top-level invariant: Python+RTDL first, then
Python+partner+RTDL, with the RTDL engine absolutely app-agnostic in both
tracks.

## Resolved Review Issues

Gemini approved the initial architecture and recommended proceeding with the
CuPy-first plan.

Claude initially identified three pre-implementation blockers:

- geometry partner semantics were underspecified;
- `partner="auto"` detection priority was underspecified;
- raw DLPack capsules and the Python Array API `__dlpack__` protocol were
  conflated.

The report was revised to resolve all three:

- geometry imported with one partner must fail on a different explicit partner
  unless the user requests a documented transfer fallback;
- `auto` detection is deterministic: explicit partner, known module/type,
  generic `__dlpack__`, named `__cuda_array_interface__` fallback, then
  failure or explicit fallback;
- v1.7 uses `__dlpack__` plus `__dlpack_device__` as the primary path, with raw
  DLPack capsules and `__cuda_array_interface__` as named fallbacks only.

Final Gemini and Claude reviews confirmed these blockers are resolved.

## Accepted Constraints

- The partner mechanism must not become a new app-specific native backdoor.
- The native engine sees only generic tensor/buffer descriptors and generic RTDL
  primitive packets.
- CuPy is first because it proves the GPU-resident array handoff problem without
  importing PyTorch autograd or ML framework assumptions into the core contract.
- PyTorch follows because of ecosystem reach, but it must not define the engine
  ABI.
- Benchmarks must use `fallback="error"` when validating device-resident or
  zero-copy claims.
- `stream_handle=0` is required in the first synchronous implementation.
- A free-form native `lifetime_token` must not enter the v1.7 ABI.
- Output allocation must use a concrete `RtdlOutputSpec` with alignment and
  layout requirements.

## Release Claim Boundary

Before measured evidence exists, RTDL may only say it is designing a
Python+partner+RTDL track based on generic partner tensor handoff.

RTDL must not claim general true zero-copy support, arbitrary PyTorch/CuPy
program acceleration, partner-code optimization, or fully app-agnostic native
internals until the corresponding measured evidence and Goal1668 release gate
exist.

## Final Recommendation

Proceed to the first implementation slice:

- `PartnerAdapter` registry;
- generic tensor descriptor;
- CuPy adapter;
- one OptiX primitive acceptance path with parity and phase timing;
- a separately named Embree NumPy host descriptor acceptance slice;
- claim-boundary artifacts generated from each run.
