# Goal2504: Columnar Typed Host-Buffer Handoff

## Result

Goal2504 adds an optional typed host-buffer handoff path inside direct
ColumnarRecordSet preparation.

When a caller supplies contiguous one-dimensional `numpy.int64` or
`numpy.float64` columns, the Python runtime now passes their existing host
buffer pointers into the generic native columnar payload descriptor instead of
building a new ctypes value array for that column.

The change applies to both direct preparation entry points:

- `rtdsl.prepare_embree_columnar_record_set(...)`
- `rtdsl.prepare_optix_columnar_record_set(...)`

The existing native ABI is unchanged.

Focused local validation passed:

- `PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2504_columnar_typed_host_buffer_handoff_test`
- Result: `6 tests OK, 1 skipped`

Fresh OptiX pod validation passed on `root@69.30.85.198 -p 22017` with key
`~/.ssh/id_ed25519_rtdl_codex`:

- `PYTHONPATH=src:. python3 -m unittest tests.goal2504_columnar_typed_host_buffer_handoff_test`
- Result: `6 tests OK`
- Artifact: `docs/reports/goal2504_optix_numpy_typed_host_buffer_pod_2026-05-22.json`

## Boundary

This removes one Python-side copy layer for matching numeric host columns. It
does not authorize true zero-copy wording:

- OptiX still needs native/device staging after Python passes the host pointer.
- Non-contiguous arrays, unsupported dtypes, boolean columns, and text-encoded
  columns still fall back to copied ctypes buffers.
- User Python code remains outside the RTDL engine performance responsibility
  boundary.

## Metadata

Prepared direct-columnar datasets now expose
`columnar_preparation_metadata()`. The metadata records:

- `typed_host_buffer_columns`
- `copied_columns`
- `text_encoded_columns`
- `all_numeric_columns_use_typed_host_buffers`
- `native_abi_added = False`
- `true_zero_copy_authorized = False`

The RayDB-style app includes this metadata in native backend payloads under
`metadata.columnar_preparation`.

## Next Target

The remaining architectural target is partner-resident column handoff. For
Python+partner+RTDL this means allowing a partner such as CuPy or another
device-array provider to hand RTDL a validated device-resident column
descriptor without first staging through Python host arrays, with explicit
ownership, lifetime, stream, dtype, and device-context contracts.
