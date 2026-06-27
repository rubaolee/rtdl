# V4 Goal4718 Release Matrix After Custom Predicate Early-Exit

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision:

`v4_python_edsl_operator_pushdown_release_candidate_pending_docs_and_final_review`

## Goal

Convert the Goal4717 serious-scale custom predicate early-exit result into the
V4 release matrix without misrepresenting it as a broad legacy all-app speedup.

The key separation is:

- legacy promoted-app all-suite high-performance remains unsupported by
  Goal4669;
- the new custom predicate early-exit workflow is a real V4 eDSL/operator-
  pushdown performance win.

## Implementation

Files:

- `src/rtdsl/v4_goal4718_release_matrix_after_custom_predicate.py`
- `scripts/v4_goal4718_release_matrix_after_custom_predicate.py`
- `tests/v4_goal4718_release_matrix_after_custom_predicate_test.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_scope.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_operator_catalog_test.py`
- `future/v4/README.md`
- `future/v4/v4_0_scope_gate.md`

Evidence:

- `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json`
- `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- `future/v4/evidence/v4_0_scope_gate_current.json`

## Matrix Result

Goal4718 records:

- measured V4 surfaces: `10`;
- new V4 workflow row:
  `ray_triangle_custom_predicate_early_exit_multi_hit`;
- API surface:
  `v4_ray_triangle_custom_predicate_early_exit_3d_numba`;
- V4/V2.14 serious-scale primary geomean: `4.632757911153888x`;
- V4/V3.0.2 serious-scale primary geomean: `4.632757911153888x`;
- minimum primary V4/V3.0.2 row: `2.054686620906942x`;
- correctness: all rows passed;
- denominator:
  `materialized_all_hit_ids_plus_device_predicate_reduce_fallback`.

This row counts as V4 eDSL/operator-pushdown value. It does not count as
legacy promoted-app all-suite speedup.

## Current Release Interpretation

Allowed as a release-candidate interpretation after Goal4718:

- V4 is a Python eDSL/runtime for measured generic RT-core operator pushdown.
- The V4 front door has `10` measured generic operator/workflow surfaces.
- The constrained Numba custom predicate early-exit workflow measured `4.633x`
  geomean versus V2.14/V3.0.2 materialized-device fallback at serious scale.
- Legacy promoted-app all-suite high-performance remains unsupported by
  Goal4669.

Still not authorized:

- public tag;
- final V4 release wording;
- broad all-app speedup;
- "all benchmark apps are faster";
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- non-Python embedding/C ABI;
- app-specific native kernels.

## Validation

Commands:

```text
py -m py_compile src/rtdsl/v4_goal4718_release_matrix_after_custom_predicate.py scripts/v4_goal4718_release_matrix_after_custom_predicate.py src/rtdsl/v4.py src/rtdsl/v4_scope.py
py scripts/v4_goal4718_release_matrix_after_custom_predicate.py --json-out future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json --md-out future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md
py scripts/v4_scope_gate.py --json-out future/v4/evidence/v4_0_scope_gate_current.json --md-out future/v4/v4_0_scope_gate.md
py -m unittest tests.v4_goal4718_release_matrix_after_custom_predicate_test tests.v4_frontdoor_test tests.v4_scope_gate_test tests.v4_goal4716_custom_predicate_early_exit_productization_test tests.v4_operator_catalog_test
```

Observed:

- Goal4718 evidence validation: `passed`;
- scope gate validation: `passed`;
- tests: `30 tests OK`.

## Next

`Goal4719: public docs, tutorials, examples, and release wording cleanup.`

Goal4719 must make the user-facing project clean and consistent with the
Goal4718 matrix before any final release/tag discussion.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal specifically prevents the stupid path: treating one true V4
workflow win as if it made every old promoted benchmark app faster.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. The correct path is to publish a truthful V4 eDSL/operator-pushdown release
candidate while keeping the legacy all-app high-performance claim false unless
future app gates actually pass.

4. Can I now try the different path that actually solves the problem?

Yes. The next path is user-facing release hardening: docs, tutorials, examples,
claim wording, and final external review.
