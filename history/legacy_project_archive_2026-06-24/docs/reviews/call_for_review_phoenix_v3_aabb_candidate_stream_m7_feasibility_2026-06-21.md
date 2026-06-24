# Call For Review: Phoenix V3 AABB Candidate-Stream M7 Feasibility

Reviewer: Claude or Gemini.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only feasibility packet:

```text
docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.json
tutorials/current/12_aabb_candidate_stream.md
```

Evidence sources:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/paired_v2_v3_summary.json
```

## Intended Decision

The generic AABB candidate-stream row is strong current-side candidate evidence,
but it must not be promoted to M7 yet.

Key facts:

- row: `librts_spatial_index/aabb_index_all_count_only_large_32768`;
- contract: `generic_prepared_aabb_index_query_2d`;
- query OptiX/Embree: 814.339x;
- wall OptiX/Embree: 132.753x;
- counts match between RTDL Embree and RTDL OptiX;
- CPU reference was skipped and `matches_cpu_reference` is null;
- dataset is not paper-equivalent;
- no LibRTS authors-code comparison is attached;
- no same-row V2.14 large 32,768/32,768 baseline exists.

## Questions For The Reviewer

1. Is this correctly classified as a strong candidate, not M7?
2. Are the paper/authors-code/V2 boundaries clear enough?
3. Is count-only scope clear enough?
4. Are the M7 blockers sufficient?
5. Would you approve this as a rebuild feasibility packet, not as public
   performance wording?

## Required Review Style

Please be strict. Reject if the packet makes the 814x query ratio too easy to
misread as a LibRTS paper result, V3-over-V2 result, or full spatial-index
speedup.
