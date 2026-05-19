# Goal2425 RT-DBSCAN Prepared CuPy Fairness Pod Evidence

Date: 2026-05-19

Status: pod evidence complete; explicit plan updated

## Purpose

Goal2424 added the missing fair baseline for RT-DBSCAN steady-state timing:

```text
partner_cupy_prepared_grid_components_3d
```

Goal2425 runs the fair comparison on the RTX A5000 pod:

```text
fresh CuPy grid
prepared CuPy grid
prepared OptiX RT count-threshold + prepared CuPy grid
```

This corrects earlier Goal2418/Goal2420 wording that compared the prepared RT
bridge against a fresh-grid pure CuPy repeat baseline.

## Environment

```text
pod: root@69.30.85.177 -p 22055
commit: 94039b7db50c07466e57665a8a6b4c1ad90afa5e
GPU: NVIDIA RTX A5000
driver: 570.211.01
OptiX library: /root/rtdl_goal2415/build/librtdl_optix.so
```

Artifacts:

```text
docs/reports/goal2425_rt_dbscan_prepared_cupy_fairness_pod_evidence/
```

## Results

All rows use repeat count 3 and report warm-tail medians over repeats 2 and 3.
All rows preserved signature parity.

| Dataset | Points | Fresh CuPy sec | Prepared CuPy sec | Prepared RT+CuPy sec | Prepared RT / prepared CuPy | Winner |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| clustered3d | 32768 | 0.177559 | 0.162435 | 0.174192 | 1.072x | prepared CuPy |
| clustered3d | 65536 | 0.531741 | 0.474191 | 0.377922 | 0.797x | prepared RT+CuPy |
| clustered3d | 131072 | 1.615494 | 1.589133 | 1.036171 | 0.652x | prepared RT+CuPy |
| clustered3d | 262144 | 5.804778 | 5.749831 | 3.233508 | 0.562x | prepared RT+CuPy |
| clustered3d | 524288 | 25.540414 | 25.941314 | 14.209671 | 0.548x | prepared RT+CuPy |
| road3d | 32768 | 0.107588 | 0.087333 | 0.135187 | 1.548x | prepared CuPy |
| road3d | 65536 | 0.290249 | 0.231199 | 0.354013 | 1.531x | prepared CuPy |
| road3d | 131072 | 0.724112 | 0.664737 | 0.768571 | 1.156x | prepared CuPy |
| road3d | 262144 | 2.002951 | 1.879623 | 1.918930 | 1.021x | prepared CuPy |
| road3d | 524288 | 6.614880 | 6.458786 | 5.494305 | 0.851x | prepared RT+CuPy |
| ngsim_dense | 32768 | 0.085485 | 0.064030 | 0.119470 | 1.866x | prepared CuPy |
| ngsim_dense | 65536 | 0.217725 | 0.170985 | 0.291603 | 1.705x | prepared CuPy |
| ngsim_dense | 131072 | 0.460498 | 0.391106 | 0.554750 | 1.418x | prepared CuPy |
| ngsim_dense | 262144 | 1.193230 | 1.057508 | 1.435580 | 1.358x | prepared CuPy |

## Interpretation

The prepared RT bridge is real and useful, but not uniformly best.

- Clustered 3-D data crosses over at 65k points and scales well after that.
- Road-like narrow manifolds cross over later, at 524k points in this pod pass.
- Compact dense `ngsim_dense` rows still favor the prepared pure-CuPy
  continuation through 262k points.

This means the current explicit benchmark plan should select by measured
dataset shape and scale. It must not claim broad DBSCAN acceleration.

## Plan Update

The app-level `planned_rt_dbscan` policy now follows this evidence:

- `tiny`: CPU correctness fixture.
- `ngsim_dense`: prepared pure CuPy through 262k.
- `road3d`: prepared pure CuPy below 524k; prepared RT+CuPy at and above 524k.
- `clustered3d`: prepared pure CuPy below 65k; prepared RT+CuPy at and above
  65k.

The policy remains explicit and inspectable. It is not a hidden dispatcher, not
a paper-reproduction claim, and not a release-level broad RT-core speedup
claim.

## Next Runtime Lesson

RTDL has the right generic contracts to compose RT count-threshold output with
partner component labeling. The next improvement is not another app-specific
DBSCAN primitive. It is a more generic device-resident radius-graph continuation
that can consume RT-produced core/count columns without redoing as much work in
the partner continuation.
