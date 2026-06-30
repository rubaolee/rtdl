# Goal2785 - Presegmented Vector-Sum Triton Offsets

Date: 2026-05-31

## Purpose

Goal2781 showed that the generic Triton grouped vector-sum preview was correct
but slower than Torch scatter-add because it used global atomic adds over
`group_ids`.

Goal2785 adds a prepared/presegmented row-offset path. If the caller already
has rows sorted by group plus `row_offsets`, Triton can reduce one group per
program without global atomic adds. This is a generic prepared-row contract, not
Barnes-Hut-specific force logic.

## What Changed

Updated:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`

Added:

- `run_triton_grouped_vector_sum_f64x2_by_offsets(...)`
- `_triton_grouped_vector_sum_f64x2_offsets_kernel(...)`
- optional `row_offsets` handling in `grouped_vector_sum_2d_partner_columns(...)`
- metadata:
  - `v2_5_triton_presegmented_offsets_used`
  - `v2_5_triton_adapter_kernel`
  - `v2_5_triton_global_atomic_add_used`

## Boundary

This goal authorizes:

- a generic presegmented row-offset vector-sum adapter path;
- atomics-free Triton reduction when caller-supplied rows are already grouped;
- same-contract comparison against the Torch scatter-add branch and the old
  Triton atomic branch.

This goal does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- embedding Barnes-Hut or force-law logic into the engine or partner primitive.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2785_presegmented_vector_sum_triton_offsets_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 7 tests in 0.030s
OK (skipped=2)

py_compile with `PYTHONPYCACHEPREFIX=scratch\pycache_goal2785_consensus2`

OK
```

Pod validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01
Work clone: /root/rtdl_goal2785_work

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2785_presegmented_vector_sum_triton_offsets_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 7 tests in 2.270s
OK
```

Pod timing artifact:

`docs/reports/goal2785_pod_artifacts/goal2785_presegmented_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json`

| Rows | Groups | Rows/group | Triton offsets sec | Triton atomic sec | Torch scatter sec | Offsets / Torch | Offsets / Atomic |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8,192 | 512 | 16 | 0.003278763 | 0.003615890 | 0.000224164 | 14.627x | 0.907x |
| 262,144 | 4,096 | 64 | 0.003516122 | 0.003834186 | 0.000541145 | 6.498x | 0.917x |
| 1,048,576 | 8,192 | 128 | 0.004123017 | 0.004153255 | 0.000966038 | 4.268x | 0.993x |

Correctness matched Torch within double precision for all rows.

## Decision

`accept-with-boundary`

The offsets path is accepted as a generic prepared-row contract and a small
implementation improvement over the atomic Triton preview. It is not promoted
as the selected vector-sum performance path because Torch remains substantially
faster on the measured dense shapes.
