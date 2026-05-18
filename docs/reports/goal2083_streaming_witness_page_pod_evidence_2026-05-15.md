# Goal2083 Streaming Witness Page Pod Evidence

Date: 2026-05-15

Pod:

- SSH: `root@213.192.2.122 -p 40153`
- Key that authenticated: `C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: NVIDIA GeForce RTX 3090, driver 580.126.20, 24576 MiB
- Commit base: `2efd4b84e8ac8e0f15c6dc32884e49e0dec6d669`
- Goal2081 overlay files were copied onto the pod before validation/timing.

## Purpose

Goal2079 showed that the old `segment_polygon_anyhit_rows` v2.0 path was slower when it returned full Python witness rows. Goal2081 added a bounded streaming exact-witness page adapter that keeps exact witness IDs in partner-owned columns instead of materializing Python row dictionaries.

Goal2083 records the first pod timing for that fix.

## Results

| count | v1.8 native OptiX rows sec | old v2 full Python rows sec | new v2 streaming witness columns sec | old v2 / v1.8 | new v2 / v1.8 | new v2 / old v2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 0.113774 | 0.136408 | 0.001387 | 1.199x | 0.012x | 0.010x |
| 8192 | 0.433377 | 0.086084 | 0.001301 | 0.199x | 0.003x | 0.015x |
| 16384 | 1.905528 | 0.340985 | 0.001421 | 0.179x | 0.001x | 0.004x |

Artifacts:

- `docs/reports/goal2081_streaming_witness_page_pod/goal2081_streaming_witness_page_perf_pod_4096_cupy_capacity.json`
- `docs/reports/goal2081_streaming_witness_page_pod/goal2081_streaming_witness_page_perf_pod_8192_cupy_capacity.json`
- `docs/reports/goal2081_streaming_witness_page_pod/goal2081_streaming_witness_page_perf_pod_16384_cupy_capacity.json`
- `docs/reports/goal2081_streaming_witness_page_pod/progress.log`
- `docs/reports/goal2081_streaming_witness_page_pod/nohup.out`

## Interpretation

The weak row was not fundamentally an RT traversal problem. It was an output-contract problem.

The old v2 full-row path had to convert exact witnesses into Python dictionaries. At 4096 rows, that path was slower than v1.8 native rows. The new path keeps exact witness IDs in CuPy columns, pages them, and avoids Python row-table materialization. That converts the row from slower-than-v1.8 into a strong speedup candidate.

The native engine remains app-agnostic:

- Native contract: generic ray/primitive candidate witness pairs.
- App-layer exact filter: CuPy RawKernel segment/triangle exact filtering.
- Output contract: bounded partner-owned witness ID columns.

## Boundary

This evidence supports updating the v2.0 performance story for the streaming witness-column contract. It does not mean the old full-Python-row contract is fast, and it does not authorize broad whole-app speedup wording by itself.

Claim boundary:

- `v2_0_release_authorized`: false
- `whole_app_speedup_claim_authorized`: false
- `native_exact_row_semantics_authorized`: false
- `app_exact_row_semantics_authorized`: true
- `full_python_row_table_materialization_avoided`: true
- external review is required before using this as final release evidence.

## Validation

Pod validation before timing:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2081_streaming_witness_page_adapter_test \
  tests.goal1997_generic_witness_pair_paging_adapter_test \
  tests.goal1861_segment_polygon_hitcount_device_count_columns_test
```

Result: 9 tests passed.
