# Goal1970 External Review Task: Goal1969 CuPy Extent Polygon Candidate Backend

Please perform a read-only independent review of Goal1969.

## Context

The v2.0 Python+partner+RTDL lane had two polygon control rows that were slower
than v1.8 after Goal1968 because candidate construction was the bottleneck:
`cpu_all_pairs` exploded and Embree row-producing candidate discovery was still
too expensive for these authored control rows.

Goal1969 adds a partner-side CuPy extent candidate backend:

- `examples/rtdl_control_apps_cupy_rawkernel.py`
  - new `_positive_candidate_pairs_cupy_extent`
  - new CLI choice `--candidate-backend cupy_extent`
- `scripts/goal1955_rawkernel_control_app_perf.py`
  - exposes `cupy_extent`
- `tests/goal1969_cupy_extent_polygon_candidate_backend_test.py`
- `docs/reports/goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md`
- `docs/reports/goal1969_pod_cupy_extent_polygon_control_perf.json`

Implementation commit: `22362c31e3c646de7009328f80296f16a3204a19`

Pod artifact refresh commit: `df3543b4` (current HEAD when this handoff was
written)

## Evidence To Check

The commit-labelled pod artifact reports:

- GPU: NVIDIA RTX 2000 Ada Generation, driver 565.57.01
- `polygon_pair_overlap_area_rows`
  - copies: 2048
  - v1.8 median: `0.279780s`
  - v2 CuPy extent median: `0.081689s`
  - ratio: `0.292x`
  - correctness matched v1.8 oracle
- `polygon_set_jaccard`
  - copies: 2048
  - v1.8 median: `0.233212s`
  - v2 CuPy extent median: `0.065533s`
  - ratio: `0.281x`
  - correctness matched v1.8 oracle

## Review Questions

1. Does Goal1969 preserve the engine app-agnostic boundary, or does the new
   `cupy_extent` path smuggle app-specific behavior into the native engine?
2. Is the performance interpretation bounded correctly?
   - This is a user-approved v2 comparison against v1.8 Python+RTDL without a
     user C/C++ extension.
   - It is not an OptiX RT-core result.
   - It is not a general polygon overlay claim.
3. Are the tests and report sufficient for this narrow implementation slice?
4. Does this support the design lesson that v2 needs compact partner-owned
   candidate/payload table construction, not dense all-pairs handoff?

## Required Output

Write one review file using your AI-family name in the filename:

- Claude: `docs/reviews/goal1970_claude_review_goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md`
- Gemini: `docs/reviews/goal1971_gemini_review_goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md`

Use one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not mutate source code. If you find issues, write them in the review.
