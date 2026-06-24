# Codex Consensus: Phoenix V3 Set A / Set B Classification Gate

Date: 2026-06-22
Status: `2ai_consensus_complete_gate_approved_with_edits_applied`

## Inputs

- Classification:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json`
- Gate script:
  `scripts/v3_phoenix_set_ab_scorecard_gate.py`
- Generated scorecard JSON:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- Generated scorecard Markdown:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- Test:
  `tests/v3_phoenix_set_ab_scorecard_gate_test.py`
- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_set_a_set_b_classification_gate_2026-06-22.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_set_a_set_b_classification_gate_review_2026-06-22.md`

## External Verdict

Claude verdict:

```text
approve_with_required_edits
```

Accepted findings:

- The Set A / Set B app classification is mechanism-based and defensible.
- AABB M2.1 can be a focused material productized-path probe while Contact
  Manifold and LibRTS all-app AABB rows remain Set B controls.
- The gate correctly keeps release/public/broad V3-over-V2 claims false.
- The gate correctly blocks another full all-app pod run right now.

## Required Edits Applied

1. Case IDs are now whitelisted.

   - `case_id_whitelist_frozen: true`
   - `approved_case_ids_by_app` lists every current scored `case_id`.
   - The gate reports `unapproved_case_rows` and fails integrity if a future
     known app silently adds a new case.

2. Focused productized-path probe count is verified from artifacts.

   - The gate now checks each `focused_productized_material_probes[].path`.
   - Current verified count is `1`, from
     `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`.

3. Set B regression blocks full all-app pod spend.

   - Current Set B row below 0.95x:
     `goal2626_large|librts_spatial_index|aabb_index_all_count_only|embree|librts_embree_aabb_index`
   - The gate records `set_b_regressions_block_pod_spend: true`.

4. Severe Set A regression is now explicit.

   - Severe floor: `0.90x`.
   - Current severe Set A app: `barnes_hut` at `0.8441965065233041x`.
   - The gate records `set_a_severe_regressions_block_pod_spend: true`.

## Current Scorecard

```text
row_count: 52
classified_row_count: 52
unapproved_case_rows: 0
set_a_row_count: 42
set_b_row_count: 10
set_a_geomean_v3_vs_v2: 1.0129340100769488
set_b_geomean_v3_vs_v2: 1.0069425307714026
set_a_apps_over_1_05x: 1
set_a_required_apps_over_1_05x: 5
set_a_severe_regression_apps: {"barnes_hut": 0.8441965065233041}
set_b_rows_below_0_95x: 1
focused_productized_material_probe_count_verified: 1
required_focused_productized_material_probe_count_before_full_all_app_pod_run: 2
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
```

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_phoenix_serious_v2x_paired_analysis_test

Ran 6 tests
OK
```

## Codex Consensus

Codex accepts Claude's review and confirms the required edits were applied.

This gate is now the current Phoenix V3 measurement-control artifact for the
next full all-app V2.14-vs-Phoenix V3 run. It does not authorize spending pod
time on that run yet. Before a full all-app pod rerun:

- a second verified focused material productized-path probe is required;
- the LibRTS Set B regression must be repaired or explicitly deferred with a
  reviewed rationale; and
- the Barnes-Hut Set A severe regression must be repaired or explicitly
  reclassified through a reviewed preregistration update.

## Non-Authorization

This consensus does not authorize:

- Phoenix V3 release;
- full all-app pod rerun;
- public performance claims;
- broad V3 faster than V2.x wording;
- true zero-copy wording;
- automatic backend/partner selection;
- V4, C ABI, embedding, SDK, or external host interop work.

## Goal-Level Decision Audit

Decision: accept the edited Set A / Set B scorecard gate as the current
measurement-control artifact, while keeping release and full all-app pod spend
blocked.

1. Was I foolish?
   No for this decision.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to keep app-level classification without
   case_id freeze, trust an editable probe count, or let severe regressions hide
   inside aggregate geomeans.
3. Was there another path?
   Yes. I could have treated Claude's `approve_with_required_edits` as approval
   without applying the edits. That would leave the gate too weak for serious
   pod planning.
4. Can I now try a different path that truly solves the problem?
   Yes. The next engineering path is constrained: fix or supersede the severe
   Set A Barnes-Hut regression, fix or defer the Set B LibRTS regression, and
   obtain a second verified focused material productized-path probe before any
   full all-app rerun.
