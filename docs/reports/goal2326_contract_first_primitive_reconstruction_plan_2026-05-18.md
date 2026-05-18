# Goal2326: Contract-First RTDSL Primitive Reconstruction Plan

Status: `closed-accept-with-boundary`

Date: 2026-05-18

## Purpose

Goal2244 correctly identified the "1000 functions" usability problem, but its
initial solution risked turning RTDL into an app-shaped facade. This goal
recasts the architecture around a stricter rule:

**RTDL is not an app library. RTDL is a language/runtime for composing
accelerated application logic from generic spatial, graph, row, columnar, and
partner contracts.**

The implementation goal is to reconstruct the public primitive surface,
internal adapter organization, dispatch path, examples, docs, and tests so that
users see a learnable generic language while app-specific policy remains in
examples, recipes, tutorials, and user code.

## Design Decision

Adopt the layering idea from Goal2244, but replace the app/domain facade with a
contract-first architecture:

| Layer | Public? | Rule |
| --- | --- | --- |
| Public RTDSL primitives | yes | Generic contracts only: data layouts, traversal, predicates, collection, reductions, grouping, partner handoff, execution policy |
| Recipes and applications | yes, but outside core | Domain examples such as Hausdorff, RayJoin, road hazard, DBSCAN, facility assignment, and graph analytics live in examples/docs/recipes |
| Execution planner | yes via reports | Backend/partner selection must be explainable, reproducible, and claim-boundary-aware |
| Internal adapters | no | Flat, explicit, performance-oriented functions grouped by generic contract family, not app family |
| Native engines | no user app semantics | Engines remain app-name-free and app-domain-free |

## Non-Negotiable Constraints

- No public core API like `rtdsl.geo.road_hazard_priority(...)`.
- No app-specific native engine entry points.
- No silent automatic backend choice that cannot be reproduced.
- No public speedup, RT-core, or zero-copy wording without an execution report
  and reviewed evidence.
- Existing v2.0 examples must keep running while the surface is migrated.
- Existing low-level adapter names may remain internally verbose, but they must
  not be the user-facing learning path.

## Target Public Shape

The public surface should be organized around generic concepts:

```python
import rtdsl as rt

policy = rt.ExecutionPolicy(
    backend="auto",
    partner="cupy",
    allow_fallback=True,
    require_rt_core=False,
    explain=True,
)

result = rt.run(
    kernel,
    inputs={
        "queries": query_points,
        "shapes": shapes,
    },
    execution=policy,
)

print(result.rows)
print(result.execution_report)
```

The execution report must include:

| Field family | Required meaning |
| --- | --- |
| backend | requested backend, selected backend, fallback backend if any |
| partner | requested partner, selected partner, unavailable-partner reason if any |
| memory | host/device residency, copy mode, zero-copy/reduced-copy status |
| acceleration | RT-core path status, CUDA-core partner status, CPU fallback status |
| contract | primitive family, output schema, exact/approximate mode |
| claim boundary | which performance/public claims are authorized or blocked |
| reproducibility | commit, platform summary when available, important env vars |

## Target Internal Organization

Split `src/rtdsl/partner_adapters.py` and related flat helper surfaces into
generic contract-family modules. Exact filenames may evolve during
implementation, but the target ownership is:

| Module family | Owns |
| --- | --- |
| `rtdsl.adapters.traversal` | any-hit, closest-hit, hit-count, witness traversal wrappers |
| `rtdsl.adapters.collection` | bounded collect, collect-k, candidate streaming wrappers |
| `rtdsl.adapters.reductions` | row reductions, grouped reductions, device/partner reductions |
| `rtdsl.adapters.columnar_payload` | columnar payload construction, prepared handles, scan/reduction wrappers |
| `rtdsl.adapters.partner_handoff` | NumPy/CuPy/PyTorch/DLPack handoff and validation |
| `rtdsl.adapters.prepared_handles` | reusable native/partner handle lifecycle |
| `rtdsl.execution` | `ExecutionPolicy`, `ExecutionReport`, planner, fallback reasons |
| `rtdsl.recipes` | optional generic recipes only; app recipes stay in docs/examples unless explicitly reviewed |

Disallowed internal grouping names include app/domain files such as
`geo_analytics.py`, `road_hazard.py`, `rayjoin.py`, or `hausdorff.py` inside the
core adapter layer.

## Migration Slices

This work must be executed in small, reviewable slices:

