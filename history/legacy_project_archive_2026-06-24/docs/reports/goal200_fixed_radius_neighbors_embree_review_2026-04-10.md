# Goal 200 Review Closure

Date: 2026-04-10

## Status

Closed under the standing `2+` bar with Codex + Claude.

## External Review Status

Successful review:

- [claude_goal200_fixed_radius_neighbors_embree_review_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/claude_goal200_fixed_radius_neighbors_embree_review_2026-04-10.md)

Attempted but not usable:

- [gemini_goal200_fixed_radius_neighbors_embree_review_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/gemini_goal200_fixed_radius_neighbors_embree_review_2026-04-10.md)

## Consensus

Claude's review passed the implementation with no blocking findings and
confirmed the overall closure shape, but one real contract-alignment note was
then fixed before final acceptance:

- the Embree callback originally used `distance <= radius + 1e-12`
- this was tightened to the exact public rule `distance <= radius`

Later, Goal 209 surfaced one more real backend bug that had escaped the earlier
closeout:

- the fixed-radius Embree runner had not set
  `g_query_kind = QueryKind::kFixedRadiusNeighbors` before `rtcPointQuery(...)`
- this caused the shared callback to take the wrong branch and could yield zero
  rows on real runs

That bug is now fixed in:

- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp`

The resulting accepted implementation now satisfies:

- inclusive radius filtering
- deterministic ordering
- correct `k_max` truncation
- rebuild hardening for modular Embree edits
- adequate bounded test coverage

Codex agrees with that assessment. The implementation was also directly
verified in this checkout with:

- `PYTHONPATH=src:. python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal198_fixed_radius_neighbors_truth_path_test`
  - `Ran 18 tests`
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.goal40_native_oracle_test tests.cpu_embree_parity_test`
  - `Ran 4 tests`
  - `OK`

## Result

Goal 200 is accepted as implemented and reviewed:

- Embree closure: yes
- external review: yes (Claude)
- second AI leg attempt preserved honestly: yes (Gemini attempt note)
