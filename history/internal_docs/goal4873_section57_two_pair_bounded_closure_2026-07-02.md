# Goal4873 - RayJoin Section 5.7 two-pair bounded closure

Date: 2026-07-02

## Verdict

`completed_section57_two_pair_bounded_correctness_closure`

## Purpose

This goal closes the current RayJoin Section 5.7 reproduction slice honestly.

After several correctness repairs and full-stream comparisons, RTDL has now
passed two serious Section 5.7 polygon-overlay pairs:

1. County x Zipcode
2. Block x Water

Both are full-stream correctness results, not count-only results and not
prefix-only results.

This closure deliberately does not claim all-eight-pair Section 5.7
reproduction, because the remaining exact CDB inputs and author baselines are
not currently validated in this workspace/POD state.

## Paper Section 5.7 matrix

The paper's Section 5.7 overlay matrix has eight pairs:

| Pair | Paper processing sec | Paper preprocessing sec | Current RTDL status |
|---|---:|---:|---|
| County x Zipcode | 0.12 | 0.07 | full-stream exact match |
| Block x Water | 0.23 | 0.12 | full-stream exact match under `Author+RTDLContractPatch` |
| LKAF x PKAF | 0.01 | 0.01 | not reproduced in this closure |
| LKAS x PKAS | 0.04 | 0.05 | not reproduced in this closure |
| LKAU x PKAU | 0.01 | 0.01 | not reproduced in this closure |
| LKEU x PKEU | 0.20 | 0.20 | not reproduced in this closure |
| LKNA x PKNA | 0.25 | 0.21 | not reproduced in this closure |
| LKSA x PKSA | 0.02 | 0.01 | not reproduced in this closure |

The paper timings are context only. They are not local denominators for any
RTDL performance claim.

## Completed pair 1 - County x Zipcode

Report:

`history/internal_docs/goal4872_county_zipcode_after_duplicate_contract_revalidation_2026-07-02.md`

External review:

`history/internal_docs/antigravity_goal4872_county_zipcode_after_duplicate_contract_revalidation_review_2026-07-02.md`

Comparator:

`/workspace/goal4861_author_intended_baseline/author_intended_county_zipcode_overlay.txt`

Result:

```json
{
  "stream_match": true,
  "first_diff": null,
  "streamed_line_count": 87758114,
  "streamed_chain_count": 29253961,
  "streamed_point_count": 58504153,
  "streamed_face_count": 115515
}
```

Interpretation:

Current RTDL still matches the County x Zipcode author-intended baseline after
the duplicate-half-edge contract repair. This is a full-stream correctness
result.

## Completed pair 2 - Block x Water

Report:

`history/internal_docs/goal4871_block_water_full_stream_compare_result_2026-07-02.md`

External review:

`history/internal_docs/antigravity_goal4871_block_water_full_stream_compare_review_2026-07-02.md`

Comparator:

`Author+RTDLContractPatch`

Result:

```json
{
  "stream_match": true,
  "first_diff": null,
  "streamed_line_count": 138674679,
  "streamed_chain_count": 46224916,
  "streamed_point_count": 92449763,
  "streamed_face_count": 2581495
}
```

Interpretation:

RTDL matches the Block x Water comparator stream exactly under the explicit
duplicate-half-edge canonicalization contract.

This comparator is not the old unpatched AuthorPatch baseline. The unpatched
baseline is not a fair comparator for this pair because duplicate half-edge
witnesses changed under the newly defined deterministic RTDL core contract.

## Core correctness repairs that made this possible

The major correctness repairs exposed during this line were:

1. LSI row direction and row materialization had to match overlay needs, not
   count-only Section 5.2 behavior.
2. Intersection coordinate display had to follow the author-style scaled
   integer output contract while keeping raw geometry identity separate.
3. Output-chain streaming had to avoid materializing tens of millions of output
   chains in memory.
4. PIP/point-location needed deterministic SoS handling for equal-height
   candidates.
5. Duplicate half-edges needed a product-level deterministic canonicalization
   rule:
   - group by unordered exact scaled endpoint pair;
   - choose the smallest stable source segment id;
   - compute canonical face from canonical segment direction.

These are RTDL product/contract repairs. They are not public performance claims.

## What is now proven

Proven:

- RTDL can reproduce two serious Section 5.7 polygon-overlay pairs at full
  output-stream correctness.
- The reproduced outputs are not count-only; they compare the full author-format
  output streams line by line.
- County x Zipcode remains exact after the duplicate-half-edge repair.
- Block x Water is exact under the explicit `Author+RTDLContractPatch`
  deterministic duplicate-half-edge contract.

## What is not proven

Not proven:

- all-eight-pair Section 5.7 reproduction;
- performance superiority over the author code;
- equivalence to the old unpatched author baseline on Block x Water;
- public release readiness;
- correctness on the six missing/unvalidated pairs;
- that Numba is materially used in these two full-output paths.

## Why the remaining six pairs are not claimed

The remaining six pairs require exact inputs and comparable author baselines
under a frozen contract. Without those, running "similar" data would be a
representative experiment, not exact Section 5.7 reproduction.

The correct next step for the remaining six is acquisition/restoration of exact
CDB inputs and generation of frozen author comparator outputs, not more RTDL
core modification.

## Next options

1. **Bounded closure now:** Treat Section 5.7 as a two-pair full-stream
   reproduction result and document it as such.
2. **Expand pair coverage:** Restore/acquire exact CDBs and author baselines for
   the remaining six pairs, then run the same full-stream gate.
3. **Separate performance goal:** After correctness scope is frozen, run a
   performance-specific benchmark with clear timing boundaries. Do not reuse the
   diagnostic streaming-compare timings as performance claims.

## Exit label

`completed_section57_two_pair_bounded_correctness_closure__no_all8_or_perf_claim`
