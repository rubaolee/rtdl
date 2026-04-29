# Goal1086 Claude Review — Robot Chunked Embree Baseline Intake

**Date:** 2026-04-29
**Reviewer:** Claude (claude-sonnet-4-6)
**Verdict:** ACCEPT

---

## Scope

This review covers:

- `scripts/goal1086_robot_chunked_embree_baseline_intake.py`
- `tests/goal1086_robot_chunked_embree_baseline_intake_test.py`
- `docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json`
- `docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.md`
- `docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.json` (upstream artifact)

---

## Checklist Findings

### 1. Expected scale: 180 chunks × 200k poses = 36M total

PASS. The script defines constants at module level:

```
EXPECTED_CHUNKS       = 180
EXPECTED_CHUNK_POSES  = 200_000
EXPECTED_TOTAL_POSES  = 36_000_000
EXPECTED_OBSTACLES    = 4096
```

The upstream Goal1085 packet records identical values (`chunk_count: 180`, `chunk_pose_count: 200000`, `total_pose_count: 36000000`, `obstacle_count: 4096`). The `complete` predicate in `build_intake` enforces all four conditions simultaneously before setting `status: "complete"`.

### 2. Missing chunks reported without failing the audit tool

PASS. The tool separates reportability (`valid`) from completeness (`status`). The `valid` key is unconditionally set to `True`; `main()` exits 0 when `valid` is true. Missing or unexpected chunk indices are written into `observed.missing_indices` and `observed.unexpected_indices` for human inspection, but do not cause a non-zero exit. The produced JSON for the current run correctly shows `status: "missing_or_invalid_chunks"` with all 180 indices listed while `valid: true` is preserved. Test `test_missing_default_chunks_are_reported_without_authorizing_claims` explicitly asserts this contract.

### 3. Complete synthetic set aggregates native-anyhit sums correctly

PASS. Test `test_complete_temp_chunk_set_aggregates_phase_sums` writes 180 synthetic chunk files each with `native_anyhit_query: 0.25` seconds, then asserts:

- `native_anyhit_sum_sec == 45.0` (180 × 0.25)
- `native_anyhit_median_chunk_sec == 0.25`
- `total_pose_count == 36_000_000`
- `status == "complete"`

The aggregation in `build_intake` uses `sum(native_query_samples)` and `statistics.median(native_query_samples)`, which are correct for these purposes.

### 4. Same-total-work vs. same-single-launch limitation explicit

PASS. The `interpretation` field in every output artifact reads:

> "it does not by itself authorize a speedup claim against the 36M single RTX timing artifact because the comparison boundary is same-total-work, not same-single-launch, and still requires 2+ AI review."

The Goal1085 upstream packet independently confirms the same framing:

> "It is a same-total-work engineering baseline, not a same-single-launch baseline, until artifact intake and 2+ AI review decide whether the comparison boundary is acceptable."

The limitation is consistent and explicit across all artifacts in the chain.

### 5. No public RTX speedup claim or release/public wording change authorized

PASS. `public_speedup_claim_authorized: false` is hardcoded in `build_intake` (not derived from any computation) and appears in both the JSON output and the upstream Goal1085 packet. The `boundary` field in every output states:

> "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."

Tests assert `public_speedup_claim_authorized` is `False` for both complete and incomplete intake states. No release-facing or public-wording language appears anywhere in the script or produced artifacts.

---

## Minor Observations (non-blocking)

- `valid` is always `True` in current code, making the `return 0 if payload["valid"] else 1` branch in `main()` unreachable. This is consistent with the design intent (the tool is a reporter, not a gate), but reviewers should be aware the exit code provides no signal beyond tool failure.
- `test_missing_default_chunks_are_reported_without_authorizing_claims` runs against the real production input directory. Once actual chunk files are deposited, this test will change behavior. It is not a defect at this stage, but should be noted for future maintenance.
- The `build` directory is assumed to exist for the temp-directory tests (line 49 of the test file). No assertion or setup ensures it is present, though this is a minor operational concern.

---

## Summary

Goal1086 correctly implements an intake/aggregation tool that: enforces the 180×200k=36M scale contract, reports gaps without aborting, aggregates timing sums with a verified synthetic test, makes the same-total-work boundary explicit throughout, and carries no authorized public speedup claim or release action. All five specific review criteria are satisfied.

**Verdict: ACCEPT**
