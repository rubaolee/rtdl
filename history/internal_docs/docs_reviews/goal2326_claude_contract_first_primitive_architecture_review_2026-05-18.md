# Goal2326 Architecture Review: Contract-First Primitive Reconstruction

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-05-18
Verdict: **accept-with-boundary**

---

## Files Reviewed

- `docs/reports/goal2326_contract_first_primitive_reconstruction_plan_2026-05-18.md`
- `src/rtdsl/execution.py`
- `src/rtdsl/primitives.py`
- `src/rtdsl/adapters/__init__.py`
- `src/rtdsl/adapters/traversal.py`
- `src/rtdsl/adapters/collection.py`
- `src/rtdsl/adapters/reductions.py`
- `src/rtdsl/adapters/columnar_payload.py`
- `src/rtdsl/adapters/partner_handoff.py`
- `src/rtdsl/adapters/prepared_handles.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl/dsl_reference.md`
- `tests/goal2326_public_primitive_contract_test.py`
- `tests/goal2326_execution_report_contract_test.py`
- `tests/goal2326_adapter_partition_test.py`
- `tests/goal2326_examples_recipe_boundary_test.py`

---

## Summary

The first Goal2326 implementation slice puts correct structural bones in place.
`ExecutionPolicy`, `ExecutionReport`, and `ExecutionResult` are well-designed and
honest. The `primitives.py` facade is genuinely generic. The adapter family split
is directionally correct and compatibility-preserving. The execution report
conservatively sets all claim-boundary flags to `False` by default.

Four specific issues must be resolved before the architecture can be declared
adopted. None of them block the direction; all of them are tractable in a
follow-on slice.

---

## Question-by-Question Findings

### 1. Does the plan keep native engines app-agnostic?

**Yes, in the plan. Partially in the implementation.**

`execution.py` dispatches to `run_cpu_python_reference`, `run_embree`,
`run_optix`, etc. by backend string, with no app-name in the dispatch path.
The plan's non-negotiable constraint ("No app-specific native engine entry
points") is architecturally satisfied by the new substrate.

However, `src/rtdsl/__init__.py` still re-exports `directed_hausdorff_2d_embree`
directly from `embree_runtime` at line 111, making it accessible as
`rt.directed_hausdorff_2d_embree`. That is an app-shaped engine entry point in
the top-level namespace. This is a slice-8 (deprecation cleanup) item, not a
blocker, but it must be tracked.

### 2. Does the public API avoid making RTDL look like a fixed app library?

**Yes for the new surface. The top-level namespace still carries legacy pollution.**

`primitives.py` exports `any_hit`, `hit_count`, `nearest`, `within_radius`,
`shape_any_hit_rows`, `shape_pair_overlap_rows`, `shape_set_similarity`, etc.
These are all generic. The guard test (`test_no_core_domain_namespace_facade`)
verifies that `rt.geo`, `rt.robotics`, `rt.road_hazard_priority`, `rt.rayjoin`,
and `rt.hausdorff` are absent as top-level names.

What the test does not check: that individually exported app-shaped symbols are
absent. `src/rtdsl/__init__.py` currently exposes:

- `RayJoinBoundedPlan`, `RayJoinFeatureServiceLayer`, `rayjoin_bounded_plans`,
  `rayjoin_feature_service_layers`, `RayJoinPublicAsset`, `rayjoin_public_assets`,
  `download_rayjoin_sample` (lines 98-103)
- `directed_hausdorff_2d_embree` (line 111)
- `app_engine_support`, `app_engine_support_matrix`, `optix_app_benchmark_readiness`,
  `optix_app_performance_support`, `rt_core_app_maturity`, `rtx_public_wording_status`,
  `public_apps`, and associated constants (lines 123-141)

A new learner running `dir(rt)` or reading IDE completions will encounter these
symbols alongside `any_hit` and `ExecutionPolicy`. The generic surface is present
but not prominent. This is acceptable as a migration state, not as a final state.

### 3. Is automatic execution explainable enough for reproducibility and claim discipline?

