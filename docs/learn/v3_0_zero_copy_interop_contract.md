# V3.0 Zero-Copy Interop Contract

Status: V3 design/readiness contract, not an implemented C ABI device-buffer
route and not public true-zero-copy wording.

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

The current readiness hook is `src/rtdsl/neutral_buffer_seam.py`:

- protocol priority includes registered partner adapters, DLPack,
  `__cuda_array_interface__`, and `__array_interface__`;
- transfer statuses distinguish host references, declared copies, host stages,
  borrowed device pointers, and measured zero-copy;
- lifetime states make borrowed/retained/released ownership explicit;
- public speedup and public true-zero-copy claims remain blocked.

## Boundary

This contract does not add DLPack fields to `include/rtdl/rtdl.h`, does not make
the C ABI accept device buffers, does not build a PyTorch/JAX/CuPy adapter, and
does not authorize performance wording. It is the checklist that the later
device-buffer C ABI and framework adapters must satisfy.
