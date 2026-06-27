# Call For Review: Phoenix V3 M11 Spatial Segment-Intersection POD A/B

Date: 2026-06-22
Status: `pending_external_review_not_release`

This packet asks for critical review of the M11 focused POD A/B. The result is
currently classified as productized-runner coverage pass but performance fail.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_pod_spend_authorized: false
```

## Inputs

- M10 consensus:
  `docs/reviews/codex_linnaeus_phoenix_v3_m10_spatial_segment_intersection_2ai_consensus_2026-06-22.md`
- M11 classification JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_segment_intersection_runner_m11_pod_ab_2026-06-22.json`
- M11 report:
  `docs/reports/phoenix_v3_spatial_segment_intersection_runner_m11_pod_ab_2026-06-22.md`
- Evidence directory:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m10_focused_pod_ab_20260622`

## Summary

Focused POD protocol:

- old route: `prepared_optix_left_id_dense_count`
- new route: `prepared_execution_segment_intersection_topology_stream`
- dataset: `derived/authored_lsi_crossing_tiled_x2048`
- repeat/warmup: `5/1`
- outer samples: `9` per route
- no rows
- same POD: RTX 4000 Ada, driver `550.127.05`

Result:

- old hot median: `0.00012440979480743408s`
- new inner hot median: `0.00013191252946853638s`
- new runner-inclusive median: `0.00020245462656021118s`
- old/new inner hot speedup: `0.9431234114656877x`
- old hot/new runner-inclusive speedup: `0.6145070474367939x`
- both routes returned count `2048`

Metadata gates all passed for the new route:

- productized execution path
- runtime trunk executes end to end
- validation passed
- internal device residency
- no hot-path host materialization flag
- prepared handle contract
- M3 phase table contract
- complete M3 table

Proposed interpretation:

M11 is a productized-runner coverage pass but performance fail. It should not
count as a V3 speed win, should not authorize all-app POD, and should not
authorize any public speedup claim. The next decision is whether to optimize
generic prepared-execution runner overhead or retarget another Set-A family
where overhead can amortize across more work.

## Questions For Reviewer

1. Is the coverage-pass/performance-fail classification correct?
2. Should the new route count as productized-runner coverage for the Spatial
   LSI Set-A probe even though it is not a speed win?
3. Does the runner-inclusive slowdown require a generic runner-overhead task
   before any more Spatial LSI POD?
4. Should the next Phoenix step be overhead reduction or retargeting another
   Set-A family?
5. Does this result authorize any all-app run, release claim, or public speedup
   wording?

## Requested Verdict Labels

Choose exactly one:

- `accept_m11_negative_retarget`: accept M11 as coverage pass/performance fail
  and recommend retargeting another Set-A family before more Spatial LSI POD.
- `accept_m11_negative_optimize_runner`: accept M11 as coverage pass/performance
  fail and recommend a local generic runner-overhead reduction task before any
  more POD.
- `revise_m11_analysis`: require parsing or methodology corrections before
  deciding next work.
- `reject_m11`: M11 classification is wrong.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- focused POD authorization for another run: yes/no
- all-app POD authorization: yes/no
- whether Spatial LSI can be counted as productized-runner coverage, not speed
  coverage

## Goal-Level Decision Audit

Decision: seek review before choosing overhead reduction or retargeting.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish move would be to call the clean metadata a speed win.
3. Was there another path?
   Yes: immediately tune runner overhead or run a broader suite. Both would be
   premature without reviewing the negative evidence.
4. Can I now try a different path?
   Yes: get review, then either optimize generic runner overhead locally or
   retarget the next Set-A family without expanding claims.
