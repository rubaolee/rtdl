# Spatial / RayJoin-Style Study

This directory shows how a v2.x user can express RayJoin-style spatial
workloads in RTDL without putting app-specific RayJoin logic inside the native
engine. The engine sees generic point, segment, polygon, traversal, and row
contracts. The application owns workload choice, positive-hit filtering,
overlay continuation, and paper-specific interpretation.

This is a serious RTDL implementation study, not a claim that RTDL reproduces
every RayJoin paper result or optimization.

## File

| File | Role |
| --- | --- |
| `rtdl_rayjoin_v2_spatial_join_app.py` | CLI and Python API for PIP, LSI, and overlay-seed workloads |

## Workloads

| Workload | Meaning | Output contract |
| --- | --- | --- |
| `pip` | Point-in-polygon positive hits | `point_to_polygon_positive_hit_rows` |
| `lsi` | Line-segment intersection | `segment_segment_intersection_rows` |
| `overlay_seed` | Polygon overlay seed dependency rows | `overlay_pair_dependency_rows_with_lsi_pip_flags` |

The default fixture data lives under `tests/fixtures/rayjoin/`:

- `br_county_subset.cdb`
- `br_soil_subset.cdb`

External `.cdb` files can be passed with `--dataset`. For two-input workloads,
use a plus-separated pair such as `left.cdb + right.cdb`.

## First Correctness Run

Run all workloads through the portable CPU Python reference:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --backend cpu_python_reference --no-rows
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py --backend cpu_python_reference --no-rows
```

The important fields are:

- `all_match_cpu_python_reference` for suite-level parity.
- `parity_vs_cpu_python_reference` for one workload.
- `row_count` and `summary` for the workload contract.
- `claim_boundary` for what the run does not authorize.

## Run Individual Workloads

Point-in-polygon:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload pip --backend cpu_python_reference --no-rows
```

Line-segment intersection:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --backend cpu_python_reference --no-rows
```

Overlay seed rows:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload overlay_seed --backend cpu_python_reference --no-rows
```

## Embree And OptiX Runs

Embree is the CPU RT backend and is useful for same-contract validation:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --backend embree --no-rows
```

OptiX requires an NVIDIA machine with the OptiX native library built:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --backend optix --no-rows
```

For the serious RayJoin-style performance lane, use the prepared OptiX route.
It separates query packing, static-scene preparation, prepared query time, and
native phase telemetry. This route currently covers PIP and LSI; overlay remains
on the generic dependency-row route until RTDL has a generic device-resident
continuation primitive.

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --execution-route prepared_optix --result-mode count --no-rows
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload pip --execution-route prepared_optix --result-mode rows --no-rows
```

Use `--result-mode count` when the application only needs a scalar count. Use
`--result-mode rows` when it needs witness rows or positive membership rows.
Rows are still omitted from JSON when `--no-rows` is supplied.

For a single external two-input dataset:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --backend embree --dataset "data/left.cdb + data/right.cdb" --no-rows
```

## Python API

The script can also be imported from a user program:

```python
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import run_rayjoin_workload

payload = run_rayjoin_workload(
    "pip",
    backend="embree",
    include_rows=False,
)
print(payload["summary"])
```

Use `run_rayjoin_suite(backend="embree", include_rows=False)` when you want all
three default workloads in one payload.

## How RTDL Maps The Paper Ideas

| RayJoin-style idea | RTDL v2.x expression |
| --- | --- |
| Point-in-polygon traversal | Generic point/polygon traversal plus inclusive positive-hit predicate |
| Segment intersection | Generic segment/segment row contract |
| Overlay dependency discovery | Generic polygon relation rows reduced to continuation flags |
| Paper/application metadata | Python-owned summary and filtering logic |
| Native acceleration | Embree/OptiX generic traversal, not RayJoin-specific native kernels |

## Interpreting Results

Use the JSON payload conservatively:

- `rt_core_accelerated` is true only for `--backend optix`.
- `paper_scale_perf_claim_authorized` is false unless a separate reviewed run
  on representative hardware and datasets authorizes a specific claim.
- `full_rayjoin_reproduction` is false because this program tests RTDL v2.x
  expression of RayJoin-style workloads, not a full clone of the paper system.
- `requires_pod_for_optix_perf` tells you whether the current run still needs
  NVIDIA hardware evidence before it can support OptiX performance wording.

## Claim Boundary

- This directory can demonstrate that RTDL v2.x can express useful
  RayJoin-style spatial workloads over generic engine primitives.
- It should not be used to claim full RayJoin reproduction, universal speedup,
  or paper-scale superiority without a separate reviewed evidence report.
- If a result is intended for a paper-facing comparison, record the commit,
  command, dataset paths, backend, hardware, row counts, parity flags, and
  elapsed seconds.
