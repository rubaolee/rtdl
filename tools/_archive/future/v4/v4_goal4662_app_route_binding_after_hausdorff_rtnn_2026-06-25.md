# V4 Goal4662 App-Route Binding After Hausdorff And RTNN

Date: 2026-06-25

Status: route matrix updated, no release authorization

## Purpose

Goal4662 updates the current V4 app-route truth after two post-Goal4655
engineering probes:

- Goal4659: Hausdorff official V4 route and large-scale correctness boundary.
- Goal4660/4661: RTNN ranked-summary V4 candidate route and same-hardware
  performance comparison.

This does not rewrite the frozen Goal4652 history artifact. It records the
current route truth in a new evidence file.

Machine evidence:

```text
future/v4/evidence/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.json
```

## Matrix Changes

### Hausdorff XHD

Current route status:

```text
official_v4_route_with_coordinate_normalized_correctness_boundary
```

Current reading:

- There is now an official V4 route through generic V4 point-group
  nearest-witness plus Torch global argmax.
- No Hausdorff-specific native kernel was added.
- At 1,048,576 points per side, exactness requires the measured
  coordinate-normalized chunk mode.
- This is route-strengthening and correctness repair, not broad app-level
  speed authorization.

Protocol treatment:

- Keep it out of formal speed-row claims until a refreshed protocol includes
  the coordinate-normalized denominator.
- Do not claim unrestricted exact Hausdorff support.

### RTNN

Current route status:

```text
candidate_ranked_summary_present_but_app_bar_not_moved
```

Current reading:

- The V4 fixed-radius ranked-summary/top-k candidate exists.
- It validates and executes through the generic V4 prepared runner.
- It is not an exact same-runner V2/V3/V4 comparison because old versions only
  expose `prepared_optix_ranked_summary`.
- Serious scales show parity rather than material app-level speedup.

Serious hot-path rows from Goal4660/4661:

| Points | V4/V2.14 Hot | V4/V3.0.2 Hot |
|---:|---:|---:|
| 262,144 | 0.999x | 1.005x |
| 1,048,576 | 0.994x | 0.993x |

Protocol treatment:

- Keep RTNN as a candidate/control row.
- Do not count it as formal high-performance V4 evidence.
- Do not trigger a full all-app rerun from this result.

## Verification

Focused validation passed:

```text
py -3 -m unittest tests.v4_goal4660_ranked_summary_candidate_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4653_app_level_protocol_test tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_scope_gate_test
```

Result:

```text
43 tests OK
```

Broader V4 boundary validation also passed:

```text
py -3 -m unittest tests.v4_goal4660_ranked_summary_candidate_test tests.v4_goal4659_hausdorff_official_route_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4653_app_level_protocol_test tests.v4_goal4655_app_benchmark_analysis_test tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_scope_gate_test tests.v4_catalog_regression_gate_test tests.v4_goal4632_release_decision_test tests.v4_goal4643_publication_decision_test tests.v4_goal4644_post_release_guardrails_test
```

Result:

```text
73 tests OK
```

## Decision

Goal4662 result:

```text
route_matrix_updated_without_speed_authorization
```

This is useful current-state cleanup, not a V4 performance success. The
important outcome is that the code and docs can no longer honestly treat RTNN
as a pending performance win or treat Hausdorff as missing a route.

## Non-Authorization

This goal does not authorize V4 release, formal high-performance V4 wording,
broad V4 speedup wording, whole-application speedup wording, unrestricted exact
Hausdorff wording, exact same-runner RTNN speedup wording, public true-zero-copy
claims, Tier-3 callback support, raw OptiX callbacks, embedding/C ABI,
non-Python host bindings, or app-specific native kernels.
