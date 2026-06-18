# RTDL C ABI Embedding Examples

Status: V3 draft source-tree examples.

These examples show how a non-Python program can load the draft RTDL C ABI
library from the source tree. They are not a packaged SDK, frozen ABI, or
release contract.

## Host AABB2 Overlap

The first example builds a host `F32` AABB2 index, runs one host AABB overlap
query, and reads a host `U64` `(query_id, primitive_id)` pair buffer.

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
