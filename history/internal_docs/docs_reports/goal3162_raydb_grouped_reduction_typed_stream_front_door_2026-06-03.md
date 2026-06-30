# Goal3162: RayDB Grouped-Reduction Typed-Stream Front Door

Date: 2026-06-03

Status: `implemented_pending_pod_evidence`

## Purpose

RayDB-style grouped aggregates already proved an important v2.5/v2.6 design
rule: when a fused RTDL primitive exactly matches a scalar grouped-reduction
request, primitive-first native execution should win and partner continuation
should not be forced. The remaining v2.8 gap is the unfused-continuation side:
when a user explicitly wants a partner continuation over grouped rows, RTDL
should expose that as a generic typed-stream contract rather than a benchmark
private wrapper.

Goal3162 adds a generic front door for caller-supplied grouped-reduction partner
columns and wires a RayDB-style preview through it.

## Implementation

- Added `rt.execute_grouped_reduction_typed_stream_partner_columns(...)`.
  - Supported operations: `segmented_count_i64`, `segmented_sum_f64`,
    `segmented_min_f64`, `segmented_max_f64`.
  - Inputs are caller-supplied partner columns (`group_ids` plus optional
    `values`).
  - The helper publishes a `grouped_reduction_stream` typed result-stream
    contract and a grouped continuation plan.
  - Execution requires an explicit user-selected `partner`; `auto` is rejected.
  - It does not build hidden host row placeholders.
- Added RayDB app wrappers:
  - `describe_raydb_v2_8_typed_stream_continuation(...)`
  - `run_raydb_v2_8_typed_stream_continuation_preview(...)`
- Preserved the existing v2.6 RayDB Numba neutral continuation path and all
  older path strings for compatibility.

## Boundary

This goal does not change native RayDB/grouped-reduction primitives, does not
promote partner continuation over fused primitive-first paths, and does not make
release, speedup, RT-core, or true-zero-copy claims.

Claim flags remain blocked:

- `release_authorized: False`
- `v2_8_release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3162_raydb_grouped_reduction_typed_stream_front_door_test tests.goal2994_raydb_numba_neutral_demo_test tests.goal2995_raydb_numba_segmented_minmax_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
...s..............................
----------------------------------------------------------------------
Ran 34 tests in 0.043s

OK (skipped=1)
```

Pod validation should rerun the same tests from clean `origin/main` so the
Numba CUDA execution cases run rather than skip.

Clean A40 pod validation:

```text
POD_HEAD=7e811232
RUN_GOAL3162_RAYDB_TYPED_STREAM
Ran 34 tests in 0.840s
OK
```

Pod metadata probe:

```json
{
  "counts": [2, 1, 2],
  "execution_path": "v2_8_grouped_reduction_typed_stream_partner_front_door",
  "operations": ["segmented_sum_f64", "segmented_count_i64"],
  "public_speedup_claim_authorized": false,
  "rows": [
    {
      "automatic_partner_selection_allowed": false,
      "device_resident_column_count": 2,
      "operation": "segmented_sum_f64",
      "path": "v2_8_grouped_reduction_typed_stream_partner_front_door",
      "producer_primitive": "ray_triangle_grouped_i64_reduction_3d",
      "release_authorized": false,
      "stream_kind": "grouped_reduction_stream"
    },
    {
      "automatic_partner_selection_allowed": false,
      "device_resident_column_count": 1,
      "operation": "segmented_count_i64",
      "path": "v2_8_grouped_reduction_typed_stream_partner_front_door",
      "producer_primitive": "ray_triangle_grouped_i64_reduction_3d",
      "release_authorized": false,
      "stream_kind": "grouped_reduction_stream"
    }
  ],
  "rt_core_speedup_claim_authorized": false,
  "sums": [4.0, 10.0, 4.0],
  "true_zero_copy_claim_authorized": false
}
```
