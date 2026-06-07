# Goal3832: Short-Row Stress Candidate Calibration On A5000

Date: 2026-06-07

Status: implemented and A5000-validated.

## Purpose

Goal3831 cleaned up the robot-collision default row by separating CPU
probe-reference validation from prepared OptiX performance timing. Goal3832
asks a follow-up question: which remaining short default rows can become useful
stress-profile candidates without changing app semantics or adding
app-specific native-engine logic?

This is a calibration packet only. It does not change the current default scale-profile registry.

## Artifacts

- `docs/reports/goal3832_short_row_stress_candidates_a5000/summary.json`
- `docs/reports/goal3832_short_row_stress_candidates_followup_a5000/summary.json`

Both artifacts were produced on the A5000 pod at commit `5cdb1cb5` using
file-backed stdout/stderr.

## Candidate Results

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `hausdorff_copies4096` | pass | 2.002 | safe but still setup dominated |
| `hausdorff_copies8192` | pass | 2.252 | safe but still setup dominated |
| `hausdorff_copies32768` | pass | 5.254 | useful Hausdorff/X-HD stress candidate |
| `contact_grid128` | pass | 1.252 | safe but short |
| `contact_grid256` | fail | 3.253 | correct fail-closed bounded-collect overflow: emitted 256 with capacity 128 |
| `contact_grid256_cap256` | pass | 3.252 | useful contact-manifold stress candidate when capacity matches the bound |
| `triangle_copies8192` | pass | 1.752 | safe but still short |
| `triangle_copies32768` | pass | 2.753 | usable medium candidate |
| `triangle_copies131072` | pass | 7.505 | useful triangle-counting stress candidate |
| `rayjoin_all_prepared_count_repeat50` | pass | 2.503 | better RayJoin whole-app count candidate than tiny PIP-only |
| `rayjoin_pip_count_repeat500` | pass | 1.752 | repeating the tiny PIP fixture does not create a meaningful scale row |

## Interpretation

The current default ten-app scale-profile registry should remain a quick health
suite. Goal3832 identifies stress candidates for future performance packets:

- Hausdorff/X-HD: `--copies 32768` gives a bounded 5.254s RT-core threshold
  decision row.
- Contact manifold: `--grid-count 256 --witness-capacity 256` gives a bounded
  3.252s collect-k row. The failed `grid256/cap128` row is useful evidence that
  the bounded primitive fails closed instead of returning partial output.
- Triangle counting: `--copies 131072` gives a 7.505s stress row, but the app
  still reports `rt_core_accelerated=false`; use it as a graph/no-regression
  stress row, not as an RT-core headline.
- RayJoin: `--workload all` is a better candidate than repeating the tiny PIP
  fixture. True RayJoin stress still needs larger public-CDB route evidence,
  not just repeat-count inflation.

## Next Engineering Target

Do not tune by increasing repeat counts on tiny fixtures. The next meaningful
performance work is:

1. promote a separate stress-profile registry or runner so default health
   checks stay quick;
2. build a larger RayJoin public-CDB scale row over the already-developed
   prepared/tile-task routes;
3. make contact-manifold stress rows choose a capacity that matches the tested
   bound, while preserving fail-closed behavior for insufficient capacity.

## Boundary

Goal3832 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a stress-candidate calibration packet only.
