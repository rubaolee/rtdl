# Phoenix V3 AABB Candidate-Stream M7 Feasibility

Status: `aabb_candidate_stream_m7_feasibility_not_promoted`.

This packet isolates the LibRTS-style generic AABB count-only row as a strong
V3 candidate. It is not release evidence and not public speedup wording.

## Bottom Line

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
librts_authors_code_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_external_review_status: blocked_current_packet
```

The useful V3 capability is `aabb_candidate_stream`: a generic
`AABB_INDEX_QUERY_2D` count-only route, not a LibRTS-specific native symbol.

## Candidate Row

Source:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
```

| Field | Value |
| --- | ---: |
| App | `librts_spatial_index` |
| Row | `aabb_index_all_count_only_large_32768` |
| Contract | `generic_prepared_aabb_index_query_2d` |
| Boxes | 32,768 |
| Point queries | 32,768 |
| Box queries | 32,768 |
| Operation | `all` |
| Warmup / repeat | 2 / 5 |
| Embree query median | 36.093761s |
| OptiX query median | 0.044323s |
| Query OptiX / Embree | 814.339x |
| Wall OptiX / Embree | 132.753x |
| Elapsed OptiX / Embree | 73.826x |

Counts match between RTDL Embree and RTDL OptiX:

```text
point_contains: 46,343,760
range_contains: 32,302,908
range_intersects: 70,429,254
```

## What This Means

Allowed internal reading:

```text
Generic AABB candidate-stream is a strong current-side V3 OptiX-over-Embree
candidate on a 32,768/32,768 count-only workload.
```

This is one of the better V3 candidates because the capability is reusable:
spatial indexes, broadphase filters, and candidate-stream builders all need
fast AABB count/candidate discovery.

## What This Does Not Mean

Forbidden public reading:

```text
Do not claim RTDL reproduces the LibRTS paper.
Do not claim RTDL beats LibRTS authors code.
Do not claim AABB candidate stream is M7-qualified.
Do not claim V3 is 814x faster than V2.
Do not claim generic AABB count-only proves full spatial-index acceleration.
```

## M7 Blockers

- `cpu_reference_skipped_and_matches_reference_null`
- `paper_equivalent_dataset_false`
- `authors_code_comparison_false`
- `large_32768_v2_14_same_row_absent`
- `public_row_level_external_review_not_done`
- `must_keep_count_only_scope`

The paired V2.14-vs-current-V3 artifact shows `librts_spatial_index` app
geomean 1.163x, but that paired comparison uses small standard rows. It does
not provide a same-row V2.14 baseline for the 32,768/32,768 large AABB row.

## Tutorial

The current tutorial entry is:

```text
tutorials/current/12_aabb_candidate_stream.md
```

It is a rebuild tutorial, not a release tutorial.

## External Review

Fresh external review is blocked:

```text
docs/reviews/external_review_blocked_phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: create a focused AABB candidate-stream feasibility packet without M7
promotion.

1. Was I foolish?

   No. The evidence is strong enough to isolate as a candidate, but not
   complete enough for public release wording.

2. If yes, what actions made the decision foolish?

   It would be foolish to call the 814x query ratio a LibRTS paper result,
   author-code win, or V3-over-V2 result.

3. Was there another path that avoided getting stuck on that idea?

   Yes. Rerun the pod immediately. That may be useful later, but first the
   current evidence needs a focused claim boundary.

4. Can I now try a different path that actually solves the problem?

   Yes. Record the strong generic AABB signal, expose the missing reference and
   paired-large-row blockers, and add a rebuild lesson.
