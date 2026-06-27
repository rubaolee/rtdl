# Goal1087 Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

Goal1087 updates the Goal1085 robot chunked Embree baseline runner generator to add resumable execution controls. The review examines the packet script, generated runner, test suite, JSON artifact, and the Goal1087 handoff document.

---

## Checklist Results

### 1. Runner supports start/end chunk range

PASS. The generated runner (`goal1085_robot_chunked_embree_baseline_runner.sh`) exports `RTDL_GOAL1085_START_CHUNK` (default `0`) and `RTDL_GOAL1085_END_CHUNK` (default `179`). The loop is `for chunk_index in $(seq "${RTDL_GOAL1085_START_CHUNK}" "${RTDL_GOAL1085_END_CHUNK}")`. Range validation rejects inverted ranges and out-of-bounds values with `exit 2`. The generator (`to_shell()`) embeds these controls programmatically, so regeneration preserves them.

### 2. Skip-existing defaults to on

PASS. The runner sets `RTDL_GOAL1085_SKIP_EXISTING="${RTDL_GOAL1085_SKIP_EXISTING:-1}"`. The skip guard uses `[ -s "${output_json}" ]` (non-empty file test), which correctly avoids resuming on partial or zero-byte artifacts. Default is `1` (enabled).

### 3. Generated command still writes chunk_.json

PASS. The output path in the command is `docs/reports/goal1085_robot_chunked_embree_baseline/chunk_${chunk_index}.json`. The `output_json` variable on the preceding line constructs the identical path and is used by the skip guard, so both the guard and the command reference the same artifact location. No output path regression introduced.

### 4. Tests cover the controls

PASS. `test_cli_writes_runner_without_running_heavy_baseline` asserts all three resume controls appear in the generated runner (`RTDL_GOAL1085_START_CHUNK`, `RTDL_GOAL1085_END_CHUNK`, `RTDL_GOAL1085_SKIP_EXISTING`), that the `seq` range invocation is present, and that `chunk_${chunk_index}.json` is the output path. `test_packet_splits_36m_robot_baseline_into_180_chunks` asserts `public_speedup_claim_authorized` is `False` and `valid` is `True`. Coverage is adequate for a runner-generation goal.

### 5. Boundary guards: no heavy baseline run, no RTX speedup claim, no release, no public wording change

PASS. The JSON artifact carries `"public_speedup_claim_authorized": false`. The `boundary` field in both the JSON and the markdown states explicitly that Goal1085 (and by extension Goal1087) does not run the heavy baseline, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims. The Goal1087 handoff document repeats this boundary without modification. No execution of the 180-chunk workload is triggered by any artifact in this goal.

---

## Minor Observations (non-blocking)

- The actual command on runner line 25 embeds the output path directly (`chunk_${chunk_index}.json`) rather than referencing `${output_json}`. Both expand identically; no functional divergence.
- The test does not assert that `chunk_${chunk_index}.json` appears specifically as the `--output-json` argument value, only that the string appears anywhere in the runner. This is acceptable for a generator-verification test.

---

## Summary

Goal1087 is a narrow execution-ergonomics update. All five required controls are present, defaults are safe, no boundary has been crossed, and the test suite exercises the generated controls without invoking the heavy workload. No blocking issues found.

**Verdict: ACCEPT**
