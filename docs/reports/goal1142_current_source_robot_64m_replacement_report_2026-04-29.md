# Goal1142 Current-Source Robot 64M Replacement Report

Date: 2026-04-29

Verdict: `VALID_EVIDENCE_COLLECTED`

## Purpose

Goal1142 replaces the stale-source robot 64M timing artifact used by the older
Goal1121 intake with a same-source artifact collected during the active
Goal1141 RTX pod window.

The original Goal1141 single-session run succeeded, but the standard Goal1118
intake remained `valid: false` because the robot 8M timing row was below the
0.1 second timing floor:

- `robot_prepared_pose_flags_8m_timing.json`
- source commit: `21fa036881bf9a0c806f69c15727d87b482ccfcf`
- median warm query: `0.018729395233094692` seconds
- finding: `median_query_below_timing_floor`

The older Goal1121 64M replacement row passed the timing floor, but it came
from source commit `2ba7ae0`, so mixing it with the current Goal1141 artifacts
would create mixed-source release evidence.

## New Artifact

Collected on the same RTX A5000 pod and copied back locally:

- `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_64m_timing_goal1142.json`
- source commit: `21fa036881bf9a0c806f69c15727d87b482ccfcf`
- pose count: `64000000`
- obstacle count: `4096`
- edge ray count: `256000000`
- median warm query: `0.17847148794680834` seconds
- result mode: `pose_count`
- validation mode: timing-only, `--skip-validation`

## Intake Result

The replacement packet and intake are:

- `docs/reports/goal1142_current_source_rtx_rerun_packet_with_robot_64m_2026-04-29.json`
- `docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json`
- `docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.md`

Summary:

- `valid`: `true`
- `row_count`: `5`
- `valid_row_count`: `5`
- `missing_row_count`: `0`
- `same_source_commit`: `true`
- `source_commits`: `['21fa036881bf9a0c806f69c15727d87b482ccfcf']`
- `public_speedup_claim_authorized`: `false`

## Tests

Executed locally after copying pod artifacts back:

```bash
PYTHONPATH=src:. python3 scripts/goal1118_current_source_rtx_rerun_intake.py \
  --packet-json docs/reports/goal1142_current_source_rtx_rerun_packet_with_robot_64m_2026-04-29.json \
  --output-json docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json \
  --output-md docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.md

PYTHONPATH=src:. python3 -m unittest \
  tests.goal1118_current_source_rtx_rerun_intake_test \
  tests.goal1136_changed_path_rtx_pod_artifact_intake_test \
  tests.goal1141_rtx_single_session_bundle_test -v
```

Result: `9` tests passed.

## Boundary

Goal1142 is evidence repair and intake validation only. It does not authorize a
public RTX speedup claim, does not change public wording, does not authorize a
release, and does not replace the need for external AI review before closure.
