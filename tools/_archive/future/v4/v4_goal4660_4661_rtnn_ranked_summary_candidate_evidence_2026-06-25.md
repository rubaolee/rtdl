# V4 Goal4660/4661 RTNN Ranked-Summary Candidate Evidence

Date: 2026-06-25

Status: candidate evidence complete, not release authorization

## Goal Scope

Goal4660 promoted the RTNN-shaped generic continuation route as a V4 candidate
surface:

```text
v4_fixed_radius_ranked_summary_3d_prepared_runner
```

Goal4661 measured that candidate on the same RTX A5000 POD against the closest
available V2.14 and V3.0.2 RTNN ranked-summary routes.

## Evidence Files

Machine summary:

```text
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json
```

Raw rows:

```text
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v2_14_prepared_optix_ranked_summary_65536.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v3_0_2_prepared_optix_ranked_summary_65536.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v4_candidate_prepared_execution_ranked_summary_65536.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v2_14_prepared_optix_ranked_summary_262144.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v3_0_2_prepared_optix_ranked_summary_262144.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v4_candidate_prepared_execution_ranked_summary_262144.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v2_14_prepared_optix_ranked_summary_1048576.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v3_0_2_prepared_optix_ranked_summary_1048576.json
future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/v4_candidate_prepared_execution_ranked_summary_1048576.json
```

## Denominator Boundary

This is not an exact same-runner V2/V3/V4 comparison.

The V2.14 and V3.0.2 RTNN apps do not expose
`prepared_execution_ranked_summary`. Their closest available old-version route
is:

```text
prepared_optix_ranked_summary
```

The V4 candidate route is:

```text
prepared_execution_ranked_summary
```

Allowed wording:

```text
closest old-version RTNN ranked-summary front door versus V4 candidate route
```

Forbidden wording:

```text
exact same runner V2/V3/V4 speedup
```

## Same-Hardware Result

All rows ran on the current POD supplied for V4 work:

```text
root@194.68.245.170:22089
NVIDIA RTX A5000, driver 570.195.03
```

Hot-path median speedup is reported as old median divided by V4 candidate
median. Values above `1.0x` mean V4 candidate is faster for that hot metric.

| Points | V4/V2.14 Hot | V4/V3.0.2 Hot | V4/V2.14 Prepare | V4/V3.0.2 Prepare |
|---:|---:|---:|---:|---:|
| 65,536 | 1.145x | 1.066x | 0.576x | 0.390x |
| 262,144 | 0.999x | 1.005x | 1.125x | 0.988x |
| 1,048,576 | 0.994x | 0.993x | 0.684x | 1.145x |

## V4 Candidate Validation

The V4 candidate row emits:

- `v4_surface: v4_fixed_radius_ranked_summary_3d_prepared_runner`
- `v4_candidate_status: candidate_goal4660_needs_pod_scorecard_not_release`
- `runtime_trunk_executes_end_to_end: true`
- `runtime_executed: true`
- `prepared_queries_resident: true`
- `hot_path_host_materialization: false`
- `validation_passed: true`
- `signature_match_status.query_count_ok: true`

This proves the candidate route exists and executes through the generic V4
runner. It does not prove a material app-level V4 speedup.

## Decision

Decision label:

```text
rtnn_candidate_does_not_move_app_level_bar
```

Reason:

- The small 65,536-point row shows a modest hot-path advantage.
- The serious 262,144-point and 1,048,576-point rows collapse to parity.
- The 1,048,576-point row is slightly slower than both old versions on the hot
  metric.
- Prepare time is mixed and does not create a broad V4 app-level win.

Therefore RTNN can remain a V4 candidate route and can be recorded as app-route
progress. It cannot be counted as formal high-performance V4 evidence, and it
does not justify a full all-app rerun by itself.

## Next Action

Proceed to Goal4662, but update the app-route matrix conservatively:

- `rtnn`: V4 candidate route present, same-hardware evidence collected, does
  not move app-level bar.
- `hausdorff_xhd`: official V4 route present with the coordinate-normalized
  correctness boundary from Goal4659.
- `spatial_rayjoin`: remains no-route unless new engineering proves otherwise.
- `barnes_hut`: remains deferred app-identity route.

## Non-Authorization

This report does not authorize V4 release, broad V4 speedup wording, exact
same-runner V2/V3/V4 RTNN speedup wording, app-level high-performance wording,
public true-zero-copy claims, arbitrary callback support, C ABI, embedding,
non-Python host bindings, or app-specific native kernels.
