# V4 Goal4678 Ranked-Summary Candidate Disposition

Date: 2026-06-25

Status:

```text
goal4678_defer_ranked_summary_no_open_candidate_no_release
```

## Decision

Defer `v4_fixed_radius_ranked_summary_3d_prepared_runner` and remove it from
the current V4 candidate front door.

This is not a code deletion. The wrapper still exists as an internal/deferred
route, but the current V4 user surface should not advertise it as an active
candidate because the serious POD evidence does not move the app-level bar.

Current V4 front door after this decision:

```text
measured Tier-2 surfaces: 9
candidate Tier-2 surfaces: 0
release authorized: false
app-level high-performance wording authorized: false
```

## Evidence

- Source evidence:
  `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json`
- Prior report:
  `future/v4/v4_goal4660_4661_rtnn_ranked_summary_candidate_evidence_2026-06-25.md`
- Goal4678 validation:
  `future/v4/evidence/v4_goal4678_ranked_summary_disposition_2026-06-25.json`

Goal4678 validation status:

```text
passed
```

## Why Deferred

The route executed and validated, but the serious scale rows did not produce a
material runtime win:

| Points | V4/V2.14 Hot | V4/V3.0.2 Hot | Reading |
| ---: | ---: | ---: | --- |
| 262144 | below 1.01x | below 1.01x | parity, not material speedup |
| 1048576 | below 1.0x | below 1.0x | below parity |

The existing summary decision label is:

```text
rtnn_candidate_does_not_move_app_level_bar
```

The summary also says it may not count as formal high-performance V4 evidence
and may not trigger a full all-app rerun.

## Code Changes

- `src/rtdsl/v4_ranked_summary.py`
  - claim boundary now reports
    `deferred_goal4678_serious_scale_parity_not_release`;
  - `candidate_surface` is false;
  - `deferred_surface` is true.
- `src/rtdsl/v4_operator_catalog.py`
  - current candidate catalog is empty;
  - ranked-summary is tracked in a deferred table;
  - planner returns `deferred_v4_x_or_research` with no API surface.
- `src/rtdsl/v4_scope.py`
  - candidate surfaces are empty;
  - scope status is `v4_bounded_operator_scope_goal4678_no_open_candidates`.
- Current public docs:
  - `README.md`
  - `docs/current_v4_status.md`
  - `future/v4/README.md`
  - `future/v4/tier2_operator_catalog.md`

## Verification

```text
py -m unittest tests.v4_goal4678_ranked_summary_disposition_test tests.v4_goal4660_ranked_summary_candidate_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_scope_gate_test tests.v4_goal4677_aggregate_frontier_promotion_test tests.v4_goal4640_public_docs_cleanup_test
```

Result:

```text
Ran 43 tests in 6.515s
OK
```

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No. Keeping ranked-summary as an open candidate after serious parity evidence
would mislead users and future agents.

2. If yes, what actions made it stupid?

Not applicable. The avoided stupid action was continuing to polish a route that
already failed to move the bar at serious scale.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes: do not rerun POD and do not re-market the route. Defer it until a new
generic lever exists.

4. Should I try a different path to solve the real problem?

Yes. The next goal must choose/design a new generic runtime lever or a material
same-primitive improvement target with V2.14 denominator and frozen bars before
any POD run.

## Non-Authorization

This goal does not authorize:

- V4 release.
- public speedup wording.
- whole-app high-performance wording.
- RTNN speedup wording.
- broad V4-over-V2/V3 claims.
- true-zero-copy wording.
- Tier-3 callback/PTX support.
- raw OptiX callbacks.
- C ABI, embedding, or non-Python hosts.
- automatic partner selection.
- app-identity native kernels.

## Next Work

Goal4679 should choose the next real V4 performance path. It must start from a
named generic runtime lever and a V2.14 denominator, not from an app identity or
partner/front-door migration.
