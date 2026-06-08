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

`grouped_prepare_run / preview_one_shot` greater than `1.0x` means the partition preview is faster for warmed one-shot execution. `grouped_prepared_run / preview_repeated_run` less than `1.0x` means grouped-stream is faster after preparation. `reuse_min` is the repeated component continuation time when the partition summary is prepared once and passed back through `partition_summary=`.

| Profile | Points | Preview One-Shot Warmed (s) | Grouped Prepare+Run (s) | One-Shot Ratio | Preview Repeated Min (s) | Reuse Min (s) | Grouped Prepared Min (s) | Grouped / Reuse |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d_1024 | 1,024 | 0.008386 | 1.101381 | 131.341x | 0.008447 | 0.001697 | 0.000515 | 0.303x |
| road3d_1024 | 1,024 | 0.008562 | 0.011997 | 1.401x | 0.008711 | 0.001786 | 0.000342 | 0.192x |
| clustered3d_2048 | 2,048 | 0.013986 | 0.037876 | 2.708x | 0.013344 | 0.002805 | 0.000695 | 0.248x |
| road3d_2048 | 2,048 | 0.013205 | 0.021368 | 1.618x | 0.013117 | 0.003138 | 0.000345 | 0.110x |
| clustered3d_4096 | 4,096 | 0.023779 | 0.061551 | 2.588x | 0.023639 | 0.005522 | 0.000878 | 0.159x |
| road3d_4096 | 4,096 | 0.023587 | 0.042247 | 1.791x | 0.023387 | 0.005874 | 0.000353 | 0.060x |
| clustered3d_8192 | 8,192 | 0.045879 | 0.103252 | 2.251x | 0.044661 | 0.010670 | 0.001074 | 0.101x |
| road3d_8192 | 8,192 | 0.044553 | 0.085388 | 1.917x | 0.044047 | 0.011622 | 0.000370 | 0.032x |

Every row had matching component-size signatures against the grouped-stream route.

## Interpretation

The partition path is now useful, but not as a universal replacement.

- For warmed one-shot execution, the partition preview wins 7 of 8 rows in this probe.
- Explicit `partition_summary=` reuse improves the partition repeated path by about 4x-5x versus rebuilding the partition summary.
- For repeated queries over a prepared scene, the current grouped-stream route still remains much faster.
- Therefore, `partition_convergence_hybrid` should remain a candidate route, not the default.

The next major improvement should not be more Python-side partition logic. It should be a prepared/native partition route that keeps the partition summary and component continuation resident across repeated queries, or a route selector that exposes the one-shot vs prepared-reuse tradeoff explicitly without hidden dispatch.

## Boundary

This artifact compares internal v2.8 candidate routes. It does not promote `partition_convergence_hybrid`, authorize public speedup wording, authorize broad RT-core wording, authorize whole-app benchmark wording, authorize release wording, authorize hidden dispatch or automatic partner selection, authorize app-specific native-engine logic, or authorize true-zero-copy wording.
