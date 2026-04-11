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

What is not normalized away:

- `fixed_radius_neighbors` still has a shared accelerated correctness gap on the
  heavy real-world case:
  - CPU and PostGIS: `45632` rows
  - Embree, OptiX, Vulkan: `45626` rows
- that is now a concrete follow-up engineering issue, not a hidden benchmark
  caveat

So Goal 228 closes as:

- benchmark implemented
- findings documented
- follow-up bug clearly identified