**Yes for honesty. The `auto` selection logic is a stub.**

`ExecutionReport` captures `requested_backend`, `selected_backend`,
`fallback_backend`, `fallback_reason`, `primitive_family`, `predicate`,
`output_schema`, `exact_mode`, `rt_core_status`, `cuda_core_partner_status`,
`cpu_status`, `claim_boundary`, and `reproducibility` (git commit, Python
version, platform, key env vars). All claim-boundary flags default to `False`.
The `rt_core_status` for OptiX is set to `"optix_selected_requires_hardware_evidence"`,
which is the correct conservative wording.

The `execution.py:162-165` `_select_backend` function resolves `backend="auto"`
to either `"optix"` (if `require_rt_core=True`) or `"cpu_python_reference"` in
all other cases. There is no capability probe — no check for whether OptiX or
Embree libraries are actually available. This is honest (the execution report
shows exactly what was selected), but users who pass `backend="auto"` expecting
the best available backend will always receive `cpu_python_reference`. The
behavior is safe; the feature is incomplete.

**Issue (boundary):** `memory_status` and `copy_status` are always
`"not_measured"` (`execution.py:259-260`). The plan requires the report to record
"host/device residency, copy mode, zero-copy/reduced-copy status." Having a field
that is permanently `"not_measured"` implies future measurement; the correct
wording for this stage would be `"runtime_layer_does_not_report"` or similar, so
readers do not assume measurement is pending when it is simply not implemented.
The `zero_copy_claim_authorized: False` in the `claim_boundary` map is the
important safety net here, and it is in place.

### 4. Are adapter module boundaries generic rather than app/domain shaped?

**Five of six are clean. One function name violates the constraint.**

`adapters/reductions.py`, `adapters/columnar_payload.py`, `adapters/collection.py`,
`adapters/partner_handoff.py`, and `adapters/traversal.py` contain only
generic-concept function names (group-by-key, columnar-payload conversion, aabb
candidates, point column conversion, hit-count columns). The `adapter_partition_test`
verifies file names contain no domain words and that the six expected modules
exist.

**Issue (blocker-grade boundary):** `adapters/prepared_handles.py` re-exports
`allocate_robot_collision_pose_partner_device_output_columns` from
`partner_adapters`. "robot" and "pose" are domain names. This function lands
inside a module that the plan describes as owning "reusable native/partner handle
lifecycle" — a generic contract. The adapter partition test only checks file
names for forbidden domain words; it does not check the exported symbol names
within each file. The function should either be renamed to remove the domain
term or moved to an explicit compatibility shim that is documented as
app-specific.

Exact file and line: `src/rtdsl/adapters/prepared_handles.py`, line 4 and the
`__all__` entry for `allocate_robot_collision_pose_partner_device_output_columns`.

### 5. Is the compatibility-preserving adapter re-export strategy safer than moving all call sites immediately?

**Yes. This is the right approach for this stage.**

Each adapter family module imports from the historical `partner_adapters.py` and
re-exports with `assertIs` identity verified in the partition test. This means:

- existing callers that import from `partner_adapters` directly still work
- the new `adapters.*` paths are available without mass refactoring
- a future slice can move the implementations one function at a time with
  `assertIs` as the regression check

No opinion on the final long-term state, but for an architecture-in-migration
this strategy is demonstrably safer than a flag-day move.

### 6. Are the new Goal2326 guard tests meaningful? What additional tests should block adoption?

**The tests are meaningful but have a scope gap that should be closed.**

**What they do correctly:**
- `goal2326_public_primitive_contract_test` checks that generic primitive names
  are present and that a specific list of domain fragments are absent from
  `primitives.__all__`
- `goal2326_execution_report_contract_test` actually runs a kernel end-to-end
  via `rt.run(...)` and asserts on every major report field including claim
  boundary flags and reproducibility keys
- `goal2326_adapter_partition_test` verifies file names and uses `assertIs` to
  confirm re-export identity, not just presence
- `goal2326_examples_recipe_boundary_test` scans all example files for forbidden
  import tokens and verifies the plan document and DSL reference both contain the
  required contract-first phrases

