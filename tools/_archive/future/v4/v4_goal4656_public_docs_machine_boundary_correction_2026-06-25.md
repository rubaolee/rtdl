# V4 Goal4656 Public Docs And Machine Boundary Correction

Date: 2026-06-25

Status: `goal4656_complete_pending_external_review_debt`

Decision label preserved from Goal4655:

```text
bounded_operator_v4_only__app_level_high_performance_not_supported
```

## Purpose

Goal4656 rewrites the current V4 public/user surface and the matching machine
claim boundary after Goal4654/Goal4655 showed that formal app-level
high-performance V4 is not supported by the serious app-level evidence.

This goal does not stop V4 high-performance engineering. It prevents the
current repository from telling users that final app-level high-performance V4
already exists.

## Concrete Changes

Public docs now say V4 is currently a bounded operator surface, not a formal
app-level high-performance release:

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `docs/learn/performance_wording.md`
- `tutorials/current/README.md`
- `tutorials/current/05_measurement_boundaries.md`
- `examples/README.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v4_0_scope_gate.md`
- `future/v4/v4_goal4643_publication_decision_2026-06-25.md`
- `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`

Machine claim boundaries now preserve the operator surface but block formal
release/app-level wording:

- `src/rtdsl/v4.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `src/rtdsl/v4_goal4644_post_release_guardrails.py`
- `scripts/v4_catalog_regression_gate.py`
- `scripts/v4_scope_gate.py`

Regression tests now lock the corrected boundary:

- `tests/v4_frontdoor_test.py`
- `tests/v4_catalog_regression_gate_test.py`
- `tests/v4_goal4632_release_decision_test.py`
- `tests/v4_goal4643_publication_decision_test.py`
- `tests/v4_goal4644_post_release_guardrails_test.py`
- `tests/v4_scope_gate_test.py`

## Public App-Level Summary Added

New public page:

```text
docs/app_level_benchmark_summary.md
```

It records the same-hardware app-level result:

| App | V4/V2.14 | V4/V3.0.2 | Current reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `1.070x` | `1.084x` | Modest gain, below formal high-performance bar. |
| RayDB-style | `0.994x` | `1.000x` | Parity, not a V4 speed win. |
| Triangle counting | `15.548x` | `1.117x` | Historical route evolution plus modest V4 increment. |
| LibRTS spatial index | `0.999x` | `1.001x` | Parity, not a V4 speed win. |

## Machine Boundary

The V4 front door now reports:

```text
front_door_status: v4_bounded_operator_front_door_goal4655_corrected
formal_release_authorized: false
bounded_operator_surface_available: true
app_level_high_performance_authorized: false
goal4655_decision_label: bounded_operator_v4_only__app_level_high_performance_not_supported
```

The scope gate now reports:

```text
status: v4_bounded_operator_scope_goal4655_corrected
release_authorized: false
blocking_reasons: goal4655_app_level_high_performance_not_supported
```

The catalog regression gate now reports:

```text
release_authorized: false
whole_app_speedup_claim_authorized: false
all_benchmark_speedup_claim_authorized: false
true_zero_copy_authorized: false
```

## Verification

Commands run:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v4\v4_frontdoor_quickstart.py
$env:PYTHONPATH='src;.'; py -3 examples\v4\operator_callback_planning.py --case complex-callback
$env:PYTHONPATH='src;.'; py -3 scripts\v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16
$env:PYTHONPATH='src;.'; py -3 scripts\v4_scope_gate.py --md-out future\v4\v4_0_scope_gate.md --json-out future\v4\evidence\v4_goal4656_scope_gate_current_boundary_2026-06-25.json
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v4_goal4632_release_decision_test tests.v4_goal4643_publication_decision_test tests.v4_goal4644_post_release_guardrails_test tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test tests.v4_goal4655_app_benchmark_analysis_test tests.v4_goal4653_app_level_protocol_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test
```

Result:

```text
59 tests OK
```

Current public/machine wording scan:

```powershell
rg -n "formal_release_authorized.*True|release_authorized.*True|formal V4\.0\.0 bounded operator release authorized|final release authorization: complete|V4\.0\.0 is now a bounded|formal high-performance generic|RTDL v4\.0\.0 formal high-performance|release authorized: `True`" README.md docs future\v4 src\rtdsl scripts tests -g "*.md" -g "*.py"
```

Result: no matches in the scanned current/public/machine scope.

## Non-Authorization

Goal4656 does not authorize formal app-level high-performance V4 release
wording, broad speedup wording, whole-application speedup wording,
all-benchmark speedup wording, public true-zero-copy wording, Tier-3 callback
support, raw OptiX callback support, CuPy blanket performance claims, C ABI,
embedding, non-Python host binding, or app-specific native kernels.

## Next Engineering Direction

The next real V4 work is not more wording. It is app-level performance
engineering:

1. Choose the next app-level blocker with a clear V4 route hypothesis.
2. Implement the route as generic operator composition, not an app-identity
   native kernel.
3. Run same-hardware V2.14/V3.0.2/V4 app-level comparison with parity.
4. Only if the app-level gate passes, reopen formal high-performance release
   authorization.

## Goal-Level Decision Audit

1. Was I being stupid?
   Yes, earlier V4 wording let an operator-level scorecard look like a final
   high-performance V4 release.

2. If yes, what action made it stupid?
   Treating the Goal4639 operator scorecard and Goal4642 publication chain as
   current truth after Goal4654/Goal4655 produced app-level no-go evidence.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Preserve the bounded operator surface, explicitly block app-level
   release wording, and send future effort into app-level route engineering.

4. Can I now try the different path that actually solves the problem?
   Yes. With public and machine boundaries corrected, the next goal can target
   real app-level V4 speed rather than release-wording cleanup.
