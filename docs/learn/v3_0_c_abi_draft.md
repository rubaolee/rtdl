# V3.0 C ABI Draft

Status: historical V3-track file retained as V4.0 preparatory material. It is a
design-stage boundary draft with a minimal stub shared-library implementation,
not V3.0 release scope, not a V3.0 completion criterion, and not a frozen or backend-capable ABI.

The draft public header is [include/rtdl/rtdl.h](../../include/rtdl/rtdl.h).
It is an early concrete artifact for future embeddability work: define a narrow
C boundary before adding language bindings or device-callable fusion.
Read [V3.0 C ABI Stability Policy](v3_0_c_abi_stability_policy.md) before
using this draft as an external contract.
Use [V3.0 C ABI Ownership And Threading Contract](v3_0_c_abi_ownership_threading_contract.md)
for the current buffer lifetime, release-callback, last-error, and threading
rules.
Use [V3.0 C ABI Staging Contract](v3_0_c_abi_staging_contract.md) for the
source-tree `make stage-c-api` bundle boundary.
The current draft symbol list is tracked in
[v3_0_c_abi_symbol_manifest_v0_1_3.json](v3_0_c_abi_symbol_manifest_v0_1_3.json).

## Scope

- Opaque handles: `rtdl_context`, `rtdl_index`, `rtdl_query`, `rtdl_buffer`.
- C status codes and explicit last-error retrieval.
- Versioned ABI macros, version functions, and the draft
  `rtdl_abi_is_compatible(major, minor, patch)` guard.
- Capability queries for the currently supported backend and primitive/query
  route surface.
- Declared external runtime handle shape: device type, device id, context,
  stream, and user data. The current proof accepts host runtime metadata only;
  CUDA/HIP/Metal/Vulkan runtime handles and external stream adoption remain
  fail-closed.
- Neutral buffer views with validated device type, dtype, shape, strides,
  ownership callback, and user data. CUDA buffer descriptors can be imported
  and exported as metadata, but no current query route consumes device buffers.

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

Goal4576 adds `make stage-c-api`, which stages the draft C ABI header, shared
library, current symbol manifest, README, and example client under
`build/c_api_stage`. This is still a source-tree staging bundle, not an install
or package contract.

Goal4578 adds draft capability queries:
`rtdl_backend_is_supported(backend)` and
`rtdl_route_is_supported(primitive_kind, query_kind, device_type)`. They report
the current source-tree support surface only: AUTO/CPU backend selection and the
host AABB2 overlap route. They do not enable OptiX/Embree C ABI execution,
device-buffer routes, or dynamic backend loading.

Goal4579 adds `examples/current/embedding/c_api_direct_link_client.c`, a
pkg-config/direct-link companion to the dlopen AABB2 example. It validates
version and capability queries before creating a CPU context.

Goal4581 adds `examples/current/embedding/python_ctypes_client.py`, a staged
Python `ctypes` client over the same draft C ABI. It validates shared-library
loading, version compatibility, capability queries, and CPU context
create/destroy from a non-C client. This is a minimal language-binding proof,
not a generated Python package, stable ABI, device-buffer binding, or
OptiX/Embree C ABI query surface.

Goal4582 adds `examples/current/embedding/python_ctypes_aabb2_query_client.py`,
a staged Python `ctypes` client that runs the current host F32 AABB2 overlap
route through the C ABI: buffer import, index build, query execute, result
export, and cleanup. This proves a non-C client can exercise the current real
query route, while still remaining outside generated package, stable ABI,
device-buffer, OptiX, Embree, and performance claims.

Goal4591 adds `examples/current/embedding/c_api_host_runtime_client.c` and
turns `rtdl_context_set_external_runtime` into a narrow host-runtime metadata
path. The current proof accepts `RTDL_DEVICE_HOST` with null context/stream
handles and rejects malformed host metadata or CUDA runtime handles. This is
not external CUDA stream, OptiX, Embree, or device-buffer support.

Goal4592 adds `examples/current/embedding/c_api_cuda_buffer_metadata_client.c`
and validates neutral CUDA buffer descriptor import/export through
`rtdl_buffer_import` and `rtdl_buffer_export`. The descriptor path preserves
pointer, dtype, shape, strides, device id, and release-callback ownership
metadata, while host AABB2 query routes still reject CUDA buffers instead of
dereferencing them.

Goal4593 adds
`examples/current/embedding/python_ctypes_cuda_buffer_metadata_client.py`, a
Python `ctypes` bridge from a `__cuda_array_interface__`-style object into the
C ABI neutral buffer view. It validates descriptor import/export and current
host-route rejection from Python, without validating CUDA pointer ownership,
stream ordering, or device-buffer query execution.

Goal4607 adds
`examples/current/embedding/python_ctypes_dlpack_like_metadata_client.py`, a
Python `ctypes` bridge from a DLPack-like producer object with explicit
dtype/shape/pointer metadata into the C ABI neutral buffer view. It validates
descriptor import/export and current host-route rejection from Python, without
parsing arbitrary DLPack capsules, validating CUDA pointer ownership, stream
ordering, or device-buffer query execution.

Goal4605 adds the
[V3.0 Binding And Device Interop Matrix](v3_0_binding_and_device_interop_matrix.md),
which consolidates the current C, Python `ctypes`, pkg-config, CMake, CUDA
metadata, and future DLPack/device-buffer boundaries. It authorizes the current
source-tree/staged examples and metadata descriptors only; it still does not
authorize DLPack support, external CUDA stream adoption, device-buffer query
execution, generated bindings, a stable SDK, release, performance wording, or
public true-zero-copy wording.

## Current Host AABB2 Query Contract

The only implemented query route is deliberately small:

- Context: `rtdl_context_create` with `RTDL_BACKEND_CPU` or `RTDL_BACKEND_AUTO`.
  Other backend requests, including OptiX and Embree, are rejected by the
  current C ABI proof until those routes have dedicated runtime validation.
- External runtime: `rtdl_context_set_external_runtime` accepts host runtime
  metadata only: `RTDL_DEVICE_HOST`, device id `0` or `-1`, and null
  `context`/`stream` handles. Malformed host metadata is rejected as invalid
  argument; CUDA/HIP/Metal/Vulkan runtime handles remain unsupported.
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
- Result ordering: rows are deterministic for the current host AABB2 route.
  RTDL emits rows by ascending `query_id`; within each query, rows are emitted
  by ascending `primitive_id`.
- Ownership: imported buffers are caller-retained when `release == NULL`; when
  `release != NULL`, `rtdl_buffer_destroy` invokes that callback for the buffer
  handle. RTDL-owned result buffers must be released with `rtdl_buffer_destroy`.

The C ABI can also import/export neutral CUDA buffer descriptors as metadata.
That path is descriptor-only: it does not validate pointer ownership with the
CUDA driver, does not synchronize streams, and does not execute a CUDA query
route.

Unsupported primitive kinds, query kinds, backend selections, non-host runtime
handles, external stream adoption, device-buffer query execution, OptiX
execution, Embree execution, and frozen binary compatibility remain outside the
current contract.
