# Phoenix V3 M41 Grouped-Reduction Serious Free Local Intake

Date: 2026-06-23
Status: `m41_serious_free_local_contract_positive_paid_pod_blocked`

## Scope

This records the serious-scale free local run requested by Claude after the
small M41 CUDA smoke. It uses local Linux `192.168.1.20`, not paid POD. It is
not RT-hardware evidence and not release evidence.

## Command

```bash
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_serious_after_warmupfix_20260623_150500 \
  --variant all \
  --row-count 262144 \
  --group-count 1024 \
  --seed 20260623 \
  --warmup 2 \
  --repeat 5
```

Artifact:

`docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_serious_after_warmupfix_20260623_150500/`

## Result

- status: `grouped_reduction_m41_local_run_complete_not_release`
- failed checks: `0`
- `step2_local_runner_contract_candidate`: `true`
- `all_variant_vector_sum_signatures_allclose`: `true`
- `runtime_trunk_executes_end_to_end`: `true`
- `internal_device_residency_between_rtdl_phases`: `true`
- `hot_path_host_materialization`: `false`
- `adapter_counts_present`: `true`
- `adapter_row_count`: `262144`
- `adapter_group_count`: `1024`

Timing medians:

| Variant | Hot sec | Inclusive wall sec |
|---|---:|---:|
| CPU NumPy same-contract control | 0.000160984 | 0.001403054 |
| Legacy Numba one-shot grouped vector sum | 0.001117234 | 0.193935999 |
| Productized prepared-execution runner | 0.000323261 | 0.003671369 |

Computed comparisons:

| Comparison | Ratio |
|---|---:|
| runner vs legacy hot | 3.456135x |
| runner vs legacy wall | 52.823894x |
| runner vs CPU hot | 0.498000x |

## Interpretation

The contract result is positive: the productized runner executes end-to-end,
keeps RTDL-owned internal residency, avoids hot-path host materialization, and
matches outputs by allclose.

The performance-readiness result is blocked: CPU NumPy remains faster than the
productized CUDA runner on the hot path at the serious local scale. Numba also
reported low GPU occupancy (`grid size 4`).

Therefore M41 should not request paid POD now. The likely next engineering
question is whether the generic grouped-reduction runner needs a different
occupancy/segmentation strategy, or whether grouped reduction should remain a
contract-positive but performance-blocked second family while Step 2 moves to a
different family.

## Claim Boundary

This intake does not authorize release, all-app POD spend, paid focused POD
spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy claims,
or broad V3-over-V2 claims.

## Local Matrix

Full `v3_rebuild` after the serious local run and harness fixes:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 120
Ran 626 tests in 77.865s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_serious_local_20260623_150330.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_serious_local_20260623_150330.stderr.txt
```

## Goal-Level Decision Audit

Decision: treat the serious local grouped-reduction result as contract-positive
but paid-POD-blocked.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be quoting the runner-vs-legacy speedup while
   hiding runner-vs-CPU hot `0.498x`.

3. Was there another path?

   Yes. Request paid POD after the contract pass. That would violate Claude's
   condition and likely waste money.

4. Can I now try a different path that actually solves the problem?

   Yes. Send this serious result for review, block paid POD for grouped
   reduction unless review says otherwise, and either improve the generic
   grouped-reduction occupancy path or select another Step-2 family.
