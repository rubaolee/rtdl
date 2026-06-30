# Goal3123: v2.8 Partner-Consumer Named Output Hardening

Date: 2026-06-03

Status: implemented locally and smoke-tested on local Linux

## Purpose

Goal3117 added the explicit v2.8 partner-consumer front door. Goal3120 proved
that caller-supplied CuPy columns could execute a `segmented_sum_f64` consumer
on the local Linux host.

While widening that smoke to `segmented_count_i64` and
`grouped_vector_sum_f64x2`, Codex found that the bridge returned raw partner
arrays for scalar count/sum operations while the Python reference consumer uses
named output columns:

- reference count output: `{"counts": ...}`
- reference sum output: `{"sums": ...}`
- reference vector output: `{"sum_x": ..., "sum_y": ...}`

Goal3123 hardens the user-facing bridge shape so actual partner execution and
the reference consumer use the same named output schema for scalar reductions.

## Code Change

File:

`src/rtdsl/v2_8_segmented_typed_stream_adapter.py`

Changes:

- `segmented_count_i64` partner execution now returns `{"counts": <partner array>}`.
- `segmented_sum_f64` partner execution now returns `{"sums": <partner array>}`.
- `grouped_vector_sum_f64x2` already returned `{"sum_x": ..., "sum_y": ...}` and
  was left unchanged.
- Release, speedup, RT-core, true-zero-copy, hidden-dispatch, and
  automatic-partner-selection flags remain false.

## Test Change

File:

`tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`

Added a dependency-free unit test using mocked partner adapters to ensure actual
partner execution wraps scalar reduction outputs in named columns.

## Windows Validation

```powershell
py -3 -m py_compile `
  src\rtdsl\v2_8_segmented_typed_stream_adapter.py `
  src\rtdsl\v2_8_typed_result_stream.py `
  src\rtdsl\__init__.py
```

Result: passed.

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test `
  tests.goal3108_v2_8_typed_result_stream_contract_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

```text
Ran 26 tests in 0.013s
OK
```

## Local Linux CuPy Sweep

Host:

- SSH target: `192.168.1.20`
- checkout: `/home/lestat/work/rtdl_codex_local_check`
- base commit: `f367f23d`
- temporary patch: Goal3123 two-file diff applied for smoke validation
- GPU: `NVIDIA GeForce GTX 1070`
- CuPy: `14.0.1`

Linux unit gate:

```text
Ran 26 tests in 0.006s
OK
```

CuPy partner-consumer sweep:

```text
[goal3123] imports ok cupy 14.0.1
[goal3123] device NVIDIA GeForce GTX 1070
[goal3123] case 1 segmented_count_i64
[goal3123] count actual [2, 1, 2] expected [2, 1, 2]
[goal3123] case 2 segmented_sum_f64
[goal3123] sum actual [4.0, 10.0, 10.0] expected [4.0, 10.0, 10.0]
[goal3123] case 3 grouped_vector_sum_f64x2
[goal3123] vector actual x [3.0, 3.0, 9.0] expected [3.0, 3.0, 9.0]
[goal3123] vector actual y [30.0, 30.0, 90.0] expected [30.0, 30.0, 90.0]
[goal3123] claim flags False False False
[goal3123] passed cases segmented_count_i64, segmented_sum_f64, grouped_vector_sum_f64x2
```

## Interpretation

Goal3123 closes a small output-schema consistency gap. It does not promote a
new native primitive or partner runtime. It makes the current v2.8 bridge easier
to validate because the actual partner path and the Python reference path now
return the same named output columns for the CuPy-covered operations.

## Boundaries

This does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- device-residency claims,
- hidden dispatch,
- automatic partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- benchmark-app performance claims.

The local Linux host remains functional-smoke evidence only.

## Next Step

The remaining v2.8 partner-front-door operations need a host or pod with the
selected partner stack installed:

- `grouped_argmin_f64`
- `grouped_argmax_f64`
- `grouped_topk_f64`
- `bounded_collect_finalize_i64`

Those checks should compare against the Goal3114 Python reference consumer and
keep timing/performance claims separate from correctness.
