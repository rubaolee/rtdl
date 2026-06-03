# Goal3120: v2.8 CuPy Partner-Consumer Local Linux Smoke

Date: 2026-06-03

Status: local Linux functional smoke, not release or performance evidence

## Purpose

Goal3117 added an explicit partner-consumer front door over the v2.8 segmented
typed-stream adapter. Windows could validate dry-run mapping and fail-closed
behavior, but it did not have Torch, Numba, or CuPy installed.

Goal3120 uses the local Linux validation host to run one actual partner
execution through that front door:

`SegmentedRowStream -> V28TypedResultStreamContract -> explicit CuPy partner columns -> segmented_sum_f64`

## Environment

Host:

- SSH target: `192.168.1.20`
- checkout: `/home/lestat/work/rtdl_codex_local_check`
- commit: `f367f23d`
- GPU: `NVIDIA GeForce GTX 1070`
- driver: `580.126.09`
- CuPy: `14.0.1`

This host is useful for functional smoke. It is not accepted release-grade
performance evidence for v2.8 claims.

## Commands

Update:

```bash
cd /home/lestat/work/rtdl_codex_local_check
git fetch origin main
git merge --ff-only origin/main
git rev-parse --short HEAD
```

Focused tests:

```bash
PYTHONPATH=src:. timeout 120 python3 -m unittest \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal3108_v2_8_typed_result_stream_contract_test \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result:

```text
Ran 25 tests in 0.005s
OK
```

CuPy probe:

```text
cupy 14.0.1
device_count 1
device NVIDIA GeForce GTX 1070
```

Partner-consumer smoke:

```python
adapter = rt.build_segmented_typed_stream_adapter(
    ((0, 1.5), (0, 2.5), (1, 10.0), (2, 3.0)),
    row_schema=("group_ids", "values"),
    column_roles={"group_ids": "group_key", "values": "score"},
    page_capacity=2,
    stream_id="goal3120_cupy_segmented_sum_smoke",
    stream_kind="grouped_reduction_stream",
    producer_primitive="segmented_row_stream_reference",
    ordering="group_ordered",
    operation="segmented_sum_f64",
    group_column="group_ids",
    value_columns=("values",),
    user_selected_partner="cupy",
)
partner_columns = {
    "group_ids": cp.asarray([0, 0, 1, 2], dtype=cp.int64),
    "values": cp.asarray([1.5, 2.5, 10.0, 3.0], dtype=cp.float64),
}
result = rt.execute_segmented_typed_stream_partner_continuation(
    adapter,
    partner="cupy",
    partner_columns=partner_columns,
)
reference = rt.execute_segmented_typed_stream_reference_continuation(adapter)
```

Observed output:

```text
request_status dry_run_partner_consumer_request
result_status completed_partner_consumer
actual [4.0, 10.0, 3.0]
expected [4.0, 10.0, 3.0]
claim_flags False False False
```

## Verdict

The local Linux smoke passed.

It shows that the Goal3117 front door can execute a real CuPy partner consumer
when caller-supplied CuPy columns are provided, and that the output matches the
Goal3114 Python reference consumer for this small segmented-sum case.

## Boundaries

This does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- device-residency claims beyond the explicit CuPy columns supplied by the
  caller,
- hidden dispatch,
- hidden partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- benchmark-app performance claims.

## Next Step

The next step is a larger hardware run on a pod or suitable CUDA host:

1. execute more partner operations through the same front door,
2. compare each against the Goal3114 Python reference consumer,
3. measure timing separately from correctness,
4. keep the release/performance boundary blocked until reviewed evidence exists.
