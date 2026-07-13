# Review Sign-Off: X-HD Midterm After Goal5216 Amendments

Date: 2026-07-09

Reviewed files:

```text
history/internal_docs/review_xhd_midterm_after_goal5216_2026-07-09.md
history/internal_docs/xhd_midterm_report_after_goal5216_2026-07-09.md
history/internal_docs/xhd_midterm_after_goal5216_review_amendment_response_2026-07-09.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Verdict

```text
approve_xhd_midterm_level_b_single_workload_status_with_caveats
```

The prior `approve_with_required_amendments` review conditions are satisfied.
The amended midterm packet now presents the current X-HD Level-B evidence with
the required narrow scope and caveats.

## Verified Amendments

### RA-1: Exact-value-only route, approximate witnesses

Verified. The amended midterm report now states that the current full public
Dragon -> HappyBuddha route is exact only for the directed-Hausdorff scalar
value. It records:

```text
global_bound_early_break_count = 409376 / 437645 (~93.5%)
per_source_witness_exact = false
```

The report now explicitly forbids presenting per-source nearest witnesses from
the full route as exact X-HD witness output.

### RA-2: Matches author re-run, not the paper log

Verified. The amended report now distinguishes the three values:

```text
Author re-run HDResult on public data: 0.12572988867759705
Paper-branch log HDResult:            0.12572969496250153
RTDL HDResult on public data:          0.12572988629271128

RTDL vs author re-run diff:            ~2.38e-9
Author re-run vs paper log diff:       ~1.94e-7
```

The report no longer says that RTDL matches the paper log. It states that RTDL
matches the author binary re-run on the public same-source workload, while the
author re-run itself differs from the pinned paper-branch log.

### RA-3: One-workload Level-B scope

Verified. The amended report now describes the evidence as one public Stanford
Dragon -> HappyBuddha same-source representative workload. It explicitly says
this is not broad Level-B paper coverage across the paper's MRI, geospatial,
and additional graphics workloads, and it is not full paper reproduction.

## Allowed Summary

RTDL currently has one Level-B same-source representative X-HD workload on
public Stanford Dragon -> HappyBuddha. On that workload, RTDL matches the
author binary re-run directed-HD scalar on the same public data to about
`2.38e-9`. The public-data author re-run remains distinct from the pinned
paper-branch log by about `1.94e-7`, so exact paper dataset reproduction is not
closed. The current route is exact-value-only: early break makes most
per-source witnesses approximate.

## Forbidden Summaries

The following remain unauthorized:

```text
RTDL matches the paper log.
Broad Level-B X-HD reproduction is complete.
Exact per-source witnesses are reproduced for the full route.
Full X-HD paper reproduction is complete.
Exact paper dataset reproduction is complete.
Author-vs-RTDL performance ratio or parity is established.
Warm-only route time is the performance headline.
```

## Register Disposition

The X-HD review register may update the midterm amendment response from
`Reviewer sign-off pending` to externally verified under the verdict:

```text
approve_xhd_midterm_level_b_single_workload_status_with_caveats
```
