# AABB Candidate Stream

Status: V3 rebuild tutorial with three M7-qualified row-scoped AABB claims; not a release claim and not release authorization.

This lesson shows the strongest current generic AABB signals without turning
them into LibRTS paper, Contact Manifold solver, broad AABB-index, or V2
speedup claims.

## What This Example Teaches

The V3 capability is `aabb_candidate_stream`: generic prepared
`AABB_INDEX_QUERY_2D` candidate discovery. It is useful because many spatial
workloads first need candidate rows before an app-specific continuation does
exact interpretation.

## Current Evidence - Count-Only Row

| Field | Value |
| --- | ---: |
| Workload | 32,768 boxes, 32,768 point queries, 32,768 box queries |
| Operation | `all` |
| Query OptiX / Embree | 814.339x |
| Wall OptiX / Embree | 132.753x |
| Elapsed OptiX / Embree | 73.826x |

The raw artifact uses `operation: all`; the review row uses `all_count_only`
to name what the route returns.

RTDL Embree and RTDL OptiX return the same counts:

```text
point_contains: 46,343,760
range_contains: 32,302,908
range_intersects: 70,429,254
```

The current final-review packet also adds an independent chunked NumPy CPU
oracle. It matches these counts under the native float32-inclusive AABB
boundary contract. A float64 exact-geometry oracle differs by small boundary
deltas, so the numeric contract must be named whenever this row is discussed.

## Current Evidence - Native Query-Handle Rows

The later native prepared-query-handle route adds exactly two row-scoped M7
rows for `range_intersection_rows` on jittered-grid workloads:

| Row | AABBs / queries | Cold-plus-collect OptiX / Embree | Query-total OptiX / Embree |
| --- | ---: | ---: | ---: |
| `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50` | 32,768 / 32,768 | 1.719x | 1.867x |
| `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50` | 65,536 / 65,536 | 1.637x | 1.743x |

These rows use warmup=3 and repeat=50. OptiX prepare alone remains slower than
Embree; the accepted speedup is for cold prepare plus collect wall time, not
for prepare alone.

## What To Learn

- Three exact `aabb_candidate_stream` rows are M7-qualified:
  `aabb_candidate_stream_all_count_only_float32_32768`,
  `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`,
  and
  `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`.
- It is count-only candidate discovery, not full spatial-index application
  acceleration.
- It is not LibRTS authors-code timing and not a paper-equivalent dataset.
- It is not a V3-over-V2 large-row claim because the paired V2.14 artifact only
  has small standard AABB rows.
- It is M7-qualified only under the native float32-inclusive boundary contract
  after Claude accepted the P0 wording fix and Codex recorded 2-AI consensus.

## Source Packets

- `docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_public_surface_closure_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2ai_consensus_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768_float32.json`
- `docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json`
- `docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/paired_v2_v3_summary.json`

## Claim Boundary

Allowed:

```text
Exactly `aabb_candidate_stream_all_count_only_float32_32768` is M7-qualified
row-scoped: on the current native float32-inclusive count-only workload, RTDL
OptiX shows 814.339x query, 132.753x wall, and 73.826x elapsed speedup over
RTDL Embree. V3 release authorization remains false.

Exactly `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
and `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`
are also M7-qualified row-scoped: on one NVIDIA RTX 4000 Ada Generation pod,
the RTDL OptiX native prepared-query-handle route is 1.719x and 1.637x faster
than the RTDL Embree route on cold prepare plus collect wall time. OptiX
prepare alone remains slower than Embree.
```

Forbidden:

```text
Do not claim RTDL reproduces the LibRTS paper.
Do not claim RTDL beats LibRTS authors code.
Do not claim any AABB row beyond the three exact row ids above is M7-qualified.
Do not claim V3 is 814x faster than V2.
Do not claim generic AABB count-only proves full spatial-index acceleration.
Do not claim AABB native query-handle evidence proves Contact Manifold solver acceleration.
Do not claim OptiX prepare alone is faster than Embree prepare.
Do not claim the row matches a float64 exact-geometry oracle.
```
