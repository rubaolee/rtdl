# Goal 1587: OptiX Collect-K Runner-Produced Ada Validation

## Verdict

`goal1586_multi_session_validation_recorded`

The new Goal1586 multi-session runner completed a full three-session Ada validation pass from a clean committed pod checkout. This confirms the reusable runner can replace the prior manual multi-session process and preserves the same claim boundary.

## Scope

- Commit: `4443d9f0bdbf5c70218f423a6181b2a017093e70`
- Sessions: `3`
- Output prefix: `/tmp/goal1587_runner_full`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Pod checkout: `/root/rtdl_goal1545_pod`
- Compact JSON artifact: `docs/reports/goal1587_v1_5_4_optix_collect_k_runner_full_ada_summary_2026-05-08.json`

## Acceptance

Each nested Goal1579 session completed its focused tests and produced accepted baseline, alias, and candidate-preset artifacts. The aggregate targeted rows preserve the expected parity/topology outcomes for the tracked counts.

## Targeted Reruns

| Session | Count | Baseline ms | Alias ms | Candidate preset ms | Alias delta ms | Candidate delta ms | Payload copies baseline/alias/candidate |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 49153 | 0.221009 | 0.212162 | 0.211531 | -0.008847 | -0.009478 | 3/1/1 |
| 1 | 65536 | 0.214236 | 0.213295 | 0.212322 | -0.000941 | -0.001914 | 0/0/0 |
| 1 | 65537 | 0.285501 | 0.264781 | 0.265794 | -0.020720 | -0.019707 | 5/0/0 |
| 2 | 49153 | 0.219145 | 0.211531 | 0.214336 | -0.007614 | -0.004809 | 3/1/1 |
| 2 | 65536 | 0.211400 | 0.213525 | 0.211550 | 0.002125 | 0.000150 | 0/0/0 |
| 2 | 65537 | 0.282164 | 0.267156 | 0.266956 | -0.015008 | -0.015208 | 5/0/0 |
| 3 | 49153 | 0.219386 | 0.214346 | 0.212422 | -0.005040 | -0.006964 | 3/1/1 |
| 3 | 65536 | 0.212342 | 0.211661 | 0.211220 | -0.000681 | -0.001122 | 0/0/0 |
| 3 | 65537 | 0.282355 | 0.265092 | 0.265934 | -0.017263 | -0.016421 | 5/0/0 |

## Interpretation

The runner-produced evidence reinforces the same Ada conclusion as Goal1585:

- `49153` improved in all three alias sessions and all three candidate-preset sessions while reducing carry payload copies from `3` to `1`.
- `65537` improved in all three alias sessions and all three candidate-preset sessions while reducing carry payload copies from `5` to `0`.
- `65536` remains essentially neutral, as expected for an even-count case with no carry payload copy to remove.

This is stronger same-architecture evidence and better validation tooling, not a default-promotion decision.

## Claim Boundary

This runner records repeated validation sessions only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
