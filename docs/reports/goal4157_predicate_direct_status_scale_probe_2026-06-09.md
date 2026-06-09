# Goal4157 - Predicate-Aware Direct-Status Scale Probe

Date: 2026-06-09

Verdict: same-contract-achieved-performance-mixed

Pod: `root@213.173.108.27 -p 15138`, NVIDIA RTX 4000 Ada Generation,
driver `550.127.05`

Commit: `d0b3f8f9`

Artifact:
`docs/reports/goal4157_predicate_direct_status_scale_factor025_pod.json`

## Purpose

Goal4156 exposed the first executable predicate-aware direct-status candidate.
Goal4157 tested whether it actually closes the Goal4153 same-contract gap
against the current RT-DBSCAN grouped-stream route.

## Result

All 18 comparisons matched the current grouped-stream signature. This is the
important correctness result: the predicate-aware direct-status route now
preserves the core/border/noise signature contract that the older component-only
direct-status route could not preserve.

Performance is mixed, so no route promotion is authorized.

| dataset | points | candidate | same signature | current / candidate |
| --- | ---: | --- | --- | ---: |
| clustered3d | 65,536 | until_stable | yes | 0.617x |
| clustered3d | 65,536 | single_pass_candidate | yes | 1.042x |
| clustered3d | 131,072 | until_stable | yes | 0.527x |
| clustered3d | 131,072 | single_pass_candidate | yes | 0.876x |
| clustered3d | 262,144 | until_stable | yes | 0.557x |
| clustered3d | 262,144 | single_pass_candidate | yes | 0.778x |
| road3d | 65,536 | until_stable | yes | 0.453x |
| road3d | 65,536 | single_pass_candidate | yes | 0.890x |
| road3d | 131,072 | until_stable | yes | 0.384x |
| road3d | 131,072 | single_pass_candidate | yes | 0.758x |
| road3d | 262,144 | until_stable | yes | 0.339x |
| road3d | 262,144 | single_pass_candidate | yes | 0.667x |
| ngsim_dense | 65,536 | until_stable | yes | 0.742x |
| ngsim_dense | 65,536 | single_pass_candidate | yes | 1.256x |
| ngsim_dense | 131,072 | until_stable | yes | 0.964x |
| ngsim_dense | 131,072 | single_pass_candidate | yes | 1.798x |
| ngsim_dense | 262,144 | until_stable | yes | 1.039x |
| ngsim_dense | 262,144 | single_pass_candidate | yes | 1.871x |

The ratio is `current grouped-stream elapsed / candidate elapsed`; values above
`1.0x` mean the candidate is faster.

## Interpretation

The design problem changed from "wrong contract" to "right contract, not yet fast enough everywhere." The candidate wins on dense NGSIM and the smallest
clustered case in single-pass mode, but loses on road and larger clustered
packets. The stable mode is mostly slower.

The likely hot spot is the predicate direct-status signature kernel. The
measured timing is dominated by `predicate_direct_status_signature_sec`, while
the OptiX count-threshold phase is cached out of measured replay rows. The next
engineering target should reduce safe-full partition border-candidate work and
avoid repeated scans of partition contents when the partition predicate summary
already proves there are no candidate updates to perform.

## Boundary

The `single_pass_candidate` rows matched signatures in this packet, but they
still report `direct_status_convergence_proven: false` and
`direct_status_final_changed_flag: 1`. They remain an explicit measured
candidate only.

Goal4157 does not authorize route promotion, release, public speedup wording,
broad RT-core wording, whole-app benchmark claims, paper reproduction, hidden
dispatch, automatic partner selection, automatic convergence-mode selection,
app-specific engine logic, AMD claims, or true-zero-copy claims.
