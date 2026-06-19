# RTDL V4 Active Experimental ABI

This directory is the active V4 implementation area. It is separate from the
archived V4 preparatory evidence under `docs/history/v4_preparatory_embedding/`.

After the 2026-06-19 V4 reframing note, this directory is Phase 2 substrate
work. It is useful and should stay active, but it is not the Phase 1 V4.0
product proof. The V4.0 product proof is a Python GPU device-array RT-core
operator route: CuPy/Numba/PyTorch array in, RT cores, device array out.

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

Frozen Phase 1 product route:

- Python API: `rtdsl.prepare_v4_fixed_radius_count_threshold_2d` and
  `rtdsl.run_v4_fixed_radius_count_threshold_2d`;
- route: `fixed_radius_count_threshold_2d`;
- input: caller-owned CUDA `ids`, `x`, `y` point columns;
- evidence-backed inputs: CuPy device columns and Numba `DeviceNDArray`
  columns through `__cuda_array_interface__`;
- target inputs without route evidence yet: PyTorch and DLPack;
- output: fixed-size CUDA `query_ids`, `neighbor_counts`, and
  `threshold_flags` columns;
- stream: nonzero caller CUDA streams are propagated through prepare and query
  synchronously; async completion is not claimed yet;
- blocked in this ABI directory until later substrate work: public non-Python
  SDK packaging, variable-length neighbor rows, and broad true-zero-copy claims.

Linux evidence command after `make build-optix`:

```bash
PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py
```

This is not a stable SDK, not a public package-install promise, and not the
V4.0 headline.
