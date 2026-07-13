# Goal5123 - X-HD Fair Performance Matrix

Date: 2026-07-08

## Verdict

```text
xhd_fair_performance_matrix_published_with_boundaries
```

## Purpose

Publish one bounded performance/phase matrix without creating an unfair
author-vs-RTDL speedup or parity claim.

## Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_bounded_performance_matrix_2026-07-08.json
```

## Matrix Summary

### Author On POD

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
variant=rt
execution=gpu
```

| Fixture | HDResult | Retained JSON Running.AvgTime | Rerun median Running.AvgTime | Rerun median process wall |
| --- | ---: | ---: | ---: | ---: |
| bounded2d | 2.0 | 3.873 ms | 3.888 ms | 1.079 s |
| bounded3d | 2.0 | 4.235 ms | 3.724 ms | 1.104 s |

`Running.AvgTime` is the author internal X-HD `ReportedTime` average, not the
whole process wall clock.

### RTDL Local Public Column Route

| Fixture | Route | Matched author directed HDResult | Route phase | Local total |
| --- | --- | ---: | ---: | ---: |
| bounded2d | `rtdl_numpy_columns_2d` | yes | 0.00142 s | 0.00272 s |
| bounded3d | `rtdl_numpy_columns_3d` | yes | 0.00159 s | 0.00302 s |

This is a public exact columnar reference route. It is not the author X-HD
RT-core algorithm and was measured in the local Python process, not in the POD
author environment.

## Why No Ratio Is Reported

No author-vs-RTDL performance ratio is reported because denominators do not
align:

- author `Running.AvgTime` is an internal paper phase on POD;
- author wall time is a process envelope on POD;
- RTDL route time is a local Python exact/reference route phase;
- RTDL route is not the author X-HD RT-core algorithm;
- local and POD hardware/runtime are not the same measurement environment.

Reporting a ratio from these values would be misleading.

## Authorized Interpretation

The matrix proves:

- bounded 2D/3D values match author `HDResult` on the same inputs;
- author phase time and process wall are very different metrics;
- RTDL bounded route timings are tiny on these toy fixtures but not comparable
  to author paper phase timing as a performance claim.

## Not Authorized

- author parity;
- RTDL speedup;
- paper benchmark reproduction;
- exact paper dataset timing;
- universal Hausdorff acceleration.
