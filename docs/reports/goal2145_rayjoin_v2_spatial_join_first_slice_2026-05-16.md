# Goal2145 RayJoin-Style RTDL v2 Spatial Join First Slice

Date: 2026-05-16

Status: implementation and local validation complete; external review pending.

## Purpose

This goal starts the RayJoin evaluation lane for RTDL v2.0 as a user-facing Python+RTDL program, not as a native-engine customization. The immediate question is whether a learner can read the RayJoin paper, map its core spatial-join workloads into RTDL v2, and run a clean app-level program over the current generic engine surface.

The answer after this slice is yes for a bounded first step:

- Point-in-polygon point-location is implemented as sparse positive-hit rows.
- Line-segment intersection is implemented as generic segment/segment intersection rows.
- Polygon overlay is represented as a seed-generation stage that identifies pairs needing LSI/PIP continuation.
- RayJoin app policy, face metadata, overlay continuation, and paper-specific tuning stay outside native engine code.

## Paper And Source Basis

RayJoin is the ICS 2024 paper "RayJoin: Fast and Precise Spatial Join" by Liang Geng, Rubao Lee, and Xiaodong Zhang. The paper presents RT-core-accelerated spatial joins, focusing on line segment intersection (LSI), point-in-polygon/point-location (PIP), and polygon overlay built from LSI and PIP.

Sources used for this implementation plan:

- Paper page: https://gengl.me/publication/ics24/
- PDF: https://gengl.me/public/publications/ics24.pdf
- ICS 2024 program listing: https://ics2024.github.io/paper.html
- RayJoin source repository named in the paper: https://github.com/pwrliang/RayJoin

Important paper facts used here:

- The abstract identifies LSI and PIP as the two vital accelerated spatial join queries and polygon overlay as a higher-level application built from them.
- The paper formulates LSI and PIP as ray-tracing problems over BVH traversal.
- The PIP workload is point location: given query points and polygons, report which polygon contains each point.
- The paper's performance and precision claims depend on conservative high-precision representation, RT-core execution, adaptive grouping, and paper-scale datasets. This first RTDL v2 slice does not claim those results yet.

## Implemented RTDL v2 User App

New app:

- `examples/rtdl_rayjoin_v2_spatial_join_app.py`

Supported workloads:

| Workload | RTDL v2 user kernel | Output contract | Current scope |
| --- | --- | --- | --- |
| `pip` | `point_in_polygon(..., result_mode="positive_hits")` | `point_to_polygon_positive_hit_rows` | Sparse point-location rows; no full matrix materialization. |
| `lsi` | `segment_intersection(exact=False)` | `segment_segment_intersection_rows` | Generic intersection rows on fixture/derived segment sets. |
| `overlay_seed` | `overlay_compose()` | `overlay_seed_rows_requiring_lsi_and_pip_continuation` | Seed-level overlay dependency rows, not full overlay topology. |

The app exposes:

- `run_rayjoin_workload(workload, backend=..., dataset=..., include_rows=...)`
- `run_rayjoin_suite(backend=..., include_rows=...)`
- CLI usage through `python examples/rtdl_rayjoin_v2_spatial_join_app.py --workload all --backend embree --no-rows`

Supported local backends:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix` when an OptiX library is available

## Design Improvement Made In This Goal

The first draft of this app used the older full-matrix PIP kernel and then filtered rows in Python. That was correct but not RayJoin-shaped: RayJoin point-location is a sparse positive result problem, not a "return every false row too" problem.

This goal replaced that with a local RTDL user kernel:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def rayjoin_point_location_positive_hits_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(
            exact=False,
            boundary_mode="inclusive",
            result_mode="positive_hits",
        ),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

That keeps PIP policy at the user/app layer while using only the generic RTDL point/polygon traversal and predicate surface. The native engine still sees generic point, polygon, traversal, and row contracts.

## Local Validation

New test:

- `tests/goal2145_rayjoin_v2_spatial_join_app_test.py`

Validated commands:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2145_rayjoin_v2_spatial_join_app_test
$env:PYTHONPATH='src;.'; py -3 examples\rtdl_rayjoin_v2_spatial_join_app.py --workload all --backend cpu_python_reference --no-rows
$env:PYTHONPATH='src;.'; py -3 examples\rtdl_rayjoin_v2_spatial_join_app.py --workload all --backend embree --no-rows
```

Observed local result:

- Focused app test: 4 pass.
- CPU reference suite: all three workloads run and match their own CPU truth path.
- Embree suite: all three workloads run and match CPU reference rows.
- PIP now reports `point_to_polygon_positive_hit_rows`, and all returned PIP rows have `contains == 1`.

The Windows Python launcher prints `Could not find platform independent libraries <prefix>` in this environment, but the commands exit successfully and the RTDL tests pass.

## Claim Boundary

This goal does not authorize a RayJoin performance claim.

Explicitly not claimed:

- Full RayJoin paper reproduction.
- Paper-scale RayJoin throughput.
- Paper-scale polygon overlay.
- Conservative FP64-equivalent precision handling.
- Adaptive grouping / BVH buildup tuning equivalent to the paper.
- OptiX/RT-core speedup evidence, because no pod run is attached to this goal.
- v2.0 release authorization.

What this goal does claim:

- A clean RTDL v2 user can express the three RayJoin-relevant workload shapes with current RTDL primitives.
- PIP is now expressed with sparse positive-hit output, not full-matrix post-filtering.
- CPU reference and Embree local execution preserve row parity for the bounded fixture cases.
- The app does not add app-specific native ABI names or domain-specific native engine hooks.

## Design Gaps Exposed

This slice is useful because it makes the next problems precise:

1. RayJoin-style PIP needs a closest-hit or point-location identity contract at scale. RTDL can emit positive-hit rows now, but paper-grade point-location should avoid extra ambiguous matches and should expose the nearest/owning polygon identity cleanly.
2. LSI needs high-throughput all-hit row streaming for large segment sets. Current fixture validation proves contract shape, not paper-scale throughput.
3. Polygon overlay is not solved by a single primitive. It needs reusable LSI/PIP continuation, topology reconstruction, and partner-side reductions without app code entering the native engine.
4. Precision must be promoted from "float_approx fixture parity" to a conservative representation and exact-refinement story before RayJoin-style correctness can be claimed.
5. OptiX pod validation is required to confirm RT-core execution and to compare against CPU, Embree, CUDA/CuPy, and RayJoin repository baselines.

## Next Work

Recommended next steps:

1. Run this app on an OptiX pod with `RTDL_OPTIX_LIBRARY` set and capture PIP/LSI/overlay-seed JSON artifacts.
2. Add derived scale datasets for PIP and LSI that run for seconds, not milliseconds, while preserving deterministic parity.
3. Compare sparse PIP positive-hit rows to a CUDA/CuPy non-RT implementation on the same inputs.
4. Compare LSI rows to a CPU/OpenMP or CUDA baseline on the same inputs.
5. Study the RayJoin repository input format and add an adapter only if it can be kept outside the engine.
6. Decide whether RTDL v2 needs a generic point-location/closest-owner row primitive or whether sparse positive-hit rows plus partner ranking are sufficient for v2.0.

## Verdict

Goal2145 is an accepted first implementation slice for RayJoin-style RTDL v2 programming, with strict boundaries. It is ready for external review and then pod-scale performance work.
