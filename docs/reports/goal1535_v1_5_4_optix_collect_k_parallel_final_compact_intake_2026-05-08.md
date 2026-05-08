# Goal 1535: OptiX COLLECT_K_BOUNDED Parallel Final Compact Intake

## Verdict

Accepted as measured implementation evidence for an env-gated OptiX `COLLECT_K_BOUNDED` final-level parallel compact path. The default path remains unchanged unless `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1` is set.

This does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.

## Source Change

- `src/native/optix/rtdl_optix_core.cpp` adds three row-width-2 final-level kernels:
  `collect_k_bounded_i64_row_width2_final_materialize`,
  `collect_k_bounded_i64_row_width2_final_mark_counts`, and
  `collect_k_bounded_i64_row_width2_final_compact`.
- `src/native/optix/rtdl_optix_api.cpp` wires the path behind `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`.
- `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py` records the stricter env-gated topology: three final kernels, no final device-to-device copy, and one final metadata field.
- `tests/goal1535_v1_5_4_optix_collect_k_parallel_final_compact_test.py` pins the source markers and default/env topology split.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Git commit: `78d22ac360df0f14e97f2f06c62a2cd5e86db10f`
- Env: `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`
- Counts: `4097`, `65537`, `131072`
- Repeats: `5`

## Before/After

| Candidate rows | Baseline native total ms | Batched-level native total ms | Parallel-final-compact native total ms | Improvement vs baseline | Improvement vs batched-level | Baseline merge sync ms | Batched-level merge sync ms | Parallel-final-compact merge sync ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 1.526860 | 1.482630 | 1.388150 | 9.08% | 6.37% | 0.339783 | 0.268560 | 0.003740 |
| 65537 | 79.377400 | 34.238100 | 30.245900 | 61.90% | 11.66% | 67.207700 | 20.177500 | 15.934500 |
| 131072 | 180.287000 | 52.834800 | 42.281200 | 76.55% | 19.97% | 156.370000 | 28.930000 | 18.225900 |

## Interpretation

The corrected final compact path solves the Goal1533 correctness problem by materializing a deterministic merged stream with duplicate ordering, marking unique rows, computing per-block counts, and compacting bounded output rows. It eliminates the expensive serial final merge level: in the clean pod run, the `131072` final level is no longer the dominant `10.7 ms` serial step.

The remaining long-count bottleneck is now level 3, where two large pair merges still use the one-active-thread pair merge. The next optimization should apply the same materialize/mark/compact idea to more than the final level, likely only when pair segment capacity is large enough to justify the extra kernels and host offset step.

## Claim Boundary

This is env-gated experimental evidence. Do not promote `COLLECT_K_BOUNDED` to stable, do not claim public speedups, and do not claim whole-app acceleration from this packet alone.

## Artifacts

- `docs/reports/goal1535_v1_5_4_optix_collect_k_parallel_final_compact_probe_2026-05-08.json`
- `docs/reports/goal1535_v1_5_4_optix_collect_k_parallel_final_compact_probe_2026-05-08.jsonl`
- `docs/reports/goal1535_v1_5_4_optix_collect_k_parallel_final_compact_probe_2026-05-08.md`
- `docs/reports/goal1535_v1_5_4_optix_collect_k_parallel_final_compact_intake_2026-05-08.md`