| Slice | Goal | Expected code movement |
| --- | --- | --- |
| 1. Inventory | Produce public/internal surface inventory | scan exported `rtdsl` symbols, example imports, adapter call sites, app-shaped names |
| 2. Execution report substrate | Add `ExecutionPolicy` and `ExecutionReport` without changing behavior | new `rtdsl.execution` module plus tests |
| 3. Adapter package skeleton | Create `rtdsl.adapters.*` modules with compatibility re-exports | move or wrap contract families while preserving existing callers |
| 4. Public primitive facade | Add generic public helpers over existing kernels/adapters | no app-shaped public names |
| 5. Example migration | Update v2.0 examples to use generic public facade where useful | apps remain in `examples/v2_0/apps` and `research_benchmarks` |
| 6. Documentation migration | Rewrite learner/API docs around contract primitives | app tutorials link to recipes/examples, not core app APIs |
| 7. Guard tests | Add scans that prevent app-shaped core facade and silent dispatch | fail on domain facade regressions |
| 8. Deprecation cleanup | Preserve or remove old import paths according to compatibility policy | document any compatibility re-exports |

## Acceptance Criteria

Goal2326 is complete only when all criteria below are satisfied:

| Area | Acceptance rule |
| --- | --- |
| Public API | Learner-facing docs introduce generic RTDL primitives before apps |
| App boundary | App names and domain policies live in examples, tutorials, recipes, or tests, not in core public primitive modules |
| Execution | Any auto/backend-selection path can emit an `ExecutionReport` |
| Claim discipline | Execution reports explicitly distinguish RT-core, CUDA-core partner, CPU, zero-copy, reduced-copy, and fallback paths |
| Adapter layout | Internal adapter files are grouped by generic contract family |
| Compatibility | Existing v2.0 examples and current public tutorial commands still run |
| Tests | New guard tests prevent app-shaped public facade names and invisible dispatch |
| Docs | API/IR/tutorial docs explain the contract-first architecture without historical clutter |

## Required Tests

Add or update tests with these responsibilities:

| Test | Purpose |
| --- | --- |
| `tests.goal2326_public_primitive_contract_test` | verifies public RTDSL facade exposes generic primitive contracts and avoids app-shaped core names |
| `tests.goal2326_execution_report_contract_test` | verifies every explicit/auto execution path can explain backend, partner, fallback, memory, and claim boundary |
| `tests.goal2326_adapter_partition_test` | verifies adapter modules are grouped by generic family and do not introduce app/domain adapter modules |
| `tests.goal2326_examples_recipe_boundary_test` | verifies apps/research benchmarks import public primitives or documented internal compatibility paths, not app-shaped core facades |
| tutorial smoke tests | verifies v2.0 learner commands still work after migration |
| focused app tests | verifies Hausdorff, RayJoin, fixed-radius, polygon, database, graph, and partner examples keep parity |

Implementation should also run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2326_public_primitive_contract_test tests.goal2326_execution_report_contract_test tests.goal2326_adapter_partition_test tests.goal2326_examples_recipe_boundary_test
PYTHONPATH=src:. python3 -m unittest tests.goal2324_examples_v2_0_directory_reorganization_test
PYTHONPATH=src:. python3 -m compileall -q src examples/v2_0
```

Windows equivalent:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2326_public_primitive_contract_test tests.goal2326_execution_report_contract_test tests.goal2326_adapter_partition_test tests.goal2326_examples_recipe_boundary_test
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2324_examples_v2_0_directory_reorganization_test
$env:PYTHONPATH='src;.'; py -3 -m compileall -q src examples/v2_0
```

## Review And Consensus

Because this changes the language architecture and public API direction, it is
a key architecture goal and requires 3-AI consensus before being declared
adopted:

| Reviewer | Required output |
| --- | --- |
| Codex | implementation plan/report and local tests |
| Claude | `docs/reviews/goal2326_claude_contract_first_primitive_architecture_review_2026-05-18.md` |
| Gemini | `docs/reviews/goal2326_gemini_contract_first_primitive_architecture_review_2026-05-18.md` |
| Consensus | `docs/reports/goal2326_contract_first_primitive_architecture_consensus_2026-05-18.md` |

Reviewers must answer:

1. Does the plan keep native engines app-agnostic?
2. Does the public API avoid making RTDL look like a fixed app library?
3. Is automatic execution explainable enough for reproducibility and public
   claim discipline?
4. Are adapter module boundaries generic rather than app/domain shaped?
5. Are the migration slices small enough to implement safely?
6. What tests must block adoption if the architecture regresses?

## Out Of Scope

- Triton/Numba integration.
- v3.0 custom shader extension APIs.
- New native primitive performance tuning.
- Moving release tags.
- Rewriting historical reports.

Any future-version implications discovered during this work must also be added
to `docs/research/future_version_to_do_list.md`.

## Executor Guidance

