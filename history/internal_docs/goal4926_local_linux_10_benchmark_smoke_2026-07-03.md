# Goal4926 Local Linux 10-Benchmark Smoke After RayJoin Repairs

Status: completed locally on `lx1` (`192.168.1.20`).

## Purpose

After the RayJoin paper-reproduction repairs and public-surface cleanup, this
goal checked whether the 10 promoted benchmark-app entry points still run on the
local Linux machine. This was not a performance benchmark and did not use the
POD.

The check used a lightweight snapshot of the current Windows worktree copied to
Linux:

```text
/home/lestat/work/rtdl_benchmark_smoke_4926_20260703_171904
```

The snapshot included `src`, `examples`, `tests`, `docs`, `tutorials`, and root
metadata files. It excluded `.git`, `history`, `build`, `__pycache__`, and
compiled Python artifacts.

## Help/Import Gate

All 10 benchmark entry points passed `--help` on local Linux.

| Benchmark | Entry point | Result |
| --- | --- | --- |
| Hausdorff / X-HD | `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | PASS |
| Spatial RayJoin | `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | PASS |
| RT-DBSCAN | `examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | PASS |
| Robot Collision | `examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py` | PASS |
| Contact Manifold | `examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | PASS |
| RayDB-style | `examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py` | PASS |
| Barnes-Hut | `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | PASS |
| LibRTS Spatial Index | `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | PASS |
| RTNN | `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` | PASS |
| Triangle Counting | `examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | PASS |

## Lightweight Execution Gate

Each app then ran a minimal CPU/reference or deterministic fixture command.

| Benchmark | Command shape | Result |
| --- | --- | --- |
| Hausdorff / X-HD | `--backend cpu_python_reference --copies 1` | PASS |
| Spatial RayJoin | `--workload all --backend cpu_python_reference --no-rows` | PASS |
| RT-DBSCAN | `--mode cpu_reference --dataset tiny --point-count 32` | PASS |
| Robot Collision | `--mode cpu_reference --dataset tiny --pose-count 4 --obstacle-count 4 --link-count 2` | PASS |
| Contact Manifold | `--mode cpu_reference --dataset tiny` | PASS |
| RayDB-style | `--mode all --backend cpu_python_reference --fixture-kind repeated --copies 1` | PASS |
| Barnes-Hut | `--mode cpu_reference --body-count 16` | PASS |
| LibRTS Spatial Index | `--mode cpu_reference --dataset tiny --operation all --box-count 16 --query-count 8` | PASS |
| RTNN | `--mode ann_cpu_quality --point-count 32 --radius 0.25` | PASS |
| Triangle Counting | `--mode run --backend cpu_python_reference --copies 1 --output-mode summary --fixture single_triangle` | PASS |

## Focused RayJoin / Workspace Check

Additional local Linux checks:

```bash
PYTHONPATH=src:. python3 examples/current/features/spatial/rtdl_planar_map_workspace_lsi_pip.py
PYTHONPATH=src:. python3 -m unittest tests.goal4913_planar_map_workspace_api_test
```

Results:

- workspace example: exited successfully with structured `status: skipped`,
  because local Linux does not have `librtdl_optix` built or configured;
- workspace API unit test: 4 tests passed.

The skip is acceptable for local Linux because this check was not an OptiX
performance run. The source still validates the public programming shape, and
the unit test checks API export, reuse, env restoration, and no bundled RayJoin
helper import.

## Impact Assessment

Only `Spatial RayJoin` is directly affected by the RayJoin/planar-map repairs.
It passed both the help/import gate and the lightweight CPU/reference execution
gate.

The other nine benchmark apps do not share the CDB planar-map LSI/PIP
Simulation-of-Simplicity or duplicate-half-edge contracts. Their lightweight
execution gates passed, so there is no local evidence that the RayJoin repairs
regressed their entry points.

## Boundary

This goal does not authorize:

- performance claims;
- OptiX timing claims;
- full POD benchmark conclusions;
- all-app release promotion;
- further post-v2.14 optimization work.

## Exit Label

`completed_local_linux_10_benchmark_smoke_all_passed_no_performance_claim`
