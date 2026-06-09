# Goal4126 - Tuned Direct-Status 262k Scale Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4126 checks whether the explicit RT-DBSCAN prepared direct-status route remains useful at a larger 262,144-point scale.

The probe reuses the Goal4117 factor-sweep runner and tests partition cell factors `0.25` and `0.5` for the three RT-DBSCAN profiles. It compares each tuned direct-status replay against the current grouped-stream Numba route under the same component-signature contract.

## Pod Evidence

Artifact:

`docs/reports/goal4126_tuned_direct_status_262k_scale_probe_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `5ddd50cd`
- Tracked worktree dirty: `false`
- Point count: 262,144
- Repeat: 4
- Warmup: 1
- Tested factors: `0.25`, `0.5`

## Result

| Profile | Current replay (s) | Best factor | Tuned direct-status replay (s) | Replay speedup | Amortized speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 1.265486 | 0.25 | 0.405822 | 3.118x | 3.119x |
| road3d | 0.471896 | 0.25 | 0.330375 | 1.428x | 1.795x |
| ngsim_dense | 0.156316 | 0.25 | 0.095173 | 1.642x | 2.550x |

All tested rows matched the current route's component-size signature.

## Factor Detail

| Profile | Factor | Replay (s) | Replay speedup | Amortized speedup | Partitions | Max neighbor offset |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.25 | 0.405822 | 3.118x | 3.119x | 5652 | 5 |
| clustered3d | 0.5 | 1.511232 | 0.837x | 1.142x | 1117 | 3 |
| road3d | 0.25 | 0.330375 | 1.428x | 1.795x | 5122 | 5 |
| road3d | 0.5 | 1.619231 | 0.291x | 0.418x | 1015 | 3 |
| ngsim_dense | 0.25 | 0.095173 | 1.642x | 2.550x | 43742 | 5 |
| ngsim_dense | 0.5 | 0.187640 | 0.833x | 1.607x | 6526 | 3 |

## Interpretation

The larger scale strengthens the explicit route guidance:

- `0.25` remains best for clustered and road-like profiles.
- Dense NGSIM-like profiles are not globally tied to one factor: `0.5` was best at 65k, but `0.25` wins at 131k and 262k.
- The direct-status path should stay an explicit user-selected repeated-component-signature route, with the advisor ranking the nearest tested scale first.

This is performance evidence for route guidance, not automatic tuning.

## Boundary

This report does not authorize automatic factor selection. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
