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
generic descriptor shapes, while preserving fail-closed behavior for unsupported
primitive/query combinations.

Goal4558 turns the first narrow query route on: host F32 AABB2 index build plus
host F32 AABB overlap query returning host U64 `(query_id, primitive_id)` pairs.
All other query/backend wording remains bounded by the documented unsupported
routes and evidence gates.

Goal4559 adds a readable source-tree C example client at
`examples/current/embedding/c_api_aabb2_overlap_client.c` and validates it on
the pod against the Makefile-built C ABI library.

## Current Host AABB2 Query Contract

The only implemented query route is deliberately small:

- Context: `rtdl_context_create` with `RTDL_BACKEND_CPU` or `RTDL_BACKEND_AUTO`.
- Primitive buffer: host `RTDL_DTYPE_F32`, contiguous AABB2 rows shaped
  `[primitive_count, 4]` as `(min_x, min_y, max_x, max_y)`.
- Index: `rtdl_index_build` with `RTDL_PRIMITIVE_AABB2`; the implementation
  copies the primitive coordinates into the index, so the source buffer may be
  destroyed after a successful build.
- Query buffer: host `RTDL_DTYPE_F32`, contiguous AABB2 rows shaped
  `[query_count, 4]` using the same coordinate order.
- Query: `rtdl_query_execute` with `RTDL_QUERY_AABB_OVERLAP`.
- Result buffer: host `RTDL_DTYPE_U64`, shaped `[hit_count, 2]`; each row is
  `(query_id, primitive_id)`.
- Ownership: imported buffers remain caller-owned; RTDL-owned result buffers
  must be released with `rtdl_buffer_destroy`.

Unsupported primitive kinds, query kinds, device buffers, OptiX execution,
Embree execution, and frozen binary compatibility remain outside the current
contract.
