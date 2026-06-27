# Codex + Kepler Phoenix V3 Hausdorff M5 Negative Classification Consensus

Date: 2026-06-22
Status: `approve_blocked_not_release`

## Scope

This records the second-AI result review for:

- `docs/reports/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622_rerun2_metric_aligned/`
- `docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622_rerun3_stability/`

The reviewed question was whether Hausdorff M5 should be counted as the third
Set-A material runtime-trunk win, rerun as invalid, or stopped as valid negative
evidence.

## Kepler Verdict

Verdict: `accept_negative_classification_stop_hausdorff_m5`

Kepler found no required report edits. The runs are valid and metadata-clean,
but both serious samples fail the pre-registered runner-vs-legacy no-regression
gate:

- rerun2 runner-vs-legacy phase-total: `0.976x`
- rerun3 runner-vs-legacy phase-total: `0.975x`
- rerun3 runner-vs-legacy wrapper wall: `0.978x`

Kepler confirmed the run is not invalid: all variants completed, stderr was
empty, scale was 1,048,576 points per side, repeat/warmup was 5/1, and both
directed runner legs executed through `prepared_execution_session_runner`
without threshold-row host materialization. Query-point residency and
true-zero-copy remained false/scoped correctly.

Kepler recommendation: do generic runner-overhead reduction first. The evidence
shows the primitive route remains useful, but the productized runner tax is
large enough to lose against the legacy prepared OptiX front door.

## Codex Consensus

Codex accepts Kepler's verdict.

Hausdorff M5 is valid negative evidence, not the third Set-A material
runtime-trunk win. Do not rerun the same Hausdorff sample hoping for noise. Do
not count OptiX-over-Embree as Phoenix V3 trunk evidence while the runner loses
to the legacy app-front-door prepared OptiX path.

## Authorized Next Work

Authorized non-release work:

1. Close Hausdorff M5 as negative.
2. Start a bounded generic runner-overhead reduction goal.
3. Prove the overhead reduction locally before any focused pod rerun.
4. Use focused pod only for no-regression/material evidence on the productized
   runtime path.

Not authorized:

- V3 release.
- all-app pod rerun.
- public speedup wording.
- broad V3-over-V2 wording.
- whole-Hausdorff speedup wording.
- true-zero-copy wording.
- V4 / external-buffer wording.

## Goal-Level Decision Audit

Decision: stop Hausdorff M5 as valid negative evidence and redirect to generic
runner-overhead reduction.

1. Was I foolish?

   No for this decision. The pre-registered gate failed twice and the second-AI
   review accepted the negative classification.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be to count the route as a V3 trunk
   win by comparing only against Embree while ignoring the relevant legacy
   OptiX incumbent.

3. Was there another path that would have avoided getting stuck?

   Yes. Repeating Hausdorff or changing the bar after seeing results would get
   stuck in noise chasing. The better path is to fix the shared runner overhead
   that this probe exposed.

4. Can I now try a different path that actually solves the problem?

   Yes. The next bounded path is a reusable runner-overhead reduction that can
   help multiple Set-A probes rather than a Hausdorff-only patch.
