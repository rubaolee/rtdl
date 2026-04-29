# Goal1089 Claude Review

Date: 2026-04-29
Reviewer: Claude Sonnet 4.6
Verdict: **ACCEPT**

## Scope

Goal1089 adds distinct pose-id ranges per chunk to the robot chunked Embree baseline.
The review covers five technical criteria and one boundary constraint.

---

## Criterion 1 — pose_id_start defaults preserve existing behavior

**PASS.**

- `make_scaled_case(...)` at `examples/rtdl_robot_collision_screening_app.py:97` declares `pose_id_start: int = 1`.
- `build_artifact(...)` at `scripts/goal839_robot_pose_count_baseline.py:306` declares `pose_id_start: int = 1`.
- The CLI `--pose-id-start` argument at `scripts/goal839_robot_pose_count_baseline.py:343` sets `default=1`.

All existing callers that omit `pose_id_start` continue to receive the value `1`,
which is the pre-Goal1089 implicit behavior. No regression risk.

---

## Criterion 2 — chunk i uses pose_id_start = i * 200000 + 1

**PASS.**

The generated runner at `scripts/goal1085_robot_chunked_embree_baseline_runner.sh:25` invokes:

```
--pose-id-start $(( chunk_index * 200000 + 1 ))
```

The packet builder at `scripts/goal1085_robot_chunked_embree_baseline_packet.py:44-45`
embeds the same formula as the command template, parameterised over
`CHUNK_POSE_COUNT = 200_000`. The formula and the constant are consistent.

---

## Criterion 3 — baseline artifacts record pose_id_start

**PASS.**

Both backend paths in `scripts/goal839_robot_pose_count_baseline.py` write
`"pose_id_start": pose_id_start` into the `benchmark_scale` dict of the artifact:

- CPU oracle path: lines 179–180.
- Embree path: lines 267–268.

The field is present unconditionally, including for the default `pose_id_start=1` case.

---

## Criterion 4 — intake validates expected pose_id_start per chunk

**PASS.**

`scripts/goal1086_robot_chunked_embree_baseline_intake.py:47–53` builds `scale_ok_chunks`
with the condition:

```python
chunk.get("benchmark_scale", {}).get("pose_id_start")
    == _chunk_index(path) * EXPECTED_CHUNK_POSES + 1
```

The `complete` flag at line 71 requires `len(scale_ok_chunks) == EXPECTED_CHUNKS`,
so any chunk whose recorded `pose_id_start` does not match its file index causes
the intake to report `missing_or_invalid_chunks`. The validation is structural and
does not require the intake to have run heavy baseline data.

---

## Criterion 5 — tests cover the change

**PASS.**

Coverage is provided across four test files:

| Test | File | What is verified |
|---|---|---|
| `test_rejects_invalid_scaled_counts` | `goal736_robot_collision_embree_scaled_test.py:47` | `pose_id_start=0` raises `ValueError` |
| `test_scaled_case_can_start_at_later_pose_id_for_chunked_baselines` | `goal736_robot_collision_embree_scaled_test.py:55` | `pose_id_start=200001` produces pose_ids `[200001, 200002, 200003]` and correct ray_id encoding |
| `test_robot_pose_count_artifact_records_pose_id_start` | `goal839_local_baseline_collectors_test.py:81` | `benchmark_scale["pose_id_start"] == 200001`; first colliding sample pose_id is `200002` (even-id pattern) |
| `test_cli_writes_runner_without_running_heavy_baseline` | `goal1085_robot_chunked_embree_baseline_packet_test.py:28` | Generated runner contains `--pose-id-start $(( chunk_index * 200000 + 1 ))` |
| `test_complete_temp_chunk_set_aggregates_phase_sums` | `goal1086_robot_chunked_embree_baseline_intake_test.py:57` | Complete set of 180 chunks, each with `pose_id_start=index * 200_000 + 1`, reaches `status == "complete"` |
| `test_invalid_scale_keeps_status_blocked` | `goal1086_robot_chunked_embree_baseline_intake_test.py:76` | Wrong `pose_count` blocks complete status; `scale_ok_chunk_count == 0` |

One gap noted for completeness: there is no dedicated test exercising wrong `pose_id_start`
alone (i.e., all other scale fields correct but `pose_id_start` mismatched). The existing
tests are sufficient to validate the formula path. A dedicated negative test for
`pose_id_start` mismatch would be incrementally useful but is not a blocker.

---

## Criterion 6 — boundary: no heavy baseline, no public RTX speedup claim, no release, no public wording change authorized

**PASS.**

Every artifact and script in scope carries an explicit boundary statement:

- `goal1085_robot_chunked_embree_baseline_packet.py:68–71`: boundary field, `public_speedup_claim_authorized: False`.
- `goal1085_robot_chunked_embree_baseline_runner.sh:4`: "Boundary: does not authorize public RTX speedup claims."
- `goal1086_robot_chunked_embree_baseline_intake.py:103`: `public_speedup_claim_authorized: False`.
- `goal1086_robot_chunked_embree_baseline_intake.py:109–113`: boundary field.
- `docs/reports/goal1089_robot_chunk_pose_id_offset_update_2026-04-29.md`: boundary section explicit.

The runner generates shell scripts; it does not execute them. No heavy baseline run
is performed by the code introduced in this goal. No public wording files are modified.

---

## Summary

All five technical criteria pass cleanly and the boundary constraint is maintained
throughout. The only observation is a minor test-coverage gap (no negative test for
a `pose_id_start`-only mismatch in the intake), which does not affect correctness
of the implementation and does not warrant blocking.

**Verdict: ACCEPT**
