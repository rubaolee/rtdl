# Goal1081 Same-Scale Baseline Execution Packet — Formal Review

Date: 2026-04-29  
Reviewer: Claude (claude-sonnet-4-6)  
Verdict: **ACCEPT**

---

## Checklist

| Check | Required | Observed | Result |
| --- | --- | --- | --- |
| Facility command scale | 2,500,000 copies | `--copies 2500000`; `scale.copies = 2500000` | PASS |
| Robot command scale — poses | 36,000,000 poses | `--pose-count 36000000`; `scale.pose_count = 36000000` | PASS |
| Robot command scale — obstacles | 4,096 obstacles | `--obstacle-count 4096`; `scale.obstacle_count = 4096` | PASS |
| Barnes-Hut blocked | `command: []`, `not_ready` | `baseline_kind: future_contract`, `recommended_host: not_ready`, `command: []` | PASS |
| No public speedup claim authorized | 0 rows | `public_speedup_claim_authorized_count: 0`; all three rows `false` | PASS |
| No public wording change | boundary explicit | Boundary string repeated in script, JSON, and MD; all rows `required_before_public_wording: true` | PASS |
| No release authorization | boundary explicit | Boundary string: "does not authorize release" | PASS |
| Packet `valid` flag | `true` | `"valid": true` in JSON; test asserts `packet["valid"]` | PASS |
| Script / JSON / MD consistency | must agree | JSON and MD are machine-generated from the same `build_packet()` call; content matches exactly | PASS |

---

## Per-Row Analysis

### Row 0 — facility_knn_assignment

- Goal1080 source confirms the RTX artifact was at 2.5M copies / 10M queries, while the prior same-semantics baseline was at 20k copies — a 125× scale mismatch that blocked public wording.
- Goal1081 command addresses exactly this gap: `--copies 2500000 --iterations 1`.
- Target artifact path, baseline kind (`cpu_oracle_same_scale`), and output JSON path are internally consistent.

### Row 1 — robot_collision_screening

- Goal1080 source confirms RTX artifact at 36M poses / 4096 obstacles; prior Embree baseline was 200k poses / 1024 obstacles.
- Goal1081 command addresses exactly this gap: `--pose-count 36000000 --obstacle-count 4096 --worker-count 8`.
- Backend flag (`--backend embree`) and baseline kind (`embree_same_scale`) are consistent.

### Row 2 — barnes_hut_force_app

- Goal1080 records `decision: needs_reviewed_20m_validation_and_baseline` and `timing_status: timing_below_floor` for the reviewed 1M row. The 20M probe is engineering evidence only.
- Goal1081 correctly carries this forward: `baseline_kind: future_contract`, `command: []`, `recommended_host: not_ready`.
- Purpose string explicitly requires a reviewed intake contract and a decision on Python input/packing overhead before any baseline collection.
- No command is emitted; no speedup ratio is possible.

---

## Test Coverage

Four test methods cover all critical invariants:

- `test_packet_is_valid_and_authorizes_no_public_speedup_claims` — validates `valid`, row count, `public_speedup_claim_authorized_count`, and `required_before_public_wording`.
- `test_facility_baseline_matches_rtx_scale` — asserts `copies == 2_500_000` and verifies CLI string.
- `test_robot_baseline_matches_rtx_scale` — asserts `pose_count == 36_000_000`, `obstacle_count == 4096`, and verifies CLI string.
- `test_barnes_hut_is_not_executable_until_contract_is_superseded` — asserts `command == []` and markdown renders "not ready".

Coverage is sufficient for the boundary constraints of this goal.

---

## Findings

No findings. All scale parameters match the RTX artifacts on record. Barnes-Hut is correctly blocked. No speedup claim is authorized anywhere in the packet. The packet scope is limited to command preparation only; no execution, no public wording change, no release action is taken.

---

## Verdict

**ACCEPT**

Goal1081 is correctly scoped, internally consistent, and consistent with the Goal1080 audit. The same-scale baseline commands for facility (2.5M copies) and robot (36M poses / 4096 obstacles) are ready for execution on the recommended hosts. Barnes-Hut remains blocked pending contract redesign. No authorized public RTX speedup claim or release action is present.
