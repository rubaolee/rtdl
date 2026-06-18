# V3.0 C ABI Draft

Status: design-stage boundary draft with a minimal stub shared-library
implementation; not a frozen or backend-capable ABI.

The draft public header is [include/rtdl/rtdl.h](../../include/rtdl/rtdl.h).
It is the first concrete artifact from the V3 embeddability strategy: define a
narrow C boundary before adding language bindings or device-callable fusion.

## Scope

- Opaque handles: `rtdl_context`, `rtdl_index`, `rtdl_query`, `rtdl_buffer`.
- C status codes and explicit last-error retrieval.
- Versioned ABI macros and version functions.
- Caller-provided external runtime handles: device type, device id, context,
  stream, and user data.
- Neutral buffer views with device type, dtype, shape, strides, ownership
  callback, and user data.

## Boundary

Goal4552 implements a minimal stub library for version, status, context
lifecycle, and neutral buffer lifecycle symbols. It does not implement backend
query execution, freeze binary compatibility, authorize release wording, or
claim DLPack, `__cuda_array_interface__`, external CUDA stream, or
device-callable fusion support. Those require separate implementation gates
and non-Python client validation.

Goal4551 adds a C11/C++17 header compile smoke for the draft only; that smoke
still does not implement or freeze the ABI.

Goal4552 adds a temporary shared-library build plus `ctypes` symbol smoke for
the stub implementation; that smoke proves loadability, not real backend
embeddability.
