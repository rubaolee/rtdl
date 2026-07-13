# X-HD Midterm After Goal5216 Review Amendment Response

Date: 2026-07-09

Review addressed:

```text
history/internal_docs/review_xhd_midterm_after_goal5216_2026-07-09.md
```

Amended documents:

```text
history/internal_docs/xhd_midterm_report_after_goal5216_2026-07-09.md
history/internal_docs/goal5217_level_b_same_pod_performance_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5217_level_b_same_pod_performance_matrix_2026-07-09.md
memory/progress.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Verdict

```text
required_amendments_addressed__awaiting_reviewer_signoff
```

## RA-1: Approximate Witnesses Under-Disclosed

Review finding:

```text
Goal5211 global-bound early break reports:
  global_bound_early_break_count = 409376 / 437645
  per_source_witness_exact = false

The midterm report stated the value match but did not carry this witness caveat.
```

Amendment made:

The midterm report now states in the Executive Summary and Completed Problems
sections that the current route is **exact-value-only** for the directed-HD
scalar:

```text
global_bound_early_break_count = 409376 / 437645 sources (~93.5%)
per_source_witness_exact = false
```

It now explicitly forbids treating the full-route per-source nearest witnesses
as exact X-HD witness output.

## RA-2: Author Re-Run vs Paper-Branch Log

Review finding:

```text
RTDL matches the author binary re-run on public data, not the paper-branch log.
Author re-run = 0.12572988867759705
Paper log    = 0.12572969496250153
RTDL route   = 0.12572988629271128
```

Amendment made:

The midterm report now distinguishes:

```text
RTDL vs author re-run diff:      ~2.38e-9
Author re-run vs paper log diff: ~1.94e-7
RTDL vs paper log diff:          ~1.91e-7
```

It no longer says that RTDL matches the paper log. It states that RTDL matches
the author re-run on public same-source data, and that the author re-run's
`~1.94e-7` paper-log gap is consistent with the public-input non-identity
boundary.

Goal5217 wording was also corrected so the same mistake does not reappear in
the same-POD performance matrix report.

## RA-3: Narrow Level-B Scope

Review finding:

```text
Current Level-B evidence is one directed-HD scalar on one public graphics pair:
Dragon -> HappyBuddha.
```

Amendment made:

The midterm report now uses:

```text
one Level-B same-source representative workload
one-workload Level-B representative reproduction
```

instead of broad "Level-B reproduction" phrasing. It states that the paper also
contains MRI, geospatial, and additional graphics workload families, and that
the current packet does not cover them.

## Additional Non-Blocking Review Notes Addressed

The amended report now also states:

```text
large-scale value correctness rests on author agreement;
independent exact-reference agreement exists only at small/bounded gates;
the full 437645 x 543652 route does not materialize an independent exact oracle.
```

Timing wording was left source-specific:

```text
Goal5212/5216 current route:
  fresh route_wall = 0.8517371863126755s
  full_total_including_load = 1.5306707620620728s

Goal5217 same-POD matrix:
  fresh route median = 0.8396428748965263s
  fresh full total median = 1.5200408399105072s
```

These are adjacent same-route evidence points, not separate algorithmic claims.

## Residual Claim Boundary

Still allowed:

```text
RTDL matches the author binary re-run directed-HD scalar on one public
Dragon -> HappyBuddha Level-B representative workload.
```

Still forbidden:

```text
RTDL matches the paper log;
broad Level-B paper reproduction is complete;
exact per-source witnesses are reproduced for the full route;
full X-HD paper reproduction is complete;
exact paper dataset reproduction is complete;
author-vs-RTDL performance ratio;
author parity;
warm-only headline.
```

## Requested Reviewer Sign-Off

Please verify that RA-1, RA-2, and RA-3 are fully addressed and, if so, upgrade
the midterm packet from:

```text
approve_with_required_amendments
```

to:

```text
approve_xhd_midterm_level_b_single_workload_status_with_caveats
```
