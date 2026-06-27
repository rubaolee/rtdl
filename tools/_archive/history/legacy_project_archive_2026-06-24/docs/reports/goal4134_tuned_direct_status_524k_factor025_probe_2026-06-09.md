# Goal4134 - Tuned Direct-Status 524k Factor-0.25 Probe

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4134 checks whether the currently winning `partition_cell_factor=0.25` direct-status route remains useful at 524,288 points.

This is a bounded extension probe, not a full factor sweep. It responds to the Goal4128/4129 non-blocking observation that `road3d` replay speedup declined from 65k to 262k and should be watched at larger scale.

## Pod Evidence

Artifact:

`docs/reports/goal4134_tuned_direct_status_warm_one_shot_524k_factor025_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `93c52cb1`
- Tracked worktree dirty: `false`
- Point count: 524,288
- Repeat: 2
- Warmup: 1
- Tested factor: `0.25`

## Result

| Profile | Current replay (s) | Direct replay (s) | Replay speedup | Current prepare+run (s) | Direct prepare+run (s) | One-shot total speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 5.063083 | 1.538509 | 3.291x | 7.518823 | 2.313301 | 3.250x |
| road3d | 1.834984 | 1.342011 | 1.367x | 3.303679 | 1.730070 | 1.910x |
| ngsim_dense | 0.597000 | 0.337514 | 1.769x | 2.001089 | 0.803873 | 2.489x |

All factor rows matched the current grouped-stream route's component-size signature.

## Interpretation

The 524k point confirms that `0.25` stays above parity for all tested profiles. The road profile still trends downward in replay speedup, but it remains positive and its prepare-plus-run one-shot total is still `1.910x`.

Because this probe tests only factor `0.25`, it does not authorize a full 524k factor ranking or a universal factor claim. It only extends the advisory evidence table for the currently winning factor.

## Boundary

This report does not authorize automatic route selection, automatic partner selection, automatic factor selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
