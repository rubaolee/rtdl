# Call For Review: Phoenix V3 AABB Candidate-Stream 32768 M7 Final Review Packet

Reviewer: Claude or Gemini.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only final public-row review packet:

```text
docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json
tutorials/current/12_aabb_candidate_stream.md
```

Evidence sources:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json
docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768_float32.json
docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768.json
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/v2_14_goal3828_full/librts_spatial_index_optix_scale_default_32768.stdout.json
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120/current_goal3828_full/librts_spatial_index_optix_scale_default_32768.stdout.json
```

## Proposed Decision

Approve exactly this row as M7-qualified row-scoped public wording, or reject it
if the numeric contract or boundaries are not release-grade:

```text
aabb_candidate_stream_all_count_only_float32_32768
```

Key facts:

- generic capability: `aabb_candidate_stream`;
- primitive contract: `generic_prepared_aabb_index_query_2d`;
- numeric contract: native float32-inclusive AABB boundary
  (`native_float32_inclusive_boundary`);
- row: 32,768 indexed boxes, 32,768 point queries, 32,768 box queries;
- operation: `all_count_only`;
- warmup/repeat: 2/5;
- query OptiX/Embree: 814.339x;
- wall OptiX/Embree: 132.753x;
- counts match RTDL Embree, RTDL OptiX, and independent chunked NumPy float32 CPU oracle;
- independent chunked NumPy float64 oracle does not match by small boundary deltas;
- not LibRTS paper reproduction;
- not LibRTS authors-code timing;
- not full spatial-index acceleration;
- not V3-over-V2 wording.

## Questions For The Reviewer

1. Is the float32-inclusive numeric contract acceptable for row-scoped M7
   wording if explicitly named?
2. Does the float64 mismatch require blocking the row, or is it sufficiently
   disclosed as a numeric-contract boundary?
3. Is the 814.339x query ratio safe to publish with the proposed wording, or is
   it too easy to misread as LibRTS paper/authors-code/V2 speedup?
4. Are the non-paper, non-authors-code, count-only, and non-V2 boundaries strong
   enough?
5. If approved, should only this exact row become M7-qualified?

## Required Review Style

Please be strict. Reject if the packet makes the 814.339x query ratio too easy
to misread as a LibRTS paper result, authors-code result, full spatial-index
speedup, float64 exact-geometry result, or V3-over-V2 result.

If you approve, list any P0 wording changes required before promotion.
