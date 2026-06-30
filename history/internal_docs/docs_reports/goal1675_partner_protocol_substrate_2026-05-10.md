# Goal1675 Partner Protocol Substrate

Date: 2026-05-10

Status: first local Python substrate for the protocol-first
Python+partner+RTDL track.

## Verdict

RTDL now has a dependency-free Python partner substrate:

- `RtdlTensorDescriptor`
- `RtdlOutputSpec`
- `PartnerContext`
- adapter registry through `rtdsl.partner`
- generic DLPack detector through `__dlpack__` and `__dlpack_device__`
- borrowed pointer extraction through `data_ptr()`, `__cuda_array_interface__`,
  or `__array_interface__` when a partner exposes one
- optional PyTorch and CuPy adapter shells registered without importing either
  framework at module import time

This implements the protocol-first portion of the Goal1670 consensus without
linking the native engine or Python package to PyTorch, CuPy, RAPIDS, JAX, or
another partner framework.

## Boundary

This is not yet a complete PyTorch adapter, complete CuPy adapter, zero-copy
implementation, or OptiX device-resident handoff claim. It is only the generic
selection and descriptor substrate needed before the reference and conformance
adapters.

The PyTorch shell currently validates framework ownership through object module
identity and DLPack protocol support, then rejects grad-enabled tensors before
export. The CuPy shell validates framework ownership and DLPack protocol
support. Both shells can populate a borrowed data pointer when the object
exposes one, but real allocation and measured device-resident handoff still
require the actual frameworks and hardware validation.

The v1.7 descriptor keeps `stream_handle=0` only. Nonzero stream handles remain
reserved until the async/lifetime design defines ownership, creator, consumer,
and failure behavior.

Fallback modes are explicit:

- `error`
- `copy`
- `host_stage`

Only `error` can be used as a future evidence path for device-resident or
zero-copy claims, and only after measured transfer evidence exists.

## API Shape

```python
import rtdsl as rt

ctx = rt.partner.auto(obj)
descriptor = ctx.tensor(obj, access="read")

ctx = rt.partner.use("none")
```

The generic DLPack adapter can identify conforming objects and create RTDL
descriptors, but it cannot allocate framework-owned outputs. Real output
allocation belongs to concrete PyTorch and CuPy adapters.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal1675_partner_protocol_substrate_test
py -3 -m py_compile src/rtdsl/partner.py src/rtdsl/__init__.py
```

Pod validation:

- `docs/reports/goal1677_partner_pod_smoke_2026-05-10.md`

The pod smoke validates real PyTorch CUDA and CuPy CUDA adapter selection,
descriptor creation, borrowed pointer capture, and CuPy output allocation. It
does not prove OptiX native runtime correctness or true zero-copy execution.
