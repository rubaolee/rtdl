# V4 Goal4719 Public Docs, Tutorials, Examples, And Release Wording Cleanup

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision:

`public_v4_docs_examples_match_goal4718_release_candidate_boundary`

## Goal

Make the current public V4 user surface match the Goal4718 release matrix:

- V4 is a Python eDSL/operator-pushdown release candidate;
- V4 has `10` measured generic operator/workflow surfaces;
- custom predicate early-exit is the current V4-only workflow win;
- broad legacy all-app high-performance wording remains unsupported.

## Files Updated

Public front door:

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/public_documentation_map.md`
- `docs/learn/performance_wording.md`

Tutorials/examples:

- `tutorials/current/README.md`
- `tutorials/current/05_measurement_boundaries.md`
- `examples/README.md`
- `examples/v4/custom_predicate_early_exit_planning.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

Tests updated:

- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `tests/v4_goal4644_post_release_guardrails_test.py`

## New Runnable Example

Added:

`examples/v4/custom_predicate_early_exit_planning.py`

This example runs without CUDA. It shows the supported custom predicate
early-exit planning boundary:

- accepted: constrained Numba C-ABI boolean predicate;
- accepted action: RTDL-owned `terminate_on_first_accept`;
- measured serious-scale result: `4.633x` V4/V2.14 and V4/V3.0.2 geomean;
- rejected: unsafe action-shaped callbacks;
- still false: release claim, whole-app speedup, arbitrary Python callback, raw
  OptiX callback, and public Tier-3 support.

## Validation

Commands:

```text
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_goal4644_post_release_guardrails_test tests.v4_frontdoor_test tests.v4_scope_gate_test tests.v4_goal4718_release_matrix_after_custom_predicate_test
rg -n "bounded operator surface|bounded V4 operator|measured Tier-2 surfaces: `9`|current V4 measured operator surface count is `9`|formal app-level high-performance V4 release yet|Goal4654/Goal4655|9 documented|nine measured" README.md docs/README.md docs/current_v4_status.md docs/app_level_benchmark_summary.md docs/public_documentation_map.md docs/learn/performance_wording.md tutorials/current examples/README.md future/v4/README.md future/v4/tier2_operator_catalog.md -g "*.md"
```

Observed:

- public docs/examples tests: `21 tests OK`;
- stale-string scan: no matches in the current public user path.

## Non-Authorization

Goal4719 does not by itself authorize:

- final public tag;
- broad all-app speedup;
- "all benchmark apps are faster";
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- embedding/C ABI or non-Python host claims;
- app-specific native kernels.

It authorizes the next step:

`Goal4720: final V4 release decision packet, machine release gate update, and broad local validation.`

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal removed stale public wording and added a runnable example for the
new measured V4 workflow instead of hiding the actual V4 value in evidence
files.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. If docs had continued to say only "bounded operator surface with 9 rows,"
users would not understand why V4 exists after Goal4717. The corrected path is
to state both facts: V4 has a real eDSL/operator-pushdown workflow win, and
broad legacy all-app speedup is still false.

4. Can I now try the different path that actually solves the problem?

Yes. The next path is the final release gate: align machine release decisions,
run broad validation, and prepare the final review packet.
