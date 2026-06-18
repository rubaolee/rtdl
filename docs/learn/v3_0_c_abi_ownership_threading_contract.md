# V3.0 C ABI Ownership And Threading Contract

Status: draft source-tree contract for the V3 embeddability track. This page
documents the current `0.1.1` C ABI behavior; it is not a frozen SDK promise.

Read this with [V3.0 C ABI Draft](v3_0_c_abi_draft.md) and
[V3.0 C ABI Stability Policy](v3_0_c_abi_stability_policy.md).

## Ownership Rules

The current C ABI uses opaque handles and explicit destroy calls:

- `rtdl_context_create` returns an RTDL-owned `rtdl_context*`; release it with
  `rtdl_context_destroy`.
- `rtdl_buffer_import` returns an RTDL-owned buffer handle over the supplied
  `rtdl_buffer_view`.
- `rtdl_index_build` returns an RTDL-owned `rtdl_index*`; release it with
  `rtdl_index_destroy`.
- `rtdl_query_execute` returns an RTDL-owned result `rtdl_buffer*`; release it
  with `rtdl_buffer_destroy`.
- Destroy functions accept `NULL` and perform no work.

`rtdl_buffer_view.release` is the current buffer ownership switch:

- If `release == NULL`, RTDL does not free or release `view.data` when the
  imported buffer handle is destroyed. The caller retains ownership and must
  keep the memory alive for every operation that reads the imported buffer.
- If `release != NULL`, `rtdl_buffer_destroy` calls that callback exactly once
  for that buffer handle, passing `view.data` and `view.user_data`. The caller
  must not release the same payload separately after transferring this callback
  responsibility to the handle. This is the release-callback-owned state.
- Release callbacks must not throw C++ exceptions, long-jump across the C ABI,
  or call back into RTDL on a handle that is being destroyed.

The current host AABB2 route copies primitive coordinates during
`rtdl_index_build`. After a successful index build, the primitive buffer handle
may be destroyed and the index remains valid. Query input buffers are read
during `rtdl_query_execute` and must remain valid for the duration of that call.

Exported result views borrow the result buffer's storage. Their `data` pointer,
shape, strides, and release callback are valid only until the owning result
buffer is destroyed.

## Last-Error Rules

`rtdl_context_last_error(context)` returns a pointer owned by the context. The
pointer is valid only until the next C ABI call that mutates the same context or
until `rtdl_context_destroy`.

The last-error string is diagnostic text. Callers must not parse it as a stable
machine contract; use `rtdl_status` for branching.

## Threading Rules

The current `0.1.1` ABI is reentrant only at the narrow utility level:

- ABI version functions and `rtdl_status_string` are safe to call concurrently.
- Independent contexts with no shared imported buffers are intended to be usable
  independently, but this is not yet a release-grade thread-safety guarantee.
- Calls that mutate or destroy the same context, buffer, index, or query handle
  require external synchronization.
- A handle must not be destroyed while any other thread may still use it.
- `rtdl_context_last_error` is per-context mutable state and is not safe to read
  concurrently with calls that can update that same context.

Stable thread-safety wording remains blocked until a dedicated concurrency test
matrix exists for every supported backend route.

## Boundary

This contract does not freeze the ABI, publish a packaged SDK, validate
cross-version compatibility, validate external CUDA/OptiX stream semantics, or
authorize public performance wording. It documents the current source-tree
ownership and threading boundary so later language bindings have a precise base
instead of folklore.
