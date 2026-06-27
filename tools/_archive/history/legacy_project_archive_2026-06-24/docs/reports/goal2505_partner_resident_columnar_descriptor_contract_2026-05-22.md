# Goal2505: Partner-Resident Columnar Descriptor Contract

## Result

Goal2505 adds the first partner-resident columnar descriptor contract for the
RayDB-style reconstruction path.

The new API is:

- `rtdsl.prepare_partner_resident_columnar_record_set(record_set, backend="optix")`

It accepts a generic columnar record-set mapping whose `row_ids` and `columns`
are CUDA partner tensors and returns a `PartnerResidentColumnarRecordSet`
descriptor. The descriptor records field names, dtype category, data pointers,
shape, strides, source protocol, CUDA device, and claim-boundary metadata.

Focused local validation passed:

- `PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2505_partner_resident_columnar_descriptor_contract_test`
- Result: `9 tests OK`

Fresh pod validation passed on `root@69.30.85.198 -p 22017` with key
`~/.ssh/id_ed25519_rtdl_codex`:

- `PYTHONPATH=src:. python3 -m unittest tests.goal2505_partner_resident_columnar_descriptor_contract_test`
- Result: `9 tests OK`
- Real CUDA partner artifact: `docs/reports/goal2505_partner_resident_torch_descriptor_pod_2026-05-22.json`
- Note: this pod did not have CuPy installed, so the real CUDA partner evidence used PyTorch CUDA tensors.

## What This Solves

This moves the architecture beyond host-only columnar preparation:

- Goal2503 removed Python row-mapping materialization.
- Goal2504 reused contiguous NumPy host buffers when possible.
- Goal2505 validates CUDA partner-resident column descriptors without staging
  those columns back to host.

The descriptor layer is app-agnostic. It contains no RayDB, SQL, SSB, or
database-specific semantics.

## Current Boundary

This is descriptor-only; native execution remains blocked until the OptiX
columnar payload runtime can execute against partner-resident columns without
reconstructing host `row_values`.

The descriptor therefore records:

- `transfer_mode = partner_resident_column_descriptor_only`
- `native_execution_authorized = False`
- `true_zero_copy_authorized = False`
- `row_id_uniqueness_validated = False`

true zero-copy remains blocked because the current OptiX DB path builds host
row-value storage for exact filtering, row metadata, primary-axis construction,
and grouped reductions. Avoiding that requires a new native execution path, not
just a Python wrapper.

## Fail-Closed Validation

The descriptor contract currently requires:

- backend `optix`
- CUDA partner columns
- one-dimensional columns
- matching row counts
- one CUDA device across all fields
- contiguous strides
- `row_ids` dtype `int64` or `uint32`
- data column dtype `int64`, `uint32`, or `float64`

Embree is rejected because partner-resident CUDA columns are not useful for a
CPU backend. NumPy host arrays remain covered by Goal2504.

## Next Target

The next target is `optix_partner_resident_columnar_payload_native_execution`:
a generic OptiX native columnar payload path that can consume validated device
column descriptors directly, build or reuse device-side row metadata and RT
axes, and perform count/sum reductions without host-staging the whole table.
