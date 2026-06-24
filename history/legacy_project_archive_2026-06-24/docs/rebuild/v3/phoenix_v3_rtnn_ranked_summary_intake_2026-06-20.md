# Phoenix V3 RTNN Ranked-Summary Candidate Intake

Status: internal candidate intake, not M7 release evidence, 2026-06-20.

This report extracts the RTNN ranked-summary rows from the current all-app
calibrated artifact and classifies them against the Phoenix V3 capability
rules.

It does not authorize V3 release wording, public speedup wording, universal
RTNN acceleration wording, paper reproduction wording, or RTNN M7
qualification.

## Artifact

Source artifact:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
```

Focused intake:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json
```

Builder:

```text
scripts/v3_phoenix_rtnn_ranked_summary_intake.py
```

## Result

The focused intake passed as internal candidate evidence:

```text
status: internal_rtnn_ranked_summary_candidate_not_m7
generic_capability: ranked_summary
generic_capability_status: distribution_specific_candidate_wall_regression
row_count: 6
group_count: 3
all_rows_ok: true
all_same_contract: true
all_same_metric_source: true
all_aggregate_summaries_match: true
all_claim_flags_blocked: true
all_hot_optix_faster_than_embree: true
all_wall_optix_slower_than_embree: true
release_authorized: false
public_speedup_claim_authorized: false
m7_qualified: false
```

## Rows

| Distribution | Hot OptiX / Embree | Wall OptiX / Embree | Classification |
| --- | ---: | ---: | --- |
| clustered | 3.333x | 0.625x | internal candidate only |
| shell | 1.182x | 0.316x | internal candidate only |
| uniform | 1.084x | 0.303x | internal candidate only |

The hot metric is `elapsed_sec` from the same app runner. The wall metric is
the all-app runner wall median around the row. OptiX wins on the hot
ranked-summary rows, but OptiX is slower on wall timing for all three
distributions in this artifact. Wall ratios below 1.0 mean OptiX is slower than
Embree.

## What This Evidence Means

Allowed reading:

```text
On the 65,536-point distribution ladder, OptiX hot elapsed ranked-summary rows
beat Embree hot elapsed rows, with the strongest result on clustered data.
```

Important supporting facts:

- Embree and OptiX rows use the same exact fixed-radius ranked-summary
  contract;
- aggregate summaries match between backends;
- all rows use 65,536 queries and `k_max=50`;
- all public speedup, paper-equivalent, RT-core neighbor-search, and true
  zero-copy claim flags remain blocked;
- summary rows are materialized, so this is not a device-resident result row.

## What This Evidence Does Not Mean

Forbidden reading:

```text
V3 proves universal RTNN acceleration, paper reproduction, or release-authorized
ranked-summary performance.
```

Current M7 blockers:

- OptiX wall timing is slower than Embree for all three distributions;
- results are distribution-specific, not universal RTNN acceleration;
- `paper_equivalent_rtnn_row=false`;
- summary rows are materialized;
- no author-code or external ANN baseline comparison is attached;
- `prepared_cuda_graph_replay=false`;
- no multi-run variance evidence is attached;
- no fresh row-level public release review has occurred.

## Decision

This packet is useful, but it is not closure.

RTNN currently has a real ranked-summary hot-path signal, especially on the
clustered distribution. It also has an equally real wall-time blocker. The next
RTNN work should either:

- keep these rows internal as distribution-specific evidence; or
- repair/characterize wall timing and build a proper M7 row packet.

It should not be promoted directly into user-facing performance claims.

## Goal-Level Decision Audit

Decision: create an RTNN focused intake from the current all-app artifact
instead of quoting the clustered 3.333x row directly.

1. Was I foolish?

   No. The intake makes the wall-timing regression visible before any claim
   work.

2. If yes, what actions would make it foolish?

   It would be foolish to cite the clustered hot-row win as universal RTNN
   acceleration while the wall metric is slower on every distribution.

3. Was there another path?

   Yes. I could rerun the pod first, but the current evidence first needs
   classification.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path accepts the ranked-summary hot signal but blocks M7
   promotion until the wall-time and distribution-specific issues are solved.
