# Current V4 Status

RTDL V4.0.0 is the current Python eDSL/operator-pushdown surface for generic
RT-core work on NVIDIA GPUs.

Release: the published tag is `v4.0.0`; clean wheel smoke passed; the release
claim boundary is locked to the measured V4.0 surfaces and app-level table.

## What V4 Gives Users

- One current import: `import rtdsl.v4 as rtdl_v4`.
- A V2/V3-compatible system surface: mature earlier routes remain usable
  through V4 when they are the right implementation.
- Generic operator planning for fixed-radius, nearest-witness, ray/triangle,
  AABB, aggregate-frontier, grouped-reduction, and constrained predicate
  workflows.
- Explicit partner selection for Torch CUDA, CuPy, Numba, and RTDL native
  prepared runners where a surface names that partner.
- Bounded planner responses for callback shapes outside V4.0 instead of silent
  guessing.

## Current Measured Surfaces

V4 exposes measured generic operator/workflow surfaces, including:

- fixed-radius count threshold;
- closest-hit grouped argmin;
- ray/triangle any-hit flags;
- primitive grouped-i64 reduction;
- point-group nearest witness;
- ray/triangle any-hit weighted sum;
- fixed-radius graph component union;
- AABB all-ops count;
- aggregate-frontier device columns;
- constrained Numba custom predicate early-exit.

The public catalog is [learn/operator_catalog.md](learn/operator_catalog.md).
Each surface lists its partner and representative denominator.

## Benchmark Snapshot

The current NVIDIA RT-core table covers all 10 promoted benchmark apps across
V2.14, V3.0.2, and V4.0 rows.

| Metric | Result |
| --- | --- |
| Apps | `10/10` |
| Version rows | `30/30` |
| Primary hardware path | NVIDIA OptiX / RT cores |
| Embree primary denominator | no |
| Missing app rows | `0` |
| Hot-path regressions in the table | `0` |
| Material hot-path rows over V2.14 | Triangle counting, Barnes-Hut |
| Similar-speed or modest-gain rows | RTDBSCAN, RayDB-style, LibRTS spatial index, Hausdorff threshold, Robot collision, Contact manifold, RTNN, Spatial RayJoin |

The detailed table is in
[app_level_benchmark_summary.md](app_level_benchmark_summary.md).

## What V4.0 Does Not Include

These remain outside the V4.0 public API:

- arbitrary Python callbacks inside OptiX;
- raw OptiX callback APIs;
- Tier-3 PTX/module-linking callback support;
- public true-zero-copy or external embedding APIs;
- C ABI or non-Python host bindings.

For supported custom logic, use the constrained Numba predicate workflow shown
in the operator catalog and examples.

## Quick Check

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\v4_frontdoor_quickstart.py
py -3 examples\simple\operator_callback_planning.py --case complex-callback
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/simple/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```
