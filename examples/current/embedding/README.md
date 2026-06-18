# RTDL C ABI Embedding Examples

Status: V3 draft source-tree examples.

These examples show how a non-Python program can load the draft RTDL C ABI
library from the source tree. They are not a packaged SDK, frozen ABI, or
release contract.

## Host AABB2 Overlap

The first example builds a host `F32` AABB2 index, runs one host AABB overlap
query, and reads a host `U64` `(query_id, primitive_id)` pair buffer.

Current data contract:

- Primitive and query buffers are host `RTDL_DTYPE_F32` AABB2 rows shaped
  `[count, 4]` as `(min_x, min_y, max_x, max_y)`.
- The result buffer is host `RTDL_DTYPE_U64`, shaped `[hit_count, 2]`, with
  rows `(query_id, primitive_id)`.
- For the current host AABB2 route, rows are deterministic: ascending
  `query_id`, then ascending `primitive_id` within each query.
- `rtdl_index_build` copies primitive coordinates into the index; imported
  buffers are caller-retained when `release == NULL` and release-callback-owned
  by the buffer handle when `release != NULL`. Query result buffers are
  RTDL-owned and must be released with `rtdl_buffer_destroy`.

Linux/pod commands from the repository root:

```bash
make build-c-api
cc -std=c11 -I include \
  examples/current/embedding/c_api_aabb2_overlap_client.c \
  -o build/rtdl_c_api_aabb2_overlap_client \
  -ldl
./build/rtdl_c_api_aabb2_overlap_client build/librtdl_c_api.so
```

Expected output:

```text
hit_count=1 first_pair=(0,0)
```

## Source-Tree Staging Bundle

For a cleaner non-Python handoff, use:

```bash
make stage-c-api
```

This creates `build/c_api_stage` with the public header, shared library, current
draft symbol manifest, `lib/pkgconfig/rtdl-c-api.pc`, this README, the AABB2
dlopen and direct-link C examples, a thin Python `ctypes` lifecycle example,
and a Python `ctypes` host AABB2 query example. It is still a source-tree
staging bundle, not an installed SDK.

To archive that same movable source-tree stage:

```bash
make package-c-api-stage
```

This writes `build/rtdl-c-api-stage-0.1.3.tar.gz`.

For direct-link clients:

```bash
export PKG_CONFIG_PATH="$PWD/build/c_api_stage/lib/pkgconfig"
pkg-config --cflags --libs rtdl-c-api
cc -std=c11 $(pkg-config --cflags rtdl-c-api) \
  build/c_api_stage/examples/c_api_direct_link_client.c \
  -o build/c_api_stage/examples/rtdl_c_api_direct_link_client \
  $(pkg-config --libs rtdl-c-api)
LD_LIBRARY_PATH="$PWD/build/c_api_stage/lib:${LD_LIBRARY_PATH:-}" \
  ./build/c_api_stage/examples/rtdl_c_api_direct_link_client
```

For a minimal language-binding style client without writing C/C++:

```bash
python3 build/c_api_stage/examples/python_ctypes_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_ok 0.1.3 ok
```

For the same Python `ctypes` path running the current host AABB2 query route:

```bash
python3 build/c_api_stage/examples/python_ctypes_aabb2_query_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_hit_count=1 first_pair=(0,0)
```

## Boundary

- This is a source-tree C client example for the V3 draft C ABI.
- `package-c-api-stage` produces a source-tree staging archive, not an installed
  SDK or stable release artifact.
- It validates only host `F32` AABB2 overlap through `librtdl_c_api`.
- The Python `ctypes` example validates version/capability/context lifecycle
  calls only; it is not a generated Python package or complete binding.
- The Python `ctypes` AABB2 query example validates host buffer import, index
  build, query execute, result export, and handle cleanup for the current host
  AABB2 route only.
- It is not an OptiX, Embree, device-buffer, packaged-SDK, or frozen-ABI claim.