Start with the inventory and execution report substrate. Do not begin by moving
hundreds of adapter call sites. The first implementation slice should make the
current system more explainable while preserving behavior; only then split the
adapter modules and migrate examples/docs.

The intended end state is a language that feels small and learnable at the top,
explicit and reproducible in the middle, and performance-direct internally -
without ever putting app customization inside the RTDL engine.

## Local Implementation Slice Completed

The first Goal2326 implementation slice is now in place:

| Area | Local change |
| --- | --- |
| Execution substrate | Added `src/rtdsl/execution.py` with `ExecutionPolicy`, `ExecutionReport`, `ExecutionResult`, and `run(...)` |
| Public primitive facade | Added `src/rtdsl/primitives.py` with generic aliases such as `any_hit`, `hit_count`, `nearest`, `within_radius`, `shape_any_hit_rows`, and `shape_pair_overlap_rows` |
| Top-level exports | Exposed the contract-first execution and primitive facade from `rtdsl.__init__` |
| Adapter skeleton | Added `src/rtdsl/adapters/` modules grouped by generic contract family: traversal, collection, reductions, columnar payload, partner handoff, and prepared handles |
| Docs | Updated `docs/rtdl/dsl_reference.md` with the contract-first public surface and execution-report boundary |
| Guard tests | Added the four Goal2326 tests named above |

The adapter split is compatibility-preserving: the new adapter-family modules
re-export selected functions from the historical flat `partner_adapters.py`
instead of moving hundreds of call sites in one risky patch.

## Local Validation

Windows local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2326_public_primitive_contract_test tests.goal2326_execution_report_contract_test tests.goal2326_adapter_partition_test tests.goal2326_examples_recipe_boundary_test
$env:PYTHONPATH='src;.'; py -3 -m compileall -q src\rtdsl tests\goal2326_public_primitive_contract_test.py tests\goal2326_execution_report_contract_test.py tests\goal2326_adapter_partition_test.py tests\goal2326_examples_recipe_boundary_test.py
```

Result: `10` Goal2326 tests pass; compileall passes.

## Remaining Adoption Gate

This local implementation did not by itself complete the architecture-adoption
decision. Because Goal2326 changes language direction and public API shape, it
required Claude and Gemini architecture reviews plus the consensus file before
the architecture could be considered accepted for release governance.

## External Review Resolution

| Reviewer | Artifact | Verdict | Resolution |
| --- | --- | --- | --- |
| Claude | `docs/reviews/goal2326_claude_contract_first_primitive_architecture_review_2026-05-18.md` | `accept-with-boundary` | Found one blocker-grade adapter export leak plus guard-test/sentinel boundaries; Codex fixed the blocker and strengthened the tests |
| Gemini | `docs/reviews/goal2326_gemini_contract_first_primitive_architecture_review_2026-05-18.md` | `accept-with-boundary` | Accepted the direction with future enforcement boundaries |
| Gemini follow-up | `docs/reviews/goal2326_gemini_followup_post_fix_review_2026-05-18.md` | `accept-with-boundary` | Verified the post-review fixes and the bounded legacy top-level compatibility surface |
| Consensus | `docs/reports/goal2326_contract_first_primitive_architecture_consensus_2026-05-18.md` | `accept-with-boundary` | Closes Goal2326 as an accepted contract-first architecture slice, not as a v2.0 release authorization |

Post-review fixes:

| Issue | Fix |
| --- | --- |
| App-shaped prepared-handle re-export | Removed `allocate_robot_collision_pose_partner_device_output_columns` from `rtdsl.adapters.prepared_handles` |
| Adapter test only scanned filenames | Extended `tests.goal2326_adapter_partition_test` to scan adapter `__all__` symbols for forbidden app/domain fragments |
| Ambiguous `not_measured` sentinel | Changed `memory_status` and `copy_status` to `not_reported_by_runtime` and covered the value in the execution-report test |
| Historical top-level namespace visible in `dir(rtdsl)` | Added a curated `__dir__()` that teaches the contract-first v2 surface first while preserving explicit legacy imports |

Final local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2326_public_primitive_contract_test tests.goal2326_execution_report_contract_test tests.goal2326_adapter_partition_test tests.goal2326_examples_recipe_boundary_test tests.goal2324_examples_v2_0_directory_reorganization_test tests.goal1765_github_learner_readiness_double_check_test
$env:PYTHONPATH='src;.'; py -3 -m compileall -q src\rtdsl examples\v2_0 tests\goal2326_public_primitive_contract_test.py tests\goal2326_execution_report_contract_test.py tests\goal2326_adapter_partition_test.py tests\goal2326_examples_recipe_boundary_test.py
```

Result: `20` focused tests pass; compileall passes.
