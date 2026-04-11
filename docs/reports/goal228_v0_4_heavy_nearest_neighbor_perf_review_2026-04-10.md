# Goal 228 Review Closure

Date: 2026-04-10
Status: closed under Codex + Gemini

## Review Inputs

- Codex consensus:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-10-codex-consensus-goal228-heavy-v0_4-nearest-neighbor-perf.md`
- Gemini review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/gemini_goal228_v0_4_heavy_nearest_neighbor_perf_review_2026-04-10.md`

## Closure

Goal 228 is closed as a performance-study slice.

What is accepted:

- the heavy Linux benchmark ran successfully
- indexed PostGIS is now part of the nearest-neighbor benchmark path
- the benchmark gives high-signal backend comparisons for both reopened
  `v0.4` workloads
- Gemini agrees the measurement methodology is technically honest

What changed after the first benchmark run:

- the initial heavy run exposed a real shared accelerated
  `fixed_radius_neighbors` boundary bug on Embree, OptiX, and Vulkan
- that bug has now been fixed and rerun on Linux
- the refreshed heavy summary shows:
  - CPU, Embree, OptiX, Vulkan, and indexed PostGIS all return `45632` rows
  - row identity now matches across all five paths

So Goal 228 closes as:

- benchmark implemented
- findings documented
- indexed PostGIS comparison path validated
- refreshed heavy rerun preserved as the active benchmark evidence
