# Goal1093 Claude Formal Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This review covers:

- `scripts/goal1093_barnes_hut_20m_contract_packet.py`
- `scripts/goal1093_barnes_hut_20m_contract_runner.sh`
- `tests/goal1093_barnes_hut_20m_contract_packet_test.py`
- `docs/reports/goal1093_barnes_hut_20m_contract_packet_2026-04-29.json`
- `docs/reports/goal1093_barnes_hut_20m_contract_packet_2026-04-29.md`

Context artifacts read: `goal1079_two_ai_consensus_2026-04-29.md`, `goal1092_v1_rtx_readiness_status_refresh_2026-04-29.json`.

---

## Checklist

### 1. Validation and timing rows share depth=8, node_count=65536, threshold=4, radius=0.1

PASS.

Both rows in the Python source, the generated JSON, the generated Markdown, and the generated shell runner carry identical contract parameters:

| Field | Validation row | Timing row |
| --- | ---: | ---: |
| `barnes_tree_depth` | 8 | 8 |
| `node_count` | 65536 | 65536 |
| `hit_threshold` | 4 | 4 |
| `radius` | 0.1 | 0.1 |

The `valid` predicate in `build_packet()` enforces all four equalities as a conjunction; it evaluates `true` in the committed JSON artifact. The test `test_packet_uses_same_depth8_contract_for_validation_and_timing` asserts each field individually for both rows.

### 2. Validation row does not use --skip-validation

PASS.

- `rows[0]["contains_skip_validation"]` is `False` in source and JSON.
- The validation command (row 1 in the runner) contains no `--skip-validation` flag; confirmed in both the Python `_command(...)` construction and the rendered runner line.
- The test asserts `assertFalse(validation["contains_skip_validation"])` and `assertNotIn("--skip-validation", validation_command)`.

### 3. Timing row is explicitly timing-only and uses --skip-validation

PASS.

- `rows[1]["requires_validation"]` is `False`; `rows[1]["contains_skip_validation"]` is `True`.
- `timing_floor_sec` is set to `0.100`.
- The rendered runner line 2 includes `--skip-validation` explicitly.
- The row `purpose` field states: *"This remains timing-only and requires the depth8_contract_validation row plus later intake/review."*
- The test asserts `assertFalse(timing["requires_validation"])`, `assertTrue(timing["contains_skip_validation"])`, `assertIn("--skip-validation", timing_command)`, and `assertEqual(timing["timing_floor_sec"], 0.100)`.

### 4. Goal1093 supersedes the Goal1076/1078 mismatch

PASS.

The packet's `supersedes` list names both:

- `docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate_2026-04-28.json`
- `docs/reports/goal1078_goal1076_artifact_intake_after_pod_2026-04-29.json`

The Goal1079 two-AI consensus (ACCEPT) independently confirmed that Goal1076 failed the 100 ms timing floor and that the Goal1078 intake status was `timing_floor_not_met`. Goal1092 then recorded the Barnes-Hut app as `blocked_pending_contract_supersession` with the explicit next action: *"Define and review a 20M validation/intake contract before spending more cloud time or changing public wording."* Goal1093 is the direct response to that blocked status.

### 5. No public RTX speedup claim, release, or public wording change authorized

PASS.

- `summary.public_speedup_claim_authorized_count` is `0`.
- The `boundary` field, present in both the Python source and all generated artifacts, states: *"Goal1093 prepares a superseding Barnes-Hut contract packet only. It does not run cloud, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."*
- The runner script carries the same boundary in its header comment.
- The test asserts `assertEqual(packet["summary"]["public_speedup_claim_authorized_count"], 0)` and `assertIn("does not authorize public RTX speedup claims", packet["boundary"])`.
- Goal1092 independently confirms `public_speedup_claim_authorized: false` for all three v1 apps; no upstream goal in the evidence chain authorizes a public claim.

---

## Additional Observations

- The runner uses `set -euo pipefail` and guards on a non-empty `RTDL_SOURCE_COMMIT` before proceeding, refusing to collect artifacts without a source commit anchor. This is consistent with prior pod-run practice.
- `nvidia-smi` is called before any benchmark, satisfying standard GPU environment documentation.
- The `validation_rows_with_skip_validation` list in `summary` is empty, providing a machine-readable assertion that no validation row was accidentally marked with `--skip-validation`.
- Artifact-to-source consistency: the committed `.json` and `.md` reports and the `.sh` runner are bit-for-bit consistent with what `build_packet()` / `to_shell()` / `to_markdown()` produce from the checked-in Python source.

---

## Verdict

**ACCEPT.**

All five required checks pass. Goal1093 is a well-scoped contract-packet preparation goal. It establishes a clean, shared depth-8 contract for subsequent cloud validation and timing, correctly supersedes the Goal1076/1078 timing-floor failure, and makes no unauthorized public claims or release decisions.
