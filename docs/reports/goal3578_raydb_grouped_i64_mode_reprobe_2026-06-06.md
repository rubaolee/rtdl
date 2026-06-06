# Goal3578 RayDB Grouped-i64 Mode Reprobe

Date: 2026-06-06

## Purpose

Goal3578 is a diagnostic follow-up to Goal3575.

The Goal3575 all-mode smoke artifact used a tiny `copies=1000`, `warmup=1`,
`repeat=10` run. It correctly verified integration, but its `count` and `sum`
rows looked slower than `stats`, `min`, and `max`, which could be misread as a
native regression. This goal reruns each partner-resident mode in isolation at
the long A5000 settings used by the accepted Goal3572/Goal3575 evidence.

This is a diagnostic packet, not a new speedup claim.

## A5000 Reprobe

Artifacts:

`docs/reports/goal3578_raydb_grouped_i64_mode_reprobe_current_a5000/*.json`

Run:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/root/rtdl_goal3556_current/build/librtdl_optix.so \
RTDL_OPTIX_LIB=/root/rtdl_goal3556_current/build/librtdl_optix.so \
python3 examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py \
  --mode <mode> \
  --backend optix_partner_resident_experimental \
  --copies 120000 \
  --warmup 3 \
  --repeat 5000
```

Pod:

| Field | Value |
| --- | --- |
| GPU | RTX A5000 |
| commit | `1bde04f7` |
| row count | `960000` |
| warmup | `3` |
| repeat | `5000` |

Results:

| Mode | CPU reference match | Native launch count | Median sec | Min sec | Max sec |
| --- | --- | ---: | ---: | ---: | ---: |
| `count` | `true` | 1 | 0.000443520956 | 0.000426984392 | 0.012400534004 |
| `sum` | `true` | 1 | 0.000502159353 | 0.000490611419 | 0.008760042489 |
| `min` | `true` | 1 | 0.000458555296 | 0.000435598195 | 0.007480672561 |
| `max` | `true` | 1 | 0.000489640050 | 0.000442805700 | 0.054995187558 |
| `stats` | `true` | 1 | 0.000525371637 | 0.000517936423 | 0.010264893994 |
| `avg_as_sum_count` | `true` | 1 | 0.000499543268 | 0.000444705598 | 0.007794342935 |

## Interpretation

The tiny Goal3575 full-mode smoke should remain classified as integration
coverage only. The long isolated reprobe shows that `count`, `sum`, and
`avg_as_sum_count` are in the expected steady-state band, with every mode:

- matching the CPU reference;
- using one native launch;
- running under 0.001 seconds median at `copies=120000`.

Therefore Goal3578 finds no grouped-i64 `count`/`sum` native regression to fix
at current head.

## Boundary

This packet does not authorize:

- release or tag action;
- public speedup claims;
- whole-app acceleration claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper reproduction claims;
- package-install claims.

