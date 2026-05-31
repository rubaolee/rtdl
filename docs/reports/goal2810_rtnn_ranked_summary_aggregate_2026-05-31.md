# Goal2810 RTNN Ranked-Summary Aggregate Path

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2810 improves the RTNN benchmark path by adding a generic prepared
fixed-radius ranked-neighbor aggregate for OptiX. The earlier Goal2800/2808
RTNN path downloaded one ranked-summary row per query, while the CuPy grid
opponent kept per-query arrays on device and downloaded only aggregate
checksums. Goal2810 closes that cost-model mismatch with a generic device-side
aggregate and adds an explicit float32 same-precision mode for the CuPy grid
comparison.

This is not an RTNN-specific native engine path. The native surface remains a
generic fixed-radius neighbor/ranked-summary contract.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_core.cpp` | Added generic ranked-summary aggregate CUDA kernels, including exact-double and float32 summary producers and a device-side aggregate reducer. |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added prepared aggregate execution over existing fixed-radius 3D prepared handles. |
| `src/native/optix/rtdl_optix_api.cpp` / `src/native/optix/rtdl_optix_prelude.h` | Added aggregate C ABI functions and aggregate result struct. |
| `src/rtdsl/optix_runtime.py` | Added `PreparedOptixFixedRadiusNeighbors3D.aggregate_ranked_summary(..., precision=...)`. |
| `scripts/goal2348_rtnn_v2_2_external_runner.py` | Added `ranked-summary-aggregate` and `ranked-summary-aggregate-float32` result modes. |
| `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` | Promoted the canonical RTNN harness to the float32 aggregate path for same-precision comparison with the CuPy grid baseline. |
| `tests/goal2800_rtnn_v25_live_ranked_summary_harness_test.py` | Updated the harness guard for the aggregate path. |

## Clean Pod Evidence

Clean-from-Git pod:

```text
commit: 734488a92f7a2a8e9c3fa18598c621558f6a1630
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX build: pass
focused tests: 8 passed
```

Final current-head guard after the Goal2809 review-only commit:

```text
commit: 000e5f34b8eb6b1d79d04f9a49254189683ce4c3
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
focused tests: 12 passed
32768 aggregate smoke: pass, exact aggregate matches on uniform/clustered/shell
```

Artifacts:

- `docs/reports/goal2810_rtnn_ranked_summary_aggregate_pod/rtnn_aggregate_f32_32768.json`
- `docs/reports/goal2810_rtnn_ranked_summary_aggregate_pod/rtnn_aggregate_f32_65536.json`

## 32768-Point Comparison

Compared with the Goal2808 current-head RTNN artifact:

| Distribution | Goal2808 RTDL exact rows (s) | Goal2810 RTDL aggregate f32 (s) | RTDL improvement | CuPy grid (s) | CuPy/RTDL |
| --- | ---: | ---: | ---: | ---: | ---: |
| uniform | 0.000923178 | 0.000508592 | 1.82x | 0.000068820 | 0.135x |
| clustered | 0.030271605 | 0.016337273 | 1.85x | 0.011979779 | 0.733x |
| shell | 0.001308178 | 0.000670793 | 1.95x | 0.000263201 | 0.392x |

All rows passed, all candidate counts matched CuPy exactly, and all aggregate
checksums matched CuPy within the artifact guard.

## 65536-Point Comparison

Compared with the Goal2800 clean 65K RTNN artifact:

| Distribution | Goal2800 RTDL rows (s) | Goal2810 RTDL aggregate f32 (s) | RTDL improvement | CuPy grid (s) | CuPy/RTDL |
| --- | ---: | ---: | ---: | ---: | ---: |
| uniform | 0.001440396 | 0.000922413 | 1.56x | 0.000139370 | 0.151x |
| clustered | 0.099562972 | 0.065411707 | 1.52x | 0.046861857 | 0.716x |
| shell | 0.005567729 | 0.002993603 | 1.86x | 0.002720822 | 0.909x |

The 65K shell row is now close to parity with the CuPy grid opponent. Uniform
and clustered still trail CuPy because upload/launch overhead and the generic
fixed-radius traversal kernel remain heavier than the highly specialized CuPy
grid kernel for these synthetic distributions.

## Interpretation

Goal2810 solves one concrete design problem: RTDL no longer has to materialize
per-query ranked-summary rows when the app asks only for aggregate checksums and
counts. That is the reusable v2.5 lesson.

The remaining RTNN gap is also clear:

- uniform rows are dominated by launch/upload overhead for very small candidate
  counts;
- clustered rows are dominated by the generic per-query top-k maintenance loop;
- a future improvement should keep query columns resident across repeated runs
  and/or add a generic tiled/cooperative top-k reducer.

## Claim Boundary

- No public speedup claim is authorized.
- No RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No native app-specific engine customization is introduced.

The exact-double aggregate path remains available through
`aggregate_ranked_summary(..., precision="float64")`; the promoted RTNN
benchmark row uses `precision="float32"` because the same-contract CuPy grid
opponent is float32.
