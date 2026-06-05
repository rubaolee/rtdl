# Goal3471 - Convex Overlay-Area Fast-Path Probe

## Status

Implemented and validated on the RTX A5000 pod.

Goal3471 adds a generic CuPy convex overlay-area continuation over the existing
shape-pair relation stream. It is exact only for supported convex rows and
returns fail-closed status codes for nonconvex, degenerate, or vertex-budget
rows.

This is the routed fast path described by Goal3470. It does not close the
public-CDB RayJoin exact-overlay gap because Goal3467 showed that most active
rows require general simple-polygon overlay.

## Status Codes

| Code | Meaning |
| --- | --- |
| `0` | convex overlay area computed |
| `1` | unsupported nonconvex row |
| `2` | unsupported vertex budget |
| `3` | unsupported degenerate shape |

## Boundary

This goal does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\geometry_relation_continuations.py scripts\goal3471_convex_overlay_area_fast_path_probe.py`
- `py -3 -m unittest tests.goal3471_convex_overlay_area_fast_path_probe_test`

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3471_convex_overlay_area_fast_path_probe.py \
  --iterations 4 \
  --max-rows 65536 \
  --simple-vertex-threshold 64 \
  --max-vertices-per-shape 128 \
  --output docs/reports/goal3471_convex_overlay_area_fast_path_probe_pod_2026-06-05.json
```

- Artifact:
  `docs/reports/goal3471_convex_overlay_area_fast_path_probe_pod_2026-06-05.json`
- Stdout:
  `docs/reports/goal3471_convex_overlay_area_fast_path_probe_pod_2026-06-05.stdout`
- Commit under test:
  `3785e7fb2d0bf5c28bf2bae6f756febd4a05690d`
- GPU:
  NVIDIA RTX A5000, driver 580.126.09
- Pod unit test:
  `PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python -m unittest tests.goal3471_convex_overlay_area_fast_path_probe_test`

Synthetic fixture:

| Check | Value |
| --- | ---: |
| expected first convex overlap area | 1.0 |
| measured first convex overlap area | 1.0 |
| first area error | 0.0 |
| synthetic statuses | `[0, 1]` |
| synthetic passed | true |

Public-CDB probe:

| Measure | Value |
| --- | ---: |
| active relation rows | 4,543 |
| convex supported rows | 168 |
| positive supported-area rows | 161 |
| unsupported nonconvex rows | 4,375 |
| total supported convex area | 0.05788295450020087 |

Timing summary:

| Phase | Median Seconds | Min Seconds | Max Seconds |
| --- | ---: | ---: | ---: |
| relation columns | 0.004306 | 0.003647 | 0.361791 |
| convex overlay-area fast path | 0.001791 | 0.001679 | 0.027043 |

The first iteration includes CUDA setup and RawKernel compilation. The
steady-state convex fast path is small, but it covers only the routed convex
subset. The public-CDB exact-overlay closure still needs a general
simple-polygon continuation for the 4,375 unsupported nonconvex rows.

## Remaining Work

The main RayJoin exact-overlay path still needs a generic simple-polygon
overlay-area continuation for nonconvex/high-vertex rows.
