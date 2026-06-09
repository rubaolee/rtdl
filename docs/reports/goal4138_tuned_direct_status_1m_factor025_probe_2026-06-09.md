# Goal4138 - Tuned Direct-Status 1M Factor-0.25 Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4138 extends the RT-DBSCAN factor-`0.25` scale check to 1,048,576 points.

This is a bounded extension probe, not a full factor sweep. It specifically checks whether the road-like profile, whose replay speedup had declined through 524k, stays above parity at 1M.

## Pod Evidence

Artifact:

`docs/reports/goal4138_tuned_direct_status_warm_one_shot_1m_factor025_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `c9469d43`
- Tracked worktree dirty: `false`
- Point count: 1,048,576
- Repeat: 2
- Warmup: 1
- Tested factor: `0.25`

## Result

| Profile | Current replay (s) | Direct replay (s) | Replay speedup | Current prepare+run (s) | Direct prepare+run (s) | One-shot total speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 19.742100 | 5.755256 | 3.430x | 23.684219 | 7.001828 | 3.383x |
| road3d | 7.275470 | 5.210240 | 1.396x | 10.153858 | 5.956892 | 1.705x |
| ngsim_dense | 2.241336 | 1.252143 | 1.790x | 5.292012 | 2.176086 | 2.432x |

All factor rows matched the current grouped-stream route's component-size signature.

## Interpretation

Factor `0.25` remains above parity at 1M for all three tested profiles. The road-like profile no longer shows a monotonic replay decline: `1.367x` at 524k becomes `1.396x` at 1M. Its one-shot total speedup continues to decline but remains positive at `1.705x`.

Because this probe tests only factor `0.25`, it does not authorize a full 1M factor ranking or a universal factor claim.

## Boundary

This report does not authorize automatic route selection, automatic partner selection, automatic factor selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
