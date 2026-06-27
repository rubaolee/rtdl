# Goal3024: Hausdorff OptiX Group Sweep And No-Threshold Reduction Probe

## Purpose

Goal3022 showed that the current exact OptiX RT Hausdorff path is correct and
RT-core-backed, but much slower than the dense CuPy grouped-grid partner path.
Goal3024 checks whether a simple parameter change can close that gap before we
start larger primitive/runtime work.

The answer is no. Group-size tuning helps only slightly, and using the native
max-distance reducer with a bounding-box radius and no threshold search is
slower than the current adaptive radius path.

## Evidence

Artifact:

`docs/reports/goal3024_hausdorff_optix_group_sweep_2026-06-02.json`

Collected from clean source commit:

`bc9b6dc670886c7491aa0dcd70fae9d7a237402b`

Pod:

`NVIDIA L4, 565.57.01`

Toolchain:

`/usr/local/cuda-12.6`

Dataset:

`4096 x 4096` deterministic dense random 2D point sets from the Hausdorff
runner.

## Sweep Result

| Strategy | Target Points Per Group | Seconds | Threshold Iterations | Witness Radius |
| --- | ---: | ---: | ---: | ---: |
| adaptive radius | 512 | `0.7740153260529041` | `4` | `0.4368355593732507` |
| adaptive radius | 1024 | `0.7783489376306534` | `4` | `0.4368355593732507` |
| adaptive radius | 4096 | `0.7854960337281227` | `4` | `0.4368355593732507` |
| adaptive radius | 8192 | `0.7862103208899498` | `4` | `0.4368355593732507` |
| adaptive radius | 256 | `0.7902204208076` | `4` | `0.4368355593732507` |
| adaptive radius | 128 | `0.7960854060947895` | `4` | `0.4368355593732507` |
| adaptive radius | 2048 | `0.8165175318717957` | `4` | `0.4368355593732507` |
| adaptive radius | 64 | `0.8343239836394787` | `4` | `0.4368355593732507` |
| reduced bbox upper bound | 64 | `1.0035458281636238` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 128 | `1.0580974780023098` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 1024 | `1.0686571709811687` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 4096 | `1.0783447995781898` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 256 | `1.0815353617072105` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 8192 | `1.097894597798586` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 512 | `1.1010729372501373` | `0` | `3.4946844749860055` |
| reduced bbox upper bound | 2048 | `1.1095162481069565` | `0` | `3.4946844749860055` |

## Interpretation

The current best measured RT row is the adaptive radius path with
`target_points_per_group=512`, at `0.7740153260529041` seconds. That is only a
small improvement over the Goal3022 adaptive 4096-point row
(`0.8692189827561378` seconds), and it remains far slower than the measured
CuPy grouped-grid row (`0.003780316561460495` seconds).

The no-threshold native max-distance reducer avoids threshold-search iterations,
but its bounding-box radius is too loose. It visits too much candidate geometry
and is slower than adaptive radius search.

## Design Consequence

This closes the cheap-tuning branch for current dense 2D exact Hausdorff. A
larger improvement needs a generic primitive/runtime change:

- a better radius-plan or sparse candidate frontier;
- device-resident witness continuation that avoids Python row handling;
- proof that BVH pruning produces substantially less work than dense CuPy
  all-pairs evaluation.

This must remain generic. It is not permission to add Hausdorff-specific native engine logic.

## Boundary

This is internal negative tuning evidence. It does not authorize v2.6 release,
public speedup wording, RT-core speedup wording, whole-app speedup wording,
true-zero-copy wording, automatic partner selection, or app-specific
native-engine behavior.
