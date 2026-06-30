# Goal971 Claude Review Request

Please review the post-Goal969 baseline/speedup package and write a verdict to:

```text
docs/reports/goal971_claude_review_2026-04-26.md
```

Scope:

- Read `scripts/goal971_post_goal969_baseline_speedup_review_package.py`.
- Read `tests/goal971_post_goal969_baseline_speedup_review_package_test.py`.
- Read generated outputs:
  - `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json`
  - `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.md`
- Cross-check the source artifact reports:
  - `docs/reports/goal969_artifact_report_group_a_robot_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_b_fixed_radius_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_c_database_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_d_spatial_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_e_segment_polygon_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_f_graph_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_g_prepared_decision_2026-04-26.json`
  - `docs/reports/goal969_artifact_report_group_h_polygon_2026-04-26.json`

Review questions:

1. Does the package correctly report `17` RTX artifact rows from the eight Goal969 group reports?
2. Does it correctly preserve the claim boundary that no public speedup claim is authorized by the package?
3. Is the baseline classification conservative and traceable to Goal836/Goal846?
4. Does the generated report clearly distinguish:
   - strict same-semantics baseline complete,
   - active-gate limited,
   - RTX artifact ready but baseline pending?
5. Are any rows overclaiming whole-app speedup, DBMS behavior, or complete polygon/graph/native continuation beyond the saved artifacts?

Please return one of:

- `ACCEPT`: if the package is correct and conservative.
- `BLOCK`: if a correctness, traceability, or claim-boundary issue must be fixed first.

Include concrete file/line references for any blocker.