**What is missing or should be added:**

1. **Top-level app-symbol audit test**: A test that scans `dir(rtdsl)` (or
   `rtdsl.__all__` if/when defined) for the same domain-word fragments checked
   in the primitives facade test. Currently `rt.directed_hausdorff_2d_embree`,
   `rt.RayJoinBoundedPair`, and `rt.optix_app_benchmark_readiness` would pass
   the guard but violate the architecture intent.

2. **`adapters` exported symbol scan**: A test that iterates each adapter module's
   `__all__` and checks for the same domain-word forbidden list that the file-name
   check uses. This would have caught the `allocate_robot_collision_pose_*` issue
   automatically.

3. **`backend="auto"` capability probe test**: A test that calls `rt.run(...)` with
   `backend="auto"` on a platform where Embree or OptiX are available and verifies
   the report reflects the better backend — or explicitly asserts that the current
   auto-selection is `cpu_python_reference` with a note that capability detection
   is not yet implemented.

4. **`memory_status` / `copy_status` field sentinel test**: A test that asserts
   the field values are an explicit sentinel string (not `"not_measured"`) when
   the runtime does not support measurement. This prevents the fields from being
   accidentally quoted in external reports as if they were measured.

---

## Specific Blockers and Minimal Fixes

### Blocker 1: Domain name in generic adapter module

**File:** `src/rtdsl/adapters/prepared_handles.py`, line 4
**Symbol:** `allocate_robot_collision_pose_partner_device_output_columns`

**Minimal fix:** Rename to a generic term such as
`allocate_pose_query_partner_device_output_columns` in `partner_adapters.py` (or
whatever the source name is) and update the re-export, OR move this function to
an explicitly app-scoped compatibility shim outside the `adapters.*` generic
family. The adapter partition test must then be extended to scan exported names.

### Boundary 1: `memory_status` / `copy_status` sentinel wording

**File:** `src/rtdsl/execution.py`, lines 259-260

**Minimal fix:** Replace `"not_measured"` with a string like
`"not_reported_by_runtime"` that does not imply future measurement is pending.

### Boundary 2: Guard test scope gap

**Test file:** `tests/goal2326_public_primitive_contract_test.py`

**Minimal fix:** Add a test that scans exported names in each `adapters.*`
module's `__all__` for the domain-word forbidden list (same fragments used in
the file-name scan).

---

## Verdict

**accept-with-boundary**

The architecture direction is correct and the first slice is solid enough to
proceed. The `ExecutionPolicy`/`ExecutionReport` substrate is honest and
conservative on all claim boundaries. The generic primitive facade is clean. The
compatibility-preserving re-export approach is the right migration strategy.

The four boundary conditions below must be met before the architecture is
declared adopted for release governance. None of them require redesign — they
are each a small, targeted change:

| # | Boundary | Location | Severity |
|---|----------|----------|----------|
| 1 | Remove domain name `robot`/`pose` from `adapters/prepared_handles.__all__` | `src/rtdsl/adapters/prepared_handles.py:4` | Must fix before adoption |
| 2 | Extend adapter partition test to scan exported symbol names, not only file names | `tests/goal2326_adapter_partition_test.py` | Must fix before adoption |
| 3 | Replace `"not_measured"` with an explicit non-measurement sentinel string | `src/rtdsl/execution.py:259-260` | Must fix before adoption |
| 4 | Add top-level `rtdsl` namespace scan for app-shaped function names | new guard test | Should fix before adoption |

The following are out-of-scope for this slice per the plan and are not required
for the adoption gate:

- `backend="auto"` capability detection (acknowledged incomplete, honest in report)
- Full migration of `__init__.py` top-level app exports (slice 8, compatibility)
- `memory_status` / `copy_status` actual measurement (future native work)

---

## Boundaries Not Authorized

This review does not authorize:
- v2.0 release readiness
- Public speedup claims
- RT-core utilization claims
- Zero-copy transfer claims

The execution report's `claim_boundary` map correctly reflects these as
unauthorized for every code path in the current implementation.
