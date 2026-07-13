# Call For Review - Goals5419-5423 X-HD Level-B Same-POD Matrix Packet

Please strictly review the X-HD Level-B same-POD matrix packet covering
Goals5419 through 5423.

This is a consolidated review node.  It should judge whether the current
Level-B evidence is accurate and whether the project should stop route
micro-optimization and return to exact dataset / denominator work.

## Files To Review

Primary reports:

```text
history/internal_docs/goal5419_xhd_figure5_level_b_same_pod_graphics_matrix_result_2026-07-10.md
history/internal_docs/goal5420_xhd_figure5_level_b_matrix_consolidation_decision_2026-07-10.md
history/internal_docs/goal5421_xhd_bounded_geo_same_pod_packet_plan_2026-07-10.md
history/internal_docs/goal5422_xhd_bounded_geo_same_pod_packet_execution_2026-07-10.md
history/internal_docs/goal5423_xhd_level_b_matrix_consolidation_after_geo_2026-07-10.md
history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md
```

Primary JSON artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5422_bounded_geo_same_pod_packet_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5423_level_b_matrix_consolidation_after_geo.json
```

Scripts and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5420_figure5_level_b_matrix_consolidation_decision.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5421_bounded_geo_same_pod_packet_plan.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5422_bounded_geo_same_pod_packet_execution.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5423_level_b_matrix_consolidation_after_geo.py
tests/goal5419_figure5_level_b_same_pod_graphics_matrix_test.py
tests/goal5420_figure5_level_b_matrix_consolidation_decision_test.py
tests/goal5421_bounded_geo_same_pod_packet_plan_test.py
tests/goal5422_bounded_geo_same_pod_packet_execution_test.py
tests/goal5423_level_b_matrix_consolidation_after_geo_test.py
```

Raw Goal5422 evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/county_zcta_bounded_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/county_zcta_bounded_rtdl_summary.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/water_bg_bounded_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/water_bg_bounded_rtdl_summary.json
```

## Current Claimed Status

```text
Level-B same-POD scalar matrix evidence: yes
Full X-HD paper reproduction: no
Figure 5 reproduction: no
Exact paper dataset reproduction: no
Author-vs-RTDL performance ratio: no
Author X-HD RT-core equivalence: no
Explicit -lb reopened: no
```

Consolidated coverage:

```text
graphics cases = 3
graphics RTDL route rows = 6
bounded geo cases = 2
bounded geo RTDL route rows = 2
total cases = 5
matched = true
```

Rows:

```text
graphics:
  dragon_happy
  thai_happy_scaled
  thai_asian_scaled

bounded geo:
  county_zcta_bounded
  water_bg_bounded
```

## Expected Verdict Labels

Choose one:

```text
approve_goals5419_5423_xhd_level_b_same_pod_matrix_packet
approve_with_required_amendments
revise_packet_before_using_as_level_b_status
block_packet_due_to_overclaim_denominator_or_stop_loss_failure
```

## Review Questions

1. Does Goal5419 genuinely execute the three graphics rows on the same POD and
   keep them at Level-B same-source status?
2. Does Goal5419 correctly require `--translate-each-input-to-min-bound` for
   RTDL graphics commands?
3. Does Goal5419 refuse author-vs-RTDL ratios and keep author internal timing,
   author process wall, RTDL route wall, RTDL process wall, and input load as
   separate denominators?
4. Does Goal5420 correctly stop route micro-optimization by default and
   authorize bounded geo packet planning only?
5. Does Goal5421 correctly define the bounded geo packet without executing it?
6. Does Goal5422 genuinely execute both bounded geo rows on the same POD and
   match same-POD author rerun scalar values within `1e-5`?
7. Does Goal5422 correctly identify the geo route as generic partner/Triton
   `directed_max_of_nearest_distance_2d_partner_columns`, not author X-HD
   RT-core?
8. Does Goal5423 correctly consolidate coverage as 3 graphics cases and 2
   bounded geo cases?
9. Does Goal5423 keep exact paper dataset, Figure 5, full paper, and
   author-vs-RTDL ratio claims false?
10. Does the packet correctly distinguish scalar-only fast routes from exact
    per-source witness routes?
11. Does the stop-loss gate correctly prevent reopening explicit `-lb` and
    other app-artifact parity work?
12. Are remaining blockers complete and honest:
    exact paper files/hashes missing, denominator alignment unresolved,
    explicit `-lb` fail-closed, and scalar-only witness caveats?
13. Should the next work branch be exact dataset acquisition / denominator
    alignment rather than more route micro-optimization?

## Required Harsh Checks

Please actively look for:

- any hidden author-vs-RTDL ratio;
- any implicit Figure 5 or full-paper claim;
- any promotion of bounded fixtures to exact paper datasets;
- any attempt to treat `cell-mbr-fast-scalar` as exact witness reproduction;
- any restart of explicit `-lb`, row identity, hash parity, or author internal
  stream matching without a valid G-1 gate;
- any mixing of graphics and geo runner families into one denominator.

## Expected Answer Shape

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
13. ...
```
