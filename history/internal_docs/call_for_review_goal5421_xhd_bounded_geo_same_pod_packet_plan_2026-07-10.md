# Call For Review - Goal5421 X-HD Bounded Geo Same-POD Packet Plan

Please strictly review Goal5421.

## Files To Review

```text
history/internal_docs/goal5421_xhd_bounded_geo_same_pod_packet_plan_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5421_bounded_geo_same_pod_packet_plan.py
tests/goal5421_bounded_geo_same_pod_packet_plan_test.py
```

Context:

```text
history/internal_docs/goal5420_xhd_figure5_level_b_matrix_consolidation_decision_2026-07-10.md
history/internal_docs/goal5305_xhd_county_zcta_rtdl_partner_gate_result_2026-07-09.md
history/internal_docs/goal5307_xhd_water_bg_author_rtdl_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
```

## Expected Verdict Labels

Choose one:

```text
approve_goal5421_bounded_geo_same_pod_packet_plan
approve_with_required_amendments
revise_goal5421_before_execution
block_goal5421_due_to_claim_boundary_or_packet_error
```

## Review Questions

1. Does Goal5421 correctly implement Goal5420's decision to plan, but not
   execute, a bounded geo same-POD packet?
2. Does the packet include exactly the two intended bounded geo rows:
   `county_zcta_bounded` and `water_bg_bounded`?
3. Are both rows correctly marked as `level_b_bounded_geo_fixture`, not exact
   paper datasets and not Figure-5 reproduction?
4. Does the packet correctly preserve the prior author/RTDL scalar matches from
   Goal5305 and Goal5307?
5. Are the author command contracts correct for WKT 2D geo runs
   (`variant=rt`, `execution=gpu`, `normalize=false`)?
6. Are the RTDL command contracts correctly based on the generic partner/Triton
   route `directed_max_of_nearest_distance_2d_partner_columns` with
   `dense_point_nearest_tiled`?
7. Does the report correctly state that this is not the author X-HD RT-core
   algorithm and not a new app-specific RTDL primitive?
8. Does the packet keep author internal timing, author process wall, RTDL route
   wall, and RTDL total as separate denominators and refuse ratios?
9. Does the builder avoid running POD commands or hidden subprocess execution?
10. Does the packet require the project POD wrapper and forbid naked SSH?
11. Does the claim boundary keep `-lb` stopped and avoid route micro-optimization
    by default?
12. Is Goal5422, bounded geo same-POD packet execution, the correct next goal if
    this packet is approved?
13. Does the Stop-Loss Gate G-1 block correctly show that this is not an
    app-artifact parity line, but a bounded scalar packet around a generic
    directed max-nearest partner route?

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
