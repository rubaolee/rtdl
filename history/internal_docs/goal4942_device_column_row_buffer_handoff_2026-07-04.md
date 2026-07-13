# Goal4942 - Device-Column Row-Buffer Handoff Reuse Adapter

Date: 2026-07-04

## Verdict Requested

`completed_reuse_first_layer1_device_column_row_buffer_adapter_no_speedup_claim`

## Objective

Implement the Layer 1 reuse-first seam:

> RTDL primitive-produced device columns should be able to enter explicit CuPy/Numba partner continuation planning through a generic row-buffer carrier, reusing the existing v2.5/v2.6 device-column and neutral-handoff work instead of inventing a new memory system.

This goal is **not** a performance claim and **not** a true-zero-copy claim.

## What Was Found Before Implementation

The historical audit found substantial prior work:

- v2.5 hit-stream device-column handoff:
  - `RtdlHitStreamColumnHandoff`
  - `RtdlRawCudaColumn`
  - `prepare_generic_device_resident_hit_stream_columns(...)`
  - native device-column metadata, reusable buffer flags, device status pointers, and stream-ordering metadata
- v2.6 neutral partner handoff:
  - `plan_v2_6_neutral_partner_handoff(...)`
  - `prepare_v2_6_neutral_partner_handoff(...)`
  - CuPy/Numba neutral partner validation
  - torch-carrier/coercion rejection
- v2.5 neutral buffer seam:
  - DLPack / `__cuda_array_interface__` observation
  - neutral lease lifecycle
  - explicit non-authorization for public zero-copy or speedup wording

Therefore Goal4942 was scoped as a **reuse adapter**, not a new architecture.

## Code Added

New module:

- `src/rtdsl/device_column_row_buffer.py`

Top-level importable, but not stable star-exported, symbols:

- `DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION`
- `DEVICE_COLUMN_ROW_BUFFER_API_MATURITY`
- `DEVICE_COLUMN_ROW_BUFFER_SOURCE_MODES`
- `RtdlDeviceColumnRowBuffer`
- `describe_device_column_row_buffer_contract`
- `prepare_device_column_row_buffer`
- `device_column_row_buffer_from_hit_stream_handoff`
- `plan_device_column_row_buffer_partner_handoff`
- `prepare_device_column_row_buffer_partner_handoff`

These are imported in `src/rtdsl/__init__.py` for explicit use, but intentionally not added to `rtdsl.__all__`.

## What The Adapter Does

`RtdlDeviceColumnRowBuffer` records:

- named primitive-output columns
- shared `row_count`
- producer name
- source mode
- host-materialization state
- stream-ordering state
- native-device-output proof flag
- phase timing metadata

`plan_device_column_row_buffer_partner_handoff(...)` delegates actual partner-side validation to the existing v2.6 neutral handoff path:

- requires explicit partner choice (`cupy` or `numba`)
- rejects torch carrier/coercion
- rejects host columns when device residency is required
- records neutral lease metadata
- preserves non-authorization flags

`device_column_row_buffer_from_hit_stream_handoff(...)` adapts existing v2.5 hit-stream columns into the new generic carrier:

```text
RtdlHitStreamColumnHandoff(ray_ids, primitive_ids)
  -> RtdlDeviceColumnRowBuffer({"ray_ids", "primitive_ids"})
  -> v2.6 neutral partner handoff
```

## Boundaries

Authorized:

- Generic named-column carrier for primitive outputs.
- Reuse of v2.5 hit-stream device-column contracts.
- Reuse of v2.6 CuPy/Numba neutral partner validation.
- Explicit fail-closed host-materialized rows when device residency is required.

Not authorized:

- Public speedup claims.
- True-zero-copy claims.
- Whole-application speedup claims.
- RayJoin output schema in core.
- App-specific row-buffer schema in core.
- Execution of a partner continuation from this adapter alone.

## Why This Is Not The Full Layer 1 Yet

Goal4942 closes the generic **carrier + validation** gap, not every producer gap.

Still open:

- Each primitive producer must still be audited individually.
- LSI/PIP must either expose compatible device columns or be marked as producer gaps.
- Same-stream async continuation is not authorized by this adapter.
- This adapter does not turn existing host-materialized rows into device-resident rows.
- This adapter does not itself run Numba kernels; it prepares the validated seam.

## Tests Added / Updated

New test:

- `tests/goal4942_device_column_row_buffer_handoff_test.py`

Small test maintenance:

- `tests/goal2990_v2_6_neutral_partner_handoff_test.py`
  - updated the historical report path from `docs/reports/...` to `history/internal_docs/docs_reports/...` after public-surface cleanup moved internal reports out of `docs/`.

## Verification

Command:

```powershell
$env:PYTHONPATH='src'; py -m unittest tests.goal4942_device_column_row_buffer_handoff_test tests.goal2990_v2_6_neutral_partner_handoff_test tests.goal4941_layer2_numba_columnar_continuations_test
```

Result:

```text
Ran 17 tests in 0.009s
OK (skipped=2)
```

Command:

```powershell
$env:PYTHONPATH='src'; py -m unittest tests.goal2685_device_resident_hit_stream_handoff_test tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test tests.goal2990_v2_6_neutral_partner_handoff_test tests.goal4942_device_column_row_buffer_handoff_test
```

Result:

```text
Ran 33 tests in 20.159s
OK (skipped=2)
```

The second run emitted existing native Embree build warnings and an optional linker failure while probing an unavailable native path, but the unittest result was still `OK` with skipped optional runtime paths.

## Exit Label

`completed_reuse_first_layer1_device_column_row_buffer_adapter_no_speedup_claim`
