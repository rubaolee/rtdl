# Phoenix V3 AABB Candidate-Stream 32768 M7 Final Review Packet

Status: `aabb_candidate_stream_32768_m7_qualified_row_scoped`.

This packet closes exactly one generic AABB count-only row after external
public-row review and Codex consensus. It is M7-qualified only as row-scoped
public wording, not V3 release authorization.

## Status

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
librts_authors_code_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
m7_promotion_authorized: true
Phoenix M7-qualified release rows: 1
current_packet_external_review_status: claude_approved_after_p0_wording_fix
current_packet_2ai_consensus_status: claude_codex_consensus_complete
```

## Candidate Row

```text
candidate_row_id: aabb_candidate_stream_all_count_only_float32_32768
generic_capability: aabb_candidate_stream
primitive_contract: generic_prepared_aabb_index_query_2d
numeric_contract: native_float32_inclusive_boundary
```

| Field | Value |
| --- | ---: |
| App | `librts_spatial_index` |
| Row | `aabb_index_all_count_only_large_32768` |
| Boxes | 32,768 |
| Point queries | 32,768 |
| Box queries | 32,768 |
| Operation | `all_count_only` |
| Warmup / repeat | 2 / 5 |
| Embree query median | 36.093761s |
| OptiX query median | 0.044323s |
| Query OptiX / Embree | 814.339x |
| Wall OptiX / Embree | 132.753x |
| Elapsed OptiX / Embree | 73.826x |

Counts:

```text
point_contains: 46,343,760
range_contains: 32,302,908
range_intersects: 70,429,254
```

## CPU Reference Closure

The old feasibility packet had this blocker:

```text
cpu_reference_skipped_and_matches_reference_null
```

That local evidence gap is now closed for the native numeric contract by:

```text
docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768_float32.json
```

The independent chunked NumPy float32 CPU oracle matches the Embree/OptiX
counts exactly:

```text
status: pass
numeric_dtype: float32
elapsed_sec: 27.466513
point_contains: 46,343,760
range_contains: 32,302,908
range_intersects: 70,429,254
```

The float64 oracle does not match:

```text
docs/rebuild/v3/evidence/phoenix_v3_aabb_cpu_reference_oracle_20260621/aabb_cpu_reference_32768.json

point_contains backend - float64: +10
range_contains backend - float64: +8
range_intersects backend - float64: +19
```

This is not a detail to hide. Any approved wording must say the row is a
native float32-inclusive AABB count-only contract, not Python float64 exact
geometry.

## V2.14 Context

The broad V3-over-V2 claim remains false.

```text
broad_v3_faster_than_v2_claim_authorized: false
```

The paired artifact contains a V2.14 OptiX large-row context but not a same-row
large Embree pair:

```text
v2.14 OptiX query median: 0.042850s
current goal3828 OptiX query median: 0.045733s
current claim-grade OptiX query median: 0.044323s
```

Therefore this packet must not say V3 is faster than V2 on the large AABB row.
The only possible reviewed claim is current RTDL OptiX versus current RTDL
Embree under the same native float32-inclusive generic AABB count-only
contract.

## Closed Local Blockers

- `cpu_reference_skipped_and_matches_reference_null_closed_by_float32_oracle`
- `count_only_scope_disclosed`
- `paper_equivalent_dataset_false_disclosed`
- `authors_code_comparison_false_disclosed`
- `large_v2_14_optix_context_disclosed_without_v2_speedup_claim`

## Closed Promotion Conditions

- `fresh_external_public_row_review_closed_by_claude`
- `reviewer_accepted_float32_numeric_contract_wording_after_p0_fix`
- `reviewer_accepted_non_paper_non_authors_code_non_v2_boundary`
- `2_ai_consensus_closed_by_claude_codex`
- `final_public_wording_approved_for_exact_row`
- `whole_app_paper_authors_code_float64_and_broad_v3_over_v2_claims_remain_false`

## Approved Row-Scoped Public Wording

```text
For a native float32-inclusive generic prepared AABB count-only workload on an
NVIDIA RTX 4000 Ada Generation pod, 32,768 indexed boxes plus 32,768 point
queries and 32,768 box queries, warmup=2 and repeat=5, RTDL's OptiX route was
814.339x faster than the RTDL Embree route for the measured float32-inclusive query median and
132.753x faster for the measured wall path. Embree and OptiX counts match an
independent chunked NumPy float32 CPU oracle for point_contains, range_contains,
and range_intersects. This is a row-scoped AABB candidate-stream result, not a
LibRTS paper reproduction, not LibRTS authors-code timing, not full
spatial-index acceleration, and not a V3-over-V2 speedup claim.
```

## Forbidden Wording

- Do not claim RTDL reproduces the LibRTS paper.
- Do not claim RTDL beats LibRTS authors code.
- Do not claim V3 is 814x faster than V2.
- Do not claim generic AABB count-only proves full spatial-index acceleration.
- Do not claim any AABB row beyond
  `aabb_candidate_stream_all_count_only_float32_32768` is M7-qualified.
- Do not claim the AABB row matches a float64 exact-geometry oracle.

## Review Closure

Review chain:

```text
Claude external review + Codex consensus
```

Only `aabb_candidate_stream_all_count_only_float32_32768` is promoted. V3
release, LibRTS paper, LibRTS authors-code, full spatial-index, float64
exact-geometry, and V3-over-V2 claims remain false.

## Goal-Level Decision Audit

Decision: promote only the native float32-inclusive AABB count-only 32768 row
to M7-qualified row-scoped status after Claude/Codex consensus.

1. Was I foolish?

   No. Claude conditionally approved the exact row, the P0 wording fix is
   applied, and second-AI consensus is now recorded.

2. If yes, what actions made the decision foolish?

   It would be foolish to hide the float64 mismatch, call this LibRTS paper
   evidence, promote other AABB rows, or use the 814.339x current
   OptiX-over-Embree ratio as a V3-over-V2 claim.

3. Was there another path?

   Yes. Leave the row blocked after external approval. That would under-use a
   reusable V3 capability whose numeric contract is now explicit.

4. Can I now try a different path that actually solves the problem?

   Yes. Promote one exact row, keep release and broad claims false, and
   continue Phoenix V3 with the next reusable capability.
