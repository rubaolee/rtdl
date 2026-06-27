# Phoenix V3 Grouped-Reduction Sum M7 Candidate Wording

Status: actual repeat100 sum-only M7 candidate wording, not release authorization.

```text
status: sum_only_actual_repeat100_candidate_wording_not_release
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
current_packet_external_review_status: blocked_current_packet
current_packet_2ai_consensus_status: not_recorded_for_this_packet
M7 candidate rows: 2
Phoenix M7-qualified release rows: 0
```

## Scope

This packet only considers grouped sum rows from the reviewed prepared-query
contract. Count rows are excluded from public promotion.

The earlier modeled repeat100 wording is superseded by actual repeat100 pod
evidence:

```text
docs\rebuild\v3\evidence\phoenix_v3_grouped_reduction_repeat100_actual_20260620
```

Clean rerun source for the 524,288-row candidate:

```text
docs\rebuild\v3\evidence\phoenix_v3_grouped_reduction_repeat100_actual_524288_clean_20260620
```


Current scalar-broadcast optimized repeat100 source:

```text
docs\rebuild\v3\evidence\phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620
```


Source contract:

```text
docs\rebuild\v3\phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json
```

## Candidate Rows

| Row | Rows | Groups | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Embree loop | OptiX loop | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| grouped_reduction_sum_scalar_broadcast_repeat100_262144 | 262,144 | 1,024 | 203.022x | 200.353x | 27.917x | 100.508s | 0.502s | sum_only_actual_repeat100_candidate_needs_final_review |
| grouped_reduction_sum_scalar_broadcast_repeat100_524288 | 524,288 | 2,048 | 158.970x | 157.642x | 2.983x | 210.183s | 1.333s | sum_only_actual_repeat100_candidate_needs_final_review |

## Cold Cost

Cold prepare is part of the user contract. The 524,288-row case is much less
impressive after cold prepare is counted, so it must not be quoted as a 33x
end-to-end row.

| Row | Embree cold prepare | OptiX cold prepare | Embree cold plus loop | OptiX cold plus loop |
| --- | ---: | ---: | ---: | ---: |
| grouped_reduction_sum_scalar_broadcast_repeat100_262144 | 1.710s | 3.160s | 102.219s | 3.662s |
| grouped_reduction_sum_scalar_broadcast_repeat100_524288 | 85.064s | 97.627s | 295.247s | 98.960s |

## Draft Public Wording

The following wording is not publishable until final external public-row review.

- Draft only: for a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod (262,144 rows / 1,024 groups), actual repeat=100 measurement showed 200.353x OptiX-over-Embree speedup for the 100-query prepared loop. Counting cold prepare once plus the measured 100-query loop, the speedup was 27.917x. The hot prepared-query median ratio was 203.022x. This is not a whole-app or whole-database speedup claim, and it is not publishable until final external public-row review.
- Draft only: for a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod (524,288 rows / 2,048 groups), actual repeat=100 measurement showed 157.642x OptiX-over-Embree speedup for the 100-query prepared loop. Counting cold prepare once plus the measured 100-query loop, the speedup was 2.983x. The hot prepared-query median ratio was 158.970x. This is not a whole-app or whole-database speedup claim, and it is not publishable until final external public-row review.

## Excluded Count Rows

| Row | Break-even repeats | Modeled repeat 100 end-to-end | Reason |
| --- | ---: | ---: | --- |
| grouped_reduction_count_repeat100_262144 | 14 | 2.452x | count row kept internal because break-even requires double-digit repeats |
| grouped_reduction_count_repeat100_524288 | 14 | 2.633x | count row kept internal because break-even requires double-digit repeats |

## Public Copy Rules

- Say fixed-schema prepared grouped-sum workload.
- Name hardware, row count, group count, backend pair, warmup, and repeat count.
- Say actual repeat 100 when quoting repeat-100 evidence.
- Report both actual 100-query loop speedup and cold-plus-loop speedup.
- Use the scalar-broadcast optimized repeat100 rerun when quoting current values.
- Do not quote the older modeled repeat 100 values as current candidate wording.
- Always show cold prepare cost next to repeat-100 wording.
- Keep whole-app and whole-database speedup unauthorized.

## Forbidden Public Wording

- Do not claim: V3 is 224x faster
- Do not claim: RayDB is 224x faster
- Do not claim: RTDL is 33x faster end to end
- Do not claim: RTDL accelerates database workloads broadly
- Do not claim: count rows are public grouped_reduction speedup rows
- Do not claim: repeat 100 is only modeled
- Do not claim: whole-app speedup is authorized

## Next Review Questions

- Is actual repeat-100 wording acceptable if cold prepare is shown beside loop timing?
- Should the 262,144-row sum row become M7-qualified after final external review?
- Should the 524,288-row sum row remain candidate despite its large cold prepare cost?
- Is the public wording understandable without project history?
- Are the count-row exclusions still strong enough?

## Goal-Level Decision Audit

Decision: replace modeled repeat100 candidate wording with actual repeat100 pod evidence

1. Was I foolish?

   Partly. The earlier modeled wording was honest about being modeled, but it was weaker than V3 should accept once pod time was available. The first actual 524,288-row run also needed a clean confirmation because the launch had a quoting mistake around artifact placement. After that, leaving the 76M-ray scalar-field allocations in place would have left a fixable generic packer cost in the V3 candidate path.

2. If yes, what actions made the decision foolish?

   It would be foolish to keep presenting modeled 32x/33x repeat100 numbers as the current candidate after measuring actual repeat100, to quote the first 524,288-row run without recording the clean rerun, or to keep using the pre-optimization evidence after the scalar-broadcast packer rerun succeeded.

3. Was there another path?

   Wait for external review of the modeled wording. That would leave a known measurement gap in the strongest V3 candidate.

4. Can I now try a different path that actually solves the problem?

   Use the actual repeat100 pod artifacts as current candidate evidence with the scalar-broadcast optimized repeat100 rerun as the current source for both scales, and keep release authorization false until final external review.
