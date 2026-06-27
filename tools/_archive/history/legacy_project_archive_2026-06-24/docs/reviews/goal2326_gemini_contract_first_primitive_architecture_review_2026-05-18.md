# Goal2326 Gemini Contract-First Primitive Architecture Review

Date: 2026-05-18

Reviewer: Gemini

Verdict: `accept-with-boundary`

Note: Gemini produced this review in `scratch/goal2326_gemini.out` but returned
the markdown as text instead of directly writing the target file. Codex saved
the review here and normalized Gemini's verdict spelling from
`accepted-with-boundary` to the project-approved value `accept-with-boundary`.

## Review Questions And Answers

### 1. Does the implemented slice keep native engines app-agnostic?

Yes, the implemented slice successfully keeps native engines app-agnostic. The
plan explicitly mandates this by stating that RTDL is not an app library and
that engines must remain app-name-free and app-domain-free. The
`src/rtdsl/execution.py` module dispatches to generic backend runners such as
`run_embree` and `run_optix` without embedding app-specific logic. Furthermore,
the `src/rtdsl/adapters/*` modules are intentionally named by generic contract
families such as `traversal` and `collection`, and a guard test
(`tests/goal2326_adapter_partition_test.py`) specifically checks for and
forbids app-specific fragments in adapter module names.

### 2. Does the new public `rtdsl.primitives` facade avoid making RTDL look like a fixed app library?

Yes, the new public `rtdsl.primitives` facade effectively avoids making RTDL
look like a fixed app library. The `src/rtdsl/primitives.py` module exposes
generic, contract-based operations such as `any_hit`, `nearest`, and
`shape_any_hit_rows`, rather than app-specific functions like
`road_hazard_priority`. The `tests/goal2326_public_primitive_contract_test.py`
explicitly verifies that these names are generic and that no app-specific names
such as `rayjoin` or `hausdorff` are exposed through `rtdsl.primitives` or at
the top-level `rt` import. The `docs/rtdl/dsl_reference.md` also clearly
articulates this contract-first approach, emphasizing generic primitives over
app-specific ones.

### 3. Is `ExecutionPolicy` / `ExecutionReport` explainable enough for reproducibility and public claim discipline?

Yes, `ExecutionPolicy` and `ExecutionReport` are designed to be highly
explainable, fostering reproducibility and public claim discipline. The
`ExecutionReport` dataclass in `src/rtdsl/execution.py` includes a
comprehensive set of fields that precisely detail the execution path, including
`requested_backend`, `selected_backend`, `fallback_backend`, `fallback_reason`,
`primitive_family`, `output_schema`, and crucially, a `claim_boundary`
dictionary and a `reproducibility` summary with `git_commit`, Python version,
platform, and environment variables. The `claim_boundary` fields are set
conservatively to `False` by default for performance claims, enforcing a
discipline that requires explicit evidence. The
`tests/goal2326_execution_report_contract_test.py` validates that these reports
are generated with the expected, conservative values, and
`docs/rtdl/dsl_reference.md` guides users on their purpose.

### 4. Are `src/rtdsl/adapters/*` module boundaries generic rather than app/domain shaped?

Yes, the `src/rtdsl/adapters/*` module boundaries are generic. The target
internal organization in the plan explicitly states the goal of grouping
modules by generic contract families such as `traversal`, `collection`, and
`reductions`, and disallows app/domain-specific names such as
`geo_analytics.py` or `rayjoin.py`. The `src/rtdsl/adapters/__init__.py`
module's `__all__` list and docstring reflect this generic grouping. The
`tests/goal2326_adapter_partition_test.py` successfully enforces this by
checking module names against a list of forbidden app/domain fragments.

### 5. Is the compatibility-preserving adapter re-export strategy safer than moving all call sites immediately?

Yes, the compatibility-preserving adapter re-export strategy is significantly
safer than immediately moving all call sites. The plan describes this as a
deliberate migration slice to preserve existing callers and avoid a risky
patch. Each new adapter module in `src/rtdsl/adapters/` imports and re-exports
specific functions from the historical `src/rtdsl/partner_adapters.py`. The
`tests/goal2326_adapter_partition_test.py` includes a test
(`test_reexports_preserve_existing_low_level_functions`) that confirms the
re-exported functions are indeed the same objects as the original ones,
ensuring seamless backward compatibility for existing codebases during the
transition.

### 6. Are the new Goal2326 guard tests meaningful, and what additional tests should block adoption later?

The new Goal2326 guard tests are meaningful and effectively enforce the
architectural principles:

- `tests/goal2326_public_primitive_contract_test.py` is crucial for preventing
  app-shaped public APIs.
- `tests/goal2326_execution_report_contract_test.py` ensures the explainability
  and claim discipline of execution reports.
- `tests/goal2326_adapter_partition_test.py` safeguards the generic naming and
  structure of internal adapter modules.
- `tests/goal2326_examples_recipe_boundary_test.py` prevents examples from
  importing app-shaped core facades, enforcing the separation of concerns.

Additional tests that should block adoption later:

- Strict claim-discipline enforcement: implement tests or tooling that actively
  prevents or flags attempts to assert claims such as zero-copy speedup when
  the corresponding `claim_boundary` flag in the `ExecutionReport` is `False`.
- New-code import policy enforcement: introduce static analysis or tests to
  ensure that new code outside `src/rtdsl/adapters/*` does not directly import
  from `rtdsl.partner_adapters.py`, and instead uses the new generic adapter
  modules or `rtdsl.primitives`.
- Cross-engine functional equivalence: develop tests that verify functional
  equivalence within acceptable tolerances of generic primitive executions
  across CPU, Embree, OptiX, and other backends, so app-agnosticism extends to
  behavior.

## Justification For Verdict

Goal2326 represents a significant and well-executed architectural refactor. The
plan is clear, the implementation adheres closely to the plan's principles, and
the guard tests are robust in verifying the core architectural invariants. The
shift to a contract-first architecture with app-agnostic engines, a generic
public primitive facade, explainable execution reports, and generic adapter
modules creates a much stronger and more maintainable foundation for RTDL.

The boundary acknowledges that while the core implementation is sound, there
are areas for further strengthening and enforcement of these architectural
principles. The additional tests outlined above are not blockers for the current
architectural change but are important for ensuring continued discipline and
the long-term success of the contract-first approach as the project evolves.
