# Goal1930 Claude Background Audit - Remaining All-App v2 Families

Please independently audit the current post-Goal1928 repository state for the remaining v2.0 all-app matrix work.

Context:
- v2.0 target: Python + partner + RTDL, PyTorch reference first, CuPy conformance alongside it.
- Engine must remain absolutely app-agnostic; app semantics can live in Python/partner adapters.
- Recent committed work:
  - Goal1924 maps all 16 active app rows into implementation families.
  - Goal1925 adds a fixed-radius family v1.8-vs-v2 partner harness for facility, Hausdorff threshold, ANN coverage, outlier, DBSCAN core, and Barnes-Hut coverage.
  - Goal1927/1928 add robot collision pose flags through generic ray/triangle any-hit flags plus partner reduction.
- Remaining families needing careful treatment:
  - Family B current rerun: `segment_polygon_anyhit_rows` already has Goal1856 evidence but should be included in the final all-app batch.
  - Family D: `polygon_pair_overlap_area_rows` and `polygon_set_jaccard`, where RT candidate discovery exists but exact geometry continuation may dominate and may remain CPU/Python fallback unless a bounded partner tensor continuation is implemented.
  - Family E: `database_analytics`, where v1.8 prepared compact summary exists but v2 partner contract may need explicit boundary or a narrow partner postprocess adapter.
  - Family F: `graph_analytics`, probably split into visibility edges, BFS, and triangle count rather than one vague row.

Requested output:
- Write a review to `docs/reviews/goal1930_claude_remaining_all_app_v2_audit_2026-05-13.md`.
- Use verdict values only: `accept`, `accept-with-boundary`, `reject`, `needs-more-evidence`.
- Identify which remaining rows can honestly be called v2 partner implementations now, which need a narrow adapter, and which should be explicit control/fallback rows.
- Flag any overclaim risk in calling the final matrix "all apps using v2.0".
- Do not edit source code or tests.
