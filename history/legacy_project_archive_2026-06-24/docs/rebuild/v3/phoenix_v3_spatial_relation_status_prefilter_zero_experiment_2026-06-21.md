# Phoenix V3 Spatial Relation-Status Prefilter-Zero Experiment

Status: `spatial_relation_status_prefilter_zero_near_miss_not_m7`.

This packet records a real generic native optimization attempt for
`point_location_topology_stream`. It does not add an M7 row and does not
authorize release or public speedup wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
m7_promotion_authorized: false
M7 rows added: 0
```

## Result

- Dataset: `data/rayjoin_public_cdb/br_county.cdb`
- Old best legal RTDL prepared query: `5.406518 ms`
- Prefilter-zero stable prepared query: `1.903493 ms`
- Improvement vs old legal route: `2.840x`
- RayJoin author Query bar: `1.865660 ms`
- Author remains faster by: `1.020x`
- Remaining gap: `0.037833 ms`
- Exact row count: `47262`
- Row count consistent: `true`

The optimization is material and correct on the public county packet, but
it remains a near-miss against the same-dataset author timer. Therefore it
is not a Phoenix V3 release row.

## Stable Candidate

- Source: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_20260621/prefilter_zero_relation_status_y_then_x_repeat50_sample7.json`
- Point order: `y_then_x`
- repeat/warmup/sample: `50` / `5` / `7`
- RT traversal median: `1.859084 ms`
- Speedup vs old route: `2.840x`
- RTDL relative to author Query: `0.980x`

## Ordering Sweep

| order | prepared query ms | row count | stable |
| --- | ---: | ---: | --- |
| `natural` | `2.760258` | `47262` | `true` |
| `x_then_y` | `2.757892` | `47262` | `true` |
| `morton_xy` | `2.221864` | `47262` | `true` |
| `y_then_x_sample5` | `2.008997` | `47262` | `true` |
| `y_then_x_sample7` | `1.903493` | `47262` | `true` |
| `restored_y_then_x_sample3` | `1.897205` | `47262` | `true` |

## Rejected Follow-Up

- `boundary_helper_exact_contact_fast_path`: `rejected_exact_count_mismatch_not_kept`
- Observed error: `validated relation-status corrected closed-shape count did not match exact prepared count: 47259 != 47262`
- Decision: The boundary-helper fast path was reverted. The surviving source keeps full f64 exact membership after zero-status prefiltering.

## Required Next Actions

- Do not promote Spatial topology-stream to M7 from this packet.
- If this path is continued, find a correctness-preserving optimization that clears the 1.865660 ms author Query bar with stable margin.
- Keep the failed boundary-helper fast path rejected unless a new proof explains the three-count loss.
- Only after a new promotable packet exists, request external AI review and Codex consensus.

## Goal-Level Decision Audit

Decision: Record relation-status zero prefiltering as real generic Spatial topology-stream optimization evidence, but keep it not-M7.

1. Was I foolish? No for the goal-level decision. The foolish move would be to call a 1.903 ms correct near-miss a release row when the same-dataset author Query bar is 1.865660 ms.
2. If yes, what actions made the decision foolish? I made one tooling mistake by using a Bash heredoc in PowerShell for a local JSON summary; it made no file changes and I reran it with a PowerShell here-string. The boundary-helper optimization was also a deliberately bounded experiment; it became invalid because it changed the exact count to 47,259.
3. Was there another path? I could have left Spatial closed as future research. That would avoid risk, but it would not test the obvious generic native bottleneck exposed by the M3 phase table.
4. Can I now try a different path? Keep the correct prefilter-zero result as no-go optimization evidence, preserve the author bar, and continue only if a next generic optimization can clear that bar without count loss.
