# Goal3820 RTNN Prepared OptiX Ranked-Summary App Mode

Date: 2026-06-07

## Purpose

Goal3818 proved that the RTNN benchmark front door was executable, but only via
the `ranked_summary_typed_stream_plan` metadata route. That was too weak for a
benchmark app whose promoted current path is prepared OptiX fixed-radius
ranked-summary aggregation.

Goal3820 adds a current executable mode:

`--mode prepared_optix_ranked_summary`

This mode wraps the existing generic Goal2348 RTNN runner in-process, generates
a deterministic 3-D point set, runs the prepared OptiX ranked-summary aggregate,
captures runner progress into JSON metadata, and prints pure JSON to stdout.

## Command

```bash
RTDL_OPTIX_LIBRARY=build/librtdl_optix.so \
PYTHONPATH=src:. \
python examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py \
  --mode prepared_optix_ranked_summary \
  --point-count 65536 \
  --radius 0.02 \
  --k 50 \
  --repeat 3 \
  --query-batch-size 65536 \
  --distribution uniform
```

## A5000 Evidence

Artifacts:

`docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_a5000/`

| Row | Point/query count | Result mode | Repeats | Median elapsed |
| --- | ---: | --- | ---: | ---: |
| `rtnn_prepared_optix_4096.stdout.json` | 4096 | `ranked-summary-aggregate-prepared-query-batch-float32` | 2 | `0.0003226594999432564` |
| `rtnn_prepared_optix_65536.stdout.json` | 65536 | `ranked-summary-aggregate-prepared-query-batch-float32` | 3 | `0.00025725364685058594` |

Both rows report:

- `runner_payload.ok=true`
- pure JSON stdout
- `runner_progress` captured as metadata rather than printed before JSON
- no RTNN-specific native engine vocabulary or native ABI change
- all public/release/speedup/broad-RT-core/AMD/automatic-partner claims false

## Interpretation

This closes the RTNN benchmark-front-door gap from Goal3818: the app now has a
current executable RTDL/OptiX ranked-summary route, not only a plan/evidence
summary. The route remains generic and primitive-first. It is a benchmark app
front door over the existing fixed-radius ranked-summary aggregate; it is not a
full RTNN paper reproduction and not a public speedup claim.

## Boundary

This goal does not authorize release action, package-install wording, public
speedup wording, broad RT-core wording, RTNN paper reproduction wording,
whole-app acceleration wording, AMD hardware/performance wording, automatic
partner selection, true-zero-copy wording, or app-specific native-engine logic.

