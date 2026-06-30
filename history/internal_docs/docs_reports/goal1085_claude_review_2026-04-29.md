# Goal1085 Formal Review

**Reviewer:** Claude (claude-sonnet-4-6)
**Date:** 2026-04-29
**Verdict:** ACCEPT

---

## Artifacts Reviewed

| Artifact | Path |
| --- | --- |
| Packet generator | `scripts/goal1085_robot_chunked_embree_baseline_packet.py` |
| Generated runner | `scripts/goal1085_robot_chunked_embree_baseline_runner.sh` |
| Test suite | `tests/goal1085_robot_chunked_embree_baseline_packet_test.py` |
| JSON output | `docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.json` |
| Markdown output | `docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.md` |
| Reference (Goal1081) | `docs/reports/goal1081_same_scale_baseline_execution_packet_2026-04-29.md` |

---

## Checklist

### 1. 36M total poses split into 180 chunks of 200k

**PASS.**

`TOTAL_POSE_COUNT = 36_000_000`, `CHUNK_POSE_COUNT = 200_000`, and `chunk_count` is computed as `TOTAL_POSE_COUNT // CHUNK_POSE_COUNT = 180`. The `valid` field additionally asserts `TOTAL_POSE_COUNT % CHUNK_POSE_COUNT == 0` and `chunk_count == 180` at build time, and the generated runner uses `seq 0 179` (180 iterations, zero-indexed). The test suite independently asserts all three values. Arithmetic is internally consistent throughout all three artifact layers (Python, JSON, shell).

### 2. Obstacle count remains 4096

**PASS.**

`OBSTACLE_COUNT = 4096` is the single source of truth in the generator. The JSON output carries `"obstacle_count": 4096`. The generated runner embeds `--obstacle-count 4096` in every chunk invocation. The test suite asserts `scale["obstacle_count"] == 4096`. This value matches the obstacle count used in the Goal1081 same-scale robot row (`--obstacle-count 4096`), confirming scale parity with the reference baseline.

### 3. Runner does not itself authorize a speedup claim

**PASS.**

The JSON artifact carries `"public_speedup_claim_authorized": false`. The generator hard-codes `public_speedup_claim_authorized: False` (not derived from any runtime condition). The shell runner contains a boundary comment at line 4: `# Boundary: does not authorize public RTX speedup claims.` The runner's closing echo instructs the operator to review chunk outputs before any comparison, not to draw conclusions. The test suite asserts `self.assertFalse(payload["public_speedup_claim_authorized"])`. No path through the generator or runner produces an authorization.

### 4. Same-total-work vs. same-single-launch limitation is honestly documented

**PASS.**

The `baseline_interpretation` field explicitly names both categories: "It is a same-total-work engineering baseline, not a same-single-launch baseline, until artifact intake and 2+ AI review decide whether the comparison boundary is acceptable." This wording appears in the JSON artifact, the markdown output, and is asserted by the test suite (`assertIn("same-total-work engineering baseline", ...)`). The packet does not claim equivalence to a monolithic 36M-pose Embree launch. The distinction is clearly deferred to a future intake and review gate, not resolved by this goal.

Cross-referencing Goal1081: the same-single-launch row for the robot baseline (`embree_same_scale`) is tagged `linux_or_windows_high_memory` and remains unprepared for non-cloud hosts. Goal1085 explicitly characterizes its chunked approach as an alternative engineering path, not a replacement for that decision.

### 5. Appropriate scope as a non-cloud robot Embree baseline packet

**PASS.**

The `boundary` field and the shell runner header both identify this as a non-cloud (`local/Linux/Windows`) Embree baseline host runner. The goal does not run the heavy 36M-pose job; it only generates the runner and packet artifacts. It does not change public wording, does not authorize release, and does not modify any RTX claim. The test `test_cli_writes_runner_without_running_heavy_baseline` confirms that invoking the CLI produces artifacts without triggering the underlying baseline workload. Scope is narrow and correctly characterized.

---

## Additional Observations

- The `${{chunk_index}}` escaping in the Python `.format()` call correctly produces `${chunk_index}` in the shell output, which is a valid bash variable reference within the generated for-loop. No shell injection risk.
- The packet carries `source_artifacts` pointers to Goal1080 and Goal1081, establishing provenance correctly.
- The `target_rtx_artifact` pointer to the Goal1072 timing artifact is recorded but not consumed; this is appropriate since no comparison is authorized at this stage.
- Exit code semantics are correct: `main()` returns `1` if `valid` is false, `0` otherwise, enabling CI gating.

---

## Summary

All five required checklist items pass. The packet is internally consistent, the limitation boundary is prominently and honestly documented across every artifact layer, and no path through the goal authorizes a speedup claim or changes public-facing state. This goal is appropriate as a preparation-only non-cloud robot Embree baseline packet.

**Verdict: ACCEPT**
