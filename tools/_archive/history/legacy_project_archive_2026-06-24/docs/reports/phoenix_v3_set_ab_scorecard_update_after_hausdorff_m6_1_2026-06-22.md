# Phoenix V3 Set-A/B Scorecard Update After Hausdorff M6.1

Date: 2026-06-22
Status: `scorecard_updated_not_release_not_all_app_authorized`

## Change

The Set-A/B classification now records the accepted Hausdorff M5 after-M6.1
focused productized-runner probe:

```text
id: hausdorff_threshold_runner_m5_after_m6_1
path: docs/reports/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_after_m6_1_2026-06-22.md
classification: positive_focused_productized_runner_backed_probe_not_release
```

The focused productized material probe count changed:

```text
before: 1 / 2
after: 2 / 2
```

## Gate Result

Regenerated:

- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`

Current gate:

```text
focused_productized_material_probe_count_verified: 2
missing_focused_productized_material_probe_count: 0
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
failed_checks: []
```

Why all-app remains blocked:

```text
Set A geomean: 1.012934x
Set A apps over 1.05x: 1 / 5 required
Set A severe regression: Barnes-Hut at 0.8441965x
Set B rows below 0.95x: LibRTS Embree AABB index row
```

## Local Gate

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_release_wording_gate_test

41 tests OK
```

## Interpretation

Phoenix V3 has made real trunk progress: the focused productized-runner probe
precondition is now satisfied by AABB plus Hausdorff M6.1. This does not mean
V3 is ready. The controlling all-app scorecard still blocks spend and release.

The next V3 task should attack the remaining Set-A/B blockers as shared runtime
work, not by rerunning Hausdorff or widening claims.

## Goal-Level Decision Audit

Decision: update the machine-readable Set-A/B scorecard to include Hausdorff
M6.1 as a second focused productized-runner probe while keeping all-app blocked.

1. Was I foolish?

   No for this decision. The probe was reviewed and accepted, and the gate still
   blocks broad spend because other requirements are unmet.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be treating 2/2 focused probes as
   release readiness.

3. Was there another path that would have avoided getting stuck?

   Yes. Leave the scorecard stale at 1/2 and confuse the next agent. Updating
   the gate makes the remaining blockers visible.

4. Can I now try a different path that actually solves the problem?

   Yes. Move from focused probe preconditions to the remaining shared runtime
   blockers: Set-A severe regression and Set-B sub-0.95 parity.
