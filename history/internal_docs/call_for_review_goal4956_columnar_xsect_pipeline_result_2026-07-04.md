# Call For Review: Goal4956 Columnar Xsect Pipeline Result

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4956_columnar_xsect_pipeline_result_2026-07-04.md`
- `history/internal_docs/goal4956_columnar_xsect_pipeline_measure.py`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `Paper-reproduction-apps/rayjoin-paper/README.md`
- `history/internal_docs/goal4955_artifacts/goal4956_pod_comparison_summary_v2.json`
- `history/internal_docs/goal4955_artifacts/goal4956_columnar_fixed_run_*.json`
- `history/internal_docs/goal4955_artifacts/section57_overlay_columnar_binary_app_probe_3.json`
- `history/internal_docs/goal4955_projected_descriptor_pipeline_status_2026-07-04.md`

## Requested Verdict

`approve_goal4956_useful_win_app_route_added`

or

`block_goal4956_until_amended`

## Review Questions

1. Does Goal4956 preserve the boundary that RTDL remains generic and RayJoin
   remains an app?
2. Does the implementation avoid changes to `src/rtdsl/**` and `src/native/**`?
3. Is the columnar xsect route a legitimate app-owned dataflow implementation
   rather than a hidden RayJoin-specific RTDL core primitive?
4. Is the int64-overflow sorting bug correctly diagnosed and repaired with
   extended-precision distance plus stable original-index tie-break?
5. Does the POD evidence prove a real useful win over the rerun baseline:
   `2.947452s -> 2.309159s`, or `1.276418x`?
6. Does the route preserve descriptor-result semantics against the baseline
   route?
7. Is it correctly bounded as writer-free numeric/binary route evidence, not
   paper text byte equality evidence?
8. Is it correctly bounded as a useful v2.14.3 candidate win, not a 1.5x target
   win and not a final high-performance solution?
9. Is the new paper-app route `section57_overlay_columnar_binary.py`
   appropriately bounded as writer-free numeric/binary pipeline evidence, not
   paper text byte-equality evidence?
10. Is the recommended exit label appropriate?

## Non-Authorization

This review should not authorize:

- public high-performance claims;
- Layer 4 traversal callback/fusion;
- broad RTDL performance claims;
- broad RayJoin paper reproduction performance claims;
- paper text byte equality claims for the numeric route;
- app-specific RTDL core primitives;
- marking the whole active v2.14.3 goal complete before independent review debt
  is closed.
