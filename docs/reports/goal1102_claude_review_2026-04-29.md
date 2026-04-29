# Goal1102 Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT with one semantic concern**

---

## What was reviewed

- `scripts/goal1102_current_contract_baseline_intake.py`
- `tests/goal1102_current_contract_baseline_intake_test.py`
- `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json`
- `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md`
- `docs/reports/goal1101_two_ai_consensus_2026-04-29.md` (upstream contract)

---

## Checklist

### Four expected artifacts

The `EXPECTED` list names exactly the four artifacts that Goal1101's two-AI consensus document declares as the intended output:

| Name | Artifact file |
| --- | --- |
| `facility_cpu_oracle` | `facility_recentered_2_5m_cpu_oracle_baseline.json` |
| `facility_embree` | `facility_recentered_2_5m_embree_baseline.json` |
| `barnes_hut_validation_embree` | `barnes_hut_depth8_4096_embree_validation_baseline.json` |
| `barnes_hut_timing_embree` | `barnes_hut_depth8_20m_embree_timing_baseline.json` |

app, path_name, backend, scenario, query_count, barnes_tree_depth, hit_threshold, and the matches_oracle / timing-only null distinction are all captured per-row. **Pass.**

### Missing-artifact waiting state

When artifacts are absent the script emits `status: "missing"` per row and `overall_status: "waiting_for_baseline_artifacts"`. The current run output confirms all four rows are missing and the status is correctly set. **Pass.**

### Bad-artifact blocking including public-claim flag

`_validate` blocks on:

- wrong `schema_version`
- `app`, `path_name`, or `backend` mismatch
- `public_speedup_claim_authorized is not False` (strict identity check, catches `None` and any truthy value)
- absent `source_commit`
- `scenario`, `query_count`, `barnes_tree_depth`, `hit_threshold` mismatches
- `matches_oracle is not True` when required
- `matches_oracle is not None` for timing-only rows
- absent `native_query_sec.median_sec`

The test `test_intake_blocks_bad_claim_flag` injects `public_speedup_claim_authorized: True` into a single artifact and confirms `status: "blocked"` with the correct issue string and `overall_status: "waiting_for_baseline_artifacts"`. **Pass.**

Output rows always carry `"public_speedup_claim_authorized": false` regardless of artifact content, so no bad flag can propagate through the intake layer. **Pass.**

### No-public-speedup-claim boundary preservation

The boundary string is written into:

- the `"boundary"` field of the JSON output
- the `"overall_status"` value (`ready_for_2ai_baseline_review_not_public_claim` makes explicit this is not a public claim)
- both the header section and the `## Boundary` footer of the markdown output
- the `to_markdown` test's assertion on `"does not authorize public RTX speedup claims"`

The boundary is structurally enforced, not just documentary. **Pass.**

---

## Concern: `valid: true` when all artifacts are missing

`valid` is computed as:

```python
summary["row_count"] == len(EXPECTED) and summary["public_speedup_claim_authorized_count"] == 0
```

When all four artifacts are absent, `row_count` is still 4 (missing rows are counted) and no bad flags exist, so `valid` evaluates to `true`. The current JSON output shows exactly this: `"valid": true` alongside four `"status": "missing"` rows.

This is internally consistent (the test explicitly asserts `self.assertTrue(payload["valid"])` for the all-missing case), but the field name is misleading. A downstream consumer reading only `valid` would incorrectly conclude the intake completed successfully. The actual readiness signal lives in `overall_status: "waiting_for_baseline_artifacts"`, which is correct.

**Risk:** low for any consumer that reads `overall_status`, but a consumer that short-circuits on `valid: true` could skip the artifact gate. The field would be less ambiguous renamed to `intake_structurally_valid` or if its semantics were documented in the boundary string.

---

## Test coverage

| Test | What it checks |
| --- | --- |
| `test_default_intake_waits_when_artifacts_are_missing` | Missing state, row count, no claim flags |
| `test_intake_accepts_complete_synthetic_artifact_set` | All four OK, ready status, no blocks |
| `test_intake_blocks_bad_claim_flag` | `public_speedup_claim_authorized: True` → blocked |
| `test_markdown_preserves_no_claim_boundary` | Boundary text in markdown output |

Coverage is adequate for the four design properties under review. No test exercises a partially-complete set (some ok, some missing), but that is a minor gap and the per-row logic is simple enough that it does not represent a risk.

---

## Summary

Goal1102 correctly identifies the four Goal1101 artifacts, honestly reports their absence as a waiting state, blocks bad artifacts including public-claim flags on strict identity, and preserves the no-public-speedup-claim boundary in every output channel. The one concern — `valid: true` when all artifacts are missing — is semantically confusing but low-risk given the unambiguous `overall_status` field. No source changes are required to accept Goal1102.
