# RTDL V4

RTDL V4 is the current RTDL user surface for measured generic RT-core
operators.

Status: RTDL V4.0.0 is a bounded operator release: 8 documented generic RT-core
operators are faster than their stated brute-force partner/CPU baselines on the
frozen Goal4639 scorecard.

## What RTDL Is

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, nearest-neighbor screening, collision checks, graph-style
queries, and database-like summaries.

The V4 contract is:

```text
Python owns the application.
RTDL owns generic RT-shaped fused operators.
Users choose measured partners explicitly.
Unsupported custom logic fails closed instead of becoming an unsafe callback.
```

The Python package is `rtdsl`.

## What V4 Adds

V4 promotes RTDL from a prepared-runtime capability surface into a measured
generic RT-core operator lane:

- one import: `import rtdsl.v4 as rtdl_v4`;
- eight measured Tier-2 operator surfaces;
- measured partner scopes: Torch CUDA, Numba, and RTDL native prepared runner;
- no current Tier-2 candidates in the public front door;
- a conservative callback/operator planner for complex user logic;
- a serious Goal4639 scorecard pass: `8/8` measured surfaces and `4/4`
  strong benchmark families passed.
- final 3-AI publication authorization for the narrow V4.0.0 operator release.

The honest Goal4639 distribution is:

- most measured operators are 1.2x-1.7x faster than their stated
  brute-force partner/CPU baselines;
- ray/triangle any-hit flags is a larger `5.671x` operator win against its
  Torch reference baseline;
- point-group nearest witness (`389.707x`) and AABB all-ops (`164.716x`) are
  large scale-dependent algorithmic-complexity wins where the alternative is
  brute force or a slower same-contract index control.

Do not use the raw geomean as a headline. These are operator-scorecard rows
with explicit denominators, not whole-application speedup claims and not
near-hand-written-OptiX claims.

## Start Here

Run from the repository root.

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

The quickstart prints JSON with the current V4 front-door status, measured
surface count, partner list, and claim-boundary flags.

## Current User Paths

| Path | Use |
| --- | --- |
| [docs/README.md](docs/README.md) | Current V4 documentation index. |
| [docs/current_v4_status.md](docs/current_v4_status.md) | V4 status, scorecard summary, and claim boundaries. |
| [tutorials/current/README.md](tutorials/current/README.md) | Short V4 learning path. |
| [examples/README.md](examples/README.md) | Runnable V4 examples. |
| [future/v4/tier2_operator_catalog.md](future/v4/tier2_operator_catalog.md) | Measured operator catalog and exact scope. |
| [docs/learn/performance_wording.md](docs/learn/performance_wording.md) | Performance wording guide. |

## Non-Claims

This front page authorizes the V4.0.0 operator release above. It does not
authorize:

- broad "V4 is faster for everything" wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy claims;
- Tier-3 callback/PTX support claims;
- raw OptiX callback support;
- CuPy performance claims;
- embedding, C ABI, or non-Python host binding claims;
- app-specific native engine kernels.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | RTDL Python DSL/runtime source. |
| `examples/v4/` | Current runnable V4 user examples. |
| `future/v4/` | V4 operator docs, evidence, and release-hardening records. |
| `tutorials/current/` | Current V4 tutorial path. |
| `docs/` | Current V4 public documentation. |
| `scripts/` | Developer and verification tools. |
| `tests/` | Regression and gate tests. |
