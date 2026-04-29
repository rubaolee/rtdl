# Goal1096 Two-AI Consensus

Date: 2026-04-29

## Scope

Goal1096 adds a local artifact-intake gate for the current RTX pod plan:

- Goal1084 facility recentered same-scale validation/timing artifact;
- Goal1093 Barnes-Hut depth-8 validation artifact;
- Goal1093 Barnes-Hut depth-8 20M timing-only artifact.

The intake can be run before cloud artifacts exist, reports missing artifacts as `needs_cloud_artifacts`, blocks malformed or semantically invalid artifacts, and never authorizes public RTX speedup claims.

## AI Reviews

| Reviewer | Verdict | Evidence |
| --- | --- | --- |
| Claude | PASS WITH FINDINGS | `docs/reports/goal1096_claude_review_2026-04-29.md` |
| Claude follow-up | ACCEPT / no blocker | `docs/reports/goal1096_claude_followup_review_2026-04-29.md` |
| Codex | ACCEPT after remediation | `scripts/goal1096_current_rtx_pod_artifact_intake.py`, `tests/goal1096_current_rtx_pod_artifact_intake_test.py`, generated Goal1096 artifacts |

## Remediation

Claude's first review found two issues:

- `valid: true` while artifacts are missing is intentional; consumers must read `overall_status`. The report preserves this as a design boundary, not a defect.
- Several blocking paths were not directly tested. Codex added coverage for skip-validation mismatch, wrong schema, non-OptiX mode, missing facility coordinate mapping, wrong Barnes-Hut contract fields, missing timing median, malformed JSON, and unknown app rows.

The new tests exposed one real bug: the facility coordinate-mapping failure branch returned a two-tuple instead of the expected three-tuple. Codex fixed that branch, reran the tests, and requested a Claude follow-up review. Claude confirmed the coverage finding is closed and no new blocker remains.

Claude's follow-up also noted a stale `# pragma: no cover` marker on the malformed-JSON path. Codex removed it after the follow-up because that path is now directly tested.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 scripts/goal1096_current_rtx_pod_artifact_intake.py
PYTHONPATH=src:. python3 -m unittest tests.goal1096_current_rtx_pod_artifact_intake_test
PYTHONPATH=src:. python3 -m unittest tests.goal1084_facility_recentered_rtx_pod_packet_test tests.goal1093_barnes_hut_20m_contract_packet_test tests.goal1095_rtx_cloud_runbook_current_audit_test tests.goal1096_current_rtx_pod_artifact_intake_test
git diff --check -- scripts/goal1096_current_rtx_pod_artifact_intake.py tests/goal1096_current_rtx_pod_artifact_intake_test.py docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.json docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.md
```

Results:

- Goal1096 current artifact intake: `overall_status: needs_cloud_artifacts`, `valid: true`
- Goal1096 unit tests: 8 tests, OK
- Focused related tests: 16 tests, OK
- Diff check: OK

## Boundary

Goal1096 is an artifact-intake gate only. It does not run cloud hardware, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims. Passing copied artifacts would only move the evidence to 2+ AI review, not to public claim authorization.
