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

## Boundary

- This is a source-tree C client example for the V3 draft C ABI.
- It validates only host `F32` AABB2 overlap through `librtdl_c_api`.
- It is not an OptiX, Embree, device-buffer, Python package, or frozen-ABI
  claim.
