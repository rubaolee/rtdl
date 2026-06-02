# Goal3007: Numba Grouped Arg Reducer L4 Pod Evidence

## Result

Status: pass.

Goal3007 validates the Goal3006 generic Numba grouped witness reducers on an
NVIDIA L4 pod from a clean Git checkout.

## Evidence

| Field | Value |
| --- | --- |
| Source commit | `a8933b1b20b5a98d388efa05a7b49cd69f65d87b` |
| Source dirty | `[]` |
| GPU | NVIDIA L4 |
| Compute capability | 8.9 |
| Numba | 0.65.1 |
| CUDA module | `numba_cuda/numba/cuda/__init__.py` |
| Artifact | `docs/reports/goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.json` |

## Cases

| Case | Rows | Groups | Argmin | Argmax | Argmin wall sec | Argmax wall sec |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| `tie_fixture` | 5 | 4 | pass | pass | 0.496389 | 0.187571 |
| `large_stream` | 1,000,000 | 4,096 | pass | pass | 0.197941 | 0.196282 |

The validated contracts are:

- `grouped_argmin_f64`: lowest score, then lowest `item_id`;
- `grouped_argmax_f64`: highest score, then lowest `item_id`;
- compact present-group outputs;
- dense per-group outputs;
- missing group ids;
- present counts;
- public adapter path for `grouped_argmax_f64_partner_columns(..., partner="numba")`.

## Boundary

The implementation is still preview-status partner continuation. It uses a
host-observed present-group compaction step. This is acceptable for the current
correctness/conformance goal, but it is not a true-zero-copy or performance
promotion.

This evidence does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Next Step

Use this primitive in a benchmark app wrapper that naturally needs per-group
witness selection, preferably Hausdorff or RTNN, while preserving the same
claim boundary until same-contract performance evidence exists.
