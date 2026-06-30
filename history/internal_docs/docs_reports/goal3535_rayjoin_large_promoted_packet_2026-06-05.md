# Goal3535 Larger RayJoin Promoted-Path Packet

Date: 2026-06-05

Status: internal A5000 scale evidence. This report does not authorize release, public speedup wording, RayJoin paper reproduction claims, broad RT-core speedup claims, true zero-copy claims, whole-app acceleration claims, or app-specific native-engine shortcuts.

## Purpose

Goal3534 showed that the old v2.3-compatible RayJoin scalar contracts are basically parity in v2.8. That still left the important v2.8 question open: do the promoted RayJoin contracts stay fast when we move beyond tiny checked-in CDB fixtures?

Goal3535 answers that with deterministic generated CDB square-grid pairs. These are not RayJoin paper inputs. They are larger, non-empty, reproducible stress inputs for the generic RTDL contracts: prepared point/shape membership, segment intersection counts, shape-pair relation columns, grouped relation continuations, bounds/witness payloads, and overlay tile-task continuations.

## Evidence

Tracked artifacts:

- `docs/reports/goal3535_rayjoin_large_promoted_packet_a5000/grid32/summary.json`
- `docs/reports/goal3535_rayjoin_large_promoted_packet_a5000/grid64/summary.json`
- `docs/reports/goal3535_rayjoin_large_promoted_packet_a5000/grid128/summary.json`

Run facts:

- Pod: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- RTDL commit: `2345dd339861c0a7a69577e8b167c576b1e4d18d`
- Generated CDB pair: left/right square grids, right offset by `(0.5, 0.5)`, side length `1.5`, spacing `2.0`
- Repeats: 3 where supported
- Generated CDB files were not committed; only compact JSON evidence was tracked.

## Results

| Grid | Shapes per side | Relation rows | Supported overlay rows | Relation columns sec | Grouped count sec | Bounds payload sec | Witness payload sec | Overlay stream sec | Tile planner sec | Tile executor sec |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 1,024 | 3,969 | 1,024 | 0.001211 | 0.000180 | 0.000970 | 0.000765 | 0.001142 | 0.004849 | 0.000823 |
| 64 | 4,096 | 16,129 | 4,096 | 0.002074 | 0.000197 | 0.000978 | 0.000799 | 0.009928 | 0.017930 | 0.000964 |
| 128 | 16,384 | 65,025 | 16,384 | 0.030991 | 0.000194 | 0.005333 | 0.000850 | 0.029844 | 0.078878 | 0.001010 |

Count/parity route timings on the same generated inputs:

| Grid | PIP prepared count sec | LSI left-id dense count sec | Overlay active-count sec |
| ---: | ---: | ---: | ---: |
| 32 | 0.000501 | 0.059127 | 0.382719 |
| 64 | 0.000371 | 0.059600 | 0.349271 |
| 128 | 0.000963 | 0.061621 | 0.368266 |

Correctness:

- Overlay positive row-count match: `true` at all three scales
- Overlay total area absolute error: `0.0` at all three scales
- Overlay max relation absolute error: `0.0` at all three scales

## Interpretation

This larger packet is a much better RayJoin v2.8 story than the old `1.096x` blended row:

- The promoted relation stream is real: 65,025 relation rows at grid 128.
- Generic grouped-count continuation is excellent at these scales, staying around `0.0002s`.
- Witness payload continuation stays under `0.001s` even at 65,025 relation rows.
- Tile execution stays near `0.001s`; the executor itself is not the bottleneck for this generated simple-square workload.

The weak rows are now precise:

- `rayjoin_count_parity_overlay_seed_active_count` remains around `0.35s` to `0.38s` even as the generated grid grows. That route is not the promoted headline.
- `rayjoin_overlay_area_device_tile_planner_cdb_pair` grows to `0.078878s` at grid 128. This is the next real optimization target if RayJoin remains top priority.
- `rayjoin_relation_columns_cdb_pair` grows to `0.030991s` at grid 128. It is acceptable but no longer invisible; future work should look at warm resident relation-stream reuse and larger repeated-query packets.

## What This Means For RayJoin

The old v2.3-compatible scalar contracts are parity. The new v2.8 promoted contracts are where the interesting work is:

- v2.8 now has a usable, scalable relation/payload/overlay continuation substrate that v2.3 did not have.
- The strongest current claim is internal engineering progress, not paper-level performance.
- The next engineering move should target the two real bottlenecks visible here: overlay active-count and device tile-task planning.

## Verdict

`accept-with-boundary`

Goal3535 finishes the requested next step: larger-scale promoted RayJoin evidence exists, is tracked, and is more informative than the old blended table. It also gives a clear next optimization target instead of hand-waving about generic "RayJoin" speed.
