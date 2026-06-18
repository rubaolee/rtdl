# V3.0 Zero-Copy Interop Contract

Status: historical V3-track file retained as V4.0 preparatory material. This is
not V3.0 release scope, not a V3.0 completion criterion, not an implemented C ABI device-buffer query route and not public true-zero-copy wording.

RTDL's embeddability plan uses DLPack and `__cuda_array_interface__` as the
framework interop layer above the C ABI. The source tree already has a neutral
buffer seam that can describe these handoffs, but description is not the same
thing as an end-to-end zero-copy proof.

## Contract Layers

- **Observed descriptor:** RTDL can inspect a buffer protocol such as DLPack,
  `__cuda_array_interface__`, or `__array_interface__` and record dtype, shape,
  device, pointer, producer, consumer, and lifetime.
- **Borrowed device pointer, unmeasured:** a CUDA pointer is present, but no
  transfer-counter evidence has yet proved that the route avoided host staging.
- **Measured zero-copy candidate:** same pointer, same device, no host stage,
  and accepted transfer-counter evidence are all present.
- **Public true-zero-copy claim:** still blocked until a dedicated reviewed
  runtime packet validates the exact C ABI or framework path.

## Current Implementation Hook

The current readiness hooks are `src/rtdsl/neutral_buffer_seam.py` and the V3
C ABI neutral buffer view:

- protocol priority includes registered partner adapters, DLPack,
  `__cuda_array_interface__`, and `__array_interface__`;
- the neutral-buffer protocol gate validates synthetic DLPack,
  `__cuda_array_interface__`, and `__array_interface__` descriptor metadata
  while keeping runtime/device-query wording blocked;
- transfer statuses distinguish host references, declared copies, host stages,
  borrowed device pointers, and measured zero-copy;
- lifetime states make borrowed/retained/released ownership explicit;
- `rtdl_buffer_import` / `rtdl_buffer_export` can carry CUDA buffer descriptors
  as metadata, preserving pointer, dtype, shape, strides, device id, and
  release-callback ownership without dereferencing the pointer;
- public speedup and public true-zero-copy claims remain blocked.

## Boundary

This contract does not add DLPack fields to `include/rtdl/rtdl.h`, does not make
any C ABI query route consume device buffers, does not validate CUDA pointer
ownership or stream ordering, does not build a PyTorch/JAX/CuPy adapter, and
does not authorize performance wording. It is the checklist that the later
device-buffer query route and framework adapters must satisfy.
