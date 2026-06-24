# Goal2420 RT-DBSCAN Prepared Grid Extended Profile

Date: 2026-05-19

Status: diagnostic pod profile complete

## Purpose

Goal2418 proved that prepared CuPy-grid continuation improves the prior
RT-count plus fresh-grid bridge. Goal2420 extends the pod profile to answer two
follow-up questions:

1. Does the prepared RT path cross over against pure CuPy on larger sparse
   road-shaped data?
2. Does the same path help dense compact `ngsim_dense` data, or should RTDL
   choose the pure CuPy continuation there?

## Environment

```text
root@69.30.85.177 -p 22055
/root/rtdl_goal2415
commit 225d823cff8dfd2f576343f95f79e76a07ee7035
NVIDIA RTX A5000, driver 570.211.01
Python 3.12.3
CuPy 14.0.1
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2415/build/librtdl_optix.so
```

Artifacts:

```text
docs/reports/goal2420_rt_dbscan_prepared_grid_extended_profile/
```

## Timing Method

All rows use:

```text
repeat_count = 3
warm-tail median = median(repeats 2 and 3)
```

Compared modes:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_prepared_grid_components_3d
```

All artifacts report `signatures_match = true`.

## Results

| Dataset / points | Pure CuPy grid app sec | Old RT-count + fresh CuPy grid app sec | Prepared RT-count + prepared CuPy grid app sec | Prepared vs pure CuPy | Prepared vs old RT-grid |
| --- | ---: | ---: | ---: | ---: | ---: |
| clustered3d / 262144 | 5.840801 | 3.781169 | 3.182007 | 1.836x faster | 1.188x faster |
| road3d / 262144 | 2.146962 | 2.567065 | 1.923938 | 1.116x faster | 1.334x faster |
| ngsim_dense / 32768 | 0.088163 | 0.161875 | 0.106384 | 0.829x of CuPy | 1.522x faster |
| ngsim_dense / 65536 | 0.216129 | 0.424097 | 0.254323 | 0.850x of CuPy | 1.668x faster |
| ngsim_dense / 131072 | 0.461203 | 0.871994 | 0.550689 | 0.838x of CuPy | 1.583x faster |

## Interpretation

The prepared path crosses over on large road-shaped data:

```text
road3d / 262144: prepared RT path is 1.116x faster than pure CuPy
```

This resolves the main open question from Goal2418. The sparse-road gap at
32k/65k was mostly fixed setup overhead and insufficient scale, not a proof
that RT traversal is intrinsically wrong for that shape.

The compact `ngsim_dense` rows tell a different story. Pure CuPy remains faster
at every measured size. In these rows, the CUDA-core grid continuation is already
so cheap that the RT count-threshold phase does not pay for itself.

## Design Lesson

RTDL should not hide this behind a magical dispatcher. The right v2.x design is
an explicit plan/explain path:

```text
plan A: pure CuPy device-grid radius components
plan B: OptiX RT count-threshold + prepared CuPy grid continuation
```

The plan must report:

- selected backend;
- partner;
- preparation/reuse status;
- RT-core phase timing;
- continuation timing;
- fallback/crossover reason;
- exact claim boundary.

For this benchmark, a sensible default recommendation is:

- clustered or very large sparse 3-D density workloads: try the prepared RT
  bridge;
- compact dense grids at current sizes: use pure CuPy grid continuation;
- never claim paper-level RT-DBSCAN reproduction from these synthetic rows.

## Next Engineering Target

Prepared reuse is now the baseline. The next larger generic primitive remains:

```text
device-resident radius-graph edge stream or grouped union continuation
```

That primitive would avoid doing threshold traversal in OptiX and then redoing
radius traversal in CuPy for component labels. It is the path toward stronger
RT-DBSCAN-style performance without adding a DBSCAN-specific native ABI.

## Claim Boundary

This report is a diagnostic performance profile. It does not authorize:

- v2.x release closure;
- RT-DBSCAN paper reproduction;
- broad DBSCAN acceleration claims;
- an automatic hidden dispatcher;
- any DBSCAN-specific native engine customization.
