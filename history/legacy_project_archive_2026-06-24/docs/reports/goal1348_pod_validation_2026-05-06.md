# Goal1348 Pod Validation

Date: 2026-05-06

Pod SSH endpoint:

```bash
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Validation was run from Git after fetch/reset to `origin/main`.

Source commit:

```text
b866fcc88a376e4988b20de0076c214097c4ce96
```

Command shape:

```bash
cd /root/rtdl_python_only
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1005_post_a5000_speedup_candidate_audit_test \
  tests.goal1022_history_release_drift_audit_test \
  tests.goal1183_goal1182_pre_pod_readiness_gate_test \
  tests.goal1188_next_rtx_pod_gap_analysis_test \
  tests.goal1278_v1_4_sales_risk_primitive_contract_test \
  tests.goal532_v0_8_release_authorization_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal684_v0_9_6_release_level_flow_audit_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal723_event_hotspot_embree_summary_test \
  tests.goal724_service_coverage_embree_summary_test \
  tests.goal836_rtx_baseline_readiness_gate_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal973_deferred_decision_baselines_test \
  tests.goal974_remaining_local_baselines_test \
  tests.goal978_rtx_speedup_claim_candidate_audit_test \
  tests.goal1230_v1_0_app_acceleration_inventory_test
```

Result:

- Ran 67 tests.
- Result: OK.

Boundary:

This pod run validates the current-state sync slice from Git. It does not authorize a release, public v1.5 wording, or new performance claims.
