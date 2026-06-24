# Goal3169 - Barnes-Hut Grouped Vector Typed-Stream Front Door

Date: 2026-06-03

Status: local and pod validation complete.

## Purpose

Barnes-Hut pressure in the v2.8 runtime-gap matrix is not another
Barnes-Hut-specific engine path. The reusable need is a grouped 2-D vector
reduction over caller-supplied columns. Goal3169 exposes that need as a generic
typed-stream front door:

`execute_grouped_vector_sum_typed_stream_partner_columns(...)`

The Barnes-Hut benchmark wrapper now has:

- `describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(...)`
- `run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview(...)`
- CLI mode `--mode v2_8_grouped_vector_sum_plan`

## What The Helper Does

The helper accepts:

- `group_ids`
- `values_x`
- `values_y`
- optional `row_offsets`
- explicit `partner`
- explicit `stream_id`

It publishes a `grouped_reduction_stream` typed result-stream contract and a
`grouped_vector_sum_f64x2` grouped continuation plan. It then executes through
the existing generic `grouped_vector_sum_2d_partner_columns(...)` adapter when
`dry_run=False`.

The typed-stream continuation semantics table now documents
`grouped_vector_sum_f64x2` as paired float64 x/y component summation per group.

## Partner Boundary

The helper rejects `partner="auto"` and records
`automatic_partner_selection_allowed: False`.

The underlying vector-sum adapter currently supports:

- `cupy`
- `torch`
- `triton`

Numba is not promoted for `grouped_vector_sum_f64x2` in this slice.

## Barnes-Hut Boundary

The benchmark wrapper is allowed to mention Barnes-Hut because it is an example
and benchmark app. The runtime helper does not embed Barnes-Hut force law,
opening predicates, tree traversal, timestep integration, or paper-specific
logic.

This goal does not add:

- a native Barnes-Hut ABI;
- native force-vector math;
- native grouped vector-sum promotion;
- full RT-BarnesHut paper reproduction;
- authors-code comparison;
- public speedup wording;
- RT-core speedup wording;
- true-zero-copy wording;
- release authorization.

## Claim Flags

The new front door sets or preserves:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

## Local Validation

Compile check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile `
  src\rtdsl\v2_8_typed_result_stream.py `
  src\rtdsl\v2_8_segmented_typed_stream_adapter.py `
  src\rtdsl\__init__.py `
  examples\v2_0\research_benchmarks\barnes_hut\rtdl_barnes_hut_benchmark_app.py `
  tests\goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test.py
```

Result: pass.

Focused regression:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test `
  tests.goal3108_v2_8_typed_result_stream_contract_test `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test `
  tests.goal2781_grouped_vector_sum_adapter_test
```

Result: 35 tests pass, 2 skipped.

CLI descriptor:

```powershell
$env:PYTHONPATH='src;.'; py -3 `
  examples\v2_0\research_benchmarks\barnes_hut\rtdl_barnes_hut_benchmark_app.py `
  --mode v2_8_grouped_vector_sum_plan `
  --partner cupy
```

Result: JSON payload reports `grouped_reduction_stream`,
`grouped_vector_sum_f64x2`, explicit partner `cupy`, presegmented offsets, and
all release/speedup/zero-copy flags as false.

## Pod Validation

Pod: `root@69.30.85.131 -p 22063`, repo `/root/rtdl_goal3151`,
virtualenv `/root/venvs/rtdl_goal3154`.

Clean commit:

```text
4fe7f12c Goal3169 add Barnes-Hut grouped vector typed stream front door
```

Command shape:

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
/root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test \
  tests.goal3108_v2_8_typed_result_stream_contract_test \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal2781_grouped_vector_sum_adapter_test
```

Result:

```text
Ran 35 tests in 0.012s
OK (skipped=2)
```

Descriptor probe:

```text
[pod] descriptor grouped_reduction_stream grouped_vector_sum_f64x2 cupy False
```

The final `False` is the benchmark metadata
`public_speedup_claim_authorized` flag.
