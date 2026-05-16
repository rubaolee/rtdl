# Gemini Task: Review Goal2126 Public Hausdorff Dataset Harness

Please perform a read-only independent review of the Goal2126 public Hausdorff dataset harness.

Relevant files:

- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `tests/goal2126_public_hausdorff_dataset_perf_test.py`
- `docs/reports/goal2126_public_hausdorff_dataset_perf_harness_2026-05-16.md`
- `docs/reports/goal2126_public_hausdorff_dataset_fetch_smoke_2026-05-16.json`

Review questions:

1. Does the harness correctly avoid overclaiming? In particular, it should not claim the exact X-HD paper datasets, 3D surface Hausdorff, release speedup, or public-dataset speedup before pod timings exist.
2. Is the early-break explanation correct? The Goal2123 winning path should be described as exact grouped nearest-witness plus on-device max reduction, with `seed_with_threshold=False`, not as a threshold/terminate shortcut.
3. Is the Stanford public-data path reasonable as the next public test while exact X-HD local datasets are unavailable?
4. Are there any correctness risks in using projected XY vertex sets from public 3D PLY files that should be called out more explicitly?
5. Are the parser/unit tests sufficient for a first pod-ready harness?

Please write your review to:

- `docs/reviews/goal2127_gemini_review_goal2126_public_hausdorff_dataset_harness_2026-05-16.md`

Use verdict terms:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not edit source code. If you find issues, describe them in the review file.
