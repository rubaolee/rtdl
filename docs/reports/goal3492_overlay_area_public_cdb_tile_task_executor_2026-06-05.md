# Goal3492 - Public-CDB Overlay-Area Tile-Task Executor

## Status

Implemented with pod execution on an NVIDIA RTX A5000.

## Purpose

Goal3491 proved the CuPy tile-task executor on small fixtures. Goal3492 moves
that same execution shape onto the public-CDB active relation stream used by the
RayJoin benchmark lane.

The runner:

- discovers active relation row ordinals with the existing RTDL/OptiX relation
  producer;
- builds Shapely/GEOS oracle geometries for correctness comparison;
- lowers supported no-hole simple polygon and multipolygon inputs into prepared
  component payloads;
- expands each active relation row into component-pair rows plus relation-row
  owners;
- plans bounded tile tasks with `max_triangle_pairs_per_task`;
- runs `evaluate_prepared_overlay_area_tile_tasks_cupy(...)`;
- compares per-relation scalar areas against the Shapely/GEOS oracle.

## Added

- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `tests/goal3492_overlay_area_public_cdb_tile_task_executor_test.py`

## Boundary

This is still partner-backed public-CDB evidence, not a release authorization
and not the final native runtime path. It does not authorize public speedup
wording, broad RT-core speedup wording, true-zero-copy wording, automatic
partner selection, paper-reproduction claims, full overlay-geometry output
claims, or app-specific native engine behavior.

The goal is scalar exact overlay area over the supported prepared stream. Full
overlay geometry output remains a later streamed component/vertex contract.

## Expected Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py \
  --max-triangle-pairs-per-task 512 \
  --progress-every 500 \
  --output docs/reports/goal3492_overlay_area_public_cdb_tile_task_executor_pod_2026-06-05.json
```

The command prints phase progress for CDB loading, Shapely geometry building,
RTDL/OptiX relation discovery, oracle-area construction, task planning, and
CuPy execution.

## Pod Result

Artifact:

- `docs/reports/goal3492_overlay_area_public_cdb_tile_task_executor_pod_2026-06-05.json`

Source commit:

- `2bdf1064`

Hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: `14.1.1`
- Shapely: `2.1.2`

Observed public-CDB workload:

- relation rows: `4,543`
- supported relation rows: `4,539`
- unsupported relation rows: `4`
- component-pair rows: `39,947`
- tile tasks: `54,232`
- planned triangle pairs: `9,653,005`
- processed triangle pairs: `9,653,005`
- task status counts: `{"0": 54232}`

Correctness against Shapely/GEOS:

- observed total area: `26.083217672086707`
- exact Shapely/GEOS total area: `26.08321766231046`
- total absolute error: `9.776247367199176e-09`
- max relation absolute error: `1.0414231699229504e-09`
- positive row count under the v2.8 row threshold: `1086` observed / `1086` exact

Timing snapshot:

- relation discovery: `1.4510477064177394` seconds
- exact Shapely/GEOS oracle area construction: `0.4159626280888915` seconds
- task planning: `0.32162592746317387` seconds
- CuPy tile-task executor: `0.48830951377749443` seconds
- payload build: `22.716640373691916` seconds

Interpretation: the scalar exact-area continuation shape is now validated over
the supported public-CDB stream. The expensive part is currently payload
construction/triangulation, not the CuPy tile-task executor. This still does not
authorize a public speedup claim or full overlay-geometry claim.

## Local Validation

Local validation checks the script/report/gap scaffolding and Python syntax.
CUDA/CuPy public-CDB execution is covered by the pod artifact.
