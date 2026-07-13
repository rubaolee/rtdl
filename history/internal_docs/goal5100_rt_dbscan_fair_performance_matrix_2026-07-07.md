# Goal5100 RT-DBSCAN Fair Performance Matrix

## Status

`completed_bounded_performance_matrix_no_public_speedup_claim`

## Purpose

Measure the representative fixtures under the regimes defined by Goal5097. The goal is to show the current performance shape honestly, not to claim full paper performance.

## Cold Process One-Shot

Each case was run in a fresh remote Python process. This includes Python startup, CUDA/Numba/OptiX initialization, and first-use compilation/setup.

| Case | RTDL wall | Author reported total | Author process wall | RTDL / author reported |
|---|---:|---:|---:|---:|
| `representative_medium_two_clusters3d` | 1.605694s | 0.047156s | 0.390483s | 34.05x |
| `representative_border_shell3d` | 1.717175s | 0.023916s | 0.376732s | 71.80x |
| `representative_three_components_noise3d` | 1.627829s | 0.026826s | 0.365603s | 60.68x |

Cold one-shot conclusion: RTDL is much slower than the author's reported phase total on these small synthetic fixtures. The dominant visible cost is first-use setup/compilation, not steady-state traversal.

## Warm Long-Lived Process Diagnostic

The same Python process ran all cases with `--repeat 3`; author binary executions remained separate process calls. These warm medians are diagnostic only. This packet does not include an equivalent author warm-process loop.

| Case | RTDL median | Author reported total median | Author process wall median | RTDL / author reported |
|---|---:|---:|---:|---:|
| `representative_medium_two_clusters3d` | 0.005739s | 0.048403s | 0.339364s | 0.119x |
| `representative_border_shell3d` | 0.004121s | 0.025299s | 0.307701s | 0.163x |
| `representative_three_components_noise3d` | 0.004083s | 0.021747s | 0.312785s | 0.188x |

Warm diagnostic conclusion: after startup/setup is paid, RTDL's generic OptiX + Numba grouped-stream route is very small on these synthetic fixtures. This is not a public speedup claim because it is a warm in-process diagnostic, the author side has no equivalent warm-process loop in this packet, and the inputs are not exact paper data.

## Key Metadata

Warm native phase metadata shows steady-state fixed-radius / grouped union phases on the order of 0.0001s after setup:

```text
count_threshold_native_elapsed_sec ~= 0.00010s
grouped_union_native_elapsed_sec ~= 0.00009s to 0.00012s after first setup
```

The first warm medium repeat recorded `grouped_union_native_elapsed_sec=0.441654s`, showing that setup can still land inside the first in-process run.

## Non-Authorization

This matrix does not authorize:

- a full paper performance claim,
- exact paper dataset performance,
- whole-program speedup,
- author-performance parity,
- using warm medians as a cold one-shot headline.
