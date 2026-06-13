# Goal4368 PIP Exact Prepared-Points Executor

Date: 2026-06-13

Status: internal v2.13 optimization evidence. This improves the exact RTDL
PIP scalar-count route, but it does not make RTDL faster than RayJoin RT.

## Summary

Goal4368 adds a reusable exact prepared-points scalar-count executor for the
OptiX closed-shape membership path:

`rtdl_optix_prepare_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d`

The executor preserves the same exact prepared-points count semantics as the
v2.12 route. It reuses candidate/output workspace across hot calls and keeps
the GEOS-backed exact refinement on the host when GEOS is available. It does
not switch to the faster device-filtered or relation-status corrected routes,
because those routes do not match the exact PIP count on this same stream.

## Pod Evidence

| Field | Value |
| --- | --- |
| Pod | `157.157.221.29:20049` |
| GPU | `NVIDIA RTX A4000, driver 580.126.20, compute capability 8.6` |
| Source basis | pod commit `ffd7420c` plus the Goal4368 native/runtime diff |
| Raw artifact | `docs/reports/goal4368_pip_exact_prepared_points_executor_2026-06-13/summary.json` |
| Raw runner markdown | `docs/reports/goal4368_pip_exact_prepared_points_executor_2026-06-13/raw_goal4354_runner_summary.md` |

Build command used on the pod:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-v8 CUDA_PREFIX=/usr/local/cuda-12.8
```

Run command used the Goal4354 same-stream runner with:

```bash
--workloads pip
--warmups 1
--repeats 7
--include-embree
--embree-warmups 1
--embree-repeats 7
--include-pip-fast-diagnostic
--pip-rtdl-count-mode exact_prepared_points_executor
```

## Result

| Row | Count | Hot median | Readout |
| --- | ---: | ---: | --- |
| RTDL OptiX exact prepared-points executor | 8,686 | 6.760860 ms | exact count preserved |
| RTDL Embree prepared scalar count | 8,686 | 19.610595 ms | CPU baseline count matches |
| v2.12 RTDL OptiX exact prepared-points row | 8,686 | 12.033907 ms | superseded baseline for this PIP contract |
| RayJoin RT query log | n/a | 0.830221 ms | still much faster than RTDL PIP |

Ratios:

| Ratio | Value | Meaning |
| --- | ---: | --- |
| New OptiX executor vs v2.12 OptiX exact prepared-points | 1.78x | RTDL PIP exact route improved |
| Embree / new OptiX executor | 2.90x | RT cores now show a clearer same-contract PIP win over Embree CPU |
| RayJoin RT / new RTDL OptiX executor | 0.123x | values below 1 mean RayJoin RT is faster |
| RayJoin RT faster than new RTDL OptiX executor | 8.14x | RTDL still does not beat RayJoin RT for PIP |

Hot OptiX executor repeats after warmup, in milliseconds:

`11.640, 7.034, 6.405, 6.761, 6.257, 6.804, 6.208`

Median phase timings:

| Phase | Median |
| --- | ---: |
| candidate write pass | 1.862633 ms |
| candidate download | 0.024287 ms |
| exact refinement | 4.826782 ms |

## Rejected Fast Route

The diagnostic fast routes remain rejected for this exact stream:

| Route | Count |
| --- | ---: |
| exact authority | 8,686 |
| device-filtered prepared-points count | 8,798 |
| relation-status corrected native executor | 8,603 |

The relation-status corrected executor took about `1.931 ms`, but its count is
wrong for this stream. It cannot be used for the same-contract PIP comparison.

## Interpretation

This is a real PIP optimization: the same exact scalar-count contract improved
from `12.034 ms` to `6.761 ms`, and the same-contract OptiX-over-Embree ratio
improved from near parity to about `2.90x`.

It is not enough to claim RTDL beats RayJoin for PIP. RayJoin RT remains about
`8.14x` faster on its original RT query-time metric. The remaining RTDL PIP
cost is explainable: candidate generation is about `1.86 ms`, while exact
host refinement is still about `4.83 ms`.

## Boundary

This report authorizes only an internal v2.13 engineering conclusion: the exact
prepared-points executor improves the RTDL PIP same-stream scalar-count route
without changing the exact count. It does not authorize public RTDL-beats-RayJoin
wording, RayJoin paper reproduction wording, whole-application speedup wording,
or broad RT-core speedup wording.
