# Current V4 Status

V4.0 is the current RTDL user surface for Python eDSL/operator-pushdown work on
generic RT-core operators, V2/V3-compatible benchmark routes, and constrained
user predicates.

Status:

```text
complete_rt_core_app_matrix__bounded_material_wins__antigravity_public_tag_approved__clean_wheel_smoke_passed__tag_target_ready
```

## User Promise

V4 gives users a clean Python front door for reusable RT-shaped GPU work:

- V4 is a V2/V3 superset. Existing V2.14/V3 routes remain part of the usable
  system when they are the best route for a task.
- V4 adds measured generic operator surfaces that accept GPU arrays and avoid
  Python row-object hot paths where the surface says so.
- Users choose partners explicitly. Current measured partner scopes include
  Torch CUDA, CuPy where explicitly named, Numba for constrained predicates and
  selected graph/continuation work, and RTDL native prepared runners.
- Unsupported complex callbacks fail closed or remain V4.1/Tier-3 work.

## 10-App RT-Core Matrix

Goal4756 completed the serious POD matrix on NVIDIA RTX A5000:

| Metric | Result |
| --- | --- |
| Apps | `10/10` |
| Version rows | `30/30` |
| V2.14/V3.0.2/V4.0 row for every app | `true` |
| Primary denominator | NVIDIA OptiX/RT-core only |
| Embree primary denominator | `false` |
| Hot-path regressions in Goal4756 table | `0` |
| Material hot-path candidates over V2.14 | `triangle_counting`, `barnes_hut` |
| V4/V2.14 hot geomean | `2.10069x`, not a headline |

The current app-level table is in
[app_level_benchmark_summary.md](app_level_benchmark_summary.md).
The compact external-review evidence manifest is in
[../future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md](../future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md).

Supplemental Barnes-Hut evidence: the native RT-BarnesHut author-semantics
route is checksum-valid at 10M and wins on comparable internal program time
with full phase accounting. This does not authorize public paper-reproduction
or no-copy tree-build wording.

## Operator/Workflow Surfaces

The Goal4639 scorecard passed for the documented operator surfaces: `8/8`
surfaces and `4/4` strong families passed. In the release wording guide,
most measured operators are 1.2x-1.7x against their stated brute-force partner/CPU baselines;
point-group nearest witness and AABB all-ops are large scale-dependent
algorithmic-complexity wins. These rows do not authorize a whole-application
speedup claim.

Baseline / denominator is part of every valid performance statement.

V4 also exposes measured generic operator/workflow surfaces, including:

- fixed-radius count-threshold;
- closest-hit grouped argmin;
- ray/triangle any-hit flags;
- primitive grouped-i64 reduction;
- point-group nearest witness;
- ray/triangle any-hit weighted sum;
- fixed-radius graph component union;
- AABB all-ops count;
- aggregate-frontier device columns;
- constrained Numba Custom predicate early-exit.

These are not blanket all-app claims. Each surface has its own denominator,
partner scope, scale, and claim boundary.

## Boundary

Allowed:

- "V4.0 is a Python eDSL/operator-pushdown release candidate and V2/V3
  superset."
- "The 10-app RT-core matrix is complete for V2.14, V3.0.2, and V4.0."
- "V4.0 has two material hot-path candidate wins over V2.14 and parity/control
  elsewhere in Goal4756."
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

V4 Python eDSL/operator-pushdown release candidate surface available; the
current V4 measured operator/workflow surface count is
`10`.

## External Review Update

Antigravity reviewed the consolidated Gemini-style full-coverage V4 packet and
returned:

```text
approve_close_gemini_debt_and_allow_v4_0_public_tag
```

Review path:

- `future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md`

The bounded V4.0 public tag is externally authorized under the framing above.
The release target must be a clean committed tree with clean-checkout and
installed-wheel smoke validation. Do not tag a dirty or stale `HEAD`.

Packaging progress:

- Goal4774 created the dirty-tree packaging audit.
- Goal4775 created a file-level staging manifest and pathspec for the intended
  V4 release commit.
- Goal4776 clean-checkout installed-wheel smoke passed on the release-candidate
  commit before tag creation.
- Current machine status: clean release commit target ready for bounded V4.0
  public tag creation.
- Post-Goal4775 full V4 local discovery: `Ran 645 tests in 94.691s`,
  `OK (skipped=1)`.

## Start Command

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```
