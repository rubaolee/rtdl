# Ranked Summary Neighbors

V4 can express a common RTDL continuation: start with candidate rows, keep the
rows inside a useful bound, rank them, and emit a compact top-k summary.

This is not a nearest-neighbor black box. The app still defines the score and
tie-break rules.

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/ranked_summary_neighbors.py --mode both
```

## Relation Shape

The input relation has one row per candidate:

| Field | Meaning |
| --- | --- |
| `query_id` | The source query. |
| `candidate_id` | A candidate produced by traversal or a prior relation. |
| `distance` | A distance or radius-bound fact. |
| `score` | The app-owned ranking signal. |

For example:

| query_id | candidate_id | distance | score |
| ---: | ---: | ---: | ---: |
| 1 | 10 | 0.20 | 0.90 |
| 1 | 11 | 0.12 | 0.75 |
| 1 | 12 | 0.18 | 0.92 |
| 2 | 20 | 0.31 | 0.60 |
| 2 | 21 | 0.09 | 0.70 |

The continuation does four small operations:

1. filter rows by radius,
2. order rows by score, distance, and id,
3. keep the first `k` rows per query,
4. emit summary rows such as best candidate and kept count.

With `k = 2`, the visible output has the same shape a larger RTNN-style app
would consume:

| query_id | rank | candidate_id | reason |
| ---: | ---: | ---: | --- |
| 1 | 1 | 12 | highest score for query 1 |
| 1 | 2 | 10 | next score after tie-breaks |
| 2 | 1 | 21 | best candidate for query 2 |
| 2 | 2 | 20 | second candidate for query 2 |

The app owns the score and tie-break policy. RTDL owns the generic row
pipeline: candidate rows in, bounded ranked rows out.

## V4 Mapping

The V4 planner can recognize the `ranked_summary` intent. In V4.0 this shape is
kept honest: the script prints the planner status instead of pretending every
ranked-summary variant is a measured public surface.

Next: [Contact Manifold Lowering](16_contact_manifold_lowering.md)
