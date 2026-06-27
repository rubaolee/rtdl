# Call For Review: Phoenix V3 M13 Spatial Segment-Intersection POD Rerun

Date: 2026-06-22
Status: `pending_external_review_not_release`

This packet asks for critical review of the M13 focused POD rerun after M12's
generic runner-overhead reduction. The proposed classification is overhead
improved but still speed-fail.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_for_another_run: false
full_all_app_pod_spend_authorized: false
```

## Inputs

- M12 consensus:
  `docs/reviews/codex_schrodinger_phoenix_v3_m12_runner_overhead_2ai_consensus_2026-06-22.md`
- M13 JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_segment_intersection_runner_m13_pod_ab_2026-06-22.json`
- M13 report:
  `docs/reports/phoenix_v3_spatial_segment_intersection_runner_m13_pod_ab_2026-06-22.md`
- M13 evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m13_focused_pod_ab_20260622`
- M11 evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m10_focused_pod_ab_20260622`

## Summary

M13 repeated the exact M11 focused A/B:

- dataset: `derived/authored_lsi_crossing_tiled_x2048`
- workload: `lsi`
- old route: `prepared_optix_left_id_dense_count`
- new route: `prepared_execution_segment_intersection_topology_stream`
- repeat/warmup: `5/1`
- outer samples: `9` per route
- no rows
- same POD/hardware class

Result:

| Metric | M11 | M13 |
| --- | ---: | ---: |
| Old hot median sec | `0.00012440979480743408` | `0.0001227855682373047` |
| New inner hot median sec | `0.00013191252946853638` | `0.00012449920177459717` |
| New runner-inclusive median sec | `0.00020245462656021118` | `0.00015626102685928345` |
| Old/new inner hot speedup | `0.9431234114656877x` | `0.9862357869539198x` |
| Old hot/new runner-inclusive speedup | `0.6145070474367939x` | `0.7857721832832689x` |

M13 improved the new runner median by `1.2956181757497736x` versus M11.
However, the productized route remains slower than the old route on the
runner-inclusive metric.

Metadata gates all passed, including:

- productized path
- runtime trunk executes end to end
- validation passed
- M3 table
- prepared handle
- `measured_run_prepared_override_used`
- `measured_output_finalized_once`
- `per_repeat_output_finalization_avoided`

## Questions For Reviewer

1. Is the overhead-improved but speed-fail classification correct?
2. Can Spatial LSI now count as productized-runner coverage only, not speed
   coverage?
3. Should Phoenix do one more local-only generic runner-overhead pass, or stop
   Spatial LSI work and retarget the next Set-A family?
4. Is any further focused POD authorized from this result?
5. Does this result authorize all-app POD, release, or public speedup wording?

## Requested Verdict Labels

Choose exactly one:

- `accept_m13_stop_spatial_retarget`: accept M13; count Spatial LSI as coverage
  only; stop Spatial LSI speed work and retarget the next Set-A family.
- `accept_m13_local_overhead_pass_only`: accept M13; do one more local-only
  generic overhead pass before deciding whether another POD could ever be
  justified.
- `revise_m13_analysis`: require parsing/methodology corrections before
  deciding.
- `reject_m13`: classification is wrong.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- focused POD authorization for another run: yes/no
- all-app POD authorization: yes/no
- whether Spatial LSI may count as productized-runner coverage
- whether Spatial LSI may count as speed coverage

## Goal-Level Decision Audit

Decision: seek review after M13 instead of continuing POD.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish move would be to treat M13's M11-relative improvement as a speed
   win against the old route.
3. Was there another path?
   Yes: keep running POD. That is explicitly not authorized.
4. Can I now try a different path?
   Yes: get review and either do local-only overhead analysis or retarget.
