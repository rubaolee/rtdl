# Benchmark Evidence Index

Status: current v2.14 source-tree evidence map.

Use this page when you want to reproduce or audit the ten benchmark-app front
doors. It is intentionally narrower than the full report history: it tells you
which row is current, what hardware it needs, and how to read the result.

For conservative performance interpretation, read the
[RT-Core Evidence Matrix](rt_core_evidence_matrix.md). It separates strong RT
evidence, mixed evidence, partner-led evidence, and coverage evidence.

Machine-readable source:

```bash
PYTHONPATH=src:. python scripts/rtdl_benchmark_evidence_index.py --json
```

Human-readable table:

```bash
PYTHONPATH=src:. python scripts/rtdl_benchmark_evidence_index.py
```

For the public release evidence, read the
[RTDL v2.14 Release Package](../release_reports/v2_14/README.md). Older raw
reports are archived under the top-level `history/` directory and are not part
of the first-user path.

v2.14 evidence:

- [v2.14 release package](../release_reports/v2_14/README.md)
- [v2.14 row-scoped RT-core vs Embree CPU comparison](../release_reports/v2_14/public_rt_vs_embree_comparison.md)
- [RayJoin Section 5.7 bounded reproduction](../release_reports/v2_14/rayjoin_section57_bounded_reproduction.md)
- [v2.14 public wording boundaries](../release_reports/v2_14/public_wording_boundaries.md)
- [v2.14 app-author implementation strategy](v2_14_app_author_implementation_strategy.md)

## Current Ten-App Rows

| App | Current front-door row | Partner/native note | Pod need |
| --- | --- | --- | --- |
| Hausdorff / X-HD | `hausdorff_xhd_current_optix_threshold` | primitive-first OptiX path; CuPy/Numba are comparison/reference lanes | NVIDIA pod for OptiX timing |
| Spatial RayJoin | `spatial_rayjoin_pip_count_current_prepared_optix` | contract-split RayJoin-style path; scalar/count paths are stronger than full paper reproduction | NVIDIA pod plus public-CDB fixture for representative route |
| RT-DBSCAN | `rt_dbscan_optix_numba_prepared_grid` | OptiX fixed-radius flags plus explicit Numba component continuation | CUDA pod with Numba |
| Robot collision | `robot_collision_optix_prepared_device_count` | primitive-only prepared static-scene collision count path | NVIDIA pod for OptiX timing |
| Contact manifold | `contact_manifold_optix_native_collect_k` | bounded collect/witness primitive path; no manifold-native ABI | NVIDIA pod for OptiX timing |
| RayDB-style | `raydb_style_optix_count_primitive_first` | primitive-first grouped count path; partner rows only for unfused continuations | NVIDIA pod; CUDA pod for CuPy/Numba partner comparison |
| Barnes-Hut | `barnes_hut_numba_exact_force` | aggregate-frontier pressure plus Numba exact-force reference | CUDA pod with Numba |
| LibRTS spatial index | `librts_spatial_index_optix_aabb_index` | prepared AABB-index benchmark slice, not full mutable LibRTS | NVIDIA pod for OptiX timing |
| RTNN | `rtnn_prepared_optix_ranked_summary` | prepared fixed-radius ranked summary path | NVIDIA pod for OptiX timing |
| Triangle counting | `triangle_counting_optix_native_summary` | explicit native graph summary path; candidate-row interpretation stays app code | NVIDIA pod for OptiX timing |

## Evidence Reports

Use the v2.14 release package links above for the current reader-facing
evidence. Raw maintainer reports are preserved under the top-level `history/`
archive, but they are not part of this learner-facing page.

## Reading Rules

- A front-door row proves that the current command executes and keeps claim
  flags clean. It is not a performance leaderboard.
- A ten-app packet is not ten broad RT-core speedup claims. Read each row by
  exact contract before using it as performance evidence.
- The v2.14 release packet keeps mixed rows explicit: Spatial RayJoin PIP is
  near parity and slightly Embree-faster in the refreshed human-scale slice,
  stricter prepared-executor rows separately show an OptiX-over-Embree exact
  PIP engineering win that still does not beat RayJoin RT, and RTNN remains
  blocked as RT-core neighbor-search speedup wording. RayJoin Section 5.7 now
  has a bounded reproduction page: two available full-stream pairs plus two
  representative public-primitives Lakes/Parks pairs, not a full exact 8/8
  hidden-input claim.
- A scale-profile row is more useful for performance planning, but still must
  be read by exact app, command, hardware, backend, partner, and dataset.
- CuPy/Numba comparison rows are partner-continuation evidence only. They do
  not become RT-core or whole-application speedup claims.
- The RayJoin external comparison is useful for LSI/PIP diagnosis, but it is
  not a full RayJoin paper reproduction and does not authorize RTDL-beats-RayJoin
  wording.
- If a row needs OptiX, use a pod or workstation with `RTDL_OPTIX_LIBRARY`
  pointing to `librtdl_optix`.
- If a row needs Numba, install the CUDA-capable Numba stack on the pod before
  running the packet.

For setup checks before running any benchmark, use the
[Source-Tree Doctor](source_tree_doctor.md).
