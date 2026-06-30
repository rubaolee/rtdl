# Goal2056 Control-App RawKernel Pod Follow-Up

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2056 uses the active NVIDIA L4 pod to recheck former-control v2 apps that use Python+CuPy RawKernel+RTDL under the explicit user-approved fairness rule:

> Compare v2 Python+CuPy RawKernel+RTDL against v1.8 Python+RTDL with no user C/C++ extension. This is useful but not absolutely fair.

This goal is not a v2.0 release gate. It is a pod evidence collection step that records both wins and hard boundaries.

## Pod Environment Repair

The first all-control-app run at `copies=4096` failed when graph v1.8 attempted to build the native oracle:

```text
cannot find -lgeos_c
```

Because this was a pod setup issue and we had root control, the pod was repaired with:

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config
```

After installation, `libgeos_c.so` resolved through `ldconfig`.

## 4096 Database Result

Artifact:

- `docs/reports/goal2056_database_rawkernel_cupy_optix_l4_4096.json`

Command shape:

```bash
timeout 300 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1955_rawkernel_control_app_perf.py \
  --apps database_analytics \
  --copies 4096 \
  --partner cupy \
  --candidate-backend optix \
  --repeats 3 \
  --warmups 1 \
  --source-commit-label 980fe21e-pod-database-4096
```

Result:

| App | Copies | v1.8 median | v2 median | Ratio |
| --- | ---: | ---: | ---: | ---: |
| database_analytics | 4096 | 0.300836 | 0.074904 | 0.249x |

Interpretation:

- v2 is about 4.0x faster than the v1.8 Python+RTDL baseline for this bounded comparison.
- Payload signatures match.
- `all_match_v1_8_python_rtdl_oracle` is `true`.

## 1024 Polygon Results

Artifact:

- `docs/reports/goal2056_polygon_rawkernel_cupy_optix_l4_1024.json`

Command shape:

```bash
timeout 600 /root/rtdl_goal2046_venv/bin/python \
  scripts/goal1955_rawkernel_control_app_perf.py \
  --apps polygon_pair_overlap_area_rows,polygon_set_jaccard \
  --copies 1024 \
  --partner cupy \
  --candidate-backend optix \
  --repeats 3 \
  --warmups 1 \
  --source-commit-label 980fe21e-pod-polygon-1024
```

Result:

| App | Copies | v1.8 median | v2 median | Ratio |
| --- | ---: | ---: | ---: | ---: |
| polygon_pair_overlap_area_rows | 1024 | 0.158836 | 0.147532 | 0.929x |
| polygon_set_jaccard | 1024 | 0.117812 | 0.102050 | 0.866x |

Interpretation:

- Both polygon rows are now modestly faster than the v1.8 Python+RTDL baseline at this bounded size.
- Payload signatures match.
- `all_match_v1_8_python_rtdl_oracle` is `true`.

## Negative Findings

These are not hidden.

1. A full all-control-app run at `copies=4096` got stuck in the graph v1.8 baseline before it could write an artifact. This means graph should be measured as a separate bounded case with smaller copies, fewer repeats, or `--skip-v1-8` when collecting v2-only scaling.
2. A non-graph `copies=4096` run reached polygon-pair OptiX candidate discovery and failed with:

```text
RuntimeError: CUDA driver error: out of memory
```

That means the current polygon rawkernel control path is not yet cleanly scalable to 4096 copies with OptiX candidate discovery on this L4 pod. It needs candidate paging, smaller batches, or a memory-bounded candidate discovery contract before we can claim large-scale polygon control-app speedup.

## Boundary

Allowed claim:

- On the L4 pod, the v2 RawKernel database control app is faster than the v1.8 Python+RTDL baseline at `copies=4096`.
- On the L4 pod, the two polygon RawKernel control apps are modestly faster than the v1.8 Python+RTDL baseline at `copies=1024`.
- The pod setup now includes GEOS development libraries needed by the v1.8 oracle build.

Not allowed:

- v2.0 release readiness;
- broad all-control-app speedup;
- broad RT-core speedup;
- polygon 4096 scalability;
- graph 4096 same-contract completion;
- package-install readiness.

## Verdict

`accept-with-boundary`
