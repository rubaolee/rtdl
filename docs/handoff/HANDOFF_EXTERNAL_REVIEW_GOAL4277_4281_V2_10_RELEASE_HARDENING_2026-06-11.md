# External Review Handoff: Goal4277-4281 v2.10 Release Hardening

Purpose: review the post-v2.10 source-tree release-hardening chain after the
published `v2.10` milestone tag. This is a review of documentation,
onboarding, evidence navigation, and pod-validation tooling, not a new
performance claim.

## Review Outputs

Please write one review file:

- Claude:
  `docs/reviews/goal4282_claude_review_goal4277_4281_v2_10_release_hardening_2026-06-11.md`
- Gemini:
  `docs/reviews/goal4283_gemini_review_goal4277_4281_v2_10_release_hardening_2026-06-11.md`

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Files To Inspect

Implementation/report chain:

- `VERSION`
- `docs/release_reports/v2_10/README.md`
- `docs/reports/goal4277_v2_10_release_artifact_alignment_2026-06-11.md`
- `docs/reports/goal4278_source_tree_doctor_2026-06-11.md`
- `docs/reports/goal4279_benchmark_evidence_index_2026-06-11.md`
- `docs/reports/goal4280_v2_10_pod_validation_bundle_2026-06-11.md`
- `docs/reports/goal4281_pod_bootstrap_probe_2026-06-11.md`

New tooling and docs:

- `scripts/rtdl_source_tree_doctor.py`
- `scripts/rtdl_benchmark_evidence_index.py`
- `scripts/rtdl_v2_10_pod_validation_bundle.py`
- `scripts/rtdl_pod_bootstrap_probe.py`
- `docs/learn/source_tree_doctor.md`
- `docs/learn/benchmark_evidence_index.md`
- `docs/audit/runbooks/v2_10_pod_validation_bundle.md`
- `docs/audit/runbooks/v2_10_pod_bootstrap_probe.md`
- `docs/partner_acceleration_boundaries.md`

Tests:

- `tests/goal4277_v2_10_release_artifact_alignment_test.py`
- `tests/goal4278_source_tree_doctor_test.py`
- `tests/goal4279_benchmark_evidence_index_test.py`
- `tests/goal4280_v2_10_pod_validation_bundle_test.py`
- `tests/goal4281_pod_bootstrap_probe_test.py`

## Questions

1. Does Goal4277 correctly align the current source-tree artifacts with v2.10
   without moving or implicitly authorizing movement of the existing `v2.10`
   tag?
2. Do Goals4278-4281 improve user/reviewer onboarding without making package
   install, broad RT-core, whole-app speedup, automatic partner selection, or
   zero-copy claims?
3. Are the doctor/probe/bundle scripts safe by default: no destructive actions,
   no hardware timing unless explicitly requested, and clear progress output?
4. Are the docs and current paths clean: `examples/current`, top-level
   `tutorials/`, v2.10 release report, and no stale v2.6/v2_0 learner paths?
5. Are the tests sufficient for this cleanup scope, and what remains before a
   fresh pod run?

## Suggested Validation

Run if possible:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4281_pod_bootstrap_probe_test \
  tests.goal4280_v2_10_pod_validation_bundle_test \
  tests.goal4279_benchmark_evidence_index_test \
  tests.goal4278_source_tree_doctor_test \
  tests.goal4277_v2_10_release_artifact_alignment_test \
  tests.goal4276_top_level_tutorial_reorganization_test \
  tests.goal4271_v2_10_user_doc_cleanup_test \
  tests.goal4274_current_doc_recheck_test \
  tests.goal4267_v2_10_milestone_release_packet_test \
  tests.goal4270_v2_10_milestone_release_consensus_test
```

Expected local result from Codex before review request:

```text
Ran 37 tests
OK
```

## Boundary

This review must not authorize release, tag movement, public speedup wording,
package-install wording, broad RT-core wording, paper-reproduction wording,
automatic partner selection, true-zero-copy wording, AMD/HIPRT performance
wording, or app-specific native-engine logic. The next hardware-dependent step
is a fresh pod run of the v2.10 bundle on current `main`.
