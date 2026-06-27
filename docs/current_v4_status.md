# Current V4 Status

RTDL V4.0.0 is the current Python eDSL/operator-pushdown surface for generic
RT-core work on NVIDIA GPUs.

Status:

```text
v4_0_0_published__complete_rt_core_app_matrix__bounded_material_wins__clean_wheel_smoke_passed
```

The published tag is `v4.0.0`; its target commit is resolved by the Git tag
object and release closure record. The release claim boundary is locked, and
clean wheel smoke passed.

## User Promise

V4 gives users one current Python front door for reusable RT-shaped GPU work:

- V4 is a V2/V3 superset. Existing V2.14 and V3 routes remain part of the
  usable system when they are the best route for a task.
- V4 adds measured generic operator and workflow surfaces that avoid Python
  row-object hot paths where the surface says so.
- Users choose partners explicitly. Current measured partner scopes include
  Torch CUDA, CuPy where explicitly named, Numba where explicitly named, and
  RTDL native prepared runners.
- Unsupported complex callbacks fail closed or remain future work.

## Complete 10-App RT-Core Matrix

The V4.0.0 release matrix was run on NVIDIA RTX A5000 with NVIDIA RT-core/OptiX
rows as the primary denominator.

| Metric | Result |
| --- | --- |
| Apps | `10/10` |
| Version rows | `30/30` |
| V2.14/V3.0.2/V4.0 row for every app | `true` |
| Primary denominator | NVIDIA OptiX/RT-core only |
| Embree primary denominator | `false` |
| Hot-path regressions in the release table | `0` |
| Material hot-path rows over V2.14 | `triangle_counting`, `barnes_hut` |
| V4/V2.14 hot geomean | `2.10069x`, not a headline |

The current app-level table is in
[app_level_benchmark_summary.md](app_level_benchmark_summary.md).

## Operator/Workflow Surfaces

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
Each surface has its own denominator, partner scope, scale, and claim boundary.
Operator-surface performance is reported against named brute-force partner/CPU baselines:
most measured operators sit in the `1.2x` to `1.7x` range; larger outliers are
labeled as scale-dependent algorithmic-complexity wins.

RT-BarnesHut paper-reproduction wording is not part of the V4.0.0 public
claim. The Barnes-Hut app row documents a released benchmark route, not a
public claim that RTDL fully reproduces the paper implementation.

## Boundary

Allowed:

- "V4.0.0 is a published Python eDSL/operator-pushdown release and V2/V3
  superset."
- "The 10-app RT-core matrix is complete for V2.14, V3.0.2, and V4.0."
- "V4.0 has two material hot-path rows over V2.14 and similar-speed
  control rows elsewhere in the release matrix."
- "The custom predicate early-exit workflow is a V4-specific bounded workflow
  win."

Not authorized:

- all benchmark apps are faster;
- broad all-app speedup wording;
- broad V4-over-V2.14 speedup wording;
- broad V4-over-V3 speedup wording;
- whole-application speedup claim;
- public true-zero-copy claims;
- Tier-3 callback/PTX support claims;
- broad CuPy performance claims beyond explicitly named measurements;
- raw OptiX callback support claims;
- app-specific native engine/kernel claims;
- embedding, C ABI, or non-Python host binding claims.

## Start Command

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```
