# Goal2795 - v2.5 Tier Label Reconciliation

Date: 2026-05-31

## Purpose

Goal2795 closes the remaining tier-label drift called out in the Goal2773
Claude review. The issue was not algorithmic: it was a planning precision bug.
The v2.5 benchmark manifest was using Tier A too broadly for two rows:

- `librts_spatial_index` is a count-only RT/AABB baseline with no partner
  continuation phase, so it behaves as Tier C no-regression evidence.
- `spatial_rayjoin` has a Tier A count/parity path, but row/overlay output is
  deferred Tier B continuation work.

This goal makes those boundaries machine-checkable in the manifest validator and
tests.

## Changes

Updated:

- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2723_v2_5_tiered_benchmark_manifest_test.py`
- `tests/goal2736_tier_a_primitive_first_plan_alignment_test.py`

Added:

- `tests/goal2795_v2_5_tier_label_reconciliation_test.py`

## Manifest Changes

| App | Previous Label | New Label / Boundary |
| --- | --- | --- |
| `librts_spatial_index` | Tier A, count-only optional Triton summary | Tier C `rt_core_aabb_no_partner_parity`; RT AABB count no-regression only; no required partner operations. |
| `spatial_rayjoin` | Tier A count/parity with vague row-heavy wording | Tier A for count/parity only; row/overlay modes are explicitly deferred Tier B continuation work. |

The v2.5 tier counts are now:

- Tier A: 3
- Tier B: 4
- Tier C: 3

The validator rejects a regression where:

- `librts_spatial_index` is not Tier C;
- `librts_spatial_index` requires partner operations;
- `librts_spatial_index` is not framed as no-regression evidence;
- `spatial_rayjoin` does not split Tier A count/parity from deferred Tier B
  row/overlay work.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- release readiness;
- treating RT-core-only baselines as partner-continuation benchmarks;
- claiming Spatial RayJoin row/overlay partner parity before a device-resident
  continuation path is designed and measured.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\v2_5_triton_app_migration.py tests\goal2723_v2_5_tiered_benchmark_manifest_test.py tests\goal2736_tier_a_primitive_first_plan_alignment_test.py tests\goal2795_v2_5_tier_label_reconciliation_test.py` passed.
- `py -3 -m unittest tests.goal2723_v2_5_tiered_benchmark_manifest_test tests.goal2736_tier_a_primitive_first_plan_alignment_test tests.goal2795_v2_5_tier_label_reconciliation_test tests.goal2676_v2_5_triton_partner_pivot_test tests.goal2730_triangle_counting_v2_5_primitive_first_plan_test tests.goal2783_v2_5_app_migration_selection_guidance_test` passed:
  31 tests.

Pod clean-check validation:

- Host: `root@69.30.85.171`, port `22167`, key:
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Checkout: `/root/rtdl_goal2785_work`.
- Commit: `7b8e409e61fa401f06ef3c8f848ab7b1a0b7cc6b`.
- Command:
  `PYTHONPATH=src:. python3 -m unittest tests.goal2723_v2_5_tiered_benchmark_manifest_test tests.goal2736_tier_a_primitive_first_plan_alignment_test tests.goal2795_v2_5_tier_label_reconciliation_test tests.goal2676_v2_5_triton_partner_pivot_test tests.goal2730_triangle_counting_v2_5_primitive_first_plan_test tests.goal2783_v2_5_app_migration_selection_guidance_test`.
- Result: 31 tests passed on Python 3.12.3.
