# V4 Goal4669 - Full App-Level Rerun After Hausdorff Focused Pass

Date: 2026-06-25

Status: complete; serious POD evidence collected; not release-authorizing

Decision label:
`bounded_operator_v4_only__app_level_high_performance_not_supported`

## Bottom Line

Goal4669 reran the serious V2.14 / V3.0.2 / V4 app-level benchmark after
Goal4667 promoted Hausdorff XHD into the full-app candidate set.

The result is mixed and important:

- Hausdorff XHD is a real V4 app-level win candidate under its frozen custom
  bar.
- The overall V4 candidate still does not support a formal high-performance
  release.
- Current evidence shows one true V4 app candidate win, not a broad app-level
  V4 performance release.

This directly answers the earlier concern: a candidate route that is only
parity with V2/V3 has no performance-release value. In Goal4669, most rows are
still parity/modest/regression. Hausdorff is the exception, not the release.

## Evidence

Raw POD evidence:

`future/v4/evidence/v4_goal4669_serious_20260625/summary.json`

Generated summary:

`future/v4/evidence/v4_goal4669_serious_20260625/summary.md`

Machine analysis:

`future/v4/evidence/v4_goal4669_app_level_benchmark_analysis_2026-06-25.json`

Runner:

`scripts/v4_goal4669_full_app_level_pod_benchmark.py`

## Scorecard

| App | V4/V2.14 hot | V4/V3.0.2 hot | V4/V2.14 primary wall | V4/V3.0.2 primary wall | Parity | Classification |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `rt_dbscan` | 1.086x | 1.083x | 1.074x | 1.071x | true | modest, below formal bar |
| `raydb_style` | 0.974x | 1.005x | 0.974x | 1.005x | true | regression vs no-regression floor |
| `triangle_counting` | 4.055x | 0.948x | 4.055x | 0.948x | true | regression vs V3.0.2 |
| `librts_spatial_index` | 1.003x | 1.004x | 1.049x | 1.195x | true | parity, not a V4 speed win |
| `hausdorff_xhd` | 201581.860x | 2.546x | 114.824x | 1.112x | true | true V4 candidate win |

All rows returned `0`, all JSON parsed, and all full rows had a hot metric.

## Hausdorff Result

Hausdorff passed its custom frozen bar:

- V4/V2.14 primary wall: 114.824x, above the 1.20x bar.
- V4/V3.0.2 hot path: 2.546x, above the 1.20x bar.
- V4 prepare vs V3.0.2: above the 0.80x floor.
- 1M coordinate-normalized correctness probe passed:
  - `coordinate_normalization_used: true`;
  - chunk count: `3`;
  - `matches_oracle: true`.

This is a meaningful V4 result because it is a real full-app row using the
official V4 point-group nearest-witness route plus the generic adaptive CuPy
argmax continuation. It is not an app-specific native kernel.

It is not enough to release V4 as a formal high-performance release.

## Release Decision

Formal high-performance V4 is still not supported.

Blocking reasons:

- old-version OptiX rows still use the declared V4 compatibility native library
  because this POD lacks the OptiX SDK headers needed to rebuild V2.14/V3.0.2
  OptiX libraries;
- most full-app rows still do not pass their frozen speed bars;
- there is only one independent true V4 app candidate win.

The machine analysis records:

- `true_v4_candidate_app_count: 1`;
- `contributing_app_count: 0` under the current provenance blocker;
- `formal_high_performance_v4_supported: false`.

## Next Goal

Goal4670 must select and execute the next non-trivial app-level performance
target. It must not be a wording/doc/review goal.

The target must satisfy all of these before work starts:

- it can plausibly create a second independent true V4 app win;
- it is a generic V4 runtime/operator improvement, not an app-identity kernel;
- it has a frozen app-level denominator against V2.14 and V3.0.2;
- it preserves correctness parity;
- it does not claim release from focused or operator-only evidence.

Likely candidates from the current scorecard:

- `triangle_counting`: V4 is far faster than V2.14 but regresses to 0.948x
  against V3.0.2; the only useful target is restoring/improving the V4 route
  versus V3 without app-specific code.
- `rt_dbscan`: currently 1.086x/1.083x, below the 1.20x formal bar; the useful
  target is a generic component/continuation improvement, not another tiny
  measurement shuffle.
- `raydb_style`: currently fails the no-regression floor against V2.14 at
  0.974x; fixing it is necessary hygiene but not sufficient by itself unless
  the same generic change moves it well past the formal bar.

## Non-Authorization

Goal4669 does not authorize:

- V4 release;
- public broad V4 speedup wording;
- formal high-performance V4 wording;
- app-suite geomean headline;
- public true-zero-copy wording;
- app-specific native kernels;
- C ABI / embedding / non-Python host claims.
