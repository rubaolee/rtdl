# Phoenix V3 M41 Grouped-Reduction Second-Family Local Harness

Date: 2026-06-23
Status: `m41_grouped_reduction_second_family_local_harness_not_release`

## Purpose

M41 selects `grouped_vector_sum_2d` / grouped reduction as the second Step-2
family after M40 component-union. The goal is to test whether Phoenix V3 is
building a reusable runtime trunk across continuation families, not another
benchmark-app-specific route.

This is local harness work only. It does not authorize a new POD run.

## Why This Family

M35 identified grouped reduction as strong row-scoped evidence that lacked a
runner-callable core node. M36 added the generic prepared-session helper:

`run_grouped_vector_sum_2d_prepared_session`

M40 then supplied one positive focused probe for a different family:

`fixed_radius_graph_component_union`

Grouped reduction is therefore the right second local family because it is:

- a different primitive family from component-union;
- continuation-rich;
- already represented in the productized prepared-execution surface;
- generic and app-agnostic;
- a good test that M40 was not a one-family special case.

## Implementation

New harness:

`scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`

New test:

`tests/v3_phoenix_m41_grouped_reduction_harness_test.py`

Matrix registration:

`scripts/run_test_matrix.py`

The harness defines three variants:

| Variant | Role |
|---|---|
| `cpu_numpy_same_contract_grouped_vector_sum_control` | CPU same-contract correctness control |
| `legacy_numba_one_shot_grouped_vector_sum` | incumbent one-shot Numba grouped vector-sum route |
| `productized_prepared_execution_runner` | M36 helper through `run_grouped_vector_sum_2d_prepared_session` |

The harness emits:

- `runner_vs_legacy_hot_speedup`
- `runner_vs_legacy_wall_speedup`
- `runner_vs_cpu_hot_speedup`
- signature match status across all variants
- runner trunk flags
- internal residency and host-materialization flags
- no-release/no-public-claim flags

## Local Validation

Focused tests:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m41_grouped_reduction_harness_test tests.v3_phoenix_m39_component_union_harness_test tests.v3_release_wording_gate_test
Ran 14 tests
OK
```

Dry run:

```text
PYTHONPATH=src;. py -3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py --dry-run --output-dir build\m41_grouped_reduction_dry_run
failed_check_count: 0
status: grouped_reduction_m41_harness_ready_not_pod_run
selected variants: cpu control, legacy one-shot, productized runner
```

Full `v3_rebuild`:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 120
Ran 625 tests in 74.220s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_grouped_reduction_harness_20260623_144304.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_grouped_reduction_harness_20260623_144304.stderr.txt
```

## Current Boundaries

This report does not say grouped reduction is now a material V3 performance
win. It says the second-family local harness exists and is ready for strict
review after full matrix validation.

No claims are authorized:

- no V3 release
- no all-app POD spend
- no additional focused POD spend
- no public speedup wording
- no broad V3-over-V2 wording
- no V4, embedding, C ABI, or true-zero-copy work

## Goal-Level Decision Audit

Decision: choose grouped reduction as M41's second-family Step-2 local target.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be jumping from M40 into another POD run or into
   RayJoin/RTNN route tuning before proving a second generic continuation
   family locally.

3. Was there another path?

   Yes. RayJoin, RTNN, Triangle, and Hausdorff are possible Set-A app families,
   but grouped reduction is the most direct reusable continuation-family test
   because M35 and M36 already isolated its generic runtime gap.

4. Can I now try a different path that actually solves the problem?

   Yes. Use grouped reduction to test the same productized runner discipline on
   a second primitive family, with hot/wall comparisons and explicit claim
   boundaries before any paid benchmark work.

## Next

Claude reviewed this packet with verdict
`accept_with_caveats_before_cuda_smoke`. Codex applied the requested P1/P2
fixes, then ran a free local CUDA smoke. See:

- `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_second_family_local_harness_recorded_review_2026-06-23.md`
- `docs/reports/phoenix_v3_m41_grouped_reduction_local_cuda_smoke_intake_2026-06-23.md`

Do not request or spend paid POD until the smoke intake receives external
review and Codex+external consensus.
