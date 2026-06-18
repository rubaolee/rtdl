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

Goal4553 adds a non-Python C11 dynamic-load client smoke against the same stub
library. It validates version, status, context lifecycle, and neutral buffer
lifecycle calls from C, but still does not validate backend query execution,
external stream semantics, DLPack, or frozen binary compatibility.

Goal4554 wires the lifecycle stub into the source-tree build front door as
`make build-c-api`. That target builds the shared library artifact, but it is
still a source-tree developer target rather than an install/package contract.

Goal4556 audits the `make build-c-api` shared library with the platform symbol
tool and verifies the current lifecycle symbols are exported. That is an
artifact-surface check, not a frozen binary compatibility promise.

Goal4557 adds draft `rtdl_index_build` and `rtdl_query_execute` entrypoints plus
generic descriptor shapes. The lifecycle stub exports those symbols but returns
`RTDL_STATUS_ERROR_UNSUPPORTED`; this is a visible fail-closed query surface,
not backend query execution.
