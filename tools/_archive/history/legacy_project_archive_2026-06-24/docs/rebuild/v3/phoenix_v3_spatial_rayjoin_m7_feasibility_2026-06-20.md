# Phoenix V3 Spatial RayJoin M7 Feasibility

Status: feasibility packet, not M7 promotion.

```text
status: spatial_rayjoin_m7_feasibility_not_promoted
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

## Verdict

Spatial RayJoin is one of the stronger Phoenix V3 internal topology-stream
evidence families in the M7 classification packet, but it is not M7-promoted
here.

The reason is not that the route lacks value. The reason is that current
evidence proves a narrower internal claim:

```text
RTDL can express same-contract point-location and active-count topology rows,
and RTDL OptiX can beat RTDL Embree on those rows.
```

It does not prove:

```text
RTDL beats the RayJoin author implementation.
RTDL reproduces the RayJoin paper.
RTDL accelerates full polygon overlay or full RayJoin end to end.
```

## Evidence Sources

| Evidence | Path |
| --- | --- |
| Current M5 pod evidence | `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md` |
| Current M5 artifact | `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620` |
| RayJoin author build evidence | `docs/rebuild/v3/evidence/rayjoin_author_build_20260620` |
| M7 row classification packet | `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md` |
| External M5 review | `docs/reviews/claude_phoenix_v3_m5_author_recovery_review_2026-06-20.md` |
| Codex 2-AI closure | `docs/reviews/codex_phoenix_v3_m5_author_recovery_2ai_consensus_2026-06-20.md` |

Current packet review status:

```text
external_review_status: blocked_current_packet
2ai_consensus_status: not_recorded_for_this_packet
blockage_report: docs/reviews/external_review_blocked_phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md
```

Superseding 2026-06-21 review state:

```text
external_review_status: claude_approved_with_required_fixes
2ai_consensus_status: claude_codex_consensus_complete_no_m7_promotion
external_review: docs/reviews/claude_phoenix_v3_spatial_rayjoin_m7_feasibility_review_2026-06-21.md
codex_consensus: docs/reviews/codex_phoenix_v3_spatial_rayjoin_m7_feasibility_2ai_consensus_2026-06-21.md
```

The earlier M5 external review supports the underlying author-code recovery
facts. The 2026-06-21 Claude review covers this feasibility packet and accepts
the not-promoted classification after the named blocker/provenance fixes below.

## Tiny Negative Row

The standard all-workload row remains a non-claim:

```text
row:   spatial_rayjoin / rayjoin_all_backend_query_summary
ratio: 0.03414924661592695x OptiX versus Embree
```

This row uses tiny route-health fixtures: LSI has `row_count=1`, overlay has
`row_count=0`, and PIP has `row_count=6`, with `warmup=0` and `repeat=1`.
It teaches users that OptiX launch and orchestration costs can dominate tiny
fixtures. It must never be used as a RayJoin paper comparison.

The detailed explanation is:

```text
docs/rebuild/v3/v3_negative_route_explanations_2026-06-20.md
```

## M5 Point-Location Evidence

The M5 PIP point-location row is the useful topology-stream result:

| Field | Value |
| --- | ---: |
| Query points | 100,000 |
| Query generation | backend-parity-filtered random bbox |
| Exact-row tie candidates rejected | 1 |
| OptiX repeats | 1000 |
| Embree repeats | 1000 |
| Row materialization in timed path | false |
| Exact `(point_id, face_id, segment_id)` mismatches | 0 |
| Positive face count | 43,738 on both backends |
| RTDL OptiX wall speedup vs RTDL Embree | 1.920x |
| RTDL OptiX native traversal speedup vs RTDL Embree | 2.834x |
| RayJoin author Query speedup vs RTDL OptiX wall | 5.728x |
| RayJoin author Query speedup vs RTDL OptiX native traversal | 3.861x |

Interpretation:

```text
RTDL OptiX beats RTDL Embree under the same point-location topology contract.
RayJoin author RT is still faster than RTDL OptiX on this row.
```

That makes the row valuable but internal. It is not an `RTDL beats RayJoin`
result and not a paper-reproduction result.

## Overlay Active-Count Evidence

The overlay row is also useful and still internal:

| Field | Value |
| --- | ---: |
| Output contract | `overlay_active_pair_dependency_count` |
| Left CDB slice | `br_county_start256_count512.cdb` |
| Right CDB slice | `br_soil_start256_count512.cdb` |
| Active count | 174 |
| OptiX and Embree active counts match | true |
| OptiX and Embree repeats | 25 / 25 |
| Row materialization avoided in timed path | true |
| OptiX speedup vs RTDL Embree timed median | 499.112x |

Interpretation:

```text
This is same-contract active-count topology evidence, not full polygon overlay
and not RayJoin Section 5.7 reproduction.
```

## Strong Authored Hot-Route Rows

The all-app calibrated route map also contains strong authored tiled rows:

| Row | Current reading |
| --- | ---: |
| `rayjoin_overlay_seed_authored_tiled_x2048` | 30489.613x OptiX over Embree, internal |
| `rayjoin_lsi_authored_tiled_x2048` | 516.792x OptiX over Embree, internal |
| `rayjoin_pip_authored_tiled_x2048` | 10.703x OptiX over Embree, internal |

Pinned provenance:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
```

