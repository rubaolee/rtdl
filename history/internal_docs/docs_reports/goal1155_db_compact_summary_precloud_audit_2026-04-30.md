# Goal1155 DB Compact-Summary Pre-Cloud Audit

Date: 2026-04-30

Valid: `true`

## Summary

- App: `database_analytics`
- Current public wording status: `public_wording_not_reviewed`
- Cloud policy: `no_pod_until_code_or_contract_changes`

## Current Evidence

| Path | RTX sec | Fastest baseline | Baseline sec | Baseline/RTX | Reason |
| --- | ---: | --- | ---: | ---: | --- |
| `prepared_db_session_sales_risk` | `0.10172516293823719` | `embree_compact_summary` | `0.061593040940351784` | `0.6054848098670358` | RTX is slower than the fastest non-OptiX same-semantics baseline in current final A5000 evidence. |
| `prepared_db_session_regional_dashboard` | `0.138423103839159` | `embree_compact_summary` | `0.12720579199958593` | `0.9189635867968468` | RTX is slower than the fastest non-OptiX same-semantics baseline in current final A5000 evidence. |

## Source Observations

- `compact_summary_has_no_public_row_materialization_gate`: `True`
- `optix_grouped_summary_uses_grouped_row_api`: `True`
- `embree_grouped_summary_uses_grouped_row_api`: `True`
- `regional_dashboard_runs_three_compact_native_ops`: `True`
- `sales_risk_runs_three_compact_native_ops`: `True`

## Local Profile

- Profile: `/tmp/goal1155_db_local_profile.json`, scenario `all`, copies `1000`, iterations `3`, output mode `compact_summary`

| Backend | Status | Observation | Warm median sec | Row-materializing ops | Compact-summary ops |
| --- | --- | --- | ---: | ---: | ---: |
| `cpu` | `ok` | `needs_interface_tuning` | `0.12789133295882493` | `3` | `0` |
| `embree` | `ok` | `needs_native_counter_artifact` | `0.006249167025089264` | `0` | `6` |

## Conclusions

- The public DB app already has a compact-summary gate that rejects row-materializing public RTX claim paths.
- The current OptiX evidence is slower than Embree compact-summary baselines for both DB scenarios, so another pod rerun without code or contract changes is low-value.
- The compact-summary implementation still performs three native DB operations per scenario and grouped summaries still travel through grouped row-return APIs before Python dict decoding.
- The next useful optimization is a generic prepared DB compact-summary batch primitive that can execute scan-count, grouped-count summary, and grouped-sum summary in one native prepared-session dispatch with explicit phase counters.

## Next Actions

- Design a generic DB compact-summary batch request format rather than hardcoding a sales/dashboard-only API.
- Implement OptiX first: one prepared dataset, one batch dispatch for the scenario's scan-count and grouped summaries, and phase counters for traversal, copyback, exact filtering/grouping, and output packing.
- Mirror the API in Embree after OptiX so the fastest same-semantics CPU RT baseline remains fair.
- Only then include database_analytics in the next consolidated RTX pod batch.

## Blockers

- None for this audit.

## Boundary

Goal1155 is a pre-cloud DB performance audit. It does not authorize public speedup wording, does not start cloud resources, and does not change release status.
