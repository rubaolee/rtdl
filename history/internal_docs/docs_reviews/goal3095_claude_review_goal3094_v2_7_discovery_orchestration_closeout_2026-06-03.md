# Goal3095: Claude Review of Goal3094 — v2.7 Primitive Discovery / Orchestration Closeout

Date: 2026-06-03
Reviewer: Claude (Sonnet 4.6)
Reviewed artifact: `docs/reports/goal3094_v2_7_primitive_discovery_orchestration_closeout_2026-06-03.md`
Verdict: **accept**

---

## Scope and Method

Read-only audit of Goal3094 against five review questions. Files inspected:

- `docs/reports/goal3094_v2_7_primitive_discovery_orchestration_closeout_2026-06-03.md`
- `docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/primitive_catalog.py`
- `src/rtdsl/primitive_recipes.py`
- `src/rtdsl/primitive_planner.py`
- `tests/goal3094_v2_7_primitive_discovery_orchestration_closeout_test.py`

Validation not directly executable in this session (environment restriction). All
numerical claims in the snapshot were cross-checked against source manually.

---

## Q1: Does the closeout accurately map D-1 through D-7 to implemented and reviewed artifacts?

**Yes.**

| Item | Claimed artifacts | Source verification |
| --- | --- | --- |
| D-1 | Goal3070/Goal3072 | `PrimitiveHierarchyNode` has all eight new fields (`capability_tags`, `aliases`, `intent_phrases`, `reference_path`, `backends`, `partner_ops`, `considered_alternatives`, `distinct_from`); `to_dict()` serializes all of them; `PRIMITIVE_CAPABILITY_TAGS` vocabulary is present and closed. |
| D-2 | Goal3090/Goal3093 | Every node at `stable_primitive`, `stable_behavior`, `stable_compatibility_path`, or `candidate_behavior` status carries non-empty `capability_tags`, `aliases`, `intent_phrases`, `reference_path`, and `backends`. Verified by hand against all 25 qualifying nodes in `PRIMITIVE_HIERARCHY`. |
| D-3 | Goal3070/Goal3072 | `primitive_discovery.py` exports `primitive_index()`, `find_primitive()`, `describe_primitive()`, and `lint_new_primitive()`. Ranking is exactly the three-tier order (facet → alias/phrase → body text) specified in the design. |
| D-4 | Goal3087/Goal3089 | `lint_new_primitive()` fails closed when a candidate shares key facets with an existing node and `distinct_from` is empty. `validate_primitive_hierarchy(enforce_promotion_metadata=True, ...)` applies the same gate inside the hierarchy. |
| D-5 | Goal3073/Goal3074 | `primitive_catalog.py` renders the catalog from the Python hierarchy; a drift test exists at `tests/goal3073_v2_7_generated_primitive_catalog_test.py`. |
| D-6 | Goal3077/Goal3078/Goal3079 | `primitive_recipes.py` defines `CompositionRecipe`, `COMPOSITION_RECIPES` (5 recipes), `find_recipe()`, `recipe_index()`, and `describe_recipe()`. |
| D-7 | Goal3081/Goal3083 | `primitive_planner.py` implements `plan_continuation()` and `validate_primitive_advisory_planner()`; the planner never dispatches or auto-selects. |

All goal numbers cited in the closeout correspond to test modules that exist on disk.

---

## Q2: Is D-8 correctly treated as optional/deferred rather than as a current blocker?

**Yes.**

The source design document (§6.2) explicitly calls embedding/semantic search "an optional later
upgrade, not a prerequisite," and §10 marks D-8 as `(optional)` in the sequencing table. The
closeout correctly inherits this: it marks D-8 as `Deferred` with the rationale "Explicitly
optional in source design; not needed for current deterministic metadata search." Nothing in the
tests, code, or prior review chain requires D-8 for acceptance. It is correctly downstream of the
current work.

---

## Q3: Does the closeout preserve the explain-only / no-auto-partner / no-runtime-claim boundary?

**Yes, and the boundary is enforced at three independent levels.**

**Code level:**
- `PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False` (primitive_planner.py:23)
- `PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False` (primitive_planner.py:24)
- `_plan_from_match()` hard-codes `selected_partner=None` on every returned plan
- `COMPOSITION_RECIPE_AUTO_PARTNER_SELECTION_ALLOWED = False` (primitive_recipes.py:12)
- `PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY` (lines 25–31) explicitly blocks: execute,
  dispatch, auto-select partners, release readiness, public speedup wording, broad RT-core
  wording, true zero-copy wording, promoting internal/candidate steps to stable.

