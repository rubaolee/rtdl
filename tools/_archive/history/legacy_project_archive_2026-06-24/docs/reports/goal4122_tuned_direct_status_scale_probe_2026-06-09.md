# Goal4122 - Tuned Direct-Status 131k Scale Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4122 checks whether Goal4117's explicit partition-cell-factor RT-DBSCAN improvement survives a larger 131,072-point packet.

The probe reuses the Goal4117 runner and tests two relevant factors, `0.25` and `0.5`, for the three RT-DBSCAN profiles.

## Pod Evidence

Artifact:

`docs/reports/goal4122_tuned_direct_status_scale_probe_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `c38d071b`
- Tracked worktree dirty: `false`
- Point count: 131,072
- Repeat: 4
- Warmup: 1
- Tested factors: `0.25`, `0.5`

## Result

| Profile | Current replay (s) | Best factor | Tuned direct-status replay (s) | Replay speedup | Amortized speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.346095 | 0.25 | 0.107770 | 3.211x | 3.207x |
| road3d | 0.127670 | 0.25 | 0.082614 | 1.545x | 2.044x |
| ngsim_dense | 0.047135 | 0.25 | 0.033681 | 1.399x | 2.725x |

All tested rows matched the current route's component-size signature.

## Interpretation

The tuned direct-status route still wins at 131k for all three profiles, but the dense-profile factor is scale-sensitive:

- At 65k, Goal4117 found `ngsim_dense` factor `0.5` best (`1.312x` replay speedup).
- At 131k, Goal4122 finds `ngsim_dense` factor `0.25` best (`1.399x` replay speedup).

So the advisor must expose scale-specific evidence rather than a single dense-profile factor.

## Boundary

This report does not authorize automatic factor selection. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
