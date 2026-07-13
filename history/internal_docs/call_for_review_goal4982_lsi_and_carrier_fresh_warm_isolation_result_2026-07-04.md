# Call For Review: Goal4982 LSI And Carrier Fresh/Warm Isolation Result

Date: 2026-07-04

Please review:

```text
history/internal_docs/goal4982_lsi_and_carrier_fresh_warm_isolation_result_2026-07-04.md
```

## Context

Claude's review of the v2.14.3 closeout plan required symmetric cold/warm isolation:

- do not warm or discount the smaller carrier cost while leaving the larger LSI producer cost uncharacterized;
- show fresh and warm side by side;
- reject any warm-only headline;
- keep costs in the fresh number unless a real product prepare-once/query-many behavior justifies amortization.

Goal4982 ran the top4 writer-free binary route and collected:

- repeated full-route timings;
- LSI extended producer timings;
- carrier side-builder timings;
- LSI repeat diagnostic output.

## Requested Verdict Label

```text
approve_goal4982_lsi_carrier_symmetric_isolation__lsi_still_dominates
```

or, if the interpretation is flawed:

```text
fail_redo_goal4982_due_to_asymmetric_or_invalid_timing_boundary
```

## Review Questions

1. Does the report treat LSI producer and grouped carrier side-builder symmetrically, rather than warming only the smaller carrier cost?

2. Does the evidence support the conclusion that carrier warm-state cost is now about `0.10-0.11s`, while LSI producer remains about `2.69-2.76s` in repeated full-route runs?

3. Is the report correct to reject the `0.000000s` LSI repeat diagnostic as invalid or insufficient timing evidence, instead of using it as a performance headline?

4. Does the LSI extended timing table correctly identify setup/ensure work (`grouped_range_ensure`, `scaled_cache_ensure`, `exact_pipeline_ensure`, `split_kernel_ensure`) as the current large LSI producer cost, rather than native launch?

5. Does the report avoid author-performance claims, warm-only claims, and any claim that v2.14.3 reaches author overlay speed?

6. Is the recommended next goal correct: decide whether LSI setup can be a real product `prepare-once/query-many` route, or else keep the `~2.7s` LSI producer in the fresh headline?

7. Should Goal4982 close with:

```text
completed_lsi_and_carrier_warmup_symmetric_matrix__lsi_still_dominates
```
