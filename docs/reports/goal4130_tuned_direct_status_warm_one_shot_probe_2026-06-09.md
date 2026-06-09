# Goal4130 - Tuned Direct-Status Warmed One-Shot Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4130 checks whether the explicit RT-DBSCAN prepared direct-status route is only a replay/reuse win, or whether it also wins when prepare is charged once for a single measured component-signature query.

The probe reuses the Goal4117 factor-sweep runner with `repeat=2` and `warmup=1`. This separates first-use/JIT noise from the measured run while still charging the prepared direct-status setup once in the one-shot total calculation.

Primary one-shot total:

`current_route_prepare_sec + current_route_replay_sec`

versus:

`direct_status_prepare_sec + direct_status_replay_sec`

## Pod Evidence

Artifacts:

- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_65k_pod.json`
- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_131k_pod.json`
- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_262k_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `f9f1b82b`
- Tracked worktree dirty: `false`
- Repeat: 2
- Warmup: 1
- Tested factors: `0.25`, `0.5`

## Result

| Scale | Profile | Best factor | Current replay (s) | Direct replay (s) | Replay speedup | Current prepare+run (s) | Direct prepare+run (s) | One-shot total speedup |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65k | clustered3d | 0.25 | 0.094783 | 0.031893 | 2.972x | 1.098135 | 0.438231 | 2.506x |
| 65k | road3d | 0.25 | 0.038714 | 0.021128 | 1.832x | 0.164097 | 0.062887 | 2.609x |
| 65k | ngsim_dense | 0.5 | 0.015835 | 0.011608 | 1.364x | 0.224437 | 0.123402 | 1.819x |
| 131k | clustered3d | 0.25 | 0.345484 | 0.108817 | 3.175x | 1.621372 | 0.521375 | 3.110x |
| 131k | road3d | 0.25 | 0.129121 | 0.083442 | 1.547x | 0.459315 | 0.176280 | 2.606x |
| 131k | ngsim_dense | 0.25 | 0.047351 | 0.036208 | 1.308x | 0.480587 | 0.140934 | 3.410x |
| 262k | clustered3d | 0.25 | 1.262912 | 0.410653 | 3.075x | 2.944638 | 0.922526 | 3.192x |
| 262k | road3d | 0.25 | 0.471716 | 0.328591 | 1.436x | 1.173671 | 0.516665 | 2.272x |
| 262k | ngsim_dense | 0.25 | 0.155041 | 0.095144 | 1.630x | 0.954759 | 0.324819 | 2.939x |

All factor rows matched the current grouped-stream route's component-size signature.

## Interpretation

The direct-status route is no longer only a repeated-query/replay story. Under warmed one-shot measurement, it wins every tested profile and scale even after prepare is charged once.

The user-facing boundary still matters:

- This does not make the route automatic.
- It does not make one factor universal for dense profiles.
- It does not change the app contract from component-size signature to full DBSCAN semantics.
- It does not authorize release or public whole-app speedup wording.

The advisor can now expose prepared direct-status as an explicit user-selectable option for both tested one-shot and repeated component-signature workloads.

## Boundary

This report does not authorize automatic route selection, automatic partner selection, automatic factor selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
