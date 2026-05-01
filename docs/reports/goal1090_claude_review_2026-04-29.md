# Goal1090 Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

Review of Goal1090 robot Embree local baseline runbook. Files examined:

- `scripts/goal1090_robot_embree_local_runbook.py`
- `tests/goal1090_robot_embree_local_runbook_test.py`
- `docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.json`
- `docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.md`
- `docs/reports/goal1089_two_ai_consensus_2026-04-29.md`
- `scripts/goal1085_robot_chunked_embree_baseline_runner.sh`
- `scripts/goal1086_robot_chunked_embree_baseline_intake.py`

---

## Checklist

### 1. Non-cloud / local work only

PASS. The runbook sets `host_policy: "non_cloud_linux_or_windows_preferred"` and `not_pod_work: true`. The boundary statement in both JSON and Markdown reads: "does not create cloud resources." The runner script carries the same boundary comment. No cloud credentials, pod configuration, or network egress is referenced anywhere.

### 2. Step sequence: smoke → one real chunk → intake → full resumable run → final intake

PASS. The five steps are present in the required order:

| # | Name | Heavy |
|---|------|-------|
| 1 | `smoke_one_small_embree_chunk` | false |
| 2 | `run_one_real_chunk` | true |
| 3 | `intake_after_partial_or_full_run` | false |
| 4 | `run_remaining_chunks_when_host_is_available` | true |
| 5 | `final_intake` | false |

The smoke step uses 1,000 poses and 128 obstacles. Step 2 pins `START_CHUNK=0 END_CHUNK=0` to run exactly one claim-scale chunk. Steps 3 and 5 call the intake script. Step 4 runs the full runner with `SKIP_EXISTING=1`.

### 3. Pose-id offset and resume controls preserved

PASS.

- The runner (`goal1085`) computes `--pose-id-start $(( chunk_index * 200000 + 1 ))`, consistent with the Goal1089 consensus formula.
- The runbook records `pose_id_start_formula: "chunk_index * 200000 + 1"` in the scale contract.
- All three resume controls are listed in `scale_contract.resume_controls` and used in step commands: `RTDL_GOAL1085_START_CHUNK`, `RTDL_GOAL1085_END_CHUNK`, `RTDL_GOAL1085_SKIP_EXISTING`.
- The intake (`goal1086`) independently validates `pose_id_start == chunk_index * 200000 + 1` per chunk at line 52–53.
- The Goal1089 two-AI consensus (ACCEPT) confirms these offsets were reviewed and a negative intake test was added before closure.

### 4. Runbook generation does not execute the heavy baseline

PASS. `build_runbook()` constructs a Python dictionary and writes JSON/Markdown artifacts. No subprocess call, shell invocation, or baseline runner execution occurs at generation time. The heavy steps are documented as future operator commands, not invoked by the script itself.

Minor observation: the `valid` self-check at line 89 (`"chunk_index * 200000 + 1" == "chunk_index * 200000 + 1"`) is a tautology and provides no real runtime validation. The flanking checks (five steps exist, runner and intake scripts referenced) are meaningful. This is non-blocking.

### 5. No public RTX speedup claim, release, or public wording change authorized

PASS.

- `summary.public_speedup_claim_authorized_count: 0` is recorded in JSON and asserted by the test suite.
- The boundary statement explicitly forbids: "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."
- The intake (`goal1086`) sets `public_speedup_claim_authorized: False` and its interpretation block states that even a complete run requires 2+ AI review before any speedup comparison.
- Tests `test_runbook_is_non_cloud_and_claim_safe` and others assert these properties directly.

---

## Test Coverage

Four unit tests cover the meaningful behavioral properties: non-cloud/claim-safe flags, presence of resumable runner and intake commands, scale contract formula, and Markdown usability. Coverage is adequate for a runbook generator.

---

## Prior Consensus

Goal1089 two-AI consensus: ACCEPT (2026-04-29). Pose-id offset implementation reviewed by both Codex and Claude; negative intake test added per Claude's earlier note. Goal1090 inherits that settled foundation.

---

## Verdict

**ACCEPT.**

All five checklist criteria pass. Goal1090 is a non-cloud documentation-only runbook generator. It correctly records the step sequence, pose-id offset formula, and all resume controls inherited from Goal1089. It does not execute the heavy baseline and explicitly forecloses any public RTX speedup claim, release, or wording change.
