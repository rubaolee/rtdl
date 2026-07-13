# Call For Review - Goal5422 X-HD Bounded Geo Same-POD Packet Execution

Please strictly review Goal5422.

## Files To Review

```text
history/internal_docs/goal5422_xhd_bounded_geo_same_pod_packet_execution_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5422_bounded_geo_same_pod_packet_execution.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5422_bounded_geo_same_pod_packet_execution.py
tests/goal5422_bounded_geo_same_pod_packet_execution_test.py
```

Raw evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/county_zcta_bounded_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/county_zcta_bounded_rtdl_summary.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/water_bg_bounded_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/water_bg_bounded_rtdl_summary.json
```

Context:

```text
history/internal_docs/goal5421_xhd_bounded_geo_same_pod_packet_plan_2026-07-10.md
history/internal_docs/goal5420_xhd_figure5_level_b_matrix_consolidation_decision_2026-07-10.md
history/internal_docs/goal5305_xhd_county_zcta_rtdl_partner_gate_result_2026-07-09.md
history/internal_docs/goal5307_xhd_water_bg_author_rtdl_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
```

## Expected Verdict Labels

Choose one:

```text
approve_goal5422_bounded_geo_same_pod_packet_execution
approve_with_required_amendments
revise_goal5422_before_matrix_consolidation
block_goal5422_due_to_execution_or_claim_boundary_error
```

## Review Questions

1. Did Goal5422 genuinely execute the Goal5421 packet on the current POD rather
   than remaining a plan?
2. Does the summary include exactly two rows: `county_zcta_bounded` and
   `water_bg_bounded`?
3. Do both rows match same-POD author rerun scalar values within the declared
   `1e-5` tolerance?
4. Are both rows correctly marked as Level-B bounded geo fixtures rather than
   exact paper datasets?
5. Does the report correctly identify the RTDL route as generic partner/Triton
   `directed_max_of_nearest_distance_2d_partner_columns`, not the author X-HD
   RT-core algorithm?
6. Are raw author and RTDL JSON outputs downloaded and referenced?
7. Does the execution use the project POD wrapper and avoid naked SSH?
8. Does the report keep author `Running.AvgTime`, author remote process wall,
   RTDL route phase, RTDL total phase, and RTDL remote process wall as separate
   denominators?
9. Does the report refuse author-vs-RTDL performance ratios?
10. Does the report avoid claims of geo Figure 5 reproduction, exact paper
    dataset recovery, full paper reproduction, or author RT-core equivalence?
11. Does the report keep explicit `-lb` stopped and avoid route
    micro-optimization by default?
12. Is Goal5423, consolidation of graphics + bounded geo evidence and blockers,
    the correct next step?
13. Does the Stop-Loss Gate G-1 block correctly show that this is not
    app-artifact parity work and does not restart row/hash/internal-stream
    matching?

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
