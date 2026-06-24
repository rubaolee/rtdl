# Call For Review - Phoenix V3 M26 Scorecard Classification And POD Resource Plan

Date: 2026-06-23

Reviewer requested: Claude

Requested verdict label, choose one:

- `approve`
- `approve_with_amendments`
- `reject`

## Context

M25 2-AI consensus returned `partial_not_closed` for the LibRTS AABB OptiX watch row. The strict single-shot current/V2.14 row is `0.922x`, below the existing `0.950x` threshold, while prepared/repeated OptiX behavior is healthy (`0.995x`, `0.999x`, and 63x-105x OptiX-vs-Embree).

The next decision is not another POD run. It is scorecard classification and resource planning.

Review target:

```text
docs/rebuild/v3/phoenix_v3_m26_scorecard_classification_and_pod_resource_plan_2026-06-23.md
```

Related M25 consensus:

```text
docs/reviews/codex_claude_phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2ai_consensus_2026-06-23.md
```

## Codex Proposed Decisions

1. Classify the strict LibRTS AABB single-shot count row as **Set B/control**, not Set A.
2. Treat prepared/repeated AABB OptiX as **supporting runner evidence**, not primary release Set-A proof.
3. Continue the all-app freeze until at least two true Set-A probes have material runtime-sourced gains.
4. Near-term POD expectation: 1-3 hours in the next 12 hours, mostly focused validation; no all-app.
5. Full Phoenix V3 path to release-candidate all-app: optimistic 2-3 days / 6-12 POD hours; realistic 3-5 days / 10-20 POD hours; stop early if Step-1/Step-2 trunk gains fail.

## Review Questions

1. Is the Set-B/control classification for LibRTS AABB single-shot correct, or should it be amended?
2. Is it correct to reject counting prepared/repeated AABB as primary release Set-A proof?
3. Are the POD time/cost estimates reasonable enough for planning?
4. Should M27 prioritize cold OptiX Set-B repair, Embree 32768 regression, or jump directly to the true Set-A runtime trunk?
5. Does this plan preserve the user's major-version performance mandate without wasting all-app POD time?
6. Does this packet authorize release, all-app, public speedup wording, or V4/external zero-copy/embedding scope?

## Required Non-Authorization Block

Unless your review explicitly says otherwise, this packet does not authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Reclassifying rows after results.
- Counting AABB single-shot as Set A.
- V4/external zero-copy/embedding claims.
