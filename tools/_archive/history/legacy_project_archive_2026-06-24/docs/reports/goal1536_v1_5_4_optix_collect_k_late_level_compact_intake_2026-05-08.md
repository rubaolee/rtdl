# Goal 1536: OptiX COLLECT_K_BOUNDED Late-Level Compact Intake

## Verdict

Accepted as measured implementation evidence for extending the env-gated parallel compact path to late large merge levels. The default path remains unchanged unless `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1` is set.

This is still experimental `COLLECT_K_BOUNDED` evidence. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.

## Source Change

- `src/native/optix/rtdl_optix_api.cpp` now applies the existing materialize/mark/compact pair merge when `output_segment_capacity >= 65536`, not only at the final level.
- `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py` records the stricter env-gated topology:
  - `4097` stays on the default one-kernel merge path.
  - `65537` uses compact for the last two large levels.
  - `131072` uses compact for the last two large levels, including the two-pair level 3 and final level 4.
- The default non-env topology is unchanged.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Git commit: `58e82b3dfaf0b5ac59d8397eb1b0d771eabf3c2e`
- Env: `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`
- Counts: `4097`, `65537`, `131072`
- Repeats: `5`

## Before/After

| Candidate rows | Baseline native total ms | Final-compact native total ms | Late-level compact native total ms | Late compact vs baseline | Late compact vs final compact | Baseline merge sync ms | Final-compact merge sync ms | Late-level compact merge sync ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 1.526860 | 1.388150 | 1.645010 | -7.74% | -18.50% | 0.339783 | 0.003740 | 0.268451 |
| 65537 | 79.377400 | 30.245900 | 24.060700 | 69.69% | 20.45% | 67.207700 | 15.934500 | 9.792510 |
| 131072 | 180.287000 | 42.281200 | 32.583600 | 81.93% | 22.94% | 156.370000 | 18.225900 | 8.518870 |

## Interpretation

The late-level compact extension is the strongest long-count result so far. For `131072` candidates, native total time is now about `32.58 ms`, down from `180.29 ms` in the original accepted baseline and `42.28 ms` in the final-only compact path.

The small `4097` case regresses because the threshold deliberately leaves it on the default one-kernel merge path, and measured run-to-run overhead dominates this short workload. This is acceptable for the current long-workload priority, but the env-gated path should not be marketed as a short-workload speedup.

The remaining large-count time is now dominated more by tile sort (`23.40 ms` for `131072`) than merge sync (`8.52 ms`). The next high-value work is likely tile-sort optimization or applying compact selectively only where it is beneficial.

## Claim Boundary

This evidence is env-gated and experimental. Do not promote `COLLECT_K_BOUNDED` to stable, do not claim public speedups, and do not claim whole-app acceleration from this packet alone.

## Artifacts

- `docs/reports/goal1536_v1_5_4_optix_collect_k_late_level_compact_probe_2026-05-08.json`
- `docs/reports/goal1536_v1_5_4_optix_collect_k_late_level_compact_probe_2026-05-08.jsonl`
- `docs/reports/goal1536_v1_5_4_optix_collect_k_late_level_compact_probe_2026-05-08.md`
- `docs/reports/goal1536_v1_5_4_optix_collect_k_late_level_compact_intake_2026-05-08.md`

