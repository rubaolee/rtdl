# Goal1777: v2.0 Partner Protocol Baseline

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

RTDL v1.8 is published as the Python+RTDL language release. The active
roadmap now moves to v2.0: Python+partner+RTDL.

The accepted partner design remains:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

Goal1777 is the first v2.0 implementation slice after v1.8. It does not add a
native backend path and does not claim zero-copy. It freezes a local Python
contract that later PyTorch and CuPy evidence must satisfy before any release
claim can be made.

## Code Boundary

The implementation stays in `src/rtdsl/partner.py` and the public Python export
surface in `src/rtdsl/__init__.py`.

New contract surface:

- `V2_0_PARTNER_PROTOCOL_VERSION = "rtdl.partner.v2.0"`
- `RtdlPartnerProtocolContract`
- `v2_0_partner_protocol_contract()`
- `validate_v2_0_partner_protocol_contract()`

The contract records:

- selection order: protocol first, PyTorch reference, CuPy conformance;
- PyTorch as the reference partner;
- CuPy as the conformance partner;
- `RtdlTensorDescriptor` as the descriptor type;
- `RtdlOutputSpec` as the framework-owned output request type;
- `python-adapter-only` as the engine boundary;
- explicit fallback modes: `error`, `copy`, `host_stage`;
- stream handles still reserved at zero;
- zero-copy wording blocked until measured evidence exists.

## Adapter Tightening

Two small allocation details were tightened before real framework tests:

- `PyTorchAdapter.allocate_output()` now spells CPU output as `device="cpu"`
  rather than `device="cpu:0"`, while preserving CUDA device IDs such as
  `cuda:1`.
- `CuPyAdapter.allocate_output()` now rejects CPU outputs explicitly and uses
  `cupy.cuda.Device(device_id)` for nonzero CUDA devices.

These changes are Python partner behavior only. They do not add PyTorch, CuPy,
or any application vocabulary to the native engine.

## Validation

Local validation:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test \
  tests.goal1671_v1_8_v2_0_partner_gate_test

PYTHONPATH=src py -3 -m py_compile \
  src/rtdsl/partner.py \
  src/rtdsl/__init__.py \
  tests/goal1777_v2_0_partner_protocol_baseline_test.py
```

Result:

```text
24 tests passed.
py_compile passed.
```

The `Could not find platform independent libraries <prefix>` line appeared from
the local Python launcher environment and did not affect the test result.

## Non-Claims

Goal1777 does not claim:

- true zero-copy support;
- OptiX partner descriptor execution;
- PyTorch allocator or stream-order proof;
- CuPy device-resident output proof;
- arbitrary PyTorch/CuPy program acceleration;
- v3.0 shader extension support.

## Next v2.0 Slice

The next implementation slice should use real frameworks:

1. PyTorch reference tests with actual CPU and CUDA tensors where available.
2. CuPy conformance tests with actual CUDA arrays.
3. explicit non-contiguous handling policy.
4. real-framework confirmation of the current reject policy for grad-enabled
   PyTorch tensors.
5. phase timing that separates device-resident handoff, fallback copy, and host
   staging.

The local fake-framework baseline now also pins export paths, grad-enabled
PyTorch rejection, descriptor/output validation guards, DLPack integer device
normalization, and `partner.auto()` framework-priority fallback behavior.

## Consensus Requirement

This is an important v2.0 architecture boundary. It should receive 3-AI
consensus: Codex implementation plus independent Claude and Gemini review.

## Verdict

`accept-with-boundary`: the v2.0 partner protocol baseline is now explicit and
locally tested. It is not v2.0 release readiness; release remains blocked until
real PyTorch and CuPy evidence, partner path hardware validation, and final
distinct-AI consensus exist.
