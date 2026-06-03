# Goal3147: Compact-Mask Front Door for v2.8 Typed Streams

Date: 2026-06-03

Status: implemented and validated on RTX 4000 Ada pod; internal v2.8 preview only.

## Purpose

Goal3145 moved segmented min/max into the v2.8 segmented typed stream partner-consumer front door and left `compact_mask_i64` as the final deferred operation. Goal3147 closes that remaining front-door gap.

`compact_mask_i64` is not a grouped reduction. It is a stable row-filter continuation over a typed candidate stream. The v2.8 adapter now exposes it with its own explicit schema instead of pretending it belongs to the grouped min/max family.

## Implementation

- Added `compact_mask_i64` to `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`.
- Removed it from `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS`; the deferred map is now empty.
- The front door accepts caller-supplied partner columns:
  - `values:int64`
  - `mask:bool`
- Canonical output schema:
  - `values:int64`
  - `original_indices:int64`
- For `partner="numba"`, the adapter calls the existing generic `run_numba_compact_mask_i64(...)`.
- For Torch/CuPy/Triton-shaped partners, the adapter uses the generic mask-index plus take helpers where that partner supports indexed selection.

## Boundary

This is a front-door promotion over an existing generic continuation primitive. It does not promote a native producer, does not add benchmark-app-specific logic, does not hide partner choice, and does not authorize public speedup, RT-core, true-zero-copy, device-resident stream, or release wording.

The Numba path remains honest about its implementation:

- `stable_input_order: true`
- `host_prefix_sum_used: true`
- `partner_consumer_promoted: false`

## Validation

Local validation:

```text
python -m unittest \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal3145_segmented_minmax_front_door_canonical_compaction_test \
  tests.goal2997_numba_compact_mask_prepared_test \
  tests.goal3139_numba_kernel_cache_contract_test

Ran 29 tests
OK
```

Pod validation on NVIDIA RTX 4000 Ada:

```text
python -m unittest \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal3145_segmented_minmax_front_door_canonical_compaction_test \
  tests.goal2997_numba_compact_mask_prepared_test \
  tests.goal3139_numba_kernel_cache_contract_test

Ran 29 tests in 0.009s
OK
```

Pod probe artifact:
`docs/reports/goal3147_pod_artifacts/compact_mask_front_door_pod_probe_2026-06-03.json`

The probe performs an explicit warmup before measured rows so the first measured row is not a JIT compilation timing.

| rows | selected | time | values match | indices match | stable order | host prefix-sum |
| ---: | ---: | ---: | --- | --- | --- | --- |
| 1,000,000 | 230,770 | 0.046104 s | yes | yes | yes | yes |
| 4,000,000 | 923,079 | 0.173104 s | yes | yes | yes | yes |

All claim-boundary flags stayed false.

## Conclusion

The v2.8 typed stream partner-consumer front door now covers the full current operation set: grouped count/sum/min/max/vector sum, grouped argmin/argmax/top-k, bounded collect, and stable compact-mask filtering. The remaining work is no longer a missing front-door operation; it is deeper runtime work such as device-resident output streams and broader partner conformance, which remains outside this goal.
