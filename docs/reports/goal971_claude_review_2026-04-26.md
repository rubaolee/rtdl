# Goal971 Claude Review — 2026-04-26

**Verdict: ACCEPT**

## Scope

Reviewed `scripts/goal971_post_goal969_baseline_speedup_review_package.py`,
`tests/goal971_post_goal969_baseline_speedup_review_package_test.py`,
the generated JSON and Markdown outputs, and all eight Goal969 group artifact reports.

## Findings by review question

### Q1 — Row count = 17 from 8 groups

Cross-checked entry counts from each group report:

| Group | entry_count |
| ----- | ----------: |
| a robot | 1 |
| b fixed_radius | 2 |
| c database | 2 |
| d spatial | 3 |
| e segment_polygon | 3 |
| f graph | 1 |
| g prepared_decision | 3 |
| h polygon | 2 |
| **Total** | **17** |

JSON `row_count: 17`, `group_count: 8`, `bad_rtx_artifact_count: 0`. All group-level `failure_count` fields are 0 and all `status` fields are `"ok"`. **Correct.**

### Q2 — Claim boundary: no public speedup claim authorized

`public_speedup_claim_authorized` is hardcoded `False` for every row (script line 99), independent of baseline status. `public_speedup_claim_authorized_count: 0` in the generated JSON. Boundary text in both outputs reads: *"It does not authorize public speedup wording."* The test at line 25 asserts `== 0`. **Boundary preserved.**

### Q3 — Baseline classification conservative and traceable to Goal836/Goal846

`_baseline_maps()` (script lines 49–60) pulls data exclusively from `analyze_plan()` (Goal836) and `build_active_claim_gate()` (Goal846). Classification logic (lines 80–94) is strictly conservative:

- `same_semantics_baselines_complete` only when all required checks are `valid` and none are `missing` or `invalid`.
- `active_gate_complete_but_full_baseline_review_limited` only when the above fails but the Goal846 active-gate `row_status` is `"ok"`.
- `rtx_artifact_ready_baseline_pending` for everything else.

Test `test_baseline_classification_is_conservative` confirms expected assignments for three representative rows, including verifying `baseline_complete_for_speedup_review` is `True` only for the fully-complete row and `public_speedup_claim_authorized` remains `False` even for that row. **Conservative and traceable.**

### Q4 — Three-tier distinction is clear

The generated report reports counts for all three tiers separately (`same_semantics_baselines_complete_count: 3`, `active_gate_limited_count: 5`, `baseline_pending_count: 9`; sum = 17). Each per-row entry carries its `baseline_status` string, `valid_baseline_count`, `required_baseline_count`, and `baseline_reason`. The Claim Boundary section of the Markdown defines each tier explicitly. **Clear and unambiguous.**

### Q5 — No overclaiming whole-app speedup, DBMS behavior, or complete polygon/graph/native continuation

Inspected all 17 `claim_scope` and `non_claim` fields. Every row:

- Scopes its claim to a specific prepared sub-path or phase gate (traversal summary, threshold decision, candidate-discovery phase).
- Explicitly denies whole-app speedup in `non_claim` (e.g., *"not a SQL engine claim and not a broad RTX RT-core app speedup claim"*, *"not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration"*, *"not a monolithic GPU polygon-area kernel and not a full app RTX speedup claim"*).

The two database rows carry a `speedup_one_shot_over_warm_query_median` metric in the source artifact reports, but Goal971 does not surface this field in its output — it extracts only `warm_query_median_sec` via `_rtx_phase_seconds()` (script line 42–46). That ratio is an internal phase metric (one-shot vs warm query on the same hardware), not an RTX-vs-CPU comparison, and is not used anywhere in the package's summary or claims. **No overclaiming found.**

## Conclusion

All five review questions pass. The package correctly counts 17 rows from 8 groups, holds `public_speedup_claim_authorized = False` for every row unconditionally, classifies baselines conservatively via Goal836/Goal846, distinguishes the three tiers clearly, and no row asserts whole-app speedup, DBMS behavior, or continuation beyond the saved artifacts.

**ACCEPT**
