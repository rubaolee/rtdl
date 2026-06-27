# Goal2407 RT-DBSCAN RT Core-Graph Union Negative Result

Date: 2026-05-19

Status: rejected/deferred prototype; no runtime API landed

## Purpose

Goal2405 proved a true OptiX RT fixed-radius count-threshold device-column
primitive. The next natural question was whether the remaining CuPy
radius-graph component continuation could be replaced by a generic RT
device-resident continuation without adding DBSCAN-specific native ABI.

Goal2407 tested the simplest candidate:

```text
fixed-radius core-graph union in OptiX any-hit
```

The prototype kept generic names and contracts:

- count threshold device columns
- core flags
- device parent array
- fixed-radius core graph union
- component labels materialized from parent

It also kept a safety fallback: if not all points were core, the adapter used
the existing CuPy grid continuation rather than pretending the all-core fast
path was a full DBSCAN continuation.

## Pod Validation

Artifacts:

```text
docs/reports/goal2407_rt_dbscan_rt_core_graph_union_pod/
```

Environment:

```text
root@69.30.85.177 -p 22055
NVIDIA RTX A5000, driver 570.211.01
OptiX SDK v8.1.0
base checkout ab8e6af7 plus the temporary Goal2407 prototype patch
```

The prototype compiled with:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

All collected JSON artifacts report `signatures_match=true`.

## Results

Warm-tail medians below drop the cold first repeat.

| Dataset | Points | Pure CuPy grid | Goal2405 RT count + CuPy grid | Goal2407 RT count + RT core-graph union | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| clustered3d | 4,096 | 0.019663 | 0.026936 | 0.027808 | Slower |
| clustered3d | 131,072 | 1.613778 | 1.260413 | 1.312342 | Slower than Goal2405 |
| road3d | 4,096 | 0.010616 | 0.026079 | 0.028496 | Slower |
| road3d | 131,072 | 0.710814 | 1.035081 | 1.034815 | Still slower than pure CuPy |

## Interpretation

The prototype answered an important design question: simply moving union-find
into OptiX any-hit is not the right generic continuation primitive. It performs
many atomic union operations inside traversal and does not beat the current
Goal2405 composition, where RTDL uses RT cores for the threshold/count phase and
CuPy handles the radius-graph component continuation.

The useful conclusion is narrower and stronger:

```text
RTDL still needs a generic device-resident radius-graph continuation, but it
should not be raw any-hit atomic union as tested here.
```

Better next candidates are:

- compact RT hit/edge streams consumed by a partner union kernel,
- cell/group-level continuation that reduces per-hit atomics,
- or a prepared fixed-radius component primitive with explicit scheduling and
  aggregation policy.

## Claim Boundary

Goal2407 is a negative result. It does not authorize a new public API, release
claim, RT-DBSCAN paper reproduction claim, or broad RT-core speedup claim.

The code prototype was not landed. The committed outcome should remain the
Goal2405 primitive plus this evidence report and future-work note.
