# Goal2781 - Grouped Vector-Sum Adapter Wiring

Date: 2026-05-31

## Purpose

Goal2781 is the next app-adapter wiring slice after Goal2780 showed that dense
top-k ranking is correct but not a good Triton performance path yet.

This goal wires a better-shaped generic continuation into the public Python
surface: grouped two-component vector sums. This is useful for force,
accumulation, and vector-field style applications without placing Barnes-Hut,
N-body, or any other app vocabulary inside the RTDL engine.

## What Changed

Added two generic partner-column helpers:

- `partner_group_vector_sum_2d_by_key(keys, values_x, values_y, group_count, partner=...)`
- `grouped_vector_sum_2d_partner_columns(vector_columns, group_count=..., partner=...)`

For `partner="triton"`, the helper routes through the existing v2.5 generic
continuation operation:

`grouped_vector_sum_f64x2`

For `partner="torch"` and `partner="cupy"`, the helper keeps same-contract
partner-owned column behavior through direct scatter/add-style grouped sums.

## Boundary

This goal authorizes:

- a generic grouped vector-sum adapter surface;
- correctness comparison against the Torch same-contract path;
- internal v2.5 preview evidence for the existing Triton continuation kernel.

This goal does not authorize:

- no public speedup claim;
- no true zero-copy claim;
- no RT-core speedup claim;
- no v2.5 release readiness;
- no claim that the native engine computes app-specific force laws.

The Triton path remains `preview_not_promoted`. It is a reusable continuation
surface, not a performance guarantee.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2781_grouped_vector_sum_adapter_test

Ran 3 tests in 0.018s
OK (skipped=1)

py -3 -m py_compile \
  src\rtdsl\partner_adapters.py \
  src\rtdsl\__init__.py \
  src\rtdsl\adapters\reductions.py \
  tests\goal2781_grouped_vector_sum_adapter_test.py

OK

$env:PYTHONPATH='src;.'
py -3 -m unittest <v2.5 preview slice through Goal2781>

Ran 117 tests in 0.083s
OK (skipped=10)
```

Pod validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01
Base repo head: 7e1ec5c2cc5a6ceafc2eec091cfe61bb0800baaa

PYTHONPATH=src:. python3 -m unittest tests.goal2781_grouped_vector_sum_adapter_test

Ran 3 tests in 2.973s
OK

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2678_v2_5_triton_compact_mask_preview_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2680_v2_5_triton_bounded_collect_preview_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test \
  tests.goal2777_v2_5_triton_grouped_topk_preview_test \
  tests.goal2778_v2_5_triton_grouped_vector_sum_preview_test \
  tests.goal2779_v2_5_triton_edge_list_components_preview_test \
  tests.goal2780_topk_adapter_triton_grouped_topk_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 117 tests in 2.546s
OK
```

Pod timing artifact:

`docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`

| rows | groups | Triton median sec | Torch median sec | Triton / Torch | correctness |
| ---: | ---: | ---: | ---: | ---: | --- |
| 8,192 | 512 | 0.002952 | 0.000178 | 16.586x | pass |
| 262,144 | 4,096 | 0.003292 | 0.000490 | 6.723x | pass |
| 1,048,576 | 8,192 | 0.003644 | 0.000890 | 4.093x | pass |

This is intentionally recorded as negative performance evidence for the current
Triton preview kernel. The adapter and generic contract are valid, but Torch
scatter-add remains the better selected partner for this dense vector-sum shape
until a stronger Triton implementation exists.

## Decision

`accept-with-boundary`

Consensus:

`docs/reports/goal2781_grouped_vector_sum_adapter_consensus_2026-05-31.md`
