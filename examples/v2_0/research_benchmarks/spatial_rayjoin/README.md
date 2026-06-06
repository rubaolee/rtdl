# Spatial / RayJoin-Style Study

This directory shows how a v2.8 user can express RayJoin-style spatial
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
native phase telemetry. The prepared route covers PIP, LSI, and overlay-seed
with generic RTDL primitives.

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --execution-route prepared_optix --result-mode count --no-rows
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload pip --execution-route prepared_optix --result-mode rows --no-rows
```

Use `--result-mode count` when the application only needs a scalar count. Use
`--result-mode rows` when it needs witness rows or positive membership rows.
Rows are still omitted from JSON when `--no-rows` is supplied.

For PIP rows or counts that need the v2.8 typed-stream plus partner-continuation
path, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload pip --execution-route prepared_optix_cupy_refined_pip --result-mode count --no-rows
```

This route produces generic OptiX point/closed-shape candidate columns with
instance identity ordinals, then filters them through a prepared CuPy simple-ring
refiner. It is useful for repeated exact PIP continuation because the point,
shape, and vertex lookup arrays are uploaded once into the prepared CuPy
refiner. Use `--candidate-max-rows` to set the fail-closed candidate capacity
for large external CDB files.

The route is still app-layer Python+CuPy policy over generic RTDL primitives.
It does not make the native engine RayJoin-specific and does not authorize a
full RayJoin paper reproduction or public speedup claim by itself.

For repeated PIP calls against the same point and shape records, use the
prepared Python handle so the OptiX scene and CuPy lookup arrays are prepared
once:

```python
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
    prepare_rayjoin_optix_cupy_refined_pip,
)

with prepare_rayjoin_optix_cupy_refined_pip(points, shapes, candidate_max_rows=60000) as prepared:
    first = prepared.run(result_mode="count", include_rows=False)
    repeated = prepared.run(result_mode="count", include_rows=False)

print(repeated["summary"])
```

This is the app-facing reusable form of the v2.8 typed-stream plus prepared
CuPy-refiner pattern measured in Goal3427.

For LSI workloads that need counts per left segment instead of exact witness
rows, use the compact grouped-count route:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --execution-route prepared_optix_compact_grouped_count --no-rows
```

That route uses generic segment-pair candidate columns plus generic compact
grouped-count device columns. Left-ID remapping stays in Python because the
grouped-count primitive uses direct-address key capacity. The compact
`group_key[]` and `count[]` columns stay CUDA-resident; a host row-count scalar
is exposed so Python can know the valid prefix length. This route is a reference
implementation path, not a full RayJoin reproduction or public speedup claim.
In short: the route combines generic compact grouped-count device columns with
Python-owned RayJoin interpretation.

For repeated count queries against the same right-side segment set, use the
prepared Python handle so the OptiX right-side scene is built once:

```python
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
    pack_rayjoin_optix_compact_grouped_count_left_segments,
    prepare_rayjoin_optix_compact_grouped_count_segments,
)

with prepare_rayjoin_optix_compact_grouped_count_segments(right_segments) as prepared:
    payload = prepared.run(left_segments, include_rows=False)
    packed_left = pack_rayjoin_optix_compact_grouped_count_left_segments(left_segments)
    repeated_payload = prepared.run_packed_left(packed_left, include_rows=False)
    dense_count_payload = prepared.run_packed_left_dense_count(packed_left, include_rows=False)

print(payload["summary"])
print(repeated_payload["summary"])
print(dense_count_payload["summary"])
```

The prepared handle is still app-layer code. Native execution still uses
generic segment-pair candidate columns and generic compact grouped-count
columns; RayJoin route policy, left-ID remapping, and repeated-query reuse
remain in Python. `run_packed_left(...)` is useful when a caller repeatedly
queries the same left segment batch against one prepared right-side scene and
wants to avoid paying Python query packing on every call.

When the app only needs dense counts per left segment and does not need
right-side witness IDs, `run_packed_left_dense_count(...)` uses a generic fused
segment-pair left-id count primitive. It returns a dense count-column contract
where `count[index]` corresponds to the remapped left segment index.

For overlay-seed workloads where the app only needs the active pair-dependency
count, use the prepared shape-pair active-count handle:

```python
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)

with prepare_rayjoin_optix_shape_pair_active_count(right_shapes) as prepared:
    payload = prepared.run(left_shapes)
    packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
    repeated_payload = prepared.run_packed_left(packed_left)

print(repeated_payload["summary"])
```

This handle uses generic prepared shape-pair relation flags plus a generic
device-side active-count continuation by default: relation flags stay on device,
containment and reduction run in a generic CUDA continuation, and only the scalar count is copied back.
It is for overlay-seed scalar summaries; full overlay row continuation remains a separate app-layer concern. Use
`prepared.run_packed_left_host_exact(...)` when you need the host exact oracle
path for debugging or validation.

## Recommended Explicit Route Choice

Current v2.8 evidence says a RayJoin-style user should not blindly run every
contract through one backend.

For the simple authored tiled fixtures in the benchmark packet:

| Contract | Recommended route | Reason |
| --- | --- | --- |
| PIP positive assignment count/refinement | CuPy dense CUDA-core count | The geometry is simple enough that a warmed dense bounds-filter kernel beats the current RT candidate-plus-refiner path |
| LSI dense left-id count at stress scale | RTDL/OptiX dense left-id count | RT traversal plus the generic dense left-id continuation beats the dense CuPy pair test at stress scale |
| Overlay active pair-dependency count | CuPy dense CUDA-core active count | The authored square fixture has cheap bounds rejection, so dense CUDA-core partner code wins |

For the bounded public CDB slices used in Goal3593:

| Contract | Recommended route | Reason |
| --- | --- | --- |
| PIP positive assignment count | CuPy dense CUDA-core count | Public county PIP still favors the warmed dense CUDA-core baseline at this size |
| LSI segment-intersection count | RTDL/OptiX prepared route | Public CDB segment columns strongly favor RT traversal over dense all-pairs CUDA-core segment tests |
| Overlay active pair-dependency count | RTDL/OptiX prepared route | Public CDB polygon-pair dependency filtering strongly favors the prepared RTDL/OptiX route over dense CuPy active-count testing |

This is an explicit user/program decision, not automatic dispatch. The app
should record the selected route, partner, RT-core status, count contract, and
claim boundary in its output. See:

- `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py`
- `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md`
- `docs/reports/goal3592_rayjoin_explicit_mixed_route_reference_packet_2026-06-06.md`
- `docs/reports/goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md`

The lesson is practical: use RTDL/OptiX where RT traversal pays, use a partner
where a cheap dense CUDA-core reduction is the better tool, and keep the choice
visible rather than hiding it behind a dispatcher.

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

| RayJoin-style idea | RTDL v2.8 expression |
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
- `full_rayjoin_reproduction` is false because this program tests RTDL v2.8
  expression of RayJoin-style workloads, not a full clone of the paper system.
- `requires_pod_for_optix_perf` tells you whether the current run still needs
  NVIDIA hardware evidence before it can support OptiX performance wording.

## Claim Boundary

- This directory can demonstrate that RTDL v2.8 can express useful
  RayJoin-style spatial workloads over generic engine primitives.
- It should not be used to claim full RayJoin reproduction, universal speedup,
  or paper-scale superiority without a separate reviewed evidence report.
- If a result is intended for a paper-facing comparison, record the commit,
  command, dataset paths, backend, hardware, row counts, parity flags, and
  elapsed seconds.