These rows support the Phoenix conclusion that point-location/topology streams
are promising. They do not remove the M7 blockers because they are authored
hot-route rows, not a public RayJoin product contract.

## M7 Blockers

- `rayjoin_author_rt_faster_than_rtdl_optix`
- `not_full_rayjoin_paper_reproduction`
- `not_full_polygon_overlay_or_materialization`
- `mixed_timing_basis_requires_public_methodology_review`
- `m3_phase_table_gap_for_pip_before_public_row`
- `tiny_standard_row_is_negative_and_must_stay_explained`
- `broad_v3_faster_than_v2_claim_authorized_false`
- `no_public_row_level_release_review`
- `no_future_public_row_2ai_consensus_for_spatial_rayjoin_m7_promotion`

## What This Allows

Allowed internal wording:

```text
Spatial RayJoin is a strong internal Phoenix V3 point-location/topology-stream
candidate. RTDL OptiX and RTDL Embree match on the backend-parity-filtered PIP
row, RTDL OptiX beats RTDL Embree on that same contract, and authored tiled
hot-route rows show large OptiX-over-Embree signals.
```

Allowed user-facing teaching after review:

```text
Use Spatial RayJoin as an example of why V3 separates route-health rows,
same-contract topology rows, and author/paper comparisons.
```

Forbidden public wording:

```text
Do not claim RTDL beats RayJoin.
Do not claim RayJoin paper reproduction.
Do not claim full polygon overlay acceleration.
Do not use the 0.034x tiny row or the 30489x hot row without the exact contract.
Do not promote any Spatial RayJoin row to M7 from this packet.
```

## Next Step

If Spatial RayJoin is promoted later, the next packet must be a public-row
review packet, not another large-ratio table. It must include:

- one named user contract;
- one exact dataset path;
- RTDL OptiX and RTDL Embree same-contract timing;
- RayJoin author timing when author comparison is mentioned;
- M3 phase table for build, traversal, continuation, and host overhead;
- explicit non-paper wording;
- external public-row review.

## Goal-Level Decision Audit

Decision: classify Spatial RayJoin as strong internal topology-stream evidence,
not an M7 release row.

1. Was I foolish?

   No. This decision uses the existing M5 pod evidence, external review, and
   M7 classification packet instead of quoting only the largest speedup number.

2. If yes, what actions would make this foolish?

   It would be foolish to hide that RayJoin author RT is faster than RTDL OptiX,
   or to place the tiny 0.034x row and the 30489x authored hot row in the same
   table without explaining their different contracts.

3. Was there another path?

   Yes. I could have tried to tune RayJoin immediately. That would be premature
   before the current evidence is separated into route-health, topology, author,
   and public-row categories.

4. Can I now try a different path that actually solves the problem?

   Yes. This packet makes the current state explicit, keeps release flags false,
   and leaves a precise M7 promotion path instead of a vague performance story.
