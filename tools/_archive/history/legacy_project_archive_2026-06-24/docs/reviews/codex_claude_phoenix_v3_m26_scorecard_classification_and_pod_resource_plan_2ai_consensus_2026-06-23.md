# 2-AI Consensus - Phoenix V3 M26 Scorecard Classification And POD Resource Plan

Date: 2026-06-23

Participants:

- Codex
- Claude

Consensus verdict: **`approve_with_amendments_applied`**

## Reviewed Inputs

- `docs/rebuild/v3/phoenix_v3_m26_scorecard_classification_and_pod_resource_plan_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m26_scorecard_classification_and_pod_resource_plan_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m26_scorecard_classification_and_pod_resource_plan_review_2026-06-23.raw.md`
- `docs/reviews/codex_claude_phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2ai_consensus_2026-06-23.md`

## Consensus Decisions

### D1 - M22 LibRTS AABB single-shot watch row is Set B/control

Codex and Claude agree that the strict M22 row:

```text
goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index
```

is a Set-B/control row, not a primary Set-A release proof.

Amendment applied:

- The M26 plan now distinguishes this row from the historical **AABB M2.1 native query-handle runner route**, which earlier documents treated as a Set-A candidate.
- The M22 row was found as watch/control/problem-row evidence, not as a frozen Set-A release row.
- D1 therefore does not demote a frozen Set-A row; it classifies the M22 watch row explicitly.

### D2 - Prepared/repeated AABB OptiX is supporting evidence

Codex and Claude agree that M25 prepared/repeated AABB OptiX evidence is useful runner and RT-hardware sanity evidence, but it is not primary Set-A release proof.

Reason:

- `0.995x` and `0.999x` are V3/V2.14 parity results, not material V3-over-V2 wins.
- The `63x-105x` figures are OptiX-vs-Embree hardware comparisons, not V3-vs-V2 runtime proof.

### D3 - All-app remains frozen

Codex and Claude agree that no full all-app run is authorized until focused evidence shows at least two true Set-A probes with runtime-sourced material gains.

Amendment applied:

```text
minimum focused Set-A material gain to count: >= 1.15x
preferred focused Set-A material gain: >= 1.20x
```

Wins must come from the productized prepared execution/session runner and must not come from route-specific caches or bypasses.

### D4 - M27 order

Claude required a sequencing amendment, accepted by Codex:

1. First reproduce/triage the Embree 32768 stress regression.
2. If reproducible below `0.950x`, log it as an independent blocker.
3. Then attempt LibRTS AABB strict cold single-shot OptiX repair to `>=0.950x`, or record why it cannot be done without app-specific bypass.

## Resource Consensus

Near-term POD expectation:

```text
next 12 hours: 1-3 POD hours
estimated cost at $0.25/hour: $0.25-$0.75
no all-app run
```

Full Phoenix V3 path to a release-candidate all-app run:

```text
optimistic: 2-3 days, 6-12 POD hours, $1.50-$3.00
realistic: 3-5 days, 10-20 POD hours, $2.50-$5.00
early stop if Step-1/Step-2 trunk gains fail: 2-4 POD hours, $0.50-$1.00
```

These are planning estimates, not release commitments.

## Non-Authorization

This 2-AI consensus does **not** authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Reclassifying rows after results.
- Counting the M22 LibRTS AABB single-shot watch row as Set A.
- Counting prepared/repeated AABB OptiX parity as primary Set-A release proof.
- V4/external zero-copy/embedding claims.

Final status: **M26 classification/resource plan accepted with amendments applied; proceed to M27 focused triage/repair, not all-app.**
