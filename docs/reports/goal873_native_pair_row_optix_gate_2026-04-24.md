# Goal873 Native Pair-Row OptiX Gate

- date: `2026-04-24`
- app: `segment_polygon_anyhit_rows`
- target path: `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded`
- local gate status: `non_strict_recorded_gaps`
- RTX promotion status: `pending_real_optix_strict_gate`

## Work Completed

Goal873 adds a focused gate script for the new native bounded pair-row OptiX
symbol introduced by Goal872.

- Added optional Python `ctypes` binding for
  `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded`.
- Added `scripts/goal873_native_pair_row_optix_gate.py`.
- Added `tests/goal873_native_pair_row_optix_gate_test.py`.
- Generated local artifact
  `docs/reports/goal873_native_pair_row_optix_gate_2026-04-24.json`.

## Gate Semantics

The gate runs the authored segment/polygon representative dataset through the
CPU Python reference, computes an order-insensitive row digest, and then tries
to run the native bounded OptiX symbol.

- Non-strict mode records missing OptiX backend or missing symbol without
  failing local development.
- Strict mode is intended for Linux/RTX and fails unless the native bounded
  symbol runs, matches the CPU row digest, and does not overflow the output
  capacity.
- The gate rejects non-positive output capacity so strict mode cannot
  accidentally validate an empty caller-owned buffer.
- The gate does not promote the public `segment_polygon_anyhit_rows` path by
  itself.

## Local Evidence

Local Mac run:

```text
PYTHONPATH=src:. python3 scripts/goal873_native_pair_row_optix_gate.py --output-json docs/reports/goal873_native_pair_row_optix_gate_2026-04-24.json
```

Result:

- CPU reference: `ok`
- OptiX native bounded: `unavailable_or_failed`
- Reason: `librtdl_optix not found. Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.`
- Overall local status: `non_strict_recorded_gaps`

This is expected on the current Mac environment and is not treated as a
release failure for local development. It is a reminder that a real RTX
strict gate is still required before any promotion or public RT-core claim.
Consumers should read `strict` and `strict_pass` together: local non-strict
runs can record gaps while exiting successfully.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal872_native_pair_row_device_emitter_packet_test tests.goal873_native_pair_row_optix_gate_test
```

Result: `7 tests OK`.

```text
PYTHONPATH=src:. python3 -m py_compile scripts/goal873_native_pair_row_optix_gate.py tests/goal873_native_pair_row_optix_gate_test.py src/rtdsl/optix_runtime.py
git diff --check
```

Result: both passed.

## Boundary

Goal873 is test infrastructure for the new native bounded device emitter. It
does not claim that `segment_polygon_anyhit_rows` is fully promoted to a public
RT-core app path. That promotion requires a Linux/RTX strict gate artifact and
independent review.
