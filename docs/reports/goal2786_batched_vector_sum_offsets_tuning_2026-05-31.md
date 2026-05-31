# Goal2786 - Batched Vector-Sum Offsets Tuning

Date: 2026-05-31

## Purpose

Goal2785 added an atomics-free presegmented row-offset path for generic grouped
2D vector sums. It was a small improvement over the original Triton atomic
preview but remained slower than Torch scatter-add.

Goal2786 tests the next obvious tuning hypothesis: reduce several presegmented
groups per Triton program so the kernel launches fewer programs. The goal is
generic vector reduction tuning only. It does not add Barnes-Hut, force-law, or
application-specific logic.

## What Changed

Updated:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`

Added:

- `_triton_grouped_vector_sum_f64x2_offsets_batched_kernel(...)`
- `groups_per_program` support in
  `run_triton_grouped_vector_sum_f64x2_by_offsets(...)`
- `triton_offset_groups_per_program` in
  `grouped_vector_sum_2d_partner_columns(...)`
- metadata:
  - `v2_5_triton_offset_groups_per_program`
  - `v2_5_triton_offset_program_count`

The default remains `groups_per_program=1`, which preserves the Goal2785
single-group offset behavior. The batched path is an explicit tuning knob, not a
new selected default.

## Pod Timing

Pod artifact:

`docs/reports/goal2786_pod_artifacts/goal2786_batched_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json`

Host:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
```

Best measured Triton offset result for each shape:

| Rows | Groups | Rows/group | Torch sec | Triton atomic sec | Best offset groups/program | Best offset sec | Best / Torch | Best / Atomic |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8,192 | 512 | 16 | 0.000199512 | 0.003436773 | 1 | 0.003362169 | 16.852x | 0.978x |
| 262,144 | 4,096 | 64 | 0.000672710 | 0.004055113 | 1 | 0.003830323 | 5.694x | 0.945x |
| 1,048,576 | 8,192 | 128 | 0.001076440 | 0.004350663 | 1 | 0.004043022 | 3.756x | 0.929x |

All tested batched values (`groups_per_program` 2, 4, 8, and 16) were slower
than the single-group offset path on every measured shape.

## Design Finding

The simple batching hypothesis is rejected for now. Serially reducing multiple
groups inside one Triton program reduces program count, but it also reduces
parallelism and adds enough per-program work that it loses on the RTX A5000
shapes tested here.

The next vector-sum performance candidate should not be simple
groups-per-program batching. It needs a genuinely different segmented/block
reduction design, or the planner should continue choosing an explicit
non-Triton same-contract partner for dense vector sums.

## Guidance Refresh

Goal2786 refreshes the dense grouped vector-sum row in:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`

The row now points to the Goal2786 pod artifact and records that the best Triton
offset path is still 3.76x-16.86x slower than Torch. Barnes-Hut planning remains
blocked from blindly auto-selecting Triton for dense grouped vector sums.

## Boundary

This goal authorizes:

- a generic batched row-offset tuning candidate;
- measured negative evidence for that candidate;
- refreshed advisory guidance for dense grouped vector sums.

This goal does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- embedding app force laws in RTDL or Triton primitives;
- auto-selecting Triton for dense grouped vector sums.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2786_batched_vector_sum_offsets_tuning_test \
  tests.goal2785_presegmented_vector_sum_triton_offsets_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 9 tests in 0.014s
OK (skipped=3)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2786_local2
OK

Broader guidance-inclusive local gate:

```text
tests.goal2786_batched_vector_sum_offsets_tuning_test
tests.goal2785_presegmented_vector_sum_triton_offsets_test
tests.goal2782_v2_5_partner_selection_guidance_test
tests.goal2783_v2_5_app_migration_selection_guidance_test
tests.goal2781_grouped_vector_sum_adapter_test

Ran 22 tests in 0.046s
OK (skipped=4)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2786_final2
OK
```
```

Pod validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2786_batched_vector_sum_offsets_tuning_test \
  tests.goal2785_presegmented_vector_sum_triton_offsets_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 9 tests in 3.100s
OK
```

Pod guidance-inclusive gate:

```text
tests.goal2786_batched_vector_sum_offsets_tuning_test
tests.goal2785_presegmented_vector_sum_triton_offsets_test
tests.goal2782_v2_5_partner_selection_guidance_test
tests.goal2783_v2_5_app_migration_selection_guidance_test
tests.goal2781_grouped_vector_sum_adapter_test

Ran 22 tests in 2.508s
OK
```

## Decision

`accept-with-boundary`

The batched kernel is accepted as a measured generic tuning candidate and a
negative design result. It is not promoted. The best measured Triton path remains
the Goal2785-style single-group offset kernel, and Torch remains the faster
same-contract branch for dense grouped vector sums.
