# Goal5509 LibRTS Exact Range-Intersects Next Batch

Status: `implemented__four_of_six_checkpointed_count_matches__two_large_cases_unresolved__review_pending`

## Scope

Goal5509 executes the next exact official query family,
`range-intersects_select_0.0001_queries_10000`, using the verified
`PPoPPAE-v2.tar.gz` archive. The six geometry members are reused from the
verified Goal5500 extraction; the six new query members are recorded with
SHA-256 values. Author and RTDL use the same geometry/query files, with RTDL
pointed at the clean Goal5508 native library.

## Checkpointed results

| Case | Author count | RTDL count | Result |
|---|---:|---:|---|
| parks_Europe | 2,486,816 | 2,486,816 | match |
| dtl_cnty | 242,920 | 242,920 | match |
| USACensusBlockGroupBoundaries | 423,893 | 423,893 | match |
| USADetailedWaterBodies | 651,647 | 651,647 | match |

The `parks.bz2` and `lakes.bz2` cases were attempted in the large batch, but
the batch process was reclaimed before independent per-case JSON checkpoints
were written. They are recorded as unresolved capacity/process-lifetime
states, not as semantic mismatches and not as matches.

## Interpretation

Goal5509 adds four exact same-input count matches in a second query family.
Together with the prior six attempted cases, the evidence now has ten
attempted exact range-intersects cases, with seven checkpointed matches from
the current and prior evidence sets plus two prior mismatches resolved by
Goal5508. The archive still contains 42 exact range-intersects pairs; this is
not a complete matrix.

The result is count-level only. The standard author binary does not expose
pair rows for this operation, so no pointwise relation claim is made. Author
internal query time, RTDL load/prepare/query phases, and process behavior are
recorded separately and no performance ratio is authorized.

## Claim boundary

This goal does not claim complete range-intersects coverage, pairwise relation
equality, Figure 6 reproduction, full-paper reproduction, performance parity,
device zero-copy, author-specific RTDL behavior, or Embree evidence. The
remaining exact pairs and large-case capacity behavior remain explicit future
work.

Machine-readable evidence:

```text
Paper-reproduction-apps/librts-paper/results/goal5509_exact_range_intersects_next_batch_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5509_range_intersects_batch_extraction.json
```
