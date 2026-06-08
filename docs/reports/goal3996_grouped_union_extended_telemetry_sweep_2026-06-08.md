# Goal3996 Grouped-Union Extended Telemetry Sweep

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3996 uses the Goal3992 extended telemetry counters to sweep grouped-union execution modes on the RTX 4000 Ada pod. The purpose is diagnostic: decide whether the next RT-DBSCAN improvement can come from a simple execution-mode toggle, or whether RTDL needs the larger generic dense grouped-union primitive described in Goal3990.

Artifact: `docs/reports/goal3996_grouped_union_extended_telemetry_sweep_pod.json`

## Pod Setup

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `11b02a508296ad7a87044900e64285fb1db93eab`
- Dataset/profile: `clustered3d`
- Radius: `0.5`
- Repeats: `3`
- Modes:
  - same-root culling on/off
  - intersection direct-side-effect on/off

## Native Median Summary

All timings below are diagnostic telemetry timings. They include extended telemetry atomics and must not be used as public speedup evidence.

| Point count | Mode | Native median sec | Ratio vs default | Radius candidates | Same-root culled | Direct hits | Reported candidates | Atomic attempts | Atomic successes |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | same-root on, direct off | 0.005041 | 1.000x | 3,483,897 | 3,473,551 | 0 | 10,346 | 11,170 | 4,095 |
| 4,096 | same-root off, direct off | 0.006583 | 1.306x | 3,483,897 | 0 | 0 | 3,483,897 | 10,160 | 4,095 |
| 4,096 | same-root on, direct on | 0.005043 | 1.000x | 3,483,897 | 3,473,717 | 10,180 | 0 | 10,838 | 4,095 |
| 4,096 | same-root off, direct on | 0.005340 | 1.059x | 3,483,897 | 0 | 3,483,897 | 0 | 10,418 | 4,095 |
| 16,384 | same-root on, direct off | 0.026752 | 1.000x | 55,770,411 | 55,743,718 | 0 | 26,693 | 29,162 | 16,383 |
| 16,384 | same-root off, direct off | 0.031312 | 1.170x | 55,770,411 | 0 | 0 | 55,770,411 | 26,695 | 16,383 |
| 16,384 | same-root on, direct on | 0.025191 | 0.942x | 55,770,411 | 55,742,955 | 27,456 | 0 | 29,811 | 16,383 |
| 16,384 | same-root off, direct on | 0.026145 | 0.977x | 55,770,411 | 0 | 55,770,411 | 0 | 26,835 | 16,383 |
| 65,536 | same-root on, direct off | 0.289941 | 1.000x | 892,847,094 | 891,004,699 | 0 | 1,842,395 | 1,310,439 | 65,535 |
| 65,536 | same-root off, direct off | 0.335920 | 1.159x | 892,847,094 | 0 | 0 | 892,847,094 | 442,001 | 65,535 |
| 65,536 | same-root on, direct on | 0.287766 | 0.992x | 892,847,094 | 891,968,008 | 879,086 | 0 | 722,773 | 65,535 |
| 65,536 | same-root off, direct on | 0.294877 | 1.017x | 892,847,094 | 0 | 892,847,094 | 0 | 401,297 | 65,535 |

## Interpretation

The simple mode switches are exhausted:

- Same-root culling is still the right default. Disabling it reports every radius candidate and is slower at all measured sizes.
- Direct side effects are not a durable large win. They are roughly neutral at `65,536` points under instrumentation and remain only a mode-level variant, not a new primitive.
- The dominant cost is dense candidate enumeration and repeated root/culling work. At `65,536` points, the native route processes about `892.8M` radius-qualified candidates for only `65,535` successful component unions.

The next meaningful RTDL/runtime improvement therefore remains the generic dense grouped-union primitive direction:

- reduce or summarize dense fixed-radius candidate work,
- avoid repeated same-root root reads where a convergence policy permits it,
- expose explicit convergence/staleness/status metadata,
- preserve exact same-contract parity against the existing grouped-stream route before any promotion.

## Boundary

This is diagnostic telemetry evidence, not a performance optimization. It does not authorize release, public speedup wording, broad RT-core speedup wording, whole-app acceleration wording, paper reproduction, true-zero-copy wording, automatic partner/backend selection, or app-specific native-engine logic.
