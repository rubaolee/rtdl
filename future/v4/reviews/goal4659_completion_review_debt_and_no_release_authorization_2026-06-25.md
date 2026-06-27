# Goal4659 Completion Review Debt And No Release Authorization

Date: 2026-06-25

Goal: V4 Goal4659 - Hausdorff Official V4 Route Evidence

Status: `goal4659_engineering_evidence_collected_external_review_debt_open_not_release`

## Engineering Evidence

- Report:
  `future/v4/v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md`
- Machine summary:
  `future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json`
- Test:
  `py -3 -m unittest tests.v4_goal4659_hausdorff_official_route_test tests.v4_point_group_device_array_api_test tests.v4_frontdoor_test tests.v4_goal4655_app_benchmark_analysis_test`
- Test result:
  `14 tests OK`

## External Review Attempts

Claude:

- Known state from refresh runbook:
  `You've hit your weekly limit - resets Jun 28, 7pm (America/New_York)`
- Per runbook, Claude was not repeatedly retested.
- Debt remains open.

Antigravity:

- Attempted once with:
  `future/v4/reviews/call_for_review_v4_goal4659_hausdorff_official_route_2026-06-25.md`
- Raw output:
  `future/v4/reviews/antigravity_v4_goal4659_hausdorff_official_route_review_2026-06-25.raw.md`
- Stderr:
  `future/v4/reviews/antigravity_v4_goal4659_hausdorff_official_route_review_2026-06-25.stderr.txt`
- Result:
  command exited `0`, but both stdout and stderr were empty.
- Interpretation:
  not a review verdict, not approval.

## Current Owner Judgment

Goal4659 produced real engineering progress:

- `hausdorff_xhd` now has a working official V4 route at correctness-passing
  scales through `v4_point_group_nearest_witness_2d_device_arrays` plus generic
  Torch `global_argmax_u32_f64`.
- The route is not an app-specific native kernel.
- The 262,144 points/side row passes correctness and shows a hot-path win over
  V3.0.2 CuPy.
- The 1,048,576 points/side row now passes correctness when the V4 route uses
  coordinate-normalized chunking (`--coordinate-normalization-span 1000000`).
  This mode keeps the same V4 point-group surface and generic Torch argmax.
  The measured span sweep found `1000000` as the largest passing span among the
  tested values; `1200000`, `1500000`, `1800000`, and `2000000` failed.

Goal4659 does not close the formal high-performance V4 release gap:

- the unnormalized 1,048,576 points/side exact row fails correctness for both
  V3.0.2 CuPy and V4 Torch because of the native float32 distance/large-coordinate
  contract;
- coordinate-normalized 1M is a correctness repair, not a speed win
  (`0.493x` vs the V3.0.2 CuPy hot metric, and the V3.0.2 comparison row is
  itself incorrect);
- cold prepare is still not better than V3.0.2 on the 262k or normalized 1M rows;
- the app-level scorecard has not been rerun with the new route.

## Non-Authorization

This record does not authorize V4 release, public tag, broad V4 speedup wording,
all-app speedup wording, unrestricted exact Hausdorff claims, public
true-zero-copy claims, Tier-3 callback support, C ABI, embedding, non-Python host
support, or app-specific native kernels.
