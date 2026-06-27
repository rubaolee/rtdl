# Codex + Rawls 2-AI Consensus: Phoenix V3 M13 Spatial Segment-Intersection POD Rerun

Date: 2026-06-22
Status: `accept_m13_stop_spatial_retarget`

This consensus records the M13 focused POD rerun review. It is not a release
authorization.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_for_another_run: false
full_all_app_pod_spend_authorized: false
```

## Inputs

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m13_spatial_segment_intersection_pod_rerun_2026-06-22.md`
- M13 JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_segment_intersection_runner_m13_pod_ab_2026-06-22.json`
- M13 report:
  `docs/reports/phoenix_v3_spatial_segment_intersection_runner_m13_pod_ab_2026-06-22.md`
- M13 parsed evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m13_focused_pod_ab_20260622/summary.parsed.json`

Local gates before consensus:

```text
M13 JSON parse: OK
M13 parsed evidence JSON parse: OK
M13 claim-boundary scan: OK
Targeted tests: 39 tests OK
```

## Reviewed Result

M13 improved the productized runner median versus M11, but it did not beat the
old route:

| Metric | M11 | M13 |
| --- | ---: | ---: |
| Old hot median sec | `0.00012440979480743408` | `0.0001227855682373047` |
| New inner hot median sec | `0.00013191252946853638` | `0.00012449920177459717` |
| New runner-inclusive median sec | `0.00020245462656021118` | `0.00015626102685928345` |
| Old/new inner hot speedup | `0.9431234114656877x` | `0.9862357869539198x` |
| Old hot/new runner-inclusive speedup | `0.6145070474367939x` | `0.7857721832832689x` |

The M13 runner is `1.2956181757497736x` faster than the M11 runner, but the
M13 productized runner is still `1.272633495145631x` slower than the old hot
route.

## Rawls Review

Rawls returned verdict `accept_m13_stop_spatial_retarget`.

Rawls accepted the classification as overhead-improved but still speed-fail:
the decisive evidence is that M13 improved versus M11, but runner-inclusive
M13 remains slower than the old route (`0.000156261s` new runner versus
`0.000122786s` old hot). Inner hot is near parity (`0.9862x`), not a win.

Rawls authorizations:

- release authorization: no
- public speedup authorization: no
- focused POD authorization for another run: no
- all-app POD authorization: no
- Spatial LSI may count as productized-runner coverage: yes
- Spatial LSI may count as speed coverage: no

## Codex Position

Codex agrees.

M13 validates one generic runner-overhead reduction and validates the
productized route metadata, but it does not produce a speed win. Treating
M13-vs-M11 improvement as a V3 speed claim would be wrong because the release
comparison is against the old/V2-aligned route on the same metric.

## Consensus

Decision: `accept_m13_stop_spatial_retarget`

- Spatial LSI counts as productized-runner coverage only.
- Spatial LSI does not count as speed coverage.
- Stop Spatial LSI speed work for now.
- Do not run another focused Spatial LSI POD.
- Do not run all-app POD from this result.
- Retarget the next Set-A runtime-trunk family.

Recommended next target: a Set-A family where the runner can actually compound
across phases, preferably the redesign Step-1 line:
fixed-radius self-query -> grouped-stream/component continuation, with
internal RTDL device residency between phases and no external host buffer
exposure.

## Goal-Level Decision Audit

Decision: stop Spatial LSI speed work after M13 and retarget.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be continuing POD or treating
   M13-vs-M11 runner improvement as release speed evidence.
3. Was there another path?
   Yes: more local overhead analysis or another POD. More POD is not justified
   because runner-inclusive M13 still loses to the old route.
4. Can I now try a different path?
   Yes: keep Spatial LSI as coverage-only and move to the next Set-A
   residency/continuation-rich runtime-trunk probe.