**Validation level:**
- `validate_primitive_advisory_planner()` iterates every recipe plan and asserts
  `executes=False`, `selected_partner=None`, `automatic_partner_selection_allowed=False`,
  `hidden_dispatch_allowed=False`. It also checks no partner option carries
  `promoted_performance_path`, `public_speedup_claim_authorized`, or
  `true_zero_copy_claim_authorized`.
- `validate_composition_recipes()` rejects any recipe with `automatic_partner_selection_allowed=True`
  or a missing `partner_policy`, `claim_boundary`, or `boundary`.

**Test level:**
- `test_closeout_states_planner_is_explain_only` asserts that both constants appear as literal
  strings in the closeout report.
- `test_closeout_preserves_claim_boundaries` asserts that all nine prohibited claim categories
  appear in the report text.

The `candidate.zero_copy_row_streams` node records design pressure under `candidate_behavior`
with `backends=("metadata_only",)`. Its presence in the hierarchy is a design note, not a
zero-copy claim; the planner's claim boundary explicitly blocks zero-copy wording in plans.

---

## Q4: Is the current validation snapshot accurate and sufficient?

**Yes.**

Cross-checked each number against source:

| Snapshot field | Closeout claim | Source verification |
| --- | --- | --- |
| `node_count` | 50 | Counted all nodes in `PRIMITIVE_HIERARCHY` tree: 7 root layer nodes + 43 children (4+8+8+3+12+4+4). Total = 50. ✓ |
| `recipe_count` | 5 | `COMPOSITION_RECIPES` tuple has exactly 5 entries. ✓ |
| `strict_hierarchy` | True | All 25 nodes at qualifying statuses have non-empty `capability_tags`, `aliases`, `intent_phrases`, `reference_path`, and `backends`. ✓ |
| `recipes` | True | All 5 recipes have known statuses, known capability tags, resolvable primitive step IDs, no auto-partner, and all three boundary fields populated. ✓ |
| `planner` | accept | `validate_primitive_advisory_planner()` returns `"status": "accept"` when no errors; the planner constraints confirmed above mean no errors would occur. ✓ |
| `planner_executes` | False | `PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False`. ✓ |
| `auto_partner` | False | `PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False`. ✓ |

The snapshot is sufficient for a metadata closeout. It covers the four pillars of the campaign:
strict hierarchy integrity, discovery metadata completeness, recipe structural validity, and
planner advisory-only contract. It does not need to record performance numbers, test runtimes,
or backend-specific benchmarks because no runtime or performance claims are being asserted.

---

## Q5: Does the packet avoid prohibited claims?

**Yes.**

The "What v2.7 Does Not Claim" section explicitly discounts all nine required categories:
release readiness, public speedup wording, zero-copy wording, broad RT-core claims,
paper-reproduction claims, stable primitive promotion, hidden auto-dispatch, hidden auto partner
selection, and app-specific native engine logic.

The source design document (§12) lists the same as non-goals. The generated catalog's claim
boundary section (`primitive_catalog.py` lines 237–240) mirrors this on the generated artifact.
The planner's `PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY` string mirrors it at runtime. These
three independent sites reduce the risk of claim-boundary drift as the code evolves.

---

## Minor Observations (non-blocking)

1. **Secondary goal numbers (Goal3072, Goal3074, Goal3078, Goal3079, Goal3083, Goal3089,
   Goal3093) appear in the table but are not checked by the closeout test.** This is acceptable
   — the test checks the primary goal numbers. The secondary references are documentation
   lineage, not required test assertions.

2. **`reduction.grouped` has `partner_ops` but is `internal_substrate`.** Discovery metadata
   validation correctly skips `internal_substrate` nodes, so this is not an inconsistency.
   The partner ops are inherited by the planner via the recipe steps that reference grouped
   reductions, which is the intended path.

3. **The `candidate.zero_copy_row_streams` node title contains "Zero-Copy."** This is a design
   pressure note, not a claim. The node's `backends=("metadata_only",)` and its
   `candidate_behavior` status correctly signal that no implementation exists, and the planner
   validation gate would reject any plan that marked zero-copy as authorized.

---

## Verdict

**accept**

Goal3094 is a well-scoped metadata closeout. D-1 through D-7 are accurately mapped to
implemented artifacts that are verifiable in source. D-8 is correctly deferred. The
explain-only and no-auto-partner boundaries are enforced at the code, validation, and test
levels with no gaps found. The validation snapshot numbers are consistent with the source.
All nine prohibited claim categories are explicitly disclaimed in the report text and
mechanically tested.
