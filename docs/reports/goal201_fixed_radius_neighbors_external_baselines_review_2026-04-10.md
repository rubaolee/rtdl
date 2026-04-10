# Goal 201 Fixed-Radius Neighbors External Baselines Review

## Status

Implementation and local verification are complete.

External-review state:

- Claude: complete
- Gemini: complete
- Codex: complete

Goal 201 is closed for `v0.4` under the standing `2+` AI bar.

## Local verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal201_fixed_radius_neighbors_external_baselines_test tests.goal200_fixed_radius_neighbors_embree_test tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal198_fixed_radius_neighbors_truth_path_test`
  - `Ran 25 tests`
  - `OK`
- `python3 -m compileall src/rtdsl tests/goal201_fixed_radius_neighbors_external_baselines_test.py`
  - `OK`

## Review update

- Claude review:
  - `docs/reports/claude_goal201_fixed_radius_neighbors_external_baselines_review_2026-04-10.md`
- Gemini review:
  - `docs/reports/gemini_goal201_fixed_radius_neighbors_external_baselines_review_2026-04-10.md`
- Codex consensus:
  - `history/ad_hoc_reviews/2026-04-10-codex-consensus-goal201-fixed-radius-neighbors-external-baselines.md`

Shared conclusion:

- Goal 201 is complete and honest.
- The SciPy `cKDTree` baseline and bounded PostGIS helper preserve the
  RTDL `fixed_radius_neighbors` contract exactly.
- Optional-dependency handling is clear and does not pollute the first-run path.
- The goal remains correctly scoped for `v0.4`: comparison support only, not a
  performance-claim slice.
