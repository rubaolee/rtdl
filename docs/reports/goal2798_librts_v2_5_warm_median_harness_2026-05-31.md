# Goal2798 - LibRTS v2.5 Warm Median Harness

Date: 2026-05-31

## Purpose

Goal2798 closes the LibRTS `needs_warm_median_harness` gap in the v2.5 tiered
benchmark manifest.

LibRTS is now a Tier C RT-core no-regression track in v2.5. That means the
correct work is to keep the generic `AABB_INDEX_QUERY_2D` prepared OptiX count
path measurable and reproducible, not to force a partner continuation or claim
Triton parity for a count-only native query.

## What Changed

Added:

- `scripts/goal2798_librts_v25_warm_median_harness.py`
- `tests/goal2798_librts_v25_warm_median_harness_test.py`
- pod artifacts under `docs/reports/goal2798_pod_artifacts/`

Updated:

- `src/rtdsl/v2_5_triton_app_migration.py`

The harness prepares once and times warm repeated native queries:

- `rt.prepare_optix_aabb_index_2d(...)`
- `rt.prepare_optix_aabb_point_queries_2d(...)`
- `rt.prepare_optix_aabb_box_queries_2d(...)`
- `prepared.count_prepared_queries(...)`

The CPU reference is used only as a correctness oracle. The measured RTDL path
remains the generic app-agnostic `AABB_INDEX_QUERY_2D` primitive.

## Pod Evidence

Artifact:

- `docs/reports/goal2798_pod_artifacts/librts_v25_warm_median_optix_4096_2048.json`

Pod:

- Host: `root@69.30.85.171`, port `22167`, key:
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- GPU: NVIDIA RTX A5000, driver `570.211.01`, memory `24564 MiB`.
- OptiX library: `/root/rtdl_goal2785_work/build/librtdl_optix.so`.

Command:

```text
PYTHONPATH=src:. python3 scripts/goal2798_librts_v25_warm_median_harness.py \
  --box-count 4096 \
  --query-count 2048 \
  --seed 2798 \
  --warmup 3 \
  --repeat 9 \
  --output docs/reports/goal2798_pod_artifacts/librts_v25_warm_median_optix_4096_2048.json
```

Result:

| Operation | Expected CPU Count | OptiX Count | Match | Warm Median ms |
| --- | ---: | ---: | --- | ---: |
| `point_contains` | 371793 | 371793 | yes | 0.840296 |
| `range_contains` | 255739 | 255739 | yes | 0.864155 |
| `range_intersects` | 553819 | 553819 | yes | 1.549192 |

Additional timing:

- CPU reference oracle: `1.796` seconds.
- OptiX scene preparation: `0.420` seconds.

These numbers are internal no-regression harness evidence, not a public speedup
claim.

## Manifest Update

The v2.5 tiered benchmark manifest now records:

- `librts_spatial_index.canonical_harness_status`:
  `ready_with_goal2798_warm_median_harness`
- `librts_spatial_index.pod_evidence_status`:
  current Goal2798 OptiX warm median evidence for all three
  `AABB_INDEX_QUERY_2D` count operations.

## Decision

`accept-with-boundary`

Goal2798 accepts LibRTS as having a v2.5 warm/median no-regression harness for
the generic prepared OptiX AABB count path. It does not convert LibRTS into a
partner-parity benchmark, and it does not claim paper reproduction.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- Triton speedup claims;
- true zero-copy claims;
- paper-reproduction claims;
- v2.5 release readiness claims.

This is Tier C no-regression harness evidence, not a public speedup claim.

## Validation

Local Windows validation:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  scripts\goal2798_librts_v25_warm_median_harness.py \
  tests\goal2798_librts_v25_warm_median_harness_test.py \
  src\rtdsl\v2_5_triton_app_migration.py

OK

PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2798_librts_v25_warm_median_harness_test.Goal2798LibRTSV25WarmMedianHarnessTest.test_harness_uses_prepared_optix_aabb_queries \
  tests.goal2798_librts_v25_warm_median_harness_test.Goal2798LibRTSV25WarmMedianHarnessTest.test_manifest_records_goal2798_warm_median_status \
  tests.goal2723_v2_5_tiered_benchmark_manifest_test \
  tests.goal2736_tier_a_primitive_first_plan_alignment_test \
  tests.goal2795_v2_5_tier_label_reconciliation_test

Ran 15 tests
OK
```

Full Goal2798 validation after the Gemini review and consensus file were added:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2798_librts_v25_warm_median_harness_test \
  tests.goal2723_v2_5_tiered_benchmark_manifest_test \
  tests.goal2736_tier_a_primitive_first_plan_alignment_test \
  tests.goal2795_v2_5_tier_label_reconciliation_test

Ran 17 tests
OK
```
