# V4 Goal4716 Custom Predicate Early-Exit Productization

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `custom_predicate_early_exit_productized_as_measured_v4_surface_not_release`

## Goal

Turn the Goal4715 focused timing win into a real V4 front-door surface instead
of leaving it as a standalone POD benchmark script.

## Productized Surface

API surface:

`v4_ray_triangle_custom_predicate_early_exit_3d_numba`

Generic primitive:

`RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_3D`

Files:

- `src/rtdsl/v4_custom_predicate_early_exit.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`
- `scripts/v4_goal4716_custom_predicate_early_exit_productization.py`
- `tests/v4_goal4716_custom_predicate_early_exit_productization_test.py`

Evidence:

- `future/v4/evidence/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.json`
- `future/v4/evidence/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.md`

## What Changed

Goal4716 adds a measured V4 operator-pushdown surface for custom predicate
early-exit:

- catalog entry in `measured_v4_tier2_operator_catalog()`;
- front-door exports through `rtdsl.v4`;
- claim-boundary function;
- constrained product wrapper;
- planner/recognizer support;
- fail-closed rejection for unsafe callbacks and unmeasured partners;
- machine evidence generation.

The measured catalog now has `10` surfaces. The new surface records the
Goal4715 result:

- primary V4/V3 geomean: `3.608025018751732x`;
- primary V4/V2 geomean: `3.608025018751732x`;
- minimum primary V4/V3 row: `1.9761904761904763x`;
- maximum primary V4/V3 row: `8.130865199087879x`;
- correctness all passed.

## Contract

Allowed:

- Numba C-ABI boolean/scalar device predicates;
- RTDL-owned actions:
  - `terminate_on_first_accept`;
  - `filter_accept_flags`;
- generated OptiX any-hit route that evaluates the predicate during traversal.

Rejected:

- arbitrary Python callbacks;
- raw OptiX callback exposure;
- user-owned any-hit action mutation;
- shared-state mutation;
- dynamic allocation;
- variable-length output;
- app-identity native kernels.

Partner boundary:

- measured partner: `numba`;
- unmeasured/deferred partners: `torch`, `cupy`, `rtdl_native`.

## Why This Matters

This productizes the first V4 route that clearly changes the cost model rather
than only moving post-hit work around. Goal4711 post-hit custom scoring produced
only about `1.029x`; Goal4715 predicate early-exit reached `3.608x` geomean
because it avoids materializing all candidates for early-accept workloads.

## Validation

Local:

```text
py -m py_compile src/rtdsl/v4_custom_predicate_early_exit.py src/rtdsl/v4_operator_catalog.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4716_custom_predicate_early_exit_productization_test tests.v4_goal4715_custom_predicate_early_exit_timing_result_test tests.v4_goal4630_pushdown_recognizer_test
py scripts/v4_goal4716_custom_predicate_early_exit_productization.py --json-out future/v4/evidence/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.json --md-out future/v4/evidence/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.md
```

Observed:

- local focused tests: `19 tests OK`;
- evidence generation: `status: passed`.

Remote POD:

```text
/usr/bin/python3 -m py_compile src/rtdsl/v4_custom_predicate_early_exit.py src/rtdsl/v4_operator_catalog.py src/rtdsl/v4.py scripts/v4_goal4716_custom_predicate_early_exit_productization.py
/usr/bin/python3 -m unittest tests.v4_goal4716_custom_predicate_early_exit_productization_test tests.v4_goal4715_custom_predicate_early_exit_timing_result_test
/usr/bin/python3 scripts/v4_goal4716_custom_predicate_early_exit_productization.py --json-out /root/v4_goal4716_productization_20260626.json --md-out /root/v4_goal4716_productization_20260626.md
```

Observed:

- remote tests: `10 tests OK`;
- remote evidence generation: `status: passed`.

## Non-Authorization

Goal4716 does not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

It authorizes the next engineering step:

`Goal4717: broaden custom predicate early-exit validation into serious app/app-like benchmark coverage.`

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal did not treat Goal4715 as a release. It converted the focused win
into a bounded product surface with fail-closed planner rules.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. If productization had required arbitrary callbacks or raw OptiX exposure,
the correct path would be to reject the surface as V4.0 support and keep it as
research. The implemented surface stays constrained.

4. Can I now try the different path that actually solves the problem?

Yes. The next useful path is broader app/app-like validation, not release
wording.
