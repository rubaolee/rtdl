# Goal1086 Robot Chunked Embree Baseline Intake

Date: 2026-04-29

Status: `complete`

Valid intake report: `true`

Goal1086 is an intake/aggregation tool for robot Embree chunk artifacts. It does not run the heavy baseline, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Observed

- Chunk count: `1` / `180`
- OK chunks: `1`
- Scale-OK chunks: `0`
- Total poses represented: `1000`
- Missing indices: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]` ...
- Timing chunk count: `180` / `180`
- Timing OK chunks: `180`
- Timing total poses represented: `36000000`
- Timing missing indices: `[]`

## Aggregated Phases

- Native any-hit sum: `92.24968472972978` seconds
- Native any-hit median chunk: `0.5073218619800173` seconds
- Backend scene-prepare sum: `269.61262179224286` seconds
- Backend scene-prepare median chunk: `1.4870285960496403` seconds

## Interpretation

This intake aggregates chunked same-total-work Embree evidence. It accepts either legacy all-validated chunks or split validation/timing chunks. Even when complete, it does not by itself authorize a speedup claim against the 36M single RTX timing artifact because the comparison boundary is same-total-work, not same-single-launch, and still requires 2+ AI review.
