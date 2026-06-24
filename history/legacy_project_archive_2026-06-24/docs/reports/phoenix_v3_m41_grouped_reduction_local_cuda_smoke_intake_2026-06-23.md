# Phoenix V3 M41 Grouped-Reduction Local CUDA Smoke Intake

Date: 2026-06-23
Status: `m41_local_cuda_smoke_positive_not_release`

## Scope

This records the free local Linux CUDA smoke requested by Claude's M41 review.
It is not paid POD evidence, not RT-hardware evidence, not serious-scale
performance evidence, and not release evidence.

## Environment

Host: `192.168.1.20` / `lx1`

GPU:

```text
NVIDIA GeForce GTX 1070, driver 580.126.09, 8192 MiB
```

Python environment:

```text
Python 3.12.3
numpy: present
numba: present
cupy: present
rtdsl: provided through PYTHONPATH=src:.
```

## Command

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_after_hotfix_20260623_145500 \
  --variant all \
  --row-count 8192 \
  --group-count 128 \
  --seed 20260623 \
  --warmup 2 \
  --repeat 5 \
  --allow-non-serious-local-smoke
```

Local artifact:

`docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_after_hotfix_20260623_145500/`

## Result

- status: `grouped_reduction_m41_local_run_complete_not_release`
- failed checks: `0`
- `step2_local_runner_contract_candidate`: `true`
- `all_variant_vector_sum_signatures_allclose`: `true`
- `all_variant_vector_sum_signatures_hash_match`: `false`
- `runtime_trunk_executes_end_to_end`: `true`
- `internal_device_residency_between_rtdl_phases`: `true`
- `hot_path_host_materialization`: `false`
- `output_counts_match_requested`: `true`
- `adapter_counts_present`: `true`
- `adapter_row_count`: `8192`
- `adapter_group_count`: `128`

Timing medians:

| Variant | Hot sec | Inclusive wall sec |
|---|---:|---:|
| CPU NumPy same-contract control | 0.000010347 | 0.000106737 |
| Legacy Numba one-shot grouped vector sum | 0.001014929 | 0.197189649 |
| Productized prepared-execution runner | 0.000236898 | 0.002986178 |

Computed comparisons:

| Comparison | Ratio |
|---|---:|
| runner vs legacy hot | 4.284241x |
| runner vs legacy wall | 66.034123x |
| runner vs CPU hot | 0.043677x |

## Interpretation

The smoke closes Claude's P0 concern that the M41 packet had no real CUDA
execution. It also verifies the M36 carry-forward concern: adapter row/group
counts are present and match.

This is not a serious performance result:

- row count is intentionally small (`8192`);
- `--allow-non-serious-local-smoke` was used;
- Numba emitted a low-occupancy warning;
- CPU NumPy is faster than the runner on this tiny row count;
- the useful result is contract execution, not public speedup.

## Claim Boundary

This intake does not authorize release, all-app POD spend, paid focused POD
spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy claims,
or broad V3-over-V2 claims.

## Local Matrix

Full `v3_rebuild` after the smoke fixes:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 120
Ran 626 tests in 77.136s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_cuda_smoke_fixes_20260623_145328.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_cuda_smoke_fixes_20260623_145328.stderr.txt
```

## Goal-Level Decision Audit

Decision: run a free local CUDA smoke after fixing Claude's P1 harness findings.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be using the GTX 1070 smoke as RT hardware evidence
   or serious performance evidence.

3. Was there another path?

   Yes. Skip local CUDA and request paid POD. That would violate Claude's
   review and waste money.

4. Can I now try a different path that actually solves the problem?

   Yes. Submit the smoke intake for review and only then decide whether a
   serious focused POD request is justified.
