# Goal4036 Partition Component Preview vs Grouped-Stream Timing

Date: 2026-06-08

## Purpose

Goal4036 compares the Goal4035 partition component-label CuPy preview against the current v2.8 grouped-stream front door.

This is a route-selection experiment for fixed-radius graph components. It asks whether the new `device_bounded_offsets` plus `cupy_safe_full` partition path should replace the existing prepared grouped-stream route.

Pod evidence was collected from:

`ssh root@213.173.108.27 -p 15138 -i id_ed25519_rtdl_codex`

Git head on the pod:

`ee2405b3`

Artifact:

`docs/reports/goal4036_partition_component_preview_vs_grouped_stream_timing_pod.json`

## Results

`grouped_prepare_run / preview_one_shot` greater than `1.0x` means the partition preview is faster for warmed one-shot execution. `grouped_prepared_run / preview_repeated_run` less than `1.0x` means grouped-stream is faster after preparation.

| Profile | Points | Preview One-Shot Warmed (s) | Grouped Prepare+Run (s) | One-Shot Ratio | Preview Repeated Min (s) | Grouped Prepared Min (s) | Repeated Ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d_1024 | 1,024 | 0.008502 | 1.097899 | 129.138x | 0.008524 | 0.000507 | 0.060x |
| road3d_1024 | 1,024 | 0.031158 | 0.012171 | 0.391x | 0.008366 | 0.000349 | 0.042x |
| clustered3d_2048 | 2,048 | 0.016924 | 0.041279 | 2.439x | 0.014379 | 0.000698 | 0.049x |
| road3d_2048 | 2,048 | 0.013411 | 0.021505 | 1.604x | 0.013366 | 0.000345 | 0.026x |
| clustered3d_4096 | 4,096 | 0.023857 | 0.060747 | 2.546x | 0.023697 | 0.000883 | 0.037x |
| road3d_4096 | 4,096 | 0.024046 | 0.042092 | 1.750x | 0.023599 | 0.000350 | 0.015x |
| clustered3d_8192 | 8,192 | 0.046579 | 0.106494 | 2.286x | 0.045154 | 0.001068 | 0.024x |
| road3d_8192 | 8,192 | 0.044021 | 0.104309 | 2.370x | 0.044119 | 0.000359 | 0.008x |

Every row had matching component-size signatures against the grouped-stream route.

## Interpretation

The partition path is now useful, but not as a universal replacement.

- For warmed one-shot execution, the partition preview wins 7 of 8 rows in this probe.
- For repeated queries over a prepared scene, the current grouped-stream route remains much faster.
- Therefore, `partition_convergence_hybrid` should remain a candidate route, not the default.

The next major improvement should not be more Python-side partition logic. It should be a prepared/native partition route that keeps the partition summary and component continuation resident across repeated queries, or a route selector that exposes the one-shot vs prepared-reuse tradeoff explicitly without hidden dispatch.

## Boundary

This artifact compares internal v2.8 candidate routes. It does not promote `partition_convergence_hybrid`, authorize public speedup wording, authorize broad RT-core wording, authorize whole-app benchmark wording, authorize release wording, authorize hidden dispatch or automatic partner selection, authorize app-specific native-engine logic, or authorize true-zero-copy wording.

