# RTDL V4

RTDL V4 is the current Python eDSL/operator-pushdown surface for generic
RT-core work on NVIDIA GPUs.

V4 is a V2/V3 superset: existing V2.14 and V3 routes remain part of the usable
system, and V4 adds measured generic operator surfaces plus constrained
predicate pushdown.

## Current Status

Status:

```text
V4.0 tag target ready, complete 10-app RT-core matrix, external public-tag review approved under bounded framing, clean wheel smoke passed
```

Goal4756 completed the serious NVIDIA RTX A5000 POD matrix:

- `10/10` promoted benchmark apps;
- `30/30` V2.14/V3.0.2/V4.0 rows executed successfully;
- all rows returned parseable JSON;
- Embree is not used as a primary denominator;
- no `n/a` rows;
- no hot-path regressions in the Goal4756 table;
- material hot-path candidates over V2.14: `triangle_counting`,
  `barnes_hut`;
- V4/V2.14 hot geomean: `2.10069x`, not a headline.

Read [docs/app_level_benchmark_summary.md](docs/app_level_benchmark_summary.md)
before making any app-level performance claim.

Final release-review evidence is indexed in
[future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md](future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md).
The consolidated Antigravity review
[future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md](future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md)
authorizes the bounded public V4.0 tag. The tag target must be a clean release
commit verified by clean checkout and installed-wheel smoke, not an uncommitted
worktree.

Supplemental Barnes-Hut evidence: RTDL V4 has a checksum-valid native
RT-BarnesHut author-semantics route at 10M and an apples-to-apples
internal-program win over the authors' binary after full phase accounting. This
remains bounded evidence: it does not authorize public paper-reproduction
wording, no-copy tree-build wording, or broad all-app speedup claims.

## What RTDL Is

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, nearest-neighbor screening, collision checks, graph-style
queries, and database-like summaries.

The V4 contract is:

```text
Python owns the application.
RTDL owns generic RT-shaped fused operators and prepared routes.
Users choose measured partners explicitly.
Unsupported custom logic fails closed or remains V4.1/Tier-3 work.
```

The Python package is `rtdsl`.

## What V4 Adds

- one import: `import rtdsl.v4 as rtdl_v4`;
- V2/V3-compatible app routes under a single current front door;
- measured generic RT-core operator/workflow surfaces;
- explicit partner scopes for Torch CUDA, CuPy where named, Numba where named,
  and RTDL native prepared runners;
- constrained custom predicate early-exit for the measured Numba workflow;
- clear claim boundaries for app rows, operator rows, and future V4.1 callback
  work.

V4 does not claim that every historical benchmark app is faster. It does claim
that the current 10-app RT-core matrix is complete and that V4 has bounded,
measured value over V2.14 in the documented rows.

For operator surfaces, most measured operators are 1.2x-1.7x against their
stated brute-force partner/CPU baselines; point-group nearest witness and AABB
all-ops are large scale-dependent algorithmic-complexity wins. These operator
rows are separate from the 10-app matrix and must keep their denominators.

## Current User Paths

| Path | Purpose |
| --- | --- |
| [docs/README.md](docs/README.md) | Current V4 documentation index. |
| [docs/current_v4_status.md](docs/current_v4_status.md) | V4 status, user promise, and boundaries. |
| [docs/app_level_benchmark_summary.md](docs/app_level_benchmark_summary.md) | Complete Goal4756 V2.14/V3.0.2/V4.0 app matrix summary. |
| [tutorials/current/README.md](tutorials/current/README.md) | Short V4 learning path. |
| [examples/README.md](examples/README.md) | Runnable V4 examples. |
| [future/v4/tier2_operator_catalog.md](future/v4/tier2_operator_catalog.md) | Measured operator catalog and exact scope. |
| [docs/learn/performance_wording.md](docs/learn/performance_wording.md) | Performance wording guide. |

## Start Here

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\custom_predicate_early_exit_planning.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/v4/custom_predicate_early_exit_planning.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Non-Claims

This front page does not authorize:

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
| `examples/v4/` | Current runnable V4 user examples. |
| `future/v4/` | V4 operator docs, evidence, and release-hardening records. |
| `tutorials/current/` | Current V4 tutorial path. |
| `docs/` | Current V4 public documentation. |
| `scripts/` | Developer and verification tools. |
| `tests/` | Regression and gate tests. |
