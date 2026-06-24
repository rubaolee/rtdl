# Goal4034 Partition Device-Pair Preview Timing

Date: 2026-06-08

## Purpose

Goal4034 times the CuPy `device_bounded_offsets` pair-enumeration preview from Goal4032 against the older CuPy preview mode that enumerates near partition pairs on the host.

This measures one bottleneck inside the `partition_convergence_hybrid` candidate path: bounded occupied-partition pair enumeration for fixed-radius graph components. It does not time the full grouped-stream application route and does not promote the candidate strategy.

Pod evidence was collected from:

`ssh root@213.173.108.27 -p 15138 -i id_ed25519_rtdl_codex`

Git head on the pod:

`b1cf8d5b`

Artifact:

`docs/reports/goal4034_partition_device_pair_preview_timing_pod.json`

## Results

The timing script warms the RawKernel before timing the device mode. Pair capacity is discovered once by the host preview and is not included in either timed row. Every timed row passed the Goal4019 same-contract validator.

| Profile | Points | Partition Pairs | Host Pair Enumeration Median (s) | Device-Bounded Offsets Median (s) | Device / Host Median Speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| clustered3d_2048 | 2,048 | 171,392 | 2.573414 | 0.011184 | 230.096x |
| road3d_2048 | 2,048 | 19,728 | 2.097370 | 0.009977 | 210.216x |
| clustered3d_4096 | 4,096 | 392,329 | 5.202382 | 0.017939 | 290.000x |
| road3d_4096 | 4,096 | 39,790 | 4.276161 | 0.016723 | 255.710x |

## Interpretation

This validates the design direction: the near-partition pair enumeration bottleneck should not remain a Python/host loop. A bounded device producer can remove seconds of host work at only a few thousand points.

It also narrows the next engineering target. The remaining performance producer should make the whole partition-summary path device-resident or native enough that pair capacity discovery, partition-key materialization, and final component continuation do not reintroduce host bottlenecks.

## Boundary

This artifact compares CuPy preview pair-enumeration modes only.

It does not:

- promote `partition_convergence_hybrid`;
- authorize public speedup wording;
- authorize broad RT-core wording;
- authorize whole-app benchmark wording;
- authorize release wording;
- authorize hidden dispatch or automatic partner selection;
- authorize app-specific native-engine logic;
- authorize true-zero-copy wording.

The next real performance step is a full partition-summary producer path with no host pair enumeration dependency, followed by large-scale same-contract timing against the current grouped-stream route.

