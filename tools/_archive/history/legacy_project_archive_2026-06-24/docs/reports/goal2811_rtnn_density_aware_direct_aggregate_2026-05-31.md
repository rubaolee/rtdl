# Goal2811 RTNN Density-Aware Direct Aggregate

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2811 continues the RTNN v2.5 performance work after Goal2810. Goal2810
removed per-query ranked-summary downloads by adding a generic device-side
aggregate. Goal2811 tightens the promoted float32 aggregate path in two ways:

1. Add a direct one-kernel aggregate for low-density fixed-radius cells, so the
   runtime no longer has to materialize per-query summaries before reducing
   them.
2. Keep the existing two-step summary-plus-reduction path for dense occupied
   cells, because the pod showed the direct kernel can lose occupancy in
   compute-heavy clustered rows.

This is still a generic fixed-radius neighbor/ranked-summary contract. No
RTNN-specific native engine path or app-shaped ABI was added.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_core.cpp` | Added `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_direct`, a generic direct aggregate kernel. |
| `src/native/optix/rtdl_optix_workloads.cpp` | Tracks prepared-grid occupied-cell density and selects direct aggregate only when mean search points per occupied cell is <= 4.0. |
| `src/rtdsl/optix_runtime.py` | Exposes timing mode `prepared_uniform_cell_ranked_summary_aggregate_f32_direct`. |
| `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` | Reports median elapsed time across repeats instead of the last repeat. |
| `tests/goal2811_rtnn_direct_aggregate_kernel_test.py` | Guards the direct kernel and density-aware fallback path. |

## Clean Pod Evidence

Clean-from-Git pod:

```text
commit: 4de076381c6012ee1d9e62e14a8d8d44399109ba
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX build: pass
focused tests: 14 passed
```

Final clean-head guard after report/artifact commit:

```text
commit: 95091daad801811d95ae2d301fd9a27235189396
source_dirty: []
focused tests: 16 passed
```

Artifacts:

- `docs/reports/goal2811_rtnn_direct_density_aggregate_pod/rtnn_direct_density_median_f32_32768.json`
- `docs/reports/goal2811_rtnn_direct_density_aggregate_pod/rtnn_direct_density_median_f32_65536.json`

## Median Timing Results

Compared with Goal2810 using the median of each artifact's recorded RTDL repeat
runs:

| Points | Distribution | Goal2810 RTDL median (s) | Goal2811 RTDL median (s) | RTDL change | Goal2811 CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: | ---: |
| 32768 | uniform | 0.000597325 | 0.000566739 | 1.054x | 0.180x |
| 32768 | clustered | 0.022810002 | 0.016192632 | 1.409x | 0.738x |
| 32768 | shell | 0.000721010 | 0.000550133 | 1.311x | 0.477x |
| 65536 | uniform | 0.001036777 | 0.000832137 | 1.246x | 0.202x |
| 65536 | clustered | 0.065391236 | 0.063930878 | 1.023x | 0.736x |
| 65536 | shell | 0.003021620 | 0.003093044 | 0.977x | 0.882x |

The one small regression is the 65K shell row. The density-aware rule still
improves five of six median rows and avoids the earlier direct-kernel clustered
regression. It does not make RTDL faster than the CuPy grid opponent.

## Interpretation

The key v2.5 design lesson is that "device-side aggregate" is not one fixed
implementation strategy. Low-density rows benefit from fusing summary and
reduction into one kernel. Dense rows can prefer a two-step path because the
direct kernel's extra shared-memory reduction can reduce occupancy while the
top-k loop is already compute-heavy.

The selection rule is intentionally generic: prepared fixed-radius search state
already knows how many search points and occupied grid cells it has. RTDL uses
that density signal without naming RTNN or adding app-specific code.

## Claim Boundary

- No public speedup claim is authorized.
- No RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No native app-specific engine customization is introduced.

Remaining work is still the same broad RTNN gap: CuPy remains faster on all
same-contract rows, especially uniform distributions where the CUDA grid kernel
has very little work per query. Future work should focus on reusable query
device residency and a generic cooperative/tiled top-k reducer.
