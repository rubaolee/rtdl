# Goal4189: RTNN Repeat-10000 Stress Evidence on RTX 4000 Ada

Date: 2026-06-09  
Source commit: `9640c330`  
Artifact directory: `docs/reports/goal4189_rtnn_repeat10000_stress_rtx4000ada/`

## Purpose

Goal4185 found that the RTNN prepared OptiX ranked-summary row already exposed
per-run timing samples, but the stress setting used there (`repeat=5000`) summed
to only `0.853672s`. That was useful smoke evidence, but just below the
one-second aggregate hot-path target.

Goal4189 reruns the same route with a larger repeat count. No runtime code is
changed.

## Pod Command

```bash
python3 examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py \
  --mode prepared_optix_ranked_summary --point-count 65536 --radius 0.02 --k 50 \
  --repeat 10000 --query-batch-size 65536 --distribution uniform
```

## Result

| Field | Value |
| --- | ---: |
| `repeat` | 10000 |
| `runner_payload.repeat` | 10000 |
| `len(runner_payload.elapsed_runs_sec)` | 10000 |
| `sum(runner_payload.elapsed_runs_sec)` | 1.704869568347931 |
| `runner_payload.elapsed_median_sec` | 0.00016932189464569092 |
| `runner_payload.elapsed_min_sec` | 0.00016395002603530884 |
| `runner_payload.elapsed_max_sec` | 0.0004943236708641052 |
| `runner_payload.ok` | `true` |
| `mode` | `prepared_optix_ranked_summary` |
| `contract` | `prepared 3-D fixed-radius bounded ranked-summary aggregate` |

The RTNN row now has second-level repeated hot-path evidence without changing
the primitive, route, dataset size, or claim boundary.

## Boundary

This does not authorize public speedup, broad RT-core speedup, ANN index,
zero-copy, AMD, automatic-partner-selection, or full RTNN paper-reproduction
claims. It only closes the short-row timing-floor issue for the current RTNN
prepared OptiX ranked-summary evidence packet.

The app remains on the generic prepared fixed-radius ranked-summary route. The
native engine is not customized for RTNN semantics.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4189_rtnn_repeat10000_stress_test
```
