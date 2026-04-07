# v0.2 User Doc Draft Handoff

Write a user-facing RTDL v0.2 draft for the current real surface only.

Read only:

- [rtdl_feature_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md)
- [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)
- [v0_2_roadmap.md](/Users/rl2025/rtdl_python_only/docs/v0_2_roadmap.md)
- [v0_2_so_far_report_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/v0_2_so_far_report_2026-04-06.md)

Return markdown only with sections exactly:

1. Title
2. What Is New
3. Workloads
4. Generate-Only
5. Platforms
6. Backend Notes
7. Quick Start
8. Current Limits

Rules:

- focus only on the current real v0.2 surface
- include:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - generate-only support for both
  - Linux as the primary validation platform
  - Mac as a limited local platform
- keep the honesty boundaries explicit
- do not invent unreleased features
- do not drift back into v0.1-only claims
