# Call For Review: Phoenix V3 Set A / Set B Classification Gate

Date: 2026-06-22
Requester: Codex
Requested reviewer: Claude or equivalent external AI
Status: bounded technical review request; no release authorization.

## Packet Under Review

Primary artifacts:

```text
docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json
scripts/v3_phoenix_set_ab_scorecard_gate.py
docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json
docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md
tests/v3_phoenix_set_ab_scorecard_gate_test.py
```

Context artifacts:

```text
docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json
docs/reports/phoenix_v3_performance_failure_optimization_accounting_2026-06-22.md
docs/reviews/codex_phoenix_v3_performance_failure_accounting_2ai_consensus_2026-06-22.md
```

## What Changed

The proposal-only Set A / Set B release bar has been turned into a frozen
classification and executable scorecard gate for the next full all-app paired
run.

Classification:

```text
Set A architecture-bearing apps:
  barnes_hut
  hausdorff_xhd
  rt_dbscan
  rtnn
  spatial_rayjoin
  triangle_counting

Set B ceiling/control apps:
  contact_manifold
  librts_spatial_index
  raydb_style
  robot_collision
```

Current scorecard against the serious 2026-06-22 V2.14-vs-Phoenix V3 run:

```text
row_count: 52
classified_row_count: 52
set_a_row_count: 42
set_b_row_count: 10
set_a_geomean_v3_vs_v2: 1.0129340100769488
set_b_geomean_v3_vs_v2: 1.0069425307714026
set_a_apps_over_1_05x: 1
set_a_required_apps_over_1_05x: 5
set_b_rows_below_0_95x: 1
focused_productized_material_probe_count: 1
required_focused_productized_material_probe_count_before_full_all_app_pod_run: 2
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
```

Focused tests:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_phoenix_serious_v2x_paired_analysis_test

Ran 6 tests
OK
```

## Questions For Reviewer

Please answer critically and directly.

1. Is the Set A / Set B classification defensible as a mechanism-based
   preregistration, or does any app belong in the other set?
2. Is it acceptable that AABB M2.1 counts as a focused material productized-path
   probe precondition while Contact Manifold and LibRTS all-app AABB rows remain
   Set B ceiling/control rows?
3. Does the gate correctly prevent another full all-app pod run right now?
4. Does the gate correctly keep release/public/broad V3-over-V2 claims false?
5. Is row-level classification by frozen `app_id` rule strong enough for the
   next run, or must every future `case_id` be listed explicitly before the run?
6. What changes are required before this gate becomes the controlling
   measurement-control artifact for Phoenix V3?

## Required Verdict

Use one of:

```text
approve_gate
approve_with_required_edits
reject_classification
reject_gate
```

## Explicit Non-Authorization

This review cannot authorize:

- Phoenix V3 release;
- public speedup wording;
- broad V3 faster than V2.x wording;
- true zero-copy wording;
- automatic backend/partner selection;
- V4, C ABI, embedding, SDK, or external host interop work.
