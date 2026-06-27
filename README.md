# RTDL V4

RTDL V4.0.0 is the current Python eDSL/operator-pushdown surface for generic
RT-core work on NVIDIA GPUs.

V4 is a V2/V3 superset: existing V2.14 and V3 routes remain part of the usable
system, and V4 adds measured generic operator surfaces plus constrained
predicate pushdown.

Use one import:

```python
import rtdsl.v4 as rtdl_v4
```

## Current Status

Status:

```text
V4.0.0 published, complete 10-app RT-core matrix, bounded material wins, clean wheel smoke passed
```

The published tag is `v4.0.0`; its target commit is resolved by the Git tag
object and release closure record. The release claim boundary is locked, and
clean wheel smoke passed.

The V4.0.0 NVIDIA RTX A5000 release matrix:

- `10/10` promoted benchmark apps;
- `30/30` V2.14/V3.0.2/V4.0 rows executed successfully;
- all rows returned parseable JSON;
- Embree is not used as a primary denominator;
- no `n/a` rows;
- no hot-path regressions in the release table;
- material hot-path rows over V2.14: `triangle_counting`,
  `barnes_hut`;
- V4/V2.14 hot geomean: `2.10069x`, not a headline.

Read [docs/app_level_benchmark_summary.md](docs/app_level_benchmark_summary.md)
before making any app-level performance claim.

## What RTDL Is

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, nearest-neighbor screening, collision checks, graph-style
queries, and database-like summaries.

The V4 contract is:

```text
Python owns the application.
RTDL owns generic RT-shaped operators and prepared routes.
Users choose measured partners explicitly.
Callback shapes are explicit: supported shapes plan cleanly, and shapes outside
V4.0 return a bounded planner result instead of guessing.
```

The Python package is `rtdsl`.

## What V4 Adds

- one import: `import rtdsl.v4 as rtdl_v4`;
- V2/V3-compatible app routes under a single current front door;
- measured generic RT-core operator/workflow surfaces;
- explicit partner scopes for Torch CUDA, CuPy where named, Numba where named,
  and RTDL native prepared runners;
- constrained custom predicate early-exit for the measured Numba workflow;
- clear claim boundaries for app rows, operator rows, and future callback work.

The current 10-app RT-core matrix is complete. The app table has two material
hot-path rows over V2.14 and similar-speed rows elsewhere; use that distribution
when describing performance.

Operator-surface performance is reported against named brute-force partner/CPU baselines:
most measured operators sit in the `1.2x` to `1.7x` range; larger outliers are
labeled as scale-dependent algorithmic-complexity wins, not as a blanket
near-hand-written-OptiX claim.

RT-BarnesHut paper-reproduction wording is not part of the V4.0.0 public
claim. The Barnes-Hut app row documents a released benchmark route, not a
public claim that RTDL fully reproduces the paper implementation.

## Current User Paths

| Path | Purpose |
| --- | --- |
| [docs/README.md](docs/README.md) | Current V4 documentation index. |
| [docs/current_v4_status.md](docs/current_v4_status.md) | V4 status, user promise, and boundaries. |
| [docs/v4_release_notes.md](docs/v4_release_notes.md) | User-facing V4.0.0 release notes. |
| [docs/learn/operator_catalog.md](docs/learn/operator_catalog.md) | Current V4 operator/workflow catalog. |
| [docs/learn/partner_choice.md](docs/learn/partner_choice.md) | How to choose Torch, CuPy, Numba, and RTDL native routes. |
| [docs/app_level_benchmark_summary.md](docs/app_level_benchmark_summary.md) | Complete V2.14/V3.0.2/V4.0 app matrix summary. |
| [tutorials/current/README.md](tutorials/current/README.md) | V4 learning path, including benchmark-app recipes. |
| [examples/README.md](examples/README.md) | Runnable V4 examples and benchmark-app learning path. |
| [docs/learn/performance_wording.md](docs/learn/performance_wording.md) | Performance wording guide. |

## Start Here

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\v4_frontdoor_quickstart.py
py -3 examples\simple\operator_callback_planning.py --case complex-callback
py -3 examples\simple\custom_predicate_early_exit_planning.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/simple/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/simple/custom_predicate_early_exit_planning.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Claim Boundaries

Use exact row-level wording. Keep these phrases out of broad public claims:

- "all benchmark apps are faster";
- broad V4-over-V2.14 speedup wording;
- broad V4-over-V3 speedup wording;
- public true-zero-copy claims;
- whole-application speedup claims;
- Tier-3 callback/PTX support claims;
- broad CuPy performance claims beyond explicitly named measurements;
- raw OptiX callback support claims;
- app-specific native engine/kernel claims;
- embedding, C ABI, or non-Python host binding claims.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | RTDL Python DSL/runtime source. |
| `examples/simple/` | Current runnable V4 user examples. |
| `examples/benchmark_apps/` | Source for the 10 benchmark apps. |
| `examples/paper_reproduction/` | Paper-oriented app entrypoints. |
| `tutorials/current/` | Current V4 tutorial path. |
| `docs/` | Current V4 public documentation. |
| `scripts/` | Developer and verification tools. |
| `tests/` | Regression and gate tests. |
