# Spatial Join Benchmark Reference

Status: current v2.10 source-tree tutorial reference.

Goal: learn how RTDL expresses RayJoin-style spatial join workloads without
putting RayJoin-specific code inside the native engine.

## Why This Comes After The First Benchmark Tutorial

The RT-DBSCAN walkthrough teaches the basic Python+RTDL+partner shape. Spatial
RayJoin is the next reference because it shows a harder application pattern:

```text
PIP positive assignment
LSI segment intersection
overlay seed pair dependency
prepared RT traversal
explicit CuPy or Numba continuation when needed
```

The code is intentionally not a one-button hidden dispatcher. A user chooses
the workload, backend, execution route, result mode, and partner route.

## First Correctness Run

Linux/macOS:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --backend cpu_python_reference --no-rows
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\current\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py --backend cpu_python_reference --no-rows
```

The expected learner signal is:

```text
all_match_cpu_python_reference: true
```

## What To Read

Read the detailed code walkthrough next:

- [Spatial RayJoin Code Walkthrough](../../../examples/current/research_benchmarks/spatial_rayjoin/CODE_WALKTHROUGH.md)

Then use the benchmark README as the route reference:

- [Spatial / RayJoin-Style Study](../../../examples/current/research_benchmarks/spatial_rayjoin/README.md)

## What The App Teaches

| Concept | What to notice |
| --- | --- |
| App semantics | Python names PIP, LSI, overlay seeds, datasets, and RayJoin interpretation. |
| Engine boundary | Native backends see generic point, segment, polygon, traversal, count, and row contracts. |
| Partner boundary | CuPy and Numba are explicit app choices for continuation or baselines. |
| Prepared execution | Reusable prepared handles avoid rebuilding static right-side geometry for repeated queries. |
| Performance reading | Results are contract-specific; do not collapse them into a universal RayJoin reproduction claim. |

## Next

Return to the [Current RTDL Tutorial Track](README.md), or study the other
research benchmarks under
[examples/current/research_benchmarks](../../../examples/current/research_benchmarks/README.md).
