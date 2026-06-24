# Goal1096 Claude Follow-Up Review — Post-Remediation

Date: 2026-04-29  
Reviewer: Claude (claude-sonnet-4-6)  
Scope: `scripts/goal1096_current_rtx_pod_artifact_intake.py`, `tests/goal1096_current_rtx_pod_artifact_intake_test.py`  
Prior review: `docs/reports/goal1096_claude_review_2026-04-29.md`

Overall verdict: **PASS — prior Finding 2 closed, no new blocker**

---

## Summary of prior findings and remediation status

| Finding | Prior verdict | Remediation status |
| --- | --- | --- |
| Finding 1 — `valid=True` with all artifacts missing | Design concern, no code change required | Unchanged — no action was requested |
| Finding 2 — Test-coverage gap for 8 blocking paths | Gap, recommended closing before adjudicating real artifacts | **CLOSED** |

---

## Finding 2 — Blocking-path test coverage (prior gap)

The prior review identified eight blocking paths confirmed by code inspection but not exercised by any test. The remediation added three new test cases:

- `test_common_blocking_paths_are_covered` — a single `unittest.subTest` table covering six sub-cases
- `test_malformed_json_blocks`
- `test_unknown_app_blocks_review_row`

Mapping each prior gap to the new tests:

| Prior uncovered path | Covered now | Test / sub-case |
| --- | --- | --- |
| `skip_validation` mismatch | YES | `skip_validation_mismatch` subTest |
| Wrong `schema_version` | YES | `wrong_schema` subTest |
| `scenario.mode` not `"optix"` | YES | `non_optix_mode` subTest |
| Facility missing `coordinate_mapping` | YES | `facility_missing_coordinate_mapping` subTest |
| Barnes-Hut wrong contract field | YES (tree_depth mismatch) | `barnes_wrong_contract` subTest |
| Barnes-Hut timing row no `optix_query_sec` median | YES | `barnes_timing_missing_median` subTest |
| Malformed / unreadable JSON | YES | `test_malformed_json_blocks` |
| Unknown `app` field | YES | `test_unknown_app_blocks_review_row` |

All eight paths are now exercised. Each new test asserts `valid=False`, `overall_status="blocked"`, and `blocked_count=1`, which is the correct expected behavior for every blocking path.

One partial note: the `barnes_wrong_contract` subTest exercises a `barnes_tree_depth` mismatch only. The two sibling checks (`hit_threshold`, `node_count`) are on the same sequential code path in `_validate_barnes` and are not individually exercised. This is acceptable — the three checks share identical structure and a single-field mismatch is sufficient to confirm the guard fires. This is not a new gap.

**Finding 2: CLOSED.**

---

## Coordinate-mapping tuple fix

The prior review flagged "facility artifact missing `coordinate_mapping`" as an untested blocking path. Two changes address this:

**1. Script validation (confirmed correct).**
`_validate_facility` checks:
```python
if _nested(artifact, ("scenario", "coordinate_mapping")) != "copy_local_recentered_queries_canonical_depots":
    return "blocked", "facility artifact is missing recentered coordinate mapping", None
```
`_nested` takes a `tuple[str, ...]` and walks `artifact["scenario"]["coordinate_mapping"]`. The test helper `_artifact()` places `coordinate_mapping` inside the `scenario_payload` dict assigned to `artifact["scenario"]`, so the lookup path is correct.

**2. Happy-path test updated.**
`test_all_current_artifacts_pass_but_do_not_authorize_claims` and `test_facility_bad_oracle_blocks` both now pass `coordinate_mapping="copy_local_recentered_queries_canonical_depots"` to the facility artifact. Without this parameter the facility row would be blocked by the coordinate-mapping check regardless of oracle outcome, which would have made those tests vacuous for their stated purpose. The fix is correct.

**3. Negative case added.**
`facility_missing_coordinate_mapping` subTest in `test_common_blocking_paths_are_covered` passes a facility artifact constructed without the `coordinate_mapping` keyword argument (so the key is absent from `artifact["scenario"]`). The test asserts `overall_status="blocked"` and `blocked_count=1`. This correctly confirms the guard fires on absence.

---

## Minor observations (no new blockers)

**`# pragma: no cover` on `_load_json` except branch is now stale.**  
`test_malformed_json_blocks` writes a single open brace `{` to the artifact path. `json.loads("{")` raises `JSONDecodeError`, which is caught by the `except Exception` clause. That branch is now covered by the test, but the `# pragma: no cover` annotation remains. This is cosmetic — it affects coverage reporting only, not behavior. The test correctly verifies the blocking outcome. No action required before using the intake to adjudicate artifacts; can be cleaned up at any time.

**Finding 1 unchanged.**  
`valid=True` when all artifacts are missing is intentional, tested, and documented in the prior review. No code change was requested and none was made. Downstream consumers must read `overall_status` explicitly. This remains a design note, not a defect.

---

## Conclusion

The test suite added by remediation closes every blocking-path gap identified in Finding 2 of the prior review. The coordinate-mapping check in `_validate_facility` uses the correct 2-tuple path, and both the passing and failing cases are now covered by tests. No new functional defects were introduced. Finding 1 (design concern, no action required) is unchanged. The intake is ready to adjudicate real cloud artifacts when they arrive.
