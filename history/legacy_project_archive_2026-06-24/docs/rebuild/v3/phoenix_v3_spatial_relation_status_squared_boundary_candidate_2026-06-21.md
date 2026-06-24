# Phoenix V3 Spatial Guarded Squared-Boundary Candidate

Status: `spatial_relation_status_squared_boundary_default_path_m7_row_accepted_with_boundary`.

This packet adds default-path POD evidence for the missing
`point_location_topology_stream` V3 capability family. The optimized
route is now default-enabled in source and has been measured with no
enabling env flags. Claude and Codex accept it as one bounded M7
release-surface row, while public speedup claims remain disabled.

- External review: `docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md`
- Codex consensus: `docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md`
- Previous external review: `docs/reviews/claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md`
- Previous Codex consensus: `docs/reviews/codex_phoenix_v3_spatial_squared_boundary_candidate_2ai_consensus_2026-06-22.md`
- Current external review status: `claude_accept_with_boundary_default_path`
- Current Codex consensus status: `claude_codex_consensus_accept_default_path_m7_row`
- P1 default-path resolution required: `false`

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
m7_promotion_authorized: true
M7 rows added now: 1
```

## Result

- Dataset: `data/rayjoin_public_cdb/br_county.cdb`
- Candidate row id: `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`
- Baseline prefilter-zero median: `1.895688 ms`
- Guarded squared-boundary median: `1.080450 ms`
- Default-path guarded squared-boundary median: `1.080599 ms`
- Default-path sample range: `1.079373` to `1.083527 ms`
- Candidate sample range: `1.078725` to `1.081970 ms`
- Speedup vs current prefilter-zero route: `1.755x`
- Default path vs disable control: `5.372x`
- Guarded-squared-only no-prefilter median: `2.845794 ms`
- Guarded-squared-only speedup vs default no-prefilter: `1.899x`
- RayJoin author Query timer: `1.865660 ms`
- Default path vs author Query timer: `1.727x`
- Default path margin under author Query: `0.785061 ms`
- Candidate vs author Query timer: `1.727x`
- Candidate margin under author Query: `0.785210 ms`
- Exact row count: `47262`
- Row count consistent: `true`

## Count Invariants

| route | raw candidates | boundary candidates | emitted | dropped |
| --- | ---: | ---: | ---: | ---: |
| baseline | `[47570]` | `[47550]` | `[47262]` | `[308]` |
| guarded squared | `[47570]` | `[47550]` | `[47262]` | `[308]` |
| default path | `[47570]` | `[47550]` | `[47262]` | `[308]` |
| disable control | `[155555]` | `[47550]` | `[47262]` | `[108293]` |

## Default Path Evidence

- Default-path packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/default_path_guarded_squared_repeat50_sample7.json`
- Activation: `default_path_no_enabling_env_flags`
- Disable-control packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/disable_control_both_zero_repeat10_sample1.json`
- Disable-control median: `5.804896 ms`
- Built OptiX library SHA256: `36500bba1bdd1bd7b517376b28ca23aeb51af82b97f908786bdb900ec1b40877`

## Predicate Equivalence

- Equivalence packet: `docs/rebuild/v3/phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.json`
- Guarded mismatch count: `0`
- Pure squared mismatch count recorded: `10`
- Guard tolerance: `1e-06`

Pure squared comparison is not claimed equivalent. The candidate uses a
guarded squared fast path and falls back to the old sqrt predicate near
thresholds.

## Guarded-Squared-Only Default-Surface Probe

- Default no-prefilter median: `5.404521 ms`
- Guarded-squared-only no-prefilter median: `2.845794 ms`
- Speedup: `1.899x`
- Clears author Query bar: `false`

The guarded squared-boundary predicate is a material generic optimization by itself, but the public-county author Query bar is cleared only when paired with relation-status zero prefiltering.

## Boundary

This packet can support external review of a row-scoped M7 candidate. It does not by itself authorize public release, broad V3-vs-V2 claims, RTDL-beats-RayJoin wording, paper reproduction wording, true zero-copy, or V4 embedding claims.

The author Query timer is used as a performance bar only. The author run
does not print result count, so this packet cannot support broad
`RTDL beats RayJoin` wording without review and wording constraints.

## Required Next Actions

- Update the release-surface breadth gate so point_location_topology_stream contributes one bounded M7 row.
- Carry the git_commit:null provenance gap forward to public-release readiness gates.
- Keep all public release, V3-vs-V2, RTDL-beats-RayJoin, paper reproduction, zero-copy, and V4/embedding claims unauthorized.

## Goal-Level Decision Audit

Decision: Accept the guarded squared-boundary evidence with Claude/Codex boundary, record the new default-path POD evidence, and promote it to one bounded M7 release-surface row after external review and consensus.

1. Was I foolish? No. The candidate is a generic predicate optimization with an explicit fallback for pure-squared edge cases, row count is stable at 47,262, the measured gain is material rather than a tiny 1.01x result, and I kept release promotion blocked after external review.
2. If yes, what actions made the decision foolish? The foolish action would be to call this a public RayJoin win, a whole-app win, or a released V3 capability because the default-path POD evidence clears the author Query timer. This packet only counts an internal M7 row and keeps public/broad claims disabled.
3. Was there another path? I could have left Spatial as a future-research gap after the prefilter-zero near miss. That would avoid risk, but it would miss a real generic hot-path optimization visible in the exact f64 helper.
4. Can I now try a different path? Update the release-surface gates with one bounded row, then keep working on Phoenix V3 breadth without weakening claim boundaries.
