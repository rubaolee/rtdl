# Goal4243 Short-Row Long-Repeat Refresh

Date: 2026-06-09

Status: internal long-repeat evidence accepted with boundary

## Purpose

Goal4235 proved all ten current benchmark front doors pass on a clean RTX 4000
Ada pod, but several current-head rows were intentionally labeled
`safe_but_short`. Goal4243 refreshes the three most visible short-row cases with
dedicated long-repeat evidence at current source commit `9a40f7f5`.

This is evidence hardening. It does not change app behavior, route policy, or
public claim authorization.

## Environment

| Field | Value |
| --- | --- |
| Source commit | `9a40f7f51bd9817e5d22b862ae4dc9675486e508` |
| Source short | `9a40f7f5` |
| Pre-artifact worktree clean | `true` |
| GPU | `NVIDIA RTX 4000 Ada Generation, 550.127.08, 20475 MiB` |

## Long-Repeat Rows

| App | Metric | Repeat | Warmup | Aggregate sec | Correctness |
| --- | --- | ---: | ---: | ---: | --- |
| `hausdorff_xhd` | `repeat_protocol.measured_query_total_sec` | `1500` | `10` | `13.046773165464401` | oracle match, RT-core path active |
| `contact_manifold` | `native_collect_total_sec` | `50000` | `0` | `10.326223134994507` | CPU reference match, no overflow |
| `triangle_counting` | `timing_ms.run_backend / 1000` | `10000` | `10` | `2.1000807359814644` | oracle match, RT-core path active |

## Reading

The current-head short rows now have dedicated repeat evidence above the
one-second floor, independent of the older Goal4185/4186 stress artifacts. This
strengthens a future release-candidate evidence packet by reducing reliance on
stale stress runs for these three rows.

The rows remain scoped:

- Hausdorff uses the threshold/prepared OptiX path, not a universal exact
  Hausdorff speedup claim.
- Contact manifold tests bounded collect-k candidate output, not a full physics
  solver.
- Triangle counting tests the current generic RT-Graph 2A1 summary route, not a
  full paper-system reproduction.

## Boundary

Goal4243 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
