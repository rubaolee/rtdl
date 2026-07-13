# Goal5484: LibRTS Exact Figure-6 Point-Contains Denominator Audit

Date: 2026-07-11

Status: `externally_reviewed_and_approved__six_exact_cases_aligned_to_author_figure6_records__no_ratio`

## Objective

Audit whether the six exact official-input point-contains gates correspond to
the author paper-branch Figure-6 RTSpatial records before any performance work.
This goal checks the workload identity and author log denominator only. It does
not run a new POD route and does not authorize a timing ratio.

## Evidence

The audit consumes:

- `librts_goal5472_author_paper_log_denominators.json`;
- `librts_goal5481_exact_point_contains.json`;
- `librts_goal5482_exact_point_contains_remaining_batch.json`.

It selects records with:

```text
paper_figure = 6
category    = point-contains_queries_100000
index_type  = rtspatial
```

For each of the six cases, it checks exact-gate matched status, geometry count,
query count, result count, and same-input author/RTDL identity against the
corresponding author log record. All six cases pass.

The result is count-level alignment only. Equal result counts do not prove
pointwise containment relation equality, and the standard author query binary
does not expose pair rows for these six cases. A separate Goal5467
app-instrumented representative PIP workload does provide relation-level
evidence: all `71,626` author/RTDL rows match with canonical SHA-256. That
reference is explicitly not evidence for the six exact Figure-6 cases.

## Result

```text
case_count       = 6
all_cases_aligned = true
```

The author timing denominator is recorded as internal `Query Time`, with
`Loading Time` excluded. RTDL route wall is present in the exact gate evidence,
but it is not the same denominator as the author internal metric and is not
authorized for a ratio. The audit result is:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5484_exact_figure6_point_contains_denominator.json
```

## Claim boundary

Authorized:

- all six exact point-contains inputs align to a Figure-6 RTSpatial 100K log
  record by geometry count, query count, and result count;
- the author Query-Time denominator and its exclusion of Loading Time are
  explicitly recorded;
- the six exact same-input count gates remain valid evidence.

Not authorized:

- a Figure-6 plot or complete Figure-6 reproduction;
- author/RTDL performance ratio;
- timing parity or whole-program speedup;
- pair-row agreement, which the standard author binary does not expose;
- complete LibRTS paper reproduction;
- Embree comparison.

The raw evidence also shows seconds-scale RTDL route wall versus sub-
millisecond author internal Query Time on these cases. This indicates that the
current RTDL route is much slower, but the phase mismatch means it is not a
valid performance ratio.

## Next decision

Any performance goal must first define an aligned RTDL counterpart to the
author's internal Query-Time boundary, including whether RTDL index preparation,
WKT parsing, point-query upload, result counting, and row materialization are
inside or outside the measured phase. Until that contract is approved, keep
the six-of-six result as correctness and denominator evidence only.
