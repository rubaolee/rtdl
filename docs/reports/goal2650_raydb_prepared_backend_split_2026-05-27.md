# Goal2650 RayDB Prepared Backend Split

Status: internal evidence only. Public speedup wording remains unauthorized pending review.

## Question

RayDB now has a paper-style RT path using generic 3-D rays, triangles,
primitive group ids, primitive integer payloads, and grouped reductions. The
current optimization question was whether the next prepared-query optimization
helps both OptiX/RT and Embree.

Answer: yes. The shared abstraction is a prepared static scene plus prepared
primitive grouped i64 payload plus prepared ray batch. OptiX keeps the scene,
payload, and rays device-resident. Embree keeps the same contract on host. The
engine primitive remains app-agnostic: native code sees only rays, triangles,
group ids, payload values, deduplication, and grouped reduction.

## Code Changes

- Added Embree support to `GenericPreparedRayTrianglePrimitiveGroupedI64Reduction3D`.
- Added Embree prepared primitive payload and prepared ray batch wrappers.
- Added `--backend {optix,embree}` to `scripts/goal2646_raydb_prepared_payload_perf_pod.py`.
- Removed a native Embree query-side full ray pre-copy in
  `rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction`.
  The function now reads each packed ray directly inside the parallel query
  loop. This keeps the ABI and contract unchanged.

## Pod Evidence

- Pod: `root@194.68.245.16 -p 22072`
- GPU: NVIDIA RTX A5000, driver `565.57.01`
- Pod repo path: `/workspace/rtdl_goal2645`
- Script: `scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- Workload: generated deterministic RayDB-style fixture, 2,000,000 rows,
  128 groups, revenue mod 64, one copy.
- Timing: median prepared query time after workload construction and
  scene/payload/ray preparation.

## Prepared Query Split

| backend | mode | rays | workload build s | prepare scene/payload s | prepare rays s | query median s | traversal first sample s | RT core |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Embree before no-precopy | count | 110,592 | 0.511251 | 0.439019 | 0.000023 | 0.009561 | 0.035070 | no |
| Embree after no-precopy | count | 110,592 | 0.500848 | 0.431815 | 0.000010 | 0.006101 | 0.006275 | no |
| OptiX prepared host rays | count | 110,592 | 0.530997 | 0.487608 | 0.001732 | 0.000227 | 0.000120 | yes |
| Embree before no-precopy | sum | 4,755,456 | 0.752815 | 0.407314 | 0.000011 | 0.215016 | 0.018469 | no |
| Embree after no-precopy | sum | 4,755,456 | 0.753227 | 0.426226 | 0.000046 | 0.095588 | 0.094187 | no |
| OptiX prepared host rays | sum | 4,755,456 | 0.866114 | 0.117259 | 0.127545 | 0.001155 | 0.000979 | yes |

## Interpretation

- The Embree no-precopy change improves prepared query time by 1.57x for
  `count` and 2.25x for `sum`.
- After the Embree fix, OptiX prepared query time is still 26.9x faster than
  Embree for `count` and 82.8x faster for `sum`.
- The RT traversal itself is already very small: about 0.120 ms for `count`
  and 0.979 ms for `sum` in the first OptiX sample.
- For end-to-end app time, the remaining dominant costs are not RT traversal:
  workload construction is roughly 0.50-0.87 s, scene/payload preparation is
  roughly 0.12-0.49 s, and host-ray preparation for the large `sum` query is
  about 0.128 s.

## Boundary

This evidence supports a narrow claim: for repeated prepared RayDB-style
queries on this generated fixture, the RT-core OptiX query path is much faster
than the same-contract Embree query path. It does not authorize a whole-app
speedup claim because Python-owned workload construction and preparation still
dominate end-to-end time.

## Next Optimization

The next shared target is prepared table/query-buffer ownership rather than
another app-specific native kernel:

- Generate triangle bounds, group ids, values, and query rays directly as typed
  partner/host buffers instead of Python object-heavy intermediate structures.
- Reuse prepared table descriptors across `count`, `sum`, and other group-by
  variants when the same RayDB table is queried repeatedly.
- Prefer partner-owned query columns for OptiX so large ray batches do not pay
  a repeated host packing/upload cost.
- Keep Embree on the same generic contract so it remains the CPU baseline.
