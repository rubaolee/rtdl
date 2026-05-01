# Goal1091 Claude Review — Robot Pose-Offset Embree Smoke Intake

Date: 2026-04-29

Reviewer: Claude (claude-sonnet-4-6)

## Verdict

**ACCEPT**

## Artifacts Reviewed

| Artifact | Purpose |
| --- | --- |
| `docs/reports/goal1091_robot_embree_pose_offset_smoke_2026-04-29.json` | Embree smoke run output |
| `scripts/goal1091_robot_pose_offset_smoke_intake.py` | Intake script |
| `tests/goal1091_robot_pose_offset_smoke_intake_test.py` | Intake unit tests |
| `docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.json` | Intake result |
| `docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.md` | Intake narrative |
| `docs/reports/goal1089_two_ai_consensus_2026-04-29.md` | Prior two-AI consensus (Goal1089) |

## Specific Checks

### 1. Smoke uses Embree with pose_id_start=200001

PASS. The smoke artifact records `"source_backend": "embree"` and `benchmark_scale.pose_id_start = 200001`. The intake script asserts both: `artifact["source_backend"] == "embree"` and `scale["pose_id_start"] == 200001`. The intake JSON confirms both checks pass (`source_backend_embree: true`, `pose_id_start_recorded: true`).

### 2. Correctness parity is true

PASS. The smoke artifact records `"correctness_parity": true` and `validation.matches_reference: true`, validated via "compare Embree compact pose summary against CPU oracle compact pose summary" with `worker_count=1`. The intake checks `artifact["correctness_parity"] is True` and the intake output confirms `correctness_parity: true`.

### 3. Colliding pose sample is in the offset range

PASS. The colliding sample is `[200001, 200018, 200019, ..., 200026]` — minimum value is `200001`, which is exactly the offset base. The intake script guards `min(summary["colliding_pose_ids_sample"]) >= 200001` (`sample_uses_offset_range: true`). The unit test independently asserts `assertGreaterEqual(min(...), 200001)`. No sample value falls below the offset start.

### 4. Does not run the heavy 36M baseline

PASS. Smoke scale is 1000 poses × 1 iteration × 128 obstacles — a lightweight local run, not the 36 million-pose full baseline. Total `native_anyhit_query` time is 7.4 ms. The boundary text explicitly states "does not run the heavy 36M baseline" and is asserted in the unit test.

### 5. No public RTX speedup claim, release, or public wording change authorized

PASS. The smoke artifact records `"authorizes_public_speedup_claim": false`. The intake records `"public_speedup_claim_authorized": false` and the check `claim_authorized_false: true` is enforced in code. The boundary text is embedded in both the intake JSON and the markdown, and is verified by the test. No release, no public wording change, and no RTX speedup claim is present or implied anywhere in the artifacts.

## Intake Check Summary

All 7 intake checks pass; intake status is `ok`; `valid` is `true`.

| Check | Result |
| --- | --- |
| `status_ok` | PASS |
| `correctness_parity` | PASS |
| `source_backend_embree` | PASS |
| `pose_id_start_recorded` | PASS |
| `pose_count_recorded` | PASS |
| `sample_uses_offset_range` | PASS |
| `claim_authorized_false` | PASS |

## Consistency with Goal1089

The prior two-AI consensus (Goal1089) established the pose-id offset convention: chunk `i` uses `pose_id_start = i * 200000 + 1`. Goal1091 correctly exercises this with `pose_id_start=200001` (chunk 0 offset base), confirming the smoke path is consistent with the established convention.

## Boundary Confirmation

Goal1091 is scoped as a small local Embree smoke intake for pose-id offsets only. It does not run the heavy 36M baseline, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims. This scope is enforced in code, recorded in the artifact, and verified by tests.

## Decision

All five required properties are satisfied. ACCEPT.
