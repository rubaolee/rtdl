# Claude Recorded Review: Phoenix V3 M41 Serious Free Local Grouped Reduction

Date: 2026-06-23
Raw review:
`docs/reviews/claude_phoenix_v3_m41_grouped_reduction_serious_free_local_review_2026-06-23.raw.md`

Verdict: `accept_contract_positive_paid_pod_blocked`

## Meaning

Claude accepted the serious-scale free local result as genuine contract-positive
evidence. It also explicitly blocked paid POD for grouped reduction.

The blocking reason is runner-vs-CPU hot-path inversion:

```text
runner_vs_cpu_hot_speedup: 0.4979998501868343
```

The runner beats the legacy Numba one-shot path, but not CPU NumPy on the hot
path at the serious free-local shape. Numba also reports low occupancy
(`grid size 4`).

## Accepted Facts

- `failed_checks`: `0`
- `step2_local_runner_contract_candidate`: `true`
- `all_variant_vector_sum_signatures_allclose`: `true`
- `runtime_trunk_executes_end_to_end`: `true`
- `internal_device_residency_between_rtdl_phases`: `true`
- `hot_path_host_materialization`: `false`
- `adapter_counts_present`: `true`
- `adapter_row_count`: `262144`
- `adapter_group_count`: `1024`

## Required Follow-Up

Claude recommends closing M41 as:

```text
contract-positive, performance-blocked
```

Before any further grouped-reduction experiment:

1. Diagnose why the Numba grouped-reduction launch uses grid size `4`.
2. Decide explicitly between:
   - Path A: one bounded shape experiment after root-cause diagnosis; or
   - Path B: switch Step-2 performance evidence to another family.

No paid POD is authorized for grouped reduction unless a later externally
reviewed free-local result clears the CPU-hot blocker.

## Non-Authorization Block

This recorded review does not authorize release, all-app POD spend, paid
focused POD spend, public speedup wording, V4/embedding/C-ABI work,
true-zero-copy claims, or broad V3-over-V2 claims.
