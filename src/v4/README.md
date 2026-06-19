# RTDL V4 Active Experimental ABI

This directory is the active V4 implementation area. It is separate from the
archived V4 preparatory evidence under `docs/history/v4_preparatory_embedding/`.

Current slice:

- pre-1.0 C ABI version `0.2.0`;
- `struct_size` descriptors;
- enum-keyed `rtdl_query_capability`;
- opaque context, buffer, index, query-plan, result, and event handles;
- host F32 AABB2 overlap route;
- RTDL-owned result mode;
- caller-provided host U64 pair output mode with required-count and
  `RTDL_STATUS_RESULT_TRUNCATED`;
- fail-closed descriptor validation for malformed shape, dtype, device, byte
  count, rank, ownership, and output descriptors.

After `make build-v4-c-api` on Linux, run:

```bash
python3 src/v4/examples/python_ctypes_aabb2_smoke.py
```

The smoke validates RTDL-owned result output, caller-provided output truncation,
and caller-provided exact-fit output for the host F32 AABB2 route.

This is not a stable SDK and is not a public package-install promise.
