# Goal1783: NumPy CPU Partner Adapter

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

The v2.0 partner track needs both GPU partner evidence and CPU/Embree parity.
The accepted gate already names the CPU/Embree partner lane:

```text
CPU/Embree partner | NumPy first, Arrow later only if app semantics stay outside the engine
```

Goal1783 implements the first local CPU partner slice by making NumPy an
explicit Python adapter rather than leaving NumPy arrays to fall through as
generic DLPack objects.

## Implementation

Changed:

- `src/rtdsl/partner.py`
- `src/rtdsl/__init__.py`

New public adapter:

```text
NumPyAdapter
```

Contract addition:

```text
cpu_reference_partner = "numpy"
```

Behavior:

- `rt.partner.auto(np_array)` now resolves to `numpy`, not generic `dlpack`.
- NumPy descriptors are CPU-only.
- NumPy descriptors preserve shape, dtype, data pointer, and host strides.
- Non-contiguous NumPy views are accepted as descriptors with explicit strides.
- NumPy output allocation uses `numpy.empty(...)`.
- NumPy output allocation rejects CUDA devices.

The adapter is Python-only. It does not link NumPy into native engine code and
does not introduce application vocabulary into engine internals.

## Validation

Local environment:

```text
numpy: yes
torch: no
cupy: no
```

Local validation:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal1783_numpy_cpu_partner_adapter_test \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test \
  tests.goal1671_v1_8_v2_0_partner_gate_test

PYTHONPATH=src py -3 -m py_compile \
  src/rtdsl/partner.py \
  src/rtdsl/__init__.py \
  tests/goal1783_numpy_cpu_partner_adapter_test.py
```

Result:

```text
26 tests ran.
21 passed.
5 skipped.
py_compile passed.
```

The 5 skips are inherited from Goal1781 because this Windows dev environment
does not have PyTorch or CuPy installed.

## Non-Claims

Goal1783 does not claim:

- Embree native descriptor execution;
- zero-copy;
- PyTorch/CuPy evidence;
- CUDA device-resident handoff;
- v2.0 release readiness.

## Next Step

The next CPU-side slice should wire one Embree host descriptor acceptance path
through NumPy-owned inputs while preserving existing public Python semantics.

The next GPU-side slice still requires a PyTorch/CuPy-capable environment or a
pod.

## Verdict

`accept-with-boundary`: NumPy is now an explicit CPU/Embree partner adapter and
has real local evidence. Native execution and v2.0 readiness remain blocked
until follow-up descriptor execution and hardware evidence exist.
